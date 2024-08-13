.. _search:

Using the Search Feature
========================

pytubefix includes functionality to search YouTube and return results almost
identical to those you would find using the search bar on YouTube's website.
The integration into pytubefix means that we can directly provide you with
YouTube objects that can be inspected and dowloaded, instead of needing to do
additional processing.


This example illustrates how the library can be used to automate YouTube searches and extract relevant data from videos::
    
    >>> from pytubefix import Search
    >>> 
    >>> results = Search('Github Issue Best Practices')
    >>> 
    >>> for video in results.videos:
    ...     print(f'Title: {video.title}')
    ...     print(f'URL: {video.watch_url}')
    ...     print(f'Duration: {video.length} seg')
    ...     print('---')
    ... 
    Title: Good Practices with GitHub Issues
    URL: https://youtube.com/watch?v=v1AeHaopAYE
    Duration: 406 seg
    ---
    Title: GitHub Issues Tips and Guidelines
    URL: https://youtube.com/watch?v=kezinXSoV5A
    Duration: 852 seg
    ---
    Title: 13 Advanced (but useful) Git Techniques and Shortcuts
    URL: https://youtube.com/watch?v=ecK3EnyGD8o
    Duration: 486 seg
    ---
    Title: Managing a GitHub Organization Tools, Tips, and Best Practices - Mark Matyas
    URL: https://youtube.com/watch?v=1T4HAPBFbb0
    Duration: 1525 seg
    ---
    Title: Do you know the best way to manage GitHub Issues?
    URL: https://youtube.com/watch?v=OccRyzAS4Vc
    Duration: 534 seg
    ---
    >>>


Using the Search object is really easy::

    >>> from pytubefix import Search
    >>> s = Search('YouTube Rewind')
    >>> len(s.results)
    17
    >>> s.results
    [\
        <pytubefix.__main__.YouTube object: videoId=YbJOTdZBX1g>, \
        <pytubefix.__main__.YouTube object: videoId=PKtnafFtfEo>, \
        ...\
    ]
    >>> 


Due to the potential for an endless stream of results, and in order to prevent
a user from accidentally entering an infinite loop of requesting additional
results, the ``.results`` attribute will only ever request the first set of
search results. Additional results can be explicitly requested by using the
``.get_next_results()`` method, which will append any additional results to
the ``.results`` attribute::

    >>> s.get_next_results()
    >>> len(s.results)
    34
    >>> 

Additional functionality
========================

In addition to the basic search functionality which returns YouTube objects,
searches also have associated autocomplete suggestions. These can be accessed
as follows::

    >>> s.completion_suggestions
    [\
        'can this video get 1 million dislikes', \
        'youtube rewind 2020 musical', \
        ...\
    ]


The .videos method will only return the videos::

    s = Search('YouTube Rewind')

    print(s.videos)


Output::

    [<pytubefix.__main__.YouTube object: videoId=_GuOjXYl5ew>, <pytubefix.__main__.YouTube object: videoId=FlsCjmMhFmw>, <pytubefix.__main__.YouTube object: videoId=KK9bwTlAvgo>, <pytubefix.__main__.YouTube object: videoId=YbJOTdZBX1g>, <pytubefix.__main__.YouTube object: videoId=H7jtC8vjXw8>, <pytubefix.__main__.YouTube object: videoId=iCkYw3cRwLo>, <pytubefix.__main__.YouTube object: videoId=zKx2B8WCQuw>, <pytubefix.__main__.YouTube object: videoId=2lAe1cqCOXo>, <pytubefix.__main__.YouTube object: videoId=By_Cn5ixYLg>, <pytubefix.__main__.YouTube object: videoId=Q5vQawTFJ0I>, <pytubefix.__main__.YouTube object: videoId=DpOCWIvpoE8>, <pytubefix.__main__.YouTube object: videoId=TjkRhh3Gh1U>, <pytubefix.__main__.YouTube object: videoId=PKtnafFtfEo>, <pytubefix.__main__.YouTube object: videoId=s7LNSuJHVww>, <pytubefix.__main__.YouTube object: videoId=diT6jc9flkc>, <pytubefix.__main__.YouTube object: videoId=SmnkYyHQqNs>, <pytubefix.__main__.YouTube object: videoId=glc2_--ZWoY>]


The .shorts method will only return the shorts.::

Here it is interesting to note that videos and shorts are from the same class of objects::

    s = Search('YouTube Rewind')

    print(s.shorts)


Output::

    [<pytubefix.__main__.YouTube object: videoId=cu7g_MB8uF4>, <pytubefix.__main__.YouTube object: videoId=sLbrJ9qWHwM>, <pytubefix.__main__.YouTube object: videoId=hNsFChiug28>, <pytubefix.__main__.YouTube object: videoId=6Qs1k7DKyfE>, <pytubefix.__main__.YouTube object: videoId=_6N44bZRJKE>, <pytubefix.__main__.YouTube object: videoId=rownH_IdP28>, <pytubefix.__main__.YouTube object: videoId=McIHLyoc2zk>, <pytubefix.__main__.YouTube object: videoId=8LEJmOzCfas>, <pytubefix.__main__.YouTube object: videoId=nbO3_bxYHx4>, <pytubefix.__main__.YouTube object: videoId=aFOmxMKsFwo>, <pytubefix.__main__.YouTube object: videoId=j28LZp08GIQ>, <pytubefix.__main__.YouTube object: videoId=u5HFzlkQ6hU>, <pytubefix.__main__.YouTube object: videoId=GNRe864aQq4>, <pytubefix.__main__.YouTube object: videoId=egdkRjY8OsE>, <pytubefix.__main__.YouTube object: videoId=luM--KkUwCc>, <pytubefix.__main__.YouTube object: videoId=HEc18y-QQYM>, <pytubefix.__main__.YouTube object: videoId=W4ET-jP6yd4>, <pytubefix.__main__.YouTube object: videoId=lxF5sF9hHPI>, <pytubefix.__main__.YouTube object: videoId=T50I0hqULkA>, <pytubefix.__main__.YouTube object: videoId=FXezutlwJog>, <pytubefix.__main__.YouTube object: videoId=rownH_IdP28>, <pytubefix.__main__.YouTube object: videoId=McIHLyoc2zk>, <pytubefix.__main__.YouTube object: videoId=8LEJmOzCfas>, <pytubefix.__main__.YouTube object: videoId=nbO3_bxYHx4>, <pytubefix.__main__.YouTube object: videoId=aFOmxMKsFwo>, <pytubefix.__main__.YouTube object: videoId=j28LZp08GIQ>, <pytubefix.__main__.YouTube object: videoId=u5HFzlkQ6hU>, <pytubefix.__main__.YouTube object: videoId=GNRe864aQq4>, <pytubefix.__main__.YouTube object: videoId=egdkRjY8OsE>, <pytubefix.__main__.YouTube object: videoId=luM--KkUwCc>]


The .playlist method will only return playlists::

	s = Search('python tutorial')

	print(s.playlist)


Output::

    [<pytubefix.contrib.Playlist object: playlistId=PLsyeobzWxl7poL9JTVyndKe62ieoN-MZ3>, <pytubefix.contrib.Playlist object: playlistId=PL-osiE80TeTt2d9bfVyTiXJA-UTHn6WwU>, <pytubefix.contrib.Playlist object: playlistId=PLWKjhJtqVAbnqBxcdjVGgT3uVR10bzTEB>, <pytubefix.contrib.Playlist object: playlistId=PLvE-ZAFRgX8hnECDn1v9HNTI71veL3oW0>]


The .channel method will return only the channels::

    s = Search('python channel')

    print(s.channel)


Output::

    [<pytubefix.contrib.Channel object: channelUri=/channel/UCI0vQvr9aFn27yR6Ej6n5UA>, <pytubefix.contrib.Channel object: channelUri=/channel/UCdu8D9NV9NP1iVPTYlenORw>, <pytubefix.contrib.Channel object: channelUri=/channel/UCqC1iSQnRIDz_rOy8LHe69g>, <pytubefix.contrib.Channel object: channelUri=/channel/UCKQdc0-Targ4nDIAUrlfKiA>, <pytubefix.contrib.Channel object: channelUri=/channel/UC3Qe9c8dZqnjwcDD2vCZBKQ>, <pytubefix.contrib.Channel object: channelUri=/channel/UC68KSmHePPePCjW4v57VPQg>, <pytubefix.contrib.Channel object: channelUri=/channel/UCGDlapuq4c7611vw44yfcNQ>, <pytubefix.contrib.Channel object: channelUri=/channel/UCripRddD4BnaMcU833ExuwA>, <pytubefix.contrib.Channel object: channelUri=/channel/UC8butISFwT-Wl7EV0hUK0BQ>, <pytubefix.contrib.Channel object: channelUri=/channel/UCTVGjydBHM2g5_K18MZqE4Q>]
