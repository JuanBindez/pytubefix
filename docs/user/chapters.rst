.. _chapters:

Chapters
========


Usage::

    >>> from pytubefix import YouTube
    >>> url = 'https://www.youtube.com/watch?v=kRzgCylePjk'
    >>> yt = YouTube(url)
    >>> print(yt.chapters)

Output::

    [<Chapter: Escapement | 0:00:00>, <Chapter: Winding | 0:01:38>, <Chapter: Automatic Winding | 0:02:36>, <Chapter: Gearing | 0:03:46>, <Chapter: Day | 0:05:15>, <Chapter: Year | 0:06:26>, <Chapter: Solar Panel | 0:07:50>, <Chapter: Lifetime | 0:08:52>, <Chapter: Year Counter | 0:09:18>, <Chapter: Cosmic Year | 0:10:00>]

Get chapter titles::

    >>> print(yt.chapters[0].title)

Output::

    Escapement

Start label::

    >>> print(yt.chapters[0].start_label)

Output::

    0:00:00

Thumbnails::

    >>> print(yt.chapters[2].thumbnails)

Output::

    [ChapterThumbnail(width=168, height=94, url='https://i.ytimg.com/vi/kRzgCylePjk/hqdefault_167900.jpg?sqp=-oaymwEiCKgBEF5IWvKriqkDFQgBFQAAAAAYASUAAMhCPQCAokN4AQ==&rs=AOn4CLDQKFt-u0x3eTAkA5xLxjSKZE7wwg'), ChapterThumbnail(width=336, height=188, url='https://i.ytimg.com/vi/kRzgCylePjk/hqdefault_167900.jpg?sqp=-oaymwEjCNACELwBSFryq4qpAxUIARUAAAAAGAElAADIQj0AgKJDeAE=&rs=AOn4CLCllQhqs7En3aPXP9a7zBmae8qIcw')]