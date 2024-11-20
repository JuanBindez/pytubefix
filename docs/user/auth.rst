.. _auth:

Add Authentication Oauth
========================

Some videos have age restrictions, so you need to authenticate to download, pass the parameters use_oauth=True and allow_oauth_cache=True::

    from pytubefix import YouTube
    from pytubefix.cli import on_progress
         
    url = input("url")
         
    yt = YouTube(url, use_oauth=True, allow_oauth_cache=True, on_progress_callback = on_progress)
    print(yt.title)
         
    ys = yt.streams.get_highest_resolution()
    ys.download()# you will only receive the authentication request if you call the download() method


Reset Cache
===========

If you need to reset the cache you can import reset_cache and call it or set allow_oauth_cache to False::

    from pytubefix import YouTube
    from pytubefix.helpers import reset_cache

    reset_cache()
        
    url = input("url")
         
    yt = YouTube(url, use_oauth=True, allow_oauth_cache=True)
    print(yt.title)
         
    ys = yt.streams.get_highest_resolution()
    ys.download()



