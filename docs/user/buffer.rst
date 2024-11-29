.. _buffer:

Using Buffer
============

**to redirect the download to stdout**::
        
        from pytubefix import YouTube
        from pytubefix import Buffer

        buffer = Buffer()

        url = "URL"

        yt = YouTube(url)
        ys = yt.streams.get_audio_only()

        buffer.download_in_buffer(ys)
        buffer.redirect_to_stdout()
