# pytubefix

#### This python package is a solution to the problem with pytube regarding delays in updates

### install:

    pip install pytubefix 


### usage:

```python

from pytubefix import YouTube
from pytubefix.cli import on_progress
 
url = input("URL >")
 
yt = YouTube(url, on_progress_callback = on_progress)
print(yt.title)
 
ys = yt.streams.get_highest_resolution()
ys.download()
```

----------

### If you want to save in .mp3 just pass the mp3=True parameter in the download() method, must be used together with the get_audio_only method:


```python

from pytubefix import YouTube
from pytubefix.cli import on_progress
 
url = input("URL >")
 
yt = YouTube(url, on_progress_callback = on_progress)
print(yt.title)
 
ys = yt.streams.get_audio_only() # use this method -> get_audio_only()
ys.download(mp3=True) # pass the parameter mp3=Tre to save in .mp3
```

-----------

### if you want to download complete playlists:

```python

from pytubefix import YouTube
from pytubefix import Playlist
from pytubefix.cli import on_progress
 
url = input("URL Here >")

pl = Playlist(url)

for video in pl.videos:
    ys = video.streams.get_audio_only()
    ys.download(mp3=True) # pass the parameter mp3=Tre to save in .mp3

```
----------

