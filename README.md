<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="./images/pytubefix_logo.svg">
    <source media="(prefers-color-scheme: light)" srcset="./images/pytubefix_logo.svg">
    <img width="430" alt="pytubefix" src="./images/pytubefix_logo.svg">
  </picture>
</p>

<p align="center">
  <img src="https://img.shields.io/pypi/dm/pytubefix">
  <img src="https://img.shields.io/github/sponsors/juanbindez">
  <img src="https://img.shields.io/pypi/l/pytubefix">
  <img src="https://img.shields.io/readthedocs/pytubefix">
  <img src="https://img.shields.io/github/v/tag/JuanBindez/pytubefix?include_prereleases">
  <img src="https://img.shields.io/pypi/v/pytubefix">
  <img src="https://img.shields.io/pypi/pyversions/pytubefix.svg">
</p>

<h2 align="center">
  Python3 Library for Downloading YouTube Videos
</h2>


## Installation

```bash
pip install pytubefix
```

---

## Quickstart

### Download MP4 Video in Highest Resolution:

```python
from pytubefix import YouTube
from pytubefix.cli import on_progress

url = "url"

yt = YouTube(url, on_progress_callback=on_progress)
print(yt.title)

ys = yt.streams.get_highest_resolution()
ys.download()
```

### Download Audio-Only (.m4a):

```python
from pytubefix import YouTube
from pytubefix.cli import on_progress

url = "url"

yt = YouTube(url, on_progress_callback=on_progress)
print(yt.title)

ys = yt.streams.get_audio_only()
ys.download()
```

### Download a Complete Playlist:

```python
from pytubefix import Playlist
from pytubefix.cli import on_progress

url = "url"

pl = Playlist(url)
for video in pl.videos:
    ys = video.streams.get_audio_only()
    ys.download()
```

### Use OAuth Authentication:

```python
from pytubefix import YouTube
from pytubefix.cli import on_progress

url = "url"

yt = YouTube(url, use_oauth=True, allow_oauth_cache=True, on_progress_callback=on_progress)
ys = yt.streams.get_highest_resolution()
ys.download()  # Authenticate once for subsequent downloads
```

### Specify Output Directory for Downloads:

```python
from pytubefix import YouTube
from pytubefix.cli import on_progress

url = "url"

yt = YouTube(url, on_progress_callback=on_progress)
ys = yt.streams.get_highest_resolution()
ys.download(output_path="path/to/directory")
```

---

### Working with Subtitles/Caption Tracks

### View Available Subtitles:

```python
from pytubefix import YouTube

yt = YouTube('http://youtube.com/watch?v=2lAe1cqCOXo')
print(yt.captions)
```

### Print Subtitle Tracks:

```python
from pytubefix import YouTube

yt = YouTube('http://youtube.com/watch?v=2lAe1cqCOXo')
caption = yt.captions['a.en']
print(caption.generate_srt_captions())
```

### Save Subtitles to a Text File:

```python
from pytubefix import YouTube

yt = YouTube('http://youtube.com/watch?v=2lAe1cqCOXo')
caption = yt.captions['a.en']
caption.save_captions("captions.txt")
```

---

### Using Channels

### Get Channel Name:

```python
from pytubefix import Channel

c = Channel("https://www.youtube.com/@ProgrammingKnowledge/featured")
print(f'Channel name: {c.channel_name}')
```

### Download All Videos from a Channel:

```python
from pytubefix import Channel

c = Channel("https://www.youtube.com/@ProgrammingKnowledge")
print(f'Downloading videos by: {c.channel_name}')

for video in c.videos:
    video.streams.get_highest_resolution().download()
```

---

### Search for Videos

### Basic Search:

```python
from pytubefix import Search

results = Search('GitHub Issue Best Practices')
for video in results.videos:
    print(f'Title: {video.title}')
    print(f'URL: {video.watch_url}')
    print(f'Duration: {video.length} sec')
    print('---')
```

### Use Filters:

```python
from pytubefix.contrib.search import Search, Filter

filters = (
    Filter.create()
        .upload_date(Filter.UploadDate.TODAY)
        .type(Filter.Type.VIDEO)
        .duration(Filter.Duration.UNDER_4_MINUTES)
        .feature([Filter.Features.CREATIVE_COMMONS, Filter.Features._4K])
        .sort_by(Filter.SortBy.UPLOAD_DATE)
     )

s = Search('music', filters=filters)
for video in s.videos:
    print(video.watch_url)
```

---

## Command Line Interface (CLI)

Installing pytubefix also installs the `pytubefix` command. It follows the usual
Unix conventions: data goes to stdout, messages and the progress bar go to
stderr, it is silent on success, errors look like `pytubefix: URL: message`
with a non-zero exit status, and `-` means stdin/stdout.

```text
pytubefix [download] [options] URL...      download videos or audio
pytubefix playlist [options] URL|ID...     download a whole playlist or channel
pytubefix streams URL                      list the available streams
pytubefix info URL                         show video metadata
pytubefix captions URL [-c CODE]           list caption tracks, or print one as SRT
pytubefix search QUERY...                  search for videos
pytubefix report URL                       save a playback report for bug reports
```

`pytubefix URL` is shorthand for `pytubefix download URL`.

### Download a video or only the audio:

```bash
pytubefix "https://www.youtube.com/watch?v=2lAe1cqCOXo"        # best quality available
pytubefix -a "https://www.youtube.com/watch?v=2lAe1cqCOXo"     # audio only (.m4a)
pytubefix -r 720p "https://www.youtube.com/watch?v=2lAe1cqCOXo"
pytubefix -i 22 "https://www.youtube.com/watch?v=2lAe1cqCOXo"  # a specific itag
```

YouTube now offers many videos only as separate video and audio streams. When
that happens, pytubefix downloads both and merges them with
[ffmpeg](https://ffmpeg.org), which must be installed and in your `PATH`
(audio-only downloads do not need it).

### Choose where to save:

```bash
pytubefix URL -o video.mp4        # a file name (one video)
pytubefix URL -o downloads/       # a directory
pytubefix -a URL -o - | mpv -     # stdout, for pipelines
```

Existing files are never overwritten: use `-f` to overwrite or `-s` to skip them.

### Download a playlist or a channel:

Playlists and channels are detected from the URL:

```bash
pytubefix -a "https://www.youtube.com/playlist?list=PLxxxx" -o music/
pytubefix -a -n 10 "https://www.youtube.com/@ProgrammingKnowledge" -o channel/
```

The `playlist` command always treats the URL as a playlist (useful for
`watch?v=...&list=...` links) and also accepts a bare playlist id:

```bash
pytubefix playlist -a "https://www.youtube.com/watch?v=VIDEO&list=PLxxxx" -o music/
pytubefix playlist -a PLxxxx -o music/
pytubefix playlist --list PLxxxx        # only print the video URLs
```

A video that fails does not stop the others (the exit status is 1 at the end).
Run the same command with `-s` to resume an interrupted playlist.

### Streams, metadata and subtitles:

```bash
pytubefix streams URL                   # table on a terminal, TSV when piped
pytubefix info URL
pytubefix captions URL                  # list the caption codes
pytubefix captions URL -c en > subtitles.srt
pytubefix search "lofi hip hop" -n 3 | cut -f1 | pytubefix -a - -o music/
```

### Options:

| Option | Description |
|---|---|
| `-a`, `--audio` | download the best audio stream (`--audio-format EXT` to choose the container) |
| `-i N`, `--itag N` | download the stream with this itag |
| `-r RES` | `720p`, `1080p`, ... or `best` (the default) |
| `-o PATH` | output file or directory (`-` for stdout) |
| `-f`, `--force` / `-s`, `--skip-existing` | overwrite / silently skip existing files |
| `-n N`, `--limit N` | for playlists and channels: only the first `N` videos |
| `--oauth` | authenticate with OAuth (token cached after the first login) |
| `-v`, `-vv` | one line per download / debug log and tracebacks |
| `-q`, `--quiet` | no warnings and no progress bar |

Exit status: `0` success, `1` error, `2` invalid usage, `130` Ctrl+C, `143` SIGTERM.

To file a bug report, run `pytubefix report URL` and attach the generated
`yt-video-ID-TIMESTAMP.json.gz` file, which bundles up the state so others can
replay your issue. See `pytubefix --help` for all options and the
[documentation](https://pytubefix.readthedocs.io) for the full CLI guide.

---

### AsyncYouTube — Advanced Guide with Complete Examples

`AsyncYouTube` is a fully **asynchronous Python interface** built on **PyTubeFix**, intended for developers who require complete control over YouTube video data. It provides access to video streams, metadata, chapters, key moments, and more — all without blocking your event loop.

---

### Quick Start Example

A full program demonstrating basic usage:

```python
import asyncio
from pytubefix import AsyncYouTube

URL = "YOUR_VIDEO_URL"

async def main():
    # Initialize AsyncYouTube with OAuth to handle age-restricted content
    yt = AsyncYouTube(URL, use_oauth=True, allow_oauth_cache=True)
    
    # Fetch all available streams asynchronously
    streams = await yt.streams()
    print("Available Streams:")
    for stream in streams:
        print(stream)

if __name__ == '__main__':
    asyncio.run(main())
```

---

### Download a Specific Stream

Complete example showing download with progress and completion callbacks:

```python
import asyncio
from pytubefix import AsyncYouTube

URL = "YOUR_VIDEO_URL"

async def main():
    def on_progress(stream, chunk, bytes_remaining):
        total = stream.filesize
        percent = (1 - bytes_remaining / total) * 100
        print(f"\rProgress: {percent:.2f}%", end="")

    def on_complete(stream, file_path):
        print(f"\n√ Done downloading: {file_path}")

    yt = AsyncYouTube(URL, use_oauth=True, allow_oauth_cache=True)

    yt.register_on_progress_callback(on_progress)
    yt.register_on_complete_callback(on_complete)

    stream = await yt.get_stream_by_itag(18) # 360p MP4 progressive stream

    print(f"Downloading: {await yt.title()}")

    stream.download(filename="my_video.mp4") # Blocking call by design

if __name__ == '__main__':
    asyncio.run(main())
```

> Note: Always use callbacks to track progress; `download()` is synchronous.

---

### Fetch Video Metadata

```python
import asyncio
from pytubefix import AsyncYouTube

URL = "YOUR_VIDEO_URL"

async def main():
    yt = AsyncYouTube(URL, use_oauth=True, allow_oauth_cache=True)

    title = await yt.title()
    views = await yt.views()
    likes = await yt.likes()
    author = await yt.author()
    thumbnail = await yt.thumbnail_url()

    print(f"Title: {title}")
    print(f"Views: {views}")
    print(f"Likes: {likes}")
    print(f"Author: {author}")
    print(f"Thumbnail URL: {thumbnail}")

if __name__ == '__main__':
    asyncio.run(main())
```

---

### Retrieve Chapters and Key Moments

```python
import asyncio
from pytubefix import AsyncYouTube

URL = "YOUR_VIDEO_URL"

async def main():
    yt = AsyncYouTube(URL, use_oauth=True, allow_oauth_cache=True)

    chapters = await yt.chapters()
    key_moments = await yt.key_moments()

    print("Chapters:", chapters)
    print("Key Moments:", key_moments)

if __name__ == '__main__':
    asyncio.run(main())
```

---

### Create AsyncYouTube from Video ID

```python
import asyncio
from pytubefix import AsyncYouTube

VIDEO_ID = "YOUR_VIDEO_ID"

async def main():
    yt = AsyncYouTube.from_id(VIDEO_ID, use_oauth=True, allow_oauth_cache=True)
    streams = await yt.streams()
    print("Streams fetched from Video ID:")
    for s in streams:
        print(s)

if __name__ == '__main__':
    asyncio.run(main())
```

---

### Best Practices

* Always `await` asynchronous methods: `streams()`, `title()`, `views()`, `likes()`, `chapters()`, `key_moments()`.
* Use `use_oauth=True` to handle age-restricted content; cache tokens to minimize repeated logins.
* Wrap network calls in `try/except` to handle errors gracefully.
* Combine callbacks with asyncio for efficient non-blocking downloads.
* Maintain consistent program structure with `main()` and `asyncio.run()` for readability and maintainability.

---
