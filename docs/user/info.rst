.. _info:

Info
====

This can be useful for debugging or logging purposes, as it allows developers to quickly check the environment in which the code is being executed. It helps ensure that the correct versions of Python and Pytubefix are being used, and can also assist in identifying any compatibility issues between the system and the application::
    >>> from pytubefix import info
    >>> 
    >>> print(info())
    {'OS': {'linux'}, 'Python': {'3.11.6 (main, Apr 10 2024, 17:26:07) [GCC 13.2.0]'}, 'Pytubefix': {'7.3.1'}}
    >>> 

to get just the operating system::
    >>> from pytubefix import info
    >>> 
    >>> system_info = info()
    >>> 
    >>> print(f"Operational System: {system_info['OS']}")
    Operational System: linux
    >>> 
    >>>

to use only the pytubefix version::
    >>> from pytubefix import info
    >>> 
    >>> system_info = info()
    >>> 
    >>> print(f"Pytubefix Version: {system_info['Pytubefix']}")
    Pytubefix Version: 7.3.1
    >>>

The main purpose is to use in logs, especially if you are using in cloud environments where you may be using a broken version of pytubefix::
    >>> import logging
    >>> from pytubefix import YouTube, info
    >>> from pytubefix.cli import on_progress
    >>> 
    >>> logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    >>> 
    >>> system_info = info()
    >>> 
    >>> def on_progress_with_logging(stream, chunk, bytes_remaining):
    ...     progress = 100 - (bytes_remaining / stream.filesize * 100)
    ...     logging.info(f"Download progress: {progress:.2f}%")
    ... 
    >>> url = "https://www.youtube.com/watch?v=9bZkp7q19f0"
    >>> 
    >>> yt = YouTube(url, on_progress_callback=on_progress_with_logging)
    >>> 
    >>> ys = yt.streams.get_highest_resolution()
    >>> ys.download()
    '/home/PSY - GANGNAM STYLE(강남스타일) MV.mp4'
    >>> 
    >>> logging.info(f"System Information: Pytubefix v{system_info['Pytubefix']}, Python{system_info['Python']}, OS {system_info['OS']}")
    2024-11-14 23:00:10,876 - INFO - System Information: Pytubefix v8.3.2, Python3.11.6 (main, Apr 10 2024, 17:26:07) [GCC 13.2.0], OS linux
    >>> logging.info(f"Video title: {yt.title}")
    2024-11-14 23:00:10,877 - INFO - Video title: PSY - GANGNAM STYLE(강남스타일) M/V
    >>> 
    >>> 

