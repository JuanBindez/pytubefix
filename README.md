# pytubefix
This python package is a solution to the problem with pytube regarding delays in updates


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
