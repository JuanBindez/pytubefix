.. _cli:

Command-line Interface (CLI)
=============================

pytubefix ships with a command-line tool for downloading videos, audio,
playlists and channels, and for inspecting streams, captions and metadata.

It follows the usual Unix conventions:

* data goes to **stdout**; messages and the progress bar go to **stderr**;
* it is **silent on success** (the progress bar is drawn only on a terminal);
* errors look like ``pytubefix: URL: message`` and set a non-zero exit status;
* ``-`` means stdin/stdout, so it works in pipelines;
* a failure on one video does not stop the others;
* files are never overwritten unless you ask for it with ``-f``.

Usage
-----

.. code:: text

    pytubefix [download] [options] URL...      download videos or audio
    pytubefix playlist [options] URL|ID...     download a whole playlist or channel
    pytubefix streams URL                      list the available streams
    pytubefix info URL                         show video metadata
    pytubefix captions URL [-c CODE]           list caption tracks, or print one as SRT
    pytubefix search QUERY...                  search for videos
    pytubefix report URL                       save a playback report for bug reports

``pytubefix URL`` is shorthand for ``pytubefix download URL``, so the
following two commands are the same:

.. code:: bash

    $ pytubefix https://www.youtube.com/watch?v=2lAe1cqCOXo
    $ pytubefix download https://www.youtube.com/watch?v=2lAe1cqCOXo

To list all options, or to see the version:

.. code:: bash

    $ pytubefix --help
    $ pytubefix download --help
    $ pytubefix -V

Downloading videos
------------------

By default the highest resolution *progressive* stream (video and audio in a
single file) is downloaded to the current directory:

.. code:: bash

    $ pytubefix https://www.youtube.com/watch?v=2lAe1cqCOXo

Nothing is printed on success. If the file already exists, the command fails
with an error; use ``-f`` to overwrite it, or ``-s`` to skip it silently.

To download only the audio (the best ``mp4``/AAC stream by default):

.. code:: bash

    $ pytubefix -a https://www.youtube.com/watch?v=2lAe1cqCOXo
    $ pytubefix --audio-format webm https://www.youtube.com/watch?v=2lAe1cqCOXo

To download a specific stream, use its itag (see ``pytubefix streams``):

.. code:: bash

    $ pytubefix -i 22 https://www.youtube.com/watch?v=2lAe1cqCOXo

To choose a resolution, use ``-r``. When the resolution is only available as
separate video and audio streams, they are downloaded and merged with
``ffmpeg``, which must be installed and in your ``PATH``. ``-r best`` picks
the highest quality available:

.. code:: bash

    $ pytubefix -r 720p https://www.youtube.com/watch?v=2lAe1cqCOXo
    $ pytubefix -r 1080p https://www.youtube.com/watch?v=2lAe1cqCOXo
    $ pytubefix -r best https://www.youtube.com/watch?v=2lAe1cqCOXo

Options for ``download`` and ``playlist``:

.. list-table::
   :header-rows: 1
   :widths: 28 72

   * - Option
     - Description
   * - ``-a``, ``--audio``
     - Download the best audio stream.
   * - ``--audio-format EXT``
     - Audio container, for example ``mp4`` or ``webm`` (implies ``-a``).
   * - ``-i N``, ``--itag N``
     - Download the stream with this itag.
   * - ``-r RES``, ``--resolution RES``
     - ``720p``, ``1080p``, ... or ``best``. Merges video and audio with ffmpeg when needed.
   * - ``-o PATH``, ``--output PATH``
     - Output file or directory. ``-`` writes to stdout.
   * - ``-f``, ``--force``
     - Overwrite existing files.
   * - ``-s``, ``--skip-existing``
     - Silently skip files that already exist (handy to resume a playlist).
   * - ``-n N``, ``--limit N``
     - For playlists and channels: only the first ``N`` videos.
   * - ``--oauth``
     - Authenticate with OAuth. The token is cached after the first login.
   * - ``--logfile FILE``
     - Write the library's debug log to ``FILE``.
   * - ``-v``, ``--verbose``
     - Print one line per download on stderr. ``-vv`` also enables the debug log and tracebacks.
   * - ``-q``, ``--quiet``
     - Suppress warnings and the progress bar.

``-a``, ``-i`` and ``-r`` are mutually exclusive, as are ``-f`` and ``-s``.

Choosing the output
-------------------

``-o`` is interpreted like the destination of ``cp``:

.. code:: bash

    # a file name (single video only)
    $ pytubefix -a https://www.youtube.com/watch?v=2lAe1cqCOXo -o song.m4a

    # a directory (created if needed; use a trailing slash for a new one)
    $ pytubefix -a https://www.youtube.com/watch?v=2lAe1cqCOXo -o music/

    # standard output, for pipelines (not allowed on a terminal)
    $ pytubefix -a https://www.youtube.com/watch?v=2lAe1cqCOXo -o - | mpv -

With several URLs, or with a playlist, ``-o`` is always a directory.

Files are first built in a private temporary directory next to the
destination and then moved into place, so an interrupted download never
leaves a partial file behind.

Playlists and channels
----------------------

Playlist and channel URLs are detected automatically, so the normal command
works:

.. code:: bash

    $ pytubefix -a "https://www.youtube.com/playlist?list=PLxxxx" -o music/

The ``playlist`` command does the same, but always treats the URL as a
playlist. This is useful for a ``watch?v=...&list=...`` link (which a plain
``download`` treats as a single video), and it also accepts a bare playlist id:

.. code:: bash

    $ pytubefix playlist -a "https://www.youtube.com/watch?v=VIDEO&list=PLxxxx" -o music/
    $ pytubefix playlist -a PLxxxx -o music/

Channels work the same way:

.. code:: bash

    $ pytubefix playlist -a -n 10 "https://www.youtube.com/@ProgrammingKnowledge" -o channel/

Notes:

* Without ``-o``, the files go to a directory named after the playlist (or
  channel).
* Use ``-n`` to limit the number of videos; a channel can have thousands.
* A video that fails (private, unavailable, age-restricted without
  ``--oauth``) is reported and the download continues. The exit status is 1.
* Run the same command again with ``-s`` to resume an interrupted playlist.
* ``playlist --list`` only prints the video URLs, one per line, without
  downloading anything.

URLs can also be read from stdin, one per line (blank lines and lines
starting with ``#`` are ignored):

.. code:: bash

    $ pytubefix playlist --list -n 5 PLxxxx | pytubefix -a - -o music/

Progress bar
------------

When stderr is a terminal, a progress line is drawn for each download. It is
kept on screen when the download finishes, and playlists show a ``[i/N]``
counter:

.. code:: text

    [1/3] Video title            ↳ |████████████| 100.0%  3.9MiB/3.9MiB  4.1MiB/s
    [2/3] Another title          ↳ |██████░░░░░░|  52.1%  2.0MiB/3.9MiB  1.8MiB/s

When video and audio are merged, one line is shown for each (``[video]`` and
``[audio]``). If the size is unknown, only the amount downloaded and the speed
are shown. The bar is not drawn when stderr is redirected, or with ``-q``.

Listing streams
---------------

.. code:: bash

    $ pytubefix streams https://www.youtube.com/watch?v=2lAe1cqCOXo

On a terminal this prints an aligned table with a header. When piped, it
prints tab-separated columns without a header, which is easy to parse:

.. code:: bash

    $ pytubefix streams URL | cut -f1,3

The columns are: itag, type, quality (resolution or bitrate), fps, mime type,
video codec, audio codec, approximate size and whether the stream is
progressive.

Video information
-----------------

.. code:: bash

    $ pytubefix info https://www.youtube.com/watch?v=2lAe1cqCOXo

Prints ``key: value`` lines (title, author, length in seconds, views,
publication date, thumbnail, URL and id).

Captions
--------

To get a list of all subtitles (``code<TAB>name``):

.. code:: bash

    $ pytubefix captions https://www.youtube.com/watch?v=2lAe1cqCOXo

To print a specific subtitle in SRT format, use ``-c`` with the caption code
(here, the English subtitles). The text goes to stdout, so you can redirect it,
or use ``-o`` to write a file:

.. code:: bash

    $ pytubefix captions https://www.youtube.com/watch?v=2lAe1cqCOXo -c en
    $ pytubefix captions https://www.youtube.com/watch?v=2lAe1cqCOXo -c en > subtitles.srt
    $ pytubefix captions https://www.youtube.com/watch?v=2lAe1cqCOXo -c en -o subtitles.srt

If the code does not exist, the error lists the available codes.

Searching
---------

.. code:: bash

    $ pytubefix search "lofi hip hop" -n 5

Each result is printed as ``URL<TAB>title<TAB>duration``. Combined with the
other commands:

.. code:: bash

    $ pytubefix search "lofi hip hop" -n 3 | cut -f1 | pytubefix -a - -o music/

Bug reports
-----------

If you are filing a bug report, the ``report`` command bundles up the state
of a video (page, player script and video info) into a compressed file,
allowing others to easily replay your issue:

.. code:: bash

    $ pytubefix report https://www.youtube.com/watch?v=2lAe1cqCOXo
    $ pytubefix report https://www.youtube.com/watch?v=2lAe1cqCOXo -o report.json.gz

The default file name is ``yt-video-ID-TIMESTAMP.json.gz``. For problems
during a download, ``-vv`` also prints the library's debug log and the full
traceback of any error.

Exit status
-----------

.. list-table::
   :header-rows: 1
   :widths: 15 85

   * - Code
     - Meaning
   * - 0
     - Success.
   * - 1
     - At least one error (unavailable video, existing file, missing ffmpeg, ...).
   * - 2
     - Invalid usage (wrong or conflicting arguments).
   * - 130
     - Interrupted with Ctrl+C.
   * - 143
     - Terminated by SIGTERM.

Temporary files are removed in every case.

Using the progress bar in your own code
---------------------------------------

The ``on_progress`` function used by the CLI is also available to library
users:

.. code:: python

    from pytubefix import YouTube
    from pytubefix.cli import on_progress

    yt = YouTube(url, on_progress_callback=on_progress)
    yt.streams.get_highest_resolution().download()

Upgrading from the previous CLI
-------------------------------

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Previous
     - Now
   * - ``pytubefix URL --list``
     - ``pytubefix streams URL``
   * - ``--itag=N``
     - ``-i N``
   * - ``--list-captions``, ``-lc``
     - ``pytubefix captions URL``
   * - ``-c CODE``
     - ``pytubefix captions URL -c CODE`` (prints the SRT; ``-o FILE`` saves it)
   * - ``-t DIR``, ``--target DIR``
     - ``-o DIR``
   * - ``-a [FORMAT]``
     - ``-a``, plus ``--audio-format FORMAT``
   * - ``-f [RES]``, ``--ffmpeg [RES]``
     - ``-r RES`` (merges automatically); ``-f`` now means ``--force``
   * - ``-v`` (debug log)
     - ``-vv``
   * - ``--build-playback-report``
     - ``pytubefix report URL``

Also note that a file that already exists is now an error (exit status 1)
instead of an "already downloaded" message: use ``-s`` to skip such files
silently, or ``-f`` to overwrite them. ``--oauth`` and ``--logfile`` are
unchanged.