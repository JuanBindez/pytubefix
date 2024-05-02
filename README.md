# pytubefix
![PyPI - Downloads](https://img.shields.io/pypi/dm/pytubefix)
![PyPI - License](https://img.shields.io/pypi/l/pytubefix)
![Read the Docs](https://img.shields.io/readthedocs/pytubefix)
![GitHub Tag](https://img.shields.io/github/v/tag/JuanBindez/pytubefix?include_prereleases)
<a href="https://pypi.org/project/pytubefix/"><img src="https://img.shields.io/pypi/v/pytubefix" /></a>


html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pytubefix Versions</title>
</head>
<body>
    <div class="container">
        <h1>Pytubefix Versions</h1>
        <div id="versions"></div>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function() {
            fetch('https://raw.githubusercontent.com/JuanBindez/pytubefix/v5dev/pytubefix/version.json')
                .then(response => response.json())
                .then(data => {
                    const versionsDiv = document.getElementById('versions');
                    const mainlineVersion = data.mainline;
                    const stableVersion = data.stable;

                    const mainlineElement = document.createElement('div');
                    mainlineElement.textContent = `Mainline Version: ${mainlineVersion}`;
                    versionsDiv.appendChild(mainlineElement);

                    const stableElement = document.createElement('div');
                    stableElement.textContent = `Stable Version: ${stableVersion}`;
                    versionsDiv.appendChild(stableElement);
                })
                .catch(error => console.error('Error fetching versions:', error));
        });
    </script>
</body>
</html>



## A pytube fork with additional features and fixes.

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
ys.download(mp3=True) # pass the parameter mp3=True to save in .mp3
```

#### if you want to download complete playlists:

```python

from pytubefix import Playlist
from pytubefix.cli import on_progress
 
url = "url"

pl = Playlist(url)

for video in pl.videos:
    ys = video.streams.get_audio_only()
    ys.download(mp3=True) # pass the parameter mp3=True to save in .mp3

```

#### if you want to add authentication

```python

from pytubefix import YouTube
from pytubefix.cli import on_progress
 
url = "url"

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

