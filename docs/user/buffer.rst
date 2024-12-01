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



to redirect the download to stdout:
        
.. code:: python

        from pytubefix import YouTube
        from pytubefix import Buffer

        buffer = Buffer()

        url = "URL"

        yt = YouTube(url)
        ys = yt.streams.get_audio_only()

        buffer.download_in_buffer(ys)
        buffer.redirect_to_stdout()

**Playing Audio on the Terminal**

If the buffer contains an audio stream, you can send it directly to players like ffplay:

.. code:: bash

        $ python3 main.py | ffplay -i -


In the terminal, run the script and pipe the output to ffmpeg:

.. code:: bash

        $ python3 main.py | ffmpeg -i - -acodec libmp3lame output.mp3

You can send buffer data to tools like cat or less to view:

.. code:: bash

        $ python3 main.py | less

Directly redirect the script output to create a file in the terminal:

.. code:: bash

        $ python3 main.py > output.webm

Share via network with NC:

.. code:: bash

        $ python3 main.py | nc 192.168.1.100 5000


**Creating a Stream for Other Software**

Route the output to audio/video editing or manipulation software.

Processing in Audacity:

Save the audio in .wav and automatically open it in Audacity:

.. code:: bash

        $ python3 main.py | ffmpeg -i - -f wav - | audacity


Play a Playlist directly on the terminal instead of saving:

.. code:: python

        from pytubefix import Playlist
        from pytubefix import Buffer

        buffer = Buffer()

        url = "url"

        pl = Playlist(url)
        for video in pl.videos:
            ys = video.streams.get_audio_only()
            
            buffer.download_in_buffer(ys)
            buffer.redirect_to_stdout()

Run the command to play the playlist in the terminal
        
.. code:: bash

        $ python3 playlist.py | ffplay -i -

Processing in Real Time

Preview with ``hexdump``:

.. code:: bash

        $ python3 main.py | hexdump -C


Send the buffer contents to an API or other service.

.. code:: python

        import requests

        response = requests.post(
        "http://example.com/upload",
        files={"file": buffer.read()}
        )
        print(response.status_code)

**Encryption or Compression**

Perform encryption or compression operations directly on the buffer.

Compression:

.. code:: python

        import gzip

        compressed_data = gzip.compress(buffer.read())
        with open("compressed.gz", "wb") as file:
            file.write(compressed_data)

Encryption Example:

.. code:: python

        from cryptography.fernet import Fernet

        key = Fernet.generate_key()
        cipher = Fernet(key)

        encrypted_data = cipher.encrypt(buffer.read())
        print("Encrypted data:", encrypted_data)

**Converting the Format**

If the content is multimedia, you can convert it before saving or using it.
Example with ``ffmpeg-python``:


.. code:: python

        import ffmpeg

        input_stream = ffmpeg.input("pipe:", format="mp3")
        output_stream = ffmpeg.output(input_stream, "output.wav")
        ffmpeg.run(output_stream, pipe_stdin=True, input=buffer.read())


**Distribute via Network**

Use sockets to send buffer contents to other computers.

.. code:: python

        import socket

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(("127.0.0.1", 65432))
            s.sendall(buffer.read())


**Cache in Memory**

Use the buffer as a cache to avoid multiple downloads or reads.

.. code:: python

        cache = buffer.read()