.. _livestreams:

Using Live Streams
=============================

**to get a list of live streams**::

        from pytubefix import Channel

        url_channel = input("url channel > ")

        c = Channel(url_channel)

        print("live streams :", c.livestreams_urls)
