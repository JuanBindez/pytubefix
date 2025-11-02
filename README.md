# Pytubefix

[![PyPI - Downloads](https://img.shields.io/pypi/dm/pytubefix)](https://pypi.org/project/pytubefix/)
[![GitHub Sponsors](https://img.shields.io/github/sponsors/juanbindez)](https://github.com/sponsors/juanbindez)
[![PyPI - License](https://img.shields.io/pypi/l/pytubefix)](https://opensource.org/licenses/MIT)
[![Read the Docs](https://img.shields.io/readthedocs/pytubefix)](https://pytubefix.readthedocs.io/)
[![GitHub Tag](https://img.shields.io/github/v/tag/JuanBindez/pytubefix?include_prereleases)](https://github.com/JuanBindez/pytubefix/releases)
[![PyPI - Version](https://img.shields.io/pypi/v/pytubefix)](https://pypi.org/project/pytubefix/)

## Python3 Library for Downloading YouTube Videos

---

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

## Working with Subtitles/Caption Tracks

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

## Using Channels

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

## Search for Videos

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


# AsyncYouTube — Advanced Guide with Complete Examples

`AsyncYouTube` is a fully **asynchronous Python interface** built on **PyTubeFix**, intended for developers who require complete control over YouTube video data. It provides access to video streams, metadata, chapters, key moments, and more — all without blocking your event loop.

---

## Quick Start Example

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

## Download a Specific Stream

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

## Fetch Video Metadata

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

## Retrieve Chapters and Key Moments

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

## Create AsyncYouTube from Video ID

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

## Best Practices

* Always `await` asynchronous methods: `streams()`, `title()`, `views()`, `likes()`, `chapters()`, `key_moments()`.
* Use `use_oauth=True` to handle age-restricted content; cache tokens to minimize repeated logins.
* Wrap network calls in `try/except` to handle errors gracefully.
* Combine callbacks with asyncio for efficient non-blocking downloads.
* Maintain consistent program structure with `main()` and `asyncio.run()` for readability and maintainability.

---

