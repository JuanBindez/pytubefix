.. _buffer:

Using Buffer
============

- The class supports handling different types of data sources, including streams and strings.
- Provides methods to:

- ``download_in_buffer()``: Downloads data into an in-memory buffer from a stream or a string.

- ``redirect_to_stdout()``: Redirects the content of the buffer to stdout for further processing or display.

- ``read()``: Reads the content from the buffer.

- ``clear()``: Clears the buffer for reuse.

- This implementation is designed for efficient handling of large data or media content like video/audio streams in memory, making it ideal for use cases like processing YouTube video data, saving temporary metadata, or streaming data to external applications.



**to redirect the download to stdout**::
        
        from pytubefix import YouTube
        from pytubefix import Buffer

        buffer = Buffer()

        url = "URL"

        yt = YouTube(url)
        ys = yt.streams.get_audio_only()

        buffer.download_in_buffer(ys)
        buffer.redirect_to_stdout()


**By doing this you can, for example, run the script with a pipe directing the audio stream to ffplay for example**::

        python3 main.py | ffplay -i -
