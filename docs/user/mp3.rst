.. _mp3:

mp3 download (MPEG-4 AAC audio codec):
=============================

**If you want to save in .mp3 just pass the mp3=True parameter**::

        from pytubefix import YouTube
        from pytubefix.cli import on_progress
         
        url = input("url >")
         
        yt = YouTube(url, on_progress_callback = on_progress)
        print(yt.title)
         
        ys = yt.streams.get_audio_only()
        ys.download(mp3=True)
