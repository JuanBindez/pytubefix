.. _playlist:

Using Playlists
===============

This guide will walk you through the basics of working with pytubefix Playlists.

Creating a Playlist
-------------------

Using pytubefix to interact with playlists is very simple. 
Begin by importing the Playlist class::

    >>> from pytubefix import Playlist

Now let's create a playlist object. You can do this by initializing the object with a playlist URL::

    >>> p = Playlist('https://www.youtube.com/playlist?list=PLS1QulWo1RIaJECMeUT4LFwJ-ghgoSH6n')

Or you can create one from a video link in a playlist::

    >>> p = Playlist('https://www.youtube.com/watch?v=41qgdwd3zAg&list=PLS1QulWo1RIaJECMeUT4LFwJ-ghgoSH6n')

Now, we have a :class:`Playlist <pytubefix.Playlist>` object called ``p`` that we can do some work with.

Interacting with a playlist
---------------------------

Fundamentally, a Playlist object is just a container for YouTube objects.

If, for example, we wanted to download all of the videos in a playlist, we would do the following::

    from pytubefix import Playlist
    from pytubefix.cli import on_progress
     
    url = input("url here >")
    
    pl = Playlist(url)
    
    for video in pl.videos:
        ys = video.streams.get_highest_resolution()
        ys.download()

Or if we wanted to download all of the audios in a playlist, we would do the following::

    from pytubefix import Playlist
    from pytubefix.cli import on_progress
     
    url = input("url here >")
    
    pl = Playlist(url)
    
    for video in pl.videos:
        ys = video.streams.get_audio_only()
        ys.download(mp3=True)

Or, if we're only interested in the URLs for the videos, we can look at those as well::

    >>> for url in p.video_urls[:3]:
    >>>     print(url)
    ['https://www.youtube.com/watch?v=41qgdwd3zAg',
    'https://www.youtube.com/watch?v=Lbs7vmx3YwU',
    'https://www.youtube.com/watch?v=YtX-Rmoea0M']

And that's basically all there is to it!
