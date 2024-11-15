.. _m4a:

M4a Download (MPEG-4 AAC audio codec)
=============================

**Attention the mp3 parameter will no longer be used, all audios will now be downloaded as .m4a, the correct extension for the codec (MPEG-4 AAC audio codec)**::

        from pytubefix import YouTube
        from pytubefix.cli import on_progress
         
        url = input("url >")
         
        yt = YouTube(url, on_progress_callback = on_progress)
        print(yt.title)
         
        ys = yt.streams.get_audio_only()
        ys.download()
