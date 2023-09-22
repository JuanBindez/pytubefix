from pytubefix import YouTube
from pytubefix.cli import on_progress

url = input("URL >")

yt = YouTube(url)
print(yt.captions)

'''
yt = YouTube(url, on_progress_callback = on_progress)
print(yt.title)
ys = yt.streams.get_highest_resolution()
ys.download()
'''

