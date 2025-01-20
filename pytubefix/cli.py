import random
import argparse
import gzip
import json
import logging
import os
import shutil
import sys
import datetime as dt
import subprocess  # nosec
from typing import List, Optional

import pytubefix.exceptions as exceptions
from pytubefix import __version__
from pytubefix import CaptionQuery, Playlist, Stream
from pytubefix import YouTube

logger = logging.getLogger(__name__)

def build_playback_report(url) -> None:
    """Serialize the request data to json for offline debugging.
    
    :param url:
        A url object.
    """
    yt = YouTube(url)

    ts = int(dt.datetime.now(dt.timezone.utc).timestamp())
    fp = os.path.join(os.getcwd(), f"yt-video-{yt.video_id}-{ts}.json.gz")

    js = yt.js
    watch_html = yt.watch_html
    vid_info = yt.vid_info

    with gzip.open(fp, "wb") as fh:
        fh.write(
            json.dumps(
                {
                    "url": yt.watch_url,
                    "js": js,
                    "watch_html": watch_html,
                    "video_info": vid_info,
                }
            ).encode("utf8"),
        )

def display_progress_bar(bytes_received: int, filesize: int, ch: str = "█", scale: float = 0.55) -> None:
    """Display a simple, pretty progress bar.

    Example:
    ~~~~~~~~
    PSY - GANGNAM STYLE(강남스타일) MV.mp4
    ↳ |███████████████████████████████████████| 100.0%

    :param int bytes_received:
        The delta between the total file size (bytes) and bytes already
        written to disk.
    :param int filesize:
        File size of the media stream in bytes.
    :param str ch:
        Character to use for presenting progress segment.
    :param float scale:
        Scale multiplier to reduce progress bar size.
    """
    columns = shutil.get_terminal_size().columns
    max_width = int(columns * scale)

    filled = int(round(max_width * bytes_received / float(filesize)))
    remaining = max_width - filled
    progress_bar = ch * filled + " " * remaining
    percent = round(100.0 * bytes_received / float(filesize), 1)
    text = f" ↳ |{progress_bar}| {percent}%\r"
    sys.stdout.write(text)
    sys.stdout.flush()

def on_progress(stream: Stream, chunk: bytes, bytes_remaining: int) -> None:  # pylint: disable=W0613
    filesize = stream.filesize
    bytes_received = filesize - bytes_remaining
    display_progress_bar(bytes_received, filesize)

def _download(stream: Stream, target: Optional[str] = None, filename: Optional[str] = None) -> None:
    filesize_megabytes = stream.filesize // 1048576
    print(f"{filename or stream.default_filename} | {filesize_megabytes} MB")
    file_path = stream.get_file_path(filename=filename, output_path=target)
    if stream.exists_at_path(file_path):
        print(f"Already downloaded at:\n{file_path}")
        return

    stream.download(output_path=target, filename=filename)
    sys.stdout.write("\n")

def _unique_name(base: str, subtype: str, media_type: str, target: str) -> str:
    """
    Given a base name, the file format, and the target directory, will generate
    a filename unique for that directory and file format.
    
    :param str base:
        The given base-name.
    :param str subtype:
        The filetype of the video which will be downloaded.
    :param str media_type:
        The media_type of the file, ie. "audio" or "video"
    :param Path target:
        Target directory for download.
    """
    counter = 0
    while True:
        file_name = f"{base}_{media_type}_{counter}"
        file_path = os.path.join(target, f"{file_name}.{subtype}")
        if not os.path.exists(file_path):
            return file_name
        counter += 1

def ffmpeg_process(url, resolution: str, target: Optional[str] = None) -> None:
    """
    Decides the correct video stream to download, then calls _ffmpeg_downloader.

    :param url:
        A valid YouTube object.
    :param str resolution:
        YouTube video resolution.
    :param str target:
        Target directory for download
    """

    yt = YouTube(url)

    yt.register_on_progress_callback(on_progress)
    target = target or os.getcwd()

    if resolution == None or resolution == "best":
        highest_quality_stream = yt.streams.filter(progressive=False).order_by("resolution").last()
        mp4_stream = yt.streams.filter(progressive=False, subtype="mp4").order_by("resolution").last()
        if highest_quality_stream.resolution == mp4_stream.resolution:
            video_stream = mp4_stream
        else:
            video_stream = highest_quality_stream
    else:
        video_stream = yt.streams.filter(progressive=False, resolution=resolution).first()

    if not video_stream:
        print(f"No streams found for resolution {resolution}")
        return

    audio_stream = yt.streams.filter(progressive=False).order_by("abr").last()

    video_file_name = _unique_name(yt.title, "mp4", "video", target)
    audio_file_name = _unique_name(yt.title, "mp4", "audio", target)

    video_path = video_stream.get_file_path(filename=video_file_name, output_path=target)
    audio_path = audio_stream.get_file_path(filename=audio_file_name, output_path=target)

    if os.path.exists(video_path) and os.path.exists(audio_path):
        print("Already downloaded both video and audio.")
        return

    _download(video_stream, target=target, filename=video_file_name)
    _download(audio_stream, target=target, filename=audio_file_name)

    # Construct the command to run ffmpeg
    command = ["ffmpeg", "-i", video_path, "-i", audio_path, "-c:v", "copy", "-c:a", "aac", "-strict", "experimental", f"{target}/{yt.title}.mp4"]

    # Execute the command
    subprocess.run(command)

def download_by_resolution(url, resolution: str, target: Optional[str] = None) -> None:
    """Download a stream by the specified resolution.

    :param YouTube youtube:
        A valid YouTube object.
    :param str resolution:
        The desired resolution of the stream.
    :param Optional[str] target:
        The target directory for the download.
    """
    print(f"Downloading {resolution}...")

    yt = YouTube(url)

    stream = yt.streams.filter(resolution=resolution).first()
    if stream is None:
        print(f"No stream found for resolution {resolution}")
    else:
        _download(stream, target)

def download_highest_resolution_progressive(url, resolution: str, target: Optional[str] = None) -> None:
    """Download a YouTube video stream at the highest resolution.

    :param YouTube youtube:
        A valid YouTube object.
    :param str resolution:
        The resolution of the stream.
    :param Optional[str] target:
        The target directory for the download.
    """
    print("Downloading highest resolution progressive stream...")

    yt = YouTube(url)

    stream = yt.streams.filter(progressive=True).order_by("resolution").last()
    if stream is None:
        print("No progressive stream found.")
    else:
        _download(stream, target)

def download_by_itag(url, itag: int, target: Optional[str] = None) -> None:
    """Download a YouTube stream by its itag.

    :param url:
        A valid YouTube object.
    :param int itag:
        The itag of the desired stream.
    :param Optional[str] target:
        The target directory for the download.
    """

    yt = YouTube(url)

    stream = yt.streams.get_by_itag(itag)
    if stream is None:
        print(f"No stream found with itag {itag}.")
    else:
        print(f"Downloading stream with itag {itag}...")
        _download(stream, target)

def download_caption(url, lang_code: str, target: Optional[str] = None) -> None:
    """Download captions for a given YouTube video.

    :param url:
        A valid YouTube object.
    :param str lang_code:
        The language code for the desired captions.
    :param Optional[str] target:
        The target directory for the downloaded captions.
    """
    print(f"Downloading captions for language: {lang_code}...")

    yt = YouTube(url)

    caption = yt.captions.get_by_language_code(lang_code)
    if caption is None:
        print(f"No captions found for language code: {lang_code}.")
    else:
        caption.download(target)

def available_captions(captions: List[CaptionQuery]) -> None:
    """Print available captions for a YouTube video.

    :param List[CaptionQuery] captions:
        The list of available captions.
    """
    print("Available captions:")
    for caption in captions:
        print(f" - {caption.language_code}: {caption.name}")

def display_streams(url) -> None:
    """Display available streams for the given YouTube video.

    :param url:
        A valid YouTube object.
    """

    yt = YouTube(url)

    print(f"Available streams for {yt.title}:")
    for stream in yt.streams:
        print(f" - {stream}")

def download_video(url):
    yt = YouTube(url, on_progress_callback=on_progress)
    print(yt.title)

    ys = yt.streams.get_highest_resolution()
    ys.download()
    sys.exit(0)

def download_audio(url):
    yt = YouTube(url, on_progress_callback=on_progress)
    print(yt.title)

    ys = yt.streams.get_audio_only()
    ys.download()
    sys.exit(0)

def download_playlist_video(url):
    pl = Playlist(url)
    for video in pl.videos:
        ys = video.streams.get_highest_resolution()
        ys.download()
        sys.exit(0)

def download_playlist_audio(url):
    pl = Playlist(url)
    for video in pl.videos:
        ys = video.streams.get_audio_only()
        ys.download()
        sys.exit(0)

def main():
    """
    CLI tool for downloading YouTube videos.
    """
    parser = argparse.ArgumentParser(description=main.__doc__)

    parser.add_argument("-u", "--url", help="The YouTube /watch URL for a video", required=False)
    parser.add_argument("-V", "--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("--itag", type=int, help="The itag for the desired stream")
    parser.add_argument("-r", "--resolution", type=str, help="The resolution for the desired stream")
    parser.add_argument("-pl", "--playlist", action="store_true", help="The URL for a YouTube playlist")
    parser.add_argument("-l", "--list", action="store_true", help="List available streams for the provided URL")
    parser.add_argument("--oauth", action="store_true", help="Use OAuth token")
    parser.add_argument("-v", "--verbose", action="store_true", dest="verbose", help="Set logger output to verbose output.")
    parser.add_argument("--logfile", action="store", help="Log debug and error messages into a file")
    parser.add_argument("--build-playback-report", action="store_true", help="Save the HTML and JS to disk")
    parser.add_argument("-c", "--caption-code", type=str, help="Download captions for a given language code")
    parser.add_argument("-lc", "--list-captions", action="store_true", help="List available caption codes for a video")
    parser.add_argument("-a", "--audio", action="store_true", help="Download the audio for the provided URL")
    parser.add_argument("-m", "--mp4", action="store_true", help="Download the video mp4 for the provided URL")
    parser.add_argument("-f", "--ffmpeg", const="best", nargs="?", help="Download video and audio using ffmpeg")

    args = parser.parse_args()

    if args.audio:
        if args.playlist and not args.mp4:
            download_playlist_audio(args.url)
        download_audio(args.url)
    
    if args.mp4:
        if args.playlist and not args.audio:
            download_playlist_video(args.url)
        download_video(args.url)


if __name__ == "__main__":
    main()