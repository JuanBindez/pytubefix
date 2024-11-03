.. _captions:

Subtitle/Caption Tracks
=======================

pytubefix exposes the caption tracks in much the same way as querying the media
streams. Let's begin by switching to a video that contains them::

    from pytubefix import YouTube

    yt = YouTube('http://youtube.com/watch?v=2lAe1cqCOXo')
    subtitles = yt.captions
    
    print(subtitles)


Now you can save subtitles to a txt file::

    from pytubefix import YouTube

    yt = YouTube('http://youtube.com/watch?v=2lAe1cqCOXo')
    
    caption = yt.captions['a.en']
    caption.save_captions("captions.txt")


Now let's checkout the english captions::

    >>> caption = yt.captions['a.en']

Great, now let's see how YouTube formats them::

    >>> caption.xml_captions
    '<?xml version="1.0" encoding="utf-8" ?><transcript><text start="10.2" dur="0.94">K-pop!</text>...'

Oh, this isn't very easy to work with, let's convert them to the srt format::

    >>> print(caption.generate_srt_captions())
    1
    00:00:10,200 --> 00:00:11,140
    K-pop!

    2
    00:00:13,400 --> 00:00:16,200
    That is so awkward to watch.
    ...
