from pytubefix import Channel

c = Channel("https://www.youtube.com/@ProgrammingKnowledge")

print(f'Downloading videos by: {c.channel_name}')

for video in c.videos:
    download = video.streams.get_highest_resolution().download()

