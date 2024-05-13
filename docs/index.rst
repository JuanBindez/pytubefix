.. pytubefix documentation master file,

pytubefix
======
Release v\ |version|. (:ref:`Installation<install>`)


.. image:: https://img.shields.io/pypi/v/pytubefix.svg
  :alt: Pypi
  :target: https://pypi.python.org/pypi/pytubefix/

.. image:: https://img.shields.io/pypi/pyversions/pytubefix.svg
  :alt: Python Versions
  :target: https://pypi.python.org/pypi/pytubefix/


**pytubefix** is a lightweight, Pythonic, dependency-free, library (and
command-line utility) for downloading YouTube Videos.

-------------------

**Behold, a perfect balance of simplicity versus flexibility**::

    from pytubefix import YouTube
    from pytubefix.cli import on_progress
     
    url = input("URL >")
     
    yt = YouTube(url, on_progress_callback = on_progress)
    print(yt.title)
     
    ys = yt.streams.get_highest_resolution()
    ys.download()

Features
--------

- Support for Both Progressive & DASH Streams
- Easily Register ``on_download_progress`` & ``on_download_complete`` callbacks
- Command-line Interfaced Included
- Caption Track Support
- Outputs Caption Tracks to .srt format (SubRip Subtitle)
- Ability to Capture Thumbnail URL.
- Extensively Documented Source Code
- No Third-Party Dependencies

The User Guide
--------------
This part of the documentation begins with some background information about
the project, then focuses on step-by-step instructions for getting the most out
of pytubefix.

.. toctree::
   :maxdepth: 2

   user/install
   user/quickstart
   user/streams
   user/auth
   user/mp3
   user/captions
   user/playlist
   user/channel
   user/search
   user/channel_playlists
   user/cli
   user/exceptions
   user/chapters
   user/dubbed_streams
   user/keymoments

The API Documentation
-----------------------------

If you are looking for information on a specific function, class, or method,
this part of the documentation is for you.

.. toctree::
   :maxdepth: 2

   api


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
