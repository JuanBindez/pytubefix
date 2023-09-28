from pytubefix import YouTube
from pytubefix.cli import on_progress
 
url = input("URL >")
 
yt = YouTube(url, on_progress_callback = on_progress)
print(yt.title)
 
ys = yt.streams.get_audio_only() # use this method -> get_audio_only()
ys.download(mp3=True) # pass the parameter mp3=Tre to save in .mp3