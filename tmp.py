from pytubefix import YouTube

url = "https://www.youtube.com/watch?v=maXsM_NFTFo"
yt = YouTube(url, use_po_token=False, use_oauth=True, allow_oauth_cache=True, client="WEB")
print("title:", yt.title)
print("author:", yt.author)
print("desc:", yt.description)
print("views:", yt.views)
print("likes:", yt.likes)
print("length:", yt.length)
print("date:", yt.publish_date)
