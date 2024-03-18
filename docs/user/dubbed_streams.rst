.. _dubbed_streams:

Filtering Dubbed Streams
==============

**YouTube added videos that contain multiple audios for re-dubbing, but they have the same Itag**::

Adds the possibility of filtering these streams that contain dubbing.


* The `includes_multiple_audio_tracks` property checks if Itag has dubbed tracks, returns True or False.

* The `audio_track_name` property returns the name of the dubbed language, returns None if the Itag is not dubbed.

* The `is_default_audio_track` property checks whether the track is the default audio.


This will only filter dubbed streams that are not the default language::

    yt = YouTube('https://www.youtube.com/watch?v=g_VxOIlg7q8')

    for s in yt.streams.get_extra_audio_track():
        print(f"{s.itag} {s.includes_multiple_audio_tracks} {s.audio_track_name}")

Output::

    139 True German
    139 True Spanish
    140 True German
    140 True Spanish
    249 True German
    249 True Spanish
    250 True German
    250 True Spanish
    251 True German
    251 True Spanish
    599 True German
    599 True Spanish
    600 True German
    600 True Spanish


We can also get just the default audio streams::

    yt = YouTube('https://www.youtube.com/watch?v=g_VxOIlg7q8')

    for s in yt.streams.get_default_audio_track():
        print(f"{s.itag} {s.includes_multiple_audio_tracks} {s.audio_track_name}")

Output::

    139 True English
    140 True English
    249 True English
    250 True English
    251 True English
    599 True English
    600 True English

If we want to get dubbed tracks we can filter by name::

    yt = YouTube('https://www.youtube.com/watch?v=g_VxOIlg7q8')

    for s in yt.streams.get_extra_audio_track_by_name("German"):
        print(f"{s.itag} {s.includes_multiple_audio_tracks} {s.audio_track_name}")

Output::

    139 True German
    140 True German
    249 True German
    250 True German
    251 True German
    599 True German
    600 True German