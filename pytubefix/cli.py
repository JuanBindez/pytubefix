#!/usr/bin/env python3
"""pytubefix - command line interface, Unix style.

    pytubefix [download] [options] URL...    download videos/audio; playlists and channels are detected
    pytubefix playlist [options] URL|ID...   download a whole playlist (or channel)
    pytubefix streams URL                    list the available streams
    pytubefix info URL                       show video metadata
    pytubefix captions URL [-c CODE]         list caption tracks / print one as SRT
    pytubefix search QUERY...                search videos
    pytubefix report URL                     save a playback report for offline debugging

`pytubefix URL` is shorthand for `pytubefix download URL`.

Conventions:
  * data goes to stdout; messages and the progress bar go to stderr;
  * silent on success (the progress bar is drawn only on a terminal);
  * errors look like "pytubefix: URL: message"; exit status 0 ok, 1 error,
    2 usage error, 130 interrupted (Ctrl+C), 143 terminated (SIGTERM);
  * '-' means stdin/stdout; a failure on one video does not stop the others;
  * files are built in a private temp dir and renamed into place, and are
    never overwritten without -f.

`on_progress` is kept as a public helper: the README uses
`YouTube(url, on_progress_callback=on_progress)`.
"""

import argparse
import datetime as dt
import gzip
import itertools
import json
import logging
import os
import re
import shutil
import signal
import subprocess  # nosec
import sys
import tempfile
import time
import traceback

from pytubefix import __version__
from pytubefix import Channel, Playlist, Search, YouTube
from pytubefix.helpers import safe_filename, setup_logger

PROG = "pytubefix"
NAME_MAX = 255
COMMANDS = ("download", "playlist", "streams", "info", "captions", "search", "report")


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

class CliError(Exception):
    def __init__(self, message, path=None):
        super().__init__(message)
        self.message = message
        self.path = path


class Fatal(CliError):
    """Aborts the whole run instead of just the current video."""


def human(n):
    n = float(n)

    for unit in ("B", "KiB", "MiB"):
        if n < 1024:
            return f"{n:.0f}{unit}" if unit == "B" else f"{n:.1f}{unit}"
        n /= 1024

    return f"{n:.1f}GiB"


def duration(seconds):
    try:
        s = int(seconds)
    except (TypeError, ValueError):
        return "-"

    h, rest = divmod(s, 3600)
    m, s = divmod(rest, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def fit_name(stem, ext):
    """Truncates stem so that stem + ext fits in NAME_MAX bytes."""
    stem = stem or "video"

    while len((stem + ext).encode("utf-8")) > NAME_MAX and len(stem) > 1:
        stem = stem[:-1]

    return stem + ext


def check_length(name):
    size = len(os.fsencode(name))

    if size > NAME_MAX:
        raise CliError(f"File name too long ({size} bytes, limit {NAME_MAX})")


def _number(stream, attr):
    m = re.match(r"\d+", str(getattr(stream, attr, None) or ""))
    return int(m.group()) if m else 0


def res_value(stream):
    return _number(stream, "resolution")


def abr_value(stream):
    return _number(stream, "abr")


def fps_value(stream):
    return getattr(stream, "fps", None) or 0


def positive_int(value):
    try:
        n = int(value)
    except ValueError:
        n = 0

    if n < 1:
        raise argparse.ArgumentTypeError(f"invalid value {value!r} (expected an integer >= 1)")

    return n


def write_atomic(dest, data, force):
    if os.path.lexists(dest) and not force:
        raise CliError("already exists (use -f to overwrite)", dest)

    parent = os.path.dirname(dest) or "."
    os.makedirs(parent, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix=".pytubefix-", dir=parent) as work:
        tmp = os.path.join(work, "out")

        with open(tmp, "wb") as f:
            f.write(data)

        os.replace(tmp, dest)


# --------------------------------------------------------------------------
# Progress bar and logging
# --------------------------------------------------------------------------

class ProgressBar:
    """Progress line on stderr, drawn only when stderr is a terminal.

        [2/10] Video title        ↳ |██████████░░░░░░░░░░|  52.1%  14.2MiB/27.3MiB  1.8MiB/s

    Each finished download keeps its last line (like curl/wget/pip). If the
    total size is unknown, only the downloaded size and speed are shown.
    """

    def __init__(self, enabled=True):
        self.enabled = enabled
        self.prefix = ""
        self.label = ""
        self._active = False
        self._dirty = False
        self._latest = None
        self._key = None
        self._t0 = 0.0
        self._last = 0.0

    @staticmethod
    def _glyphs():
        try:
            "█░↳".encode(sys.stderr.encoding or "ascii")
            return "█", "░", "↳"
        except (UnicodeEncodeError, LookupError):
            return "#", "-", ">"

    def update(self, stream, bytes_remaining):
        if not self.enabled or not sys.stderr.isatty():
            return

        total = int(getattr(stream, "filesize", 0) or 0)
        finished = total > 0 and bytes_remaining <= 0
        now = time.monotonic()
        key = (getattr(stream, "itag", None), self.prefix, self.label)

        if key != self._key:
            self._key, self._t0, self._last = key, now, 0.0

        self._latest = (stream, bytes_remaining)
        self._dirty = True

        if finished or now - self._last >= 0.1:
            self._draw(now)

    def _draw(self, now):
        stream, bytes_remaining = self._latest
        total = int(getattr(stream, "filesize", 0) or 0)
        done = total - bytes_remaining if total else -bytes_remaining
        self._last = now
        self._dirty = False
        full, empty, arrow = self._glyphs()
        speed = max(done, 0) / max(now - self._t0, 1e-6)
        columns = shutil.get_terminal_size((80, 24)).columns
        name_width = max(8, min(30, columns // 3))
        name = (self.prefix + self.label)[:name_width].ljust(name_width)

        if total:
            frac = min(max(done / total, 0.0), 1.0)
            stats = f" {frac * 100:5.1f}%  {human(done)}/{human(total)}  {human(speed)}/s"
            width = max(8, min(40, columns - len(name) - len(stats) - 6))
            filled = int(round(width * frac))
            line = f"{name} {arrow} |{full * filled}{empty * (width - filled)}|{stats}"
        else:
            line = f"{name} {arrow} {human(max(done, 0))}  {human(speed)}/s"

        sys.stderr.write("\r\x1b[K" + line[: columns - 1])
        sys.stderr.flush()
        self._active = True

    def finish(self):
        """Draws the final state, keeps the line and moves to the next one."""
        if self._latest is not None and self._dirty and self.enabled and sys.stderr.isatty():
            self._draw(time.monotonic())

        if self._active:
            sys.stderr.write("\n")
            sys.stderr.flush()
            self._active = False

        self._latest = None

    def clear(self):
        """Erases an unfinished line (before printing a message)."""
        if self._active:
            sys.stderr.write("\r\x1b[K")
            sys.stderr.flush()
            self._active = False


_LIBRARY_BAR = ProgressBar()


def on_progress(stream, chunk, bytes_remaining):  # pylint: disable=W0613
    """Progress callback for library use: YouTube(url, on_progress_callback=on_progress)."""
    _LIBRARY_BAR.update(stream, bytes_remaining)

    if getattr(stream, "filesize", 0) and bytes_remaining <= 0:
        _LIBRARY_BAR.finish()


class Log:
    def __init__(self, verbose=False, quiet=False, debug=False):
        self.quiet = quiet
        self.verbose = verbose and not quiet
        self.debug = debug
        self.failures = 0
        self.bar = ProgressBar(enabled=not quiet)

    def _emit(self, msg):
        self.bar.clear()
        sys.stderr.write(f"{PROG}: {msg}\n")
        sys.stderr.flush()

    def error(self, msg):
        self.failures += 1
        self._emit(msg)

    def warn(self, msg):
        if not self.quiet:
            self._emit(f"warning: {msg}")

    def note(self, msg):
        if self.verbose:
            self._emit(msg)

    def fail(self, exc, path=None):
        if isinstance(exc, CliError):
            where, msg = exc.path or path, exc.message
        elif isinstance(exc, OSError):
            where, msg = exc.filename or path, exc.strerror or str(exc)
        else:
            where, msg = path, str(exc)

        msg = " ".join(msg.split()) or exc.__class__.__name__
        self.error(f"{where}: {msg}" if where else msg)

        if self.debug:
            sys.stderr.write("".join(traceback.format_exception(exc)))


# --------------------------------------------------------------------------
# Input: URLs, playlists and channels
# --------------------------------------------------------------------------

_PLAYLIST_ID = re.compile(r"^(PL|UU|OL|LL|FL|RD)[\w-]{10,}$")


def kind_of(url):
    u = url.lower()

    if "/playlist" in u or ("list=" in u and "watch?v=" not in u and "youtu.be/" not in u):
        return "playlist"

    if re.search(r"youtube\.com/(@|channel/|c/|user/)", u):
        return "channel"

    return "video"


def effective_kind(url, forced):
    kind = kind_of(url)
    return "playlist" if forced and kind == "video" else kind


def playlist_url(arg):
    """`pytubefix playlist PLxxxx` accepts a bare playlist id."""
    if _PLAYLIST_ID.match(arg):
        return f"https://www.youtube.com/playlist?list={arg}"

    return arg


def collect_urls(args, parser):
    items = list(args.urls)

    if not items:
        if sys.stdin.isatty():
            parser.error("no URL given (use '-' to read URLs from stdin)")

        items = ["-"]

    urls = []

    for item in items:
        if item == "-":
            for line in sys.stdin:
                line = line.strip()

                if line and not line.startswith("#"):
                    urls.append(line)
        else:
            urls.append(item)

    if not urls:
        parser.error("no URL given")

    return urls


def make_yt(url, args):
    kwargs = {"use_oauth": True, "allow_oauth_cache": True} if args.oauth else {}
    return YouTube(url, **kwargs)


def open_collection(url, kind):
    return Playlist(url) if kind == "playlist" else Channel(url)


def video_urls_of(collection, limit):
    try:
        urls = collection.video_urls
    except AttributeError:
        urls = (v.watch_url for v in collection.videos)

    return itertools.islice(urls, limit) if limit else urls


def collection_total(collection, limit):
    """Number of videos, when cheaply known (for the [i/N] counter)."""
    try:
        total = int(getattr(collection, "length", None))
    except Exception:
        return limit

    return min(total, limit) if limit else total


def collection_dir(collection, kind):
    """Default directory for a playlist/channel: named after it."""
    try:
        title = collection.title if kind == "playlist" else collection.channel_name
    except Exception:
        title = None

    return fit_name(safe_filename(title), "") if title else kind


# --------------------------------------------------------------------------
# Choosing streams and downloading
# --------------------------------------------------------------------------

def choose(yt, args):
    """Returns [stream] or [video_stream, audio_stream] (to be merged)."""
    streams = yt.streams

    if args.itag is not None:
        stream = streams.get_by_itag(args.itag)

        if stream is None:
            raise CliError(f"itag {args.itag} is not available (see: {PROG} streams URL)")

        return [stream]

    if args.audio or args.audio_format:
        fmt = args.audio_format or "mp4"
        audio = [s for s in streams.filter(progressive=False)
                 if getattr(s, "type", None) == "audio" and s.subtype == fmt]
        best = max(audio, key=abr_value, default=None)

        if best is None:
            raise CliError(f"no {fmt} audio stream available (see: {PROG} streams URL)")

        return [best]

    if args.resolution is None:
        stream = streams.get_highest_resolution()

        if stream is None:
            raise CliError("no progressive stream available (try -r best)")

        return [stream]

    progressive = list(streams.filter(progressive=True))
    video_only = [s for s in streams.filter(progressive=False)
                  if getattr(s, "type", None) == "video"]

    def quality(s):
        return (res_value(s), s.subtype == "mp4", fps_value(s))

    if args.resolution == "best":
        best_v = max(video_only, key=quality, default=None)
        best_p = max(progressive, key=res_value, default=None)

        if best_v is None or (best_p is not None and res_value(best_p) >= res_value(best_v)):
            if best_p is None:
                raise CliError("no stream available")

            return [best_p]
    else:
        want = int(args.resolution)
        same = [s for s in progressive if res_value(s) == want]

        if same:
            return [max(same, key=fps_value)]

        candidates = [s for s in video_only if res_value(s) == want]

        if not candidates:
            raise CliError(f"no {want}p stream available (see: {PROG} streams URL)")

        best_v = max(candidates, key=quality)

    audio = [s for s in streams.filter(progressive=False)
             if getattr(s, "type", None) == "audio"]
    best_a = max(audio, key=lambda s: (s.subtype == "mp4", abr_value(s)), default=None)

    if best_a is None:
        raise CliError("no audio stream to merge with")

    return [best_v, best_a]


def merge(video, audio_stream, audio, out):
    acodec = "copy" if audio_stream.subtype == "mp4" else "aac"
    proc = subprocess.run(  # nosec
        ["ffmpeg", "-nostdin", "-v", "error", "-i", video, "-i", audio,
         "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", acodec, out],
        capture_output=True,
        text=True,
    )

    if proc.returncode != 0:
        raise CliError("ffmpeg failed: " + (proc.stderr.strip() or f"exit status {proc.returncode}"))


def fetch(yt, args, log, out_dir, out_name, to_stdout):
    """Downloads one video. Returns the destination ('-' for stdout) or None if skipped."""
    plan = choose(yt, args)
    merging = len(plan) == 2

    if merging and not shutil.which("ffmpeg"):
        raise CliError("ffmpeg is required to merge video and audio at this resolution, "
                       "but it was not found in PATH")

    title = yt.title

    if merging:
        default = fit_name(safe_filename(title), ".mp4")
    else:
        stream = plan[0]
        default = getattr(stream, "default_filename", None) or fit_name(
            safe_filename(title), "." + (getattr(stream, "subtype", None) or "mp4")
        )

    dest = "-"

    if not to_stdout:
        if out_name:
            name = out_name
            check_length(name)
        else:
            stem, ext = os.path.splitext(default)
            name = fit_name(stem, ext)

        dest = os.path.normpath(os.path.join(out_dir, name))

        if os.path.lexists(dest) and not args.force:
            if args.skip_existing:
                return None

            raise CliError("already exists (use -f to overwrite, or -s to skip)", dest)

        os.makedirs(out_dir, exist_ok=True)

    # Private work dir next to the destination, so the final rename is atomic.
    with tempfile.TemporaryDirectory(
        prefix=".pytubefix-", dir=None if to_stdout else out_dir
    ) as work:
        parts = []

        for i, stream in enumerate(plan):
            sub = os.path.join(work, str(i))
            os.makedirs(sub)
            tag = f" [{'video' if i == 0 else 'audio'}]" if merging else ""
            log.bar.label = f"{title}{tag}"
            # A short name keeps long titles out of the work dir; the real path is returned.
            path = stream.download(output_path=sub, filename="media")
            log.bar.finish()

            if not path or not os.path.exists(path):
                raise CliError("download failed: no file was produced")

            parts.append(path)

        if merging:
            result = os.path.join(work, "merged.mp4")
            merge(parts[0], plan[1], parts[1], result)
        else:
            result = parts[0]

        if to_stdout:
            with open(result, "rb") as f:
                shutil.copyfileobj(f, sys.stdout.buffer)

            sys.stdout.buffer.flush()
        else:
            os.replace(result, dest)

    return dest


# --------------------------------------------------------------------------
# Commands
# --------------------------------------------------------------------------

def plan_output(args, urls, forced, parser):
    """Returns (to_stdout, directory, file_name_or_None)."""
    out = args.output
    many = len(urls) > 1 or any(effective_kind(u, forced) != "video" for u in urls)

    if out == "-":
        if sys.stdout.isatty():
            raise Fatal("refusing to write media data to a terminal (use -o FILE or redirect)")

        if many:
            parser.error("'-o -' needs exactly one video URL")

        return True, None, None

    if out and (os.path.isdir(out) or out.endswith(("/", os.sep)) or many):
        return False, out, None

    if out:
        return False, os.path.dirname(out) or ".", os.path.basename(out)

    return False, ".", None


def list_urls(args, urls, forced, log):
    for url in urls:
        try:
            kind = effective_kind(url, forced)

            if kind == "video":
                print(url)
                continue

            for video_url in video_urls_of(open_collection(url, kind), args.limit):
                print(video_url)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            log.fail(e, url)


def cmd_download(args, parser, log):
    forced = args.force_playlist
    urls = collect_urls(args, parser)

    if forced:
        urls = [playlist_url(u) for u in urls]

    if args.audio_format and (args.itag is not None or args.resolution):
        parser.error("--audio-format cannot be combined with -i or -r")

    if getattr(args, "list", False):
        list_urls(args, urls, forced, log)
        return

    to_stdout, out_dir, out_name = plan_output(args, urls, forced, parser)

    def callback(stream, chunk, bytes_remaining):
        log.bar.update(stream, bytes_remaining)

    def handle(video_url, directory, name, counter=""):
        try:
            log.bar.prefix = counter
            yt = make_yt(video_url, args)
            yt.register_on_progress_callback(callback)
            dest = fetch(yt, args, log, directory, name, to_stdout)

            if dest is None:
                log.note(f"{video_url}: already downloaded, skipped")
            else:
                log.note(f"{video_url} -> {'(stdout)' if dest == '-' else dest}")
        except (KeyboardInterrupt, Fatal):
            raise
        except Exception as e:
            log.fail(e, video_url)

    for url in urls:
        try:
            kind = effective_kind(url, forced)

            if kind == "video":
                handle(url, out_dir, out_name)
                continue

            collection = open_collection(url, kind)
            directory = args.output if args.output else collection_dir(collection, kind)
            total = collection_total(collection, args.limit)

            for i, video_url in enumerate(video_urls_of(collection, args.limit), start=1):
                handle(video_url, directory, None, f"[{i}/{total}] " if total else f"[{i}] ")
        except (KeyboardInterrupt, Fatal):
            raise
        except Exception as e:
            log.fail(e, url)


def cmd_streams(args, parser, log):
    yt = make_yt(args.url, args)
    streams = sorted(
        yt.streams,
        key=lambda s: (getattr(s, "type", "") != "video", -res_value(s), -abr_value(s), -fps_value(s)),
    )

    def val(stream, name):
        v = getattr(stream, name, None)
        return "-" if v in (None, "") else str(v)

    def size(stream):
        try:
            approx = getattr(stream, "filesize_approx", None)
            return human(approx) if approx else "-"
        except Exception:
            return "-"

    rows = [
        (
            val(s, "itag"),
            val(s, "type"),
            getattr(s, "resolution", None) or getattr(s, "abr", None) or "-",
            val(s, "fps"),
            val(s, "mime_type"),
            val(s, "video_codec"),
            val(s, "audio_codec"),
            size(s),
            "yes" if getattr(s, "is_progressive", False) else "no",
        )
        for s in streams
    ]

    if sys.stdout.isatty():
        table = [("ITAG", "TYPE", "QUALITY", "FPS", "MIME", "VCODEC", "ACODEC", "SIZE", "PROG")] + rows
        widths = [max(len(str(r[i])) for r in table) for i in range(len(table[0]))]

        for row in table:
            print("  ".join(str(c).ljust(w) for c, w in zip(row, widths)).rstrip())
    else:
        for row in rows:  # tab separated, no header: easy to parse
            print("\t".join(map(str, row)))


def cmd_info(args, parser, log):
    yt = make_yt(args.url, args)
    print(f"title: {yt.title}")  # required: a failure here is a real error

    for label, attr in (
        ("author", "author"),
        ("length", "length"),
        ("views", "views"),
        ("published", "publish_date"),
        ("thumbnail", "thumbnail_url"),
        ("url", "watch_url"),
        ("id", "video_id"),
    ):
        try:
            value = getattr(yt, attr)
        except Exception:
            continue

        if value is not None:
            print(f"{label}: {value}")


def caption_tracks(captions):
    return [captions[item] if isinstance(item, str) else item for item in captions]


def track_code(track):
    return getattr(track, "language_code", None) or getattr(track, "code", "")


def cmd_captions(args, parser, log):
    yt = make_yt(args.url, args)
    captions = yt.captions

    if not args.code:
        for track in caption_tracks(captions):
            print(f"{track_code(track)}\t{track.name}")

        return

    track = captions.get_by_language_code(args.code)

    if track is None:
        available = ", ".join(track_code(t) for t in caption_tracks(captions)) or "none"
        raise CliError(f"no caption track '{args.code}' (available: {available})")

    data = track.generate_srt_captions().encode("utf-8")

    if args.output in (None, "-"):
        sys.stdout.buffer.write(data)
        sys.stdout.buffer.flush()
    else:
        write_atomic(args.output, data, args.force)
        log.note(f"{args.url} -> {args.output}")


def cmd_search(args, parser, log):
    for video in itertools.islice(Search(" ".join(args.query)).videos, args.limit):
        title = " ".join(str(video.title).split())
        print(f"{video.watch_url}\t{title}\t{duration(video.length)}")


def cmd_report(args, parser, log):
    """Saves the request data as gzip'd JSON for offline debugging."""
    yt = make_yt(args.url, args)
    stamp = int(dt.datetime.now(dt.timezone.utc).timestamp())
    dest = args.output or f"yt-video-{yt.video_id}-{stamp}.json.gz"

    payload = json.dumps(
        {"url": yt.watch_url, "js": yt.js, "watch_html": yt.watch_html, "video_info": yt.vid_info}
    ).encode("utf8")

    write_atomic(dest, gzip.compress(payload), args.force)
    log.note(f"{args.url} -> {dest}")


# --------------------------------------------------------------------------
# Argument parsing
# --------------------------------------------------------------------------

def resolution_arg(value):
    v = value.strip().lower()

    if v == "best":
        return v

    m = re.fullmatch(r"(\d+)p?", v)

    if not m:
        raise argparse.ArgumentTypeError(f"invalid resolution {value!r} (use e.g. 720p, 1080 or best)")

    return m.group(1)


def add_verbosity(p, suppress):
    p.add_argument("-v", "--verbose", action="count",
                   default=argparse.SUPPRESS if suppress else 0,
                   help="one line per download on stderr (-vv: debug log and tracebacks)")
    p.add_argument("-q", "--quiet", action="store_true",
                   default=argparse.SUPPRESS if suppress else False,
                   help="suppress warnings and the progress bar")


def common_parent():
    p = argparse.ArgumentParser(add_help=False)
    add_verbosity(p, suppress=True)
    p.add_argument("--oauth", action="store_true",
                   help="authenticate with OAuth (token cached after the first login)")
    p.add_argument("--logfile", metavar="FILE", default=argparse.SUPPRESS,
                   help="write the library's debug log to FILE")
    return p


def add_download_options(p, playlist_mode):
    what = "playlist or channel URLs, or playlist ids" if playlist_mode \
        else "video, playlist or channel URLs"
    p.add_argument("urls", nargs="*", metavar="URL",
                   help=f"{what} ('-': read from stdin)")

    pick = p.add_mutually_exclusive_group()
    pick.add_argument("-a", "--audio", action="store_true",
                      help="download the best audio stream (mp4 unless --audio-format)")
    pick.add_argument("-i", "--itag", type=int, metavar="N", help="download this itag")
    pick.add_argument("-r", "--resolution", type=resolution_arg, metavar="RES",
                      help="720p, 1080p, ... or 'best'; above the progressive limit, "
                           "video and audio are merged with ffmpeg "
                           "(default: highest progressive stream)")
    p.add_argument("--audio-format", metavar="EXT",
                   help="audio container, e.g. mp4 or webm (implies -a)")
    p.add_argument("-o", "--output", metavar="PATH",
                   help="output file or directory ('-' for stdout); playlists default "
                        "to a directory named after the playlist")

    existing = p.add_mutually_exclusive_group()
    existing.add_argument("-f", "--force", action="store_true", help="overwrite existing files")
    existing.add_argument("-s", "--skip-existing", action="store_true",
                          help="silently skip files that already exist (resume a playlist)")

    p.add_argument("-n", "--limit", type=positive_int, metavar="N",
                   help="for playlists and channels: only the first N videos")

    if playlist_mode:
        p.add_argument("--list", action="store_true",
                       help="only print the video URLs, one per line (no download)")

    p.set_defaults(force_playlist=playlist_mode)


def build_parser():
    parent = common_parent()
    parser = argparse.ArgumentParser(
        prog=PROG,
        description=(
            f"pytubefix v{__version__}. Download YouTube videos. "
            f"'{PROG} URL' is shorthand for '{PROG} download URL'; "
            "playlists and channels are detected from the URL."
        ),
    )
    parser.add_argument("-V", "--version", action="version", version=f"%(prog)s {__version__}")
    add_verbosity(parser, suppress=False)

    sub = parser.add_subparsers(dest="cmd", metavar="COMMAND", required=True)

    dl = sub.add_parser("download", parents=[parent], help="download videos or audio (default)")
    add_download_options(dl, playlist_mode=False)

    pl = sub.add_parser("playlist", parents=[parent],
                        help="download a whole playlist or channel (also accepts a playlist id)")
    add_download_options(pl, playlist_mode=True)

    st = sub.add_parser("streams", parents=[parent], help="list the available streams")
    st.add_argument("url", metavar="URL")

    info = sub.add_parser("info", parents=[parent], help="show video metadata")
    info.add_argument("url", metavar="URL")

    cap = sub.add_parser("captions", parents=[parent],
                         help="list caption tracks, or print one as SRT")
    cap.add_argument("url", metavar="URL")
    cap.add_argument("-c", "--code", metavar="CODE", help="language code, e.g. en or a.en")
    cap.add_argument("-o", "--output", metavar="FILE", help="write to FILE instead of stdout")
    cap.add_argument("-f", "--force", action="store_true", help="overwrite an existing file")

    se = sub.add_parser("search", parents=[parent], help="search videos")
    se.add_argument("query", nargs="+", metavar="QUERY")
    se.add_argument("-n", "--limit", type=positive_int, default=10, metavar="N",
                    help="number of results (default: 10)")

    rep = sub.add_parser("report", parents=[parent],
                         help="save the html/js/video info of a video for offline debugging")
    rep.add_argument("url", metavar="URL")
    rep.add_argument("-o", "--output", metavar="FILE",
                     help="output file (default: yt-video-ID-TIMESTAMP.json.gz)")
    rep.add_argument("-f", "--force", action="store_true", help="overwrite an existing file")

    return parser, {
        "download": dl, "playlist": pl, "streams": st, "info": info,
        "captions": cap, "search": se, "report": rep,
    }


_GLOBAL_FLAGS = re.compile(r"^(-[vq]+|--verbose|--quiet)$")


def normalize_argv(argv):
    """`pytubefix URL ...` (and `pytubefix -a URL`) mean `pytubefix download ...`."""
    for i, arg in enumerate(argv):
        if _GLOBAL_FLAGS.match(arg):
            continue

        if arg in ("-h", "--help", "-V", "--version") or arg in COMMANDS:
            return argv

        return argv[:i] + ["download"] + argv[i:]

    return argv


HANDLERS = {
    "download": cmd_download,
    "playlist": cmd_download,
    "streams": cmd_streams,
    "info": cmd_info,
    "captions": cmd_captions,
    "search": cmd_search,
    "report": cmd_report,
}


def _terminate(signum, frame):  # pylint: disable=W0613
    sys.exit(128 + signum)  # lets `with` blocks clean the temp dirs


def main(argv=None):
    if hasattr(signal, "SIGPIPE"):
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)

    signal.signal(signal.SIGTERM, _terminate)

    argv = normalize_argv(list(sys.argv[1:] if argv is None else argv))
    parser, subparsers = build_parser()
    args = parser.parse_args(argv)

    logfile = getattr(args, "logfile", None)

    if args.verbose >= 2 or logfile:
        setup_logger(logging.DEBUG, log_filename=logfile)

    log = Log(verbose=args.verbose >= 1, quiet=args.quiet, debug=args.verbose >= 2)

    try:
        HANDLERS[args.cmd](args, subparsers[args.cmd], log)
    except KeyboardInterrupt:
        log.bar.clear()
        return 130
    except Exception as e:
        log.fail(e, getattr(args, "url", None))

    return 1 if log.failures else 0


if __name__ == "__main__":
    sys.exit(main())