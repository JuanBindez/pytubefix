# pytubefix

![PyPI - Downloads](https://img.shields.io/pypi/dm/pytubefix)
![PyPI - License](https://img.shields.io/pypi/l/pytubefix)
![PyPI - Version](https://img.shields.io/pypi/v/pytubefix)


### Python3 library for downloading YouTube Videos.

## install:

    pip install pytubefix

## usage:

#### mp4 video download highest resolution:

```python

from pytubefix import YouTube
from pytubefix.cli import on_progress
 
url = input("url >")
 
yt = YouTube(url, on_progress_callback = on_progress)
print(yt.title)
 
ys = yt.streams.get_highest_resolution()
ys.download()
```

#### If you want to save in .mp3 just pass the mp3=True parameter (MPEG-4 AAC audio codec):


```python

from pytubefix import YouTube
from pytubefix.cli import on_progress
 
url = input("url >")
 
yt = YouTube(url, on_progress_callback = on_progress)
print(yt.title)
 
ys = yt.streams.get_audio_only()
ys.download(mp3=True) # pass the parameter mp3=True to save in .mp3
```

#### if you want to download complete playlists:

```python

from pytubefix import YouTube
from pytubefix import Playlist
from pytubefix.cli import on_progress
 
url = input("url Here >")

pl = Playlist(url)

for video in pl.videos:
    ys = video.streams.get_audio_only()
    ys.download(mp3=True) # pass the parameter mp3=True to save in .mp3

```

#### if you want to add authentication

```python

from pytubefix import YouTube
 
url = input("url Here >")

yt = YouTube(url, use_oauth=True, allow_oauth_cache=True, on_progress_callback = on_progress)
           
ys = yt.streams.get_audio_only()

ys.download(mp3=True) # you will only get the request to authenticate once you download

```

## Subtitle/Caption Tracks:

#### viewing available subtitles:

```python

from pytubefix import YouTube

yt = YouTube('http://youtube.com/watch?v=2lAe1cqCOXo')
subtitles = yt.captions

print(subtitles)

```

#### printing the subtitle tracks:

```python

from pytubefix import YouTube
 

yt = YouTube('http://youtube.com/watch?v=2lAe1cqCOXo')

caption = yt.captions.get_by_language_code('en')
print(caption.generate_srt_captions())

```

#### now you can save subtitles to a txt file:

```python

from pytubefix import YouTube
 

yt = YouTube('http://youtube.com/watch?v=2lAe1cqCOXo')

caption = yt.captions.get_by_language_code('en')
caption.save_captions("captions.txt")

```

## Using Channels:

#### get the channel name:

```python

from pytubefix import Channel

c = Channel("https://www.youtube.com/@ProgrammingKnowledge/featured")

print(f'Channel name: {c.channel_name}')

```

#### to download all videos from a channel:


```python

from pytubefix import Channel

c = Channel("https://www.youtube.com/@ProgrammingKnowledge")

print(f'Downloading videos by: {c.channel_name}')

for video in c.videos:
    download = video.streams.get_highest_resolution().download()

```


#### to get a list of live streams:

```python

from pytubefix import Channel

url_channel = input("url > ")

c = Channel(url_channel)

print("live streams :", c.livestreams_urls)

```