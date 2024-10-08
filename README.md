# pytubefix

![PyPI - Downloads](https://img.shields.io/pypi/dm/pytubefix)
![GitHub Sponsors](https://img.shields.io/github/sponsors/juanbindez)
![PyPI - License](https://img.shields.io/pypi/l/pytubefix)
![Read the Docs](https://img.shields.io/readthedocs/pytubefix)
![GitHub Tag](https://img.shields.io/github/v/tag/JuanBindez/pytubefix?include_prereleases)
<a href="https://pypi.org/project/pytubefix/"><img src="https://img.shields.io/pypi/v/pytubefix" /></a>



## Python3 library for downloading YouTube Videos.

----------
## install

    pip install pytubefix


## Quickstart

#### mp4 video download highest resolution:

```python

from pytubefix import YouTube
from pytubefix.cli import on_progress
 
url = "url"
 
yt = YouTube(url, on_progress_callback = on_progress)
print(yt.title)
 
ys = yt.streams.get_highest_resolution()
ys.download()
```

#### If you want to save in .mp3 just pass the mp3=True parameter (MPEG-4 AAC audio codec):

```python

from pytubefix import YouTube
from pytubefix.cli import on_progress
 
url = "url"
 
yt = YouTube(url, on_progress_callback = on_progress)
print(yt.title)
 
ys = yt.streams.get_audio_only()
ys.download(mp3=True)
```

#### if you want to download complete playlists:

```python

from pytubefix import Playlist
from pytubefix.cli import on_progress
 
url = "url"

pl = Playlist(url)

for video in pl.videos:
    ys = video.streams.get_audio_only()
    ys.download(mp3=True)

```

#### if you want to add authentication

```python

from pytubefix import YouTube
from pytubefix.cli import on_progress
 
url = "url"

yt = YouTube(url, use_oauth=True, allow_oauth_cache=True, on_progress_callback = on_progress)
           
ys = yt.streams.get_highest_resolution()

ys.download() # you will only get the request to authenticate once you download

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

### Search:

```python
>>> from pytubefix import Search
>>> 
>>> results = Search('Github Issue Best Practices')
>>> 
>>> for video in results.videos:
...     print(f'Title: {video.title}')
...     print(f'URL: {video.watch_url}')
...     print(f'Duration: {video.length} sec')
...     print('---')
... 
Title: Good Practices with GitHub Issues
URL: https://youtube.com/watch?v=v1AeHaopAYE
Duration: 406 sec
---
Title: GitHub Issues Tips and Guidelines
URL: https://youtube.com/watch?v=kezinXSoV5A
Duration: 852 sec
---
Title: 13 Advanced (but useful) Git Techniques and Shortcuts
URL: https://youtube.com/watch?v=ecK3EnyGD8o
Duration: 486 sec
---
Title: Managing a GitHub Organization Tools, Tips, and Best Practices - Mark Matyas
URL: https://youtube.com/watch?v=1T4HAPBFbb0
Duration: 1525 sec
---
Title: Do you know the best way to manage GitHub Issues?
URL: https://youtube.com/watch?v=OccRyzAS4Vc
Duration: 534 sec
---
>>>


```


### Using Filters

```python
>>> from pytubefix.contrib.search import Search, Filter
>>> 
>>> 
>>> f = {
...     'upload_data': Filter.get_upload_data('Today'),
...     'type': Filter.get_type("Video"),
...     'duration': Filter.get_duration("Under 4 minutes"),
...     'features': [Filter.get_features("4K"), Filter.get_features("Creative Commons")],
...     'sort_by': Filter.get_sort_by("Upload date")
... }
>>> 
>>> s = Search('music', filters=f)
>>> for c in s.videos:
...     print(c.watch_url)
... 
https://youtube.com/watch?v=_Rq8MzYz0YU
https://youtube.com/watch?v=YHPGM8nBk3U
https://youtube.com/watch?v=m98WShs7MLE
https://youtube.com/watch?v=-vBqfC3Nir0
https://youtube.com/watch?v=LbtrnCjopwk
https://youtube.com/watch?v=pfl2ga6AS3c
https://youtube.com/watch?v=TzNk2ygEU4c
https://youtube.com/watch?v=yQfXVRKvA70
https://youtube.com/watch?v=G5tQX990XU0
https://youtube.com/watch?v=4LQzYMhtXV8
https://youtube.com/watch?v=BOLGwdjCSAo
https://youtube.com/watch?v=CgSH3Ww3MHs
https://youtube.com/watch?v=_43tx98VEWc
https://youtube.com/watch?v=wLDRGZaBEoQ
https://youtube.com/watch?v=3qaHb2t3Lkw
https://youtube.com/watch?v=56deLmbicLg
https://youtube.com/watch?v=pQk2TzmwnS0
https://youtube.com/watch?v=NJ3sOlg8KGo
https://youtube.com/watch?v=kfDSHjlk4Pg
https://youtube.com/watch?v=8KHak4ZNO3k
>>> 


```

### info:

```python
>>> from pytubefix import info
>>> 
>>> print(info())
{'OS': {'linux'}, 'Python': {'3.11.6 (main, Apr 10 2024, 17:26:07) [GCC 13.2.0]'}, 'Pytubefix': {'7.3.1'}}
>>> 

```
