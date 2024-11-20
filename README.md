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

filters = {
    'upload_date': Filter.get_upload_date('Today'),
    'type': Filter.get_type("Video"),
    'duration': Filter.get_duration("Under 4 minutes"),
    'features': [Filter.get_features("4K"), Filter.get_features("Creative Commons")],
    'sort_by': Filter.get_sort_by("Upload date")
}

s = Search('music', filters=filters)
for video in s.videos:
    print(video.watch_url)
```
