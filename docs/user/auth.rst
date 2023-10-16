.. _auth:

Add Authentication:
=============================

**Some videos have age restrictions, so you need to authenticate to download, pass the parameters use_oauth=True and allow_oauth_cache=True**::

        from pytubefix import YouTube
        from pytubefix.cli import on_progress
         
        url = input("url >")
         
        yt = YouTube(url, use_oauth=True, allow_oauth_cache=True, on_progress_callback = on_progress)
        print(yt.title)
         
        ys = yt.streams.get_highest_resolution()
        ys.download()# you will only receive the authentication request if you call the download() method


