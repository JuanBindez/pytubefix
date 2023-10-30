from pytubefix import YouTube
from pytubefix.cli import on_progress
 
url = input("url >")
 
yt = YouTube(url, on_progress_callback = on_progress)
print(yt.title)
 
ys = yt.streams.get_audio_only()
ys.download() # pass the parameter mp3=True to save in .mp3