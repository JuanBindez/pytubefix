from pytubefix import Channel, YouTube
import os

api_key = os.environ["SCRAPING_BEE_API_KEY"]
proxies = {
    "http": f"http://{api_key}:render_js=False&premium_proxy=False@proxy.scrapingbee.com:8886",
    "https": f"https://{api_key}:render_js=False&premium_proxy=False@proxy.scrapingbee.com:8887",
}


youtube_video_url = "https://www.youtube.com/watch?v=BP7FZsx0gz4"

# videos
video = YouTube(youtube_video_url, proxies=proxies)
print(video.channel_url)
print(video.length)
print(video.thumbnail_url)

# streams
audio_stream = video.streams.filter(only_audio=True).order_by("abr").desc().first()
file_extension = audio_stream.mime_type.split("/")[-1]
audio_stream.download(output_path=f".", filename=f"{video.video_id}.{file_extension}")

# channels
c = Channel(video.channel_url, proxies=proxies)
print(c)
print(c.channel_id)

# captions # TODO: Make sure these work.
caption = video.captions.get_by_language_code("en")
print(caption)
