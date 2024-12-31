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
    ...     print(f'Duration: {video.length} sec')
    ...     print('---')
    ... 
    Title: Good Practices with GitHub Issues
    URL: https://youtube.com/watch?v=v1AeHaopAYE
    Duration: 406 sec
    ---
    Title: GitHub Issues Tips and Guidelines
    URL: https://youtube.com/watch?v=kezinXSoV5A
    Duration: 852 sec
    ---
    Title: 13 Advanced (but useful) Git Techniques and Shortcuts
    URL: https://youtube.com/watch?v=ecK3EnyGD8o
    Duration: 486 sec
    ---
    Title: Managing a GitHub Organization Tools, Tips, and Best Practices - Mark Matyas
    URL: https://youtube.com/watch?v=1T4HAPBFbb0
    Duration: 1525 sec
    ---
    Title: Do you know the best way to manage GitHub Issues?
    URL: https://youtube.com/watch?v=OccRyzAS4Vc
    Duration: 534 sec
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

    >>> from pytubefix import Search
    >>> 
    >>> s = Search('YouTube Rewind')
    >>> 
    >>> print(s.videos)
    [<pytubefix.__main__.YouTube object: videoId=_GuOjXYl5ew>, <pytubefix.__main__.YouTube object: videoId=YbJOTdZBX1g>, <pytubefix.__main__.YouTube object: videoId=FlsCjmMhFmw>, <pytubefix.__main__.YouTube object: videoId=H7jtC8vjXw8>, <pytubefix.__main__.YouTube object: videoId=KK9bwTlAvgo>, <pytubefix.__main__.YouTube object: videoId=zKx2B8WCQuw>, <pytubefix.__main__.YouTube object: videoId=IPZO85HFM4w>, <pytubefix.__main__.YouTube object: videoId=QkVgMSoQ43w>, <pytubefix.__main__.YouTube object: videoId=By_Cn5ixYLg>, <pytubefix.__main__.YouTube object: videoId=dUWB52DuKIQ>, <pytubefix.__main__.YouTube object: videoId=TjkRhh3Gh1U>, <pytubefix.__main__.YouTube object: videoId=iCkYw3cRwLo>, <pytubefix.__main__.YouTube object: videoId=PKtnafFtfEo>, <pytubefix.__main__.YouTube object: videoId=2lAe1cqCOXo>, <pytubefix.__main__.YouTube object: videoId=6Ko7BpR27Qc>, <pytubefix.__main__.YouTube object: videoId=G4iwifB0bKg>]
    >>> 


The .shorts method will only return the shorts.::

Here it is interesting to note that videos and shorts are from the same class of objects::

    >>> from pytubefix import Search
    >>> 
    >>> s = Search('YouTube Rewind')
    >>> 
    >>> print(s.shorts)
    [<pytubefix.__main__.YouTube object: videoId=hNsFChiug28>, <pytubefix.__main__.YouTube object: videoId=IWsnehFPjRA>, <pytubefix.__main__.YouTube object: videoId=7yFTNuHaL_Q>, <pytubefix.__main__.YouTube object: videoId=lxF5sF9hHPI>, <pytubefix.__main__.YouTube object: videoId=Sm5rm2XKjGE>, <pytubefix.__main__.YouTube object: videoId=7U6Ixt6HaY4>, <pytubefix.__main__.YouTube object: videoId=F2jsqWWghgo>, <pytubefix.__main__.YouTube object: videoId=3KOubezv0Rw>, <pytubefix.__main__.YouTube object: videoId=7-SBiPOKKTM>, <pytubefix.__main__.YouTube object: videoId=6Qs1k7DKyfE>, <pytubefix.__main__.YouTube object: videoId=lO7uzfjH2A0>, <pytubefix.__main__.YouTube object: videoId=luM--KkUwCc>, <pytubefix.__main__.YouTube object: videoId=wla6nswDLwk>, <pytubefix.__main__.YouTube object: videoId=_6N44bZRJKE>, <pytubefix.__main__.YouTube object: videoId=syq2Te2-CUQ>, <pytubefix.__main__.YouTube object: videoId=QG8j9VTdLNU>, <pytubefix.__main__.YouTube object: videoId=GNRe864aQq4>, <pytubefix.__main__.YouTube object: videoId=icipLFXofZo>, <pytubefix.__main__.YouTube object: videoId=j28LZp08GIQ>, <pytubefix.__main__.YouTube object: videoId=NmihbYu1dQs>, <pytubefix.__main__.YouTube object: videoId=b677xPIMzvM>, <pytubefix.__main__.YouTube object: videoId=Nf8bxAeLSHM>, <pytubefix.__main__.YouTube object: videoId=v7Sg9o9zw3o>, <pytubefix.__main__.YouTube object: videoId=vDJNpZ1bA0E>, <pytubefix.__main__.YouTube object: videoId=jwjiCUcuuhE>, <pytubefix.__main__.YouTube object: videoId=sLbrJ9qWHwM>, <pytubefix.__main__.YouTube object: videoId=pte1aSZicko>, <pytubefix.__main__.YouTube object: videoId=tpk0guPDuR0>, <pytubefix.__main__.YouTube object: videoId=MQyrTdZZzDs>, <pytubefix.__main__.YouTube object: videoId=2WW4VITeP3g>, <pytubefix.__main__.YouTube object: videoId=lC8gdwUnY_c>, <pytubefix.__main__.YouTube object: videoId=jZH93IcT8_I>, <pytubefix.__main__.YouTube object: videoId=hv42H3K1FhM>, <pytubefix.__main__.YouTube object: videoId=fP81TJW7-jY>, <pytubefix.__main__.YouTube object: videoId=m4ibgbrM77s>, <pytubefix.__main__.YouTube object: videoId=7U6Ixt6HaY4>, <pytubefix.__main__.YouTube object: videoId=F2jsqWWghgo>, <pytubefix.__main__.YouTube object: videoId=3KOubezv0Rw>, <pytubefix.__main__.YouTube object: videoId=7-SBiPOKKTM>, <pytubefix.__main__.YouTube object: videoId=6Qs1k7DKyfE>, <pytubefix.__main__.YouTube object: videoId=lO7uzfjH2A0>, <pytubefix.__main__.YouTube object: videoId=luM--KkUwCc>, <pytubefix.__main__.YouTube object: videoId=wla6nswDLwk>, <pytubefix.__main__.YouTube object: videoId=_6N44bZRJKE>, <pytubefix.__main__.YouTube object: videoId=syq2Te2-CUQ>]
    >>> 


The .playlist method will only return playlists::

    >>> from pytubefix import Search
    >>> 
    >>> s = Search('python tutorial')
    >>> 
    >>> 
    >>> for p in s.playlist:
    ...     print('url', p.playlist_url)
    ... 
    url https://www.youtube.com/playlist?list=PL-osiE80TeTt2d9bfVyTiXJA-UTHn6WwU
    url https://www.youtube.com/playlist?list=PLsyeobzWxl7poL9JTVyndKe62ieoN-MZ3
    url https://www.youtube.com/playlist?list=PLWKjhJtqVAbnqBxcdjVGgT3uVR10bzTEB
    url https://www.youtube.com/playlist?list=PLTjRvDozrdlxj5wgH4qkvwSOdHLOCx10f
    url https://www.youtube.com/playlist?list=PLBZBJbE_rGRWeh5mIBhD-hhDwSEDxogDg
    url https://www.youtube.com/playlist?list=PLGjplNEQ1it8-0CmoljS5yeV-GlKSUEt0
    url https://www.youtube.com/playlist?list=PLS1QulWo1RIaJECMeUT4LFwJ-ghgoSH6n
    url https://www.youtube.com/playlist?list=PLu0W_9lII9agwh1XjRt242xIpHhPT2llg
    >>> 



The .channel method will return only the channels::

    >>> from pytubefix import Search
    >>> 
    >>> s = Search('python channel')
    >>> 
    >>> print(s.channel)

    [<pytubefix.contrib.Channel object: channelUri=/channel/UC2liIKa5d4tvBiNzBng20PA>, <pytubefix.contrib.Channel object: channelUri=/channel/UCI0vQvr9aFn27yR6Ej6n5UA>, <pytubefix.contrib.Channel object: channelUri=/channel/UCqC1iSQnRIDz_rOy8LHe69g>, <pytubefix.contrib.Channel object: channelUri=/channel/UC3Qe9c8dZqnjwcDD2vCZBKQ>, <pytubefix.contrib.Channel object: channelUri=/channel/UClbtTCONv0ZFoM399-r4CnA>, <pytubefix.contrib.Channel object: channelUri=/channel/UC68KSmHePPePCjW4v57VPQg>, <pytubefix.contrib.Channel object: channelUri=/channel/UCKQdc0-Targ4nDIAUrlfKiA>]
    >>> 
    >>>


Using Filters
=============

It wouldn't be very practical for the user or developer to have to manually retrieve the custom filter from YouTube whenever they want to do a search, so the Filter class will do all the work of providing all the available filters, combining them, coding them in protobuf and send to the Search class, all we need to do is import it and create a dictionary with the necessary filters::
    
    >>> from pytubefix.contrib.search import Search, Filter
    >>> 
    >>> 
    >>> filters = {
    ...     'upload_date': Filter.get_upload_date('Today'),
    ...     'type': Filter.get_type("Video"),
    ...     'duration': Filter.get_duration("Under 4 minutes"),
    ...     'features': [Filter.get_features("4K"), Filter.get_features("Creative Commons")],
    ...     'sort_by': Filter.get_sort_by("Upload date")
    ... }
    >>> 
    >>> s = Search('music', filters=f)
    >>> for c in s.videos:
    ...     print(c.watch_url)
    ... 
    https://youtube.com/watch?v=_Rq8MzYz0YU
    https://youtube.com/watch?v=YHPGM8nBk3U
    https://youtube.com/watch?v=m98WShs7MLE
    https://youtube.com/watch?v=-vBqfC3Nir0
    https://youtube.com/watch?v=LbtrnCjopwk
    https://youtube.com/watch?v=pfl2ga6AS3c
    https://youtube.com/watch?v=TzNk2ygEU4c
    https://youtube.com/watch?v=yQfXVRKvA70
    https://youtube.com/watch?v=G5tQX990XU0
    https://youtube.com/watch?v=4LQzYMhtXV8
    https://youtube.com/watch?v=BOLGwdjCSAo
    https://youtube.com/watch?v=CgSH3Ww3MHs
    https://youtube.com/watch?v=_43tx98VEWc
    https://youtube.com/watch?v=wLDRGZaBEoQ
    https://youtube.com/watch?v=3qaHb2t3Lkw
    https://youtube.com/watch?v=56deLmbicLg
    https://youtube.com/watch?v=pQk2TzmwnS0
    https://youtube.com/watch?v=NJ3sOlg8KGo
    https://youtube.com/watch?v=kfDSHjlk4Pg
    https://youtube.com/watch?v=8KHak4ZNO3k
    >>> 
