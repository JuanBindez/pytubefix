.. _problematic_characters:

Problematic Character
=====================

**Some operating systems do not allow saving downloads with some titles with special characters, to resolve this you can pass the character to the 'problematic_characters' parameter, pytubefix currently already automatically removes some characters such as "/, :, *, ", < , >, and |".**::

        from pytubefix import YouTube
        from pytubefix.cli import on_progress
        
        url = "url"
        
        yt = YouTube(url, on_progress_callback = on_progress)
        print(yt.title)
        
        ys = yt.streams.get_audio_only()
        ys.download(mp3=True, remove_problematic_character="?")
