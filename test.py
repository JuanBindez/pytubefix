from pytubefix import YouTube
from pytubefix import Playlist
from pytubefix.cli import on_progress
 
url = input("URL Here >")

pl = Playlist(url)

for video in pl.videos:
    ys = video.streams.get_audio_only()
    ys.download(mp3=True)