.. _channel_playlists:

Getting Channel Playlists
=============================

**This code takes the ids of the channel's playlists and returns an array containing the playlist objects:**::

        from pytubefix import Channel

        ch = Channel('https://www.youtube.com/@Alanwalkermusic')

        print(ch.playlists)

Output::

    [<pytube.contrib.Playlist object: playlistId=PLYT4vq6pQVSsZjqBrHZ4Snm2DL9hJO9Tu>, <pytube.contrib.Playlist object: playlistId=PLYT4vq6pQVSsYQQK6tiJARRzNtz7N9tVx>, <pytube.contrib.Playlist object: playlistId=PLYT4vq6pQVSvyFkY8-7OBgVK9NEgCcnv3>, <pytube.contrib.Playlist object: playlistId=PLYT4vq6pQVSvc1KlnC6Qg8FFqyQK5l-RW>, <pytube.contrib.Playlist object: playlistId=PLYT4vq6pQVStw9p0DEl7jGxDV-Swg3ENl>, <pytube.contrib.Playlist object: playlistId=PLYT4vq6pQVSuPVcXOaeW_ZJlKBcHTcOyp>, <pytube.contrib.Playlist object: playlistId=PLYT4vq6pQVSsPGIkBqrFDux-fKZXSSZ9g>, <pytube.contrib.Playlist object: playlistId=PLYT4vq6pQVStbQ33sKs1cQJUkXRyPNHkX>, <pytube.contrib.Playlist object: playlistId=PLYT4vq6pQVSuNn7a_JBgvg6lxbIG8E-8Z>, <pytube.contrib.Playlist object: playlistId=PLYT4vq6pQVSvgqA8Qsm8TXjYJMTT2XyNV>, <pytube.contrib.Playlist object: playlistId=PLYT4vq6pQVSu7K54xk1A8GTcJ2DcW1Mih>, <pytube.contrib.Playlist object: playlistId=PLYT4vq6pQVSsNQTHcU2fj5zWnLkZVb_Mu>, <pytube.contrib.Playlist object: playlistId=PLYT4vq6pQVSvs1PubZJnP9guAkNWz71L9>, <pytube.contrib.Playlist object: playlistId=PLYT4vq6pQVSuqGM4Q_UL4EV8VVf5py0_B>, <pytube.contrib.Playlist object: playlistId=PLYT4vq6pQVStn6XNcTF9EovQ6WkOBv98u>, <pytube.contrib.Playlist object: playlistId=PLYT4vq6pQVSvWapTdSzFGErAua7uC9ul0>, <pytube.contrib.Playlist object: playlistId=PLYT4vq6pQVSsyXWNiXAwEUBKfr-_BG-z9>, <pytube.contrib.Playlist object: playlistId=PLYT4vq6pQVSsT-mKS0puL64QtEcWKZrsU>, <pytube.contrib.Playlist object: playlistId=PLYT4vq6pQVSuJMlsIhTkQS7tHIzbAcoTK>, <pytube.contrib.Playlist object: playlistId=PLYT4vq6pQVStpbZ99S4MWXUkkElB6dl0z>, <pytube.contrib.Playlist object: playlistId=PLYT4vq6pQVSs9M1CRPgHmVhoG47BRbNg_>, <pytube.contrib.Playlist object: playlistId=PLYT4vq6pQVSu743ULpyGUVZTZtWMUKIXf>, <pytube.contrib.Playlist object: playlistId=PLYT4vq6pQVSvL-YWEkaYoR1HWJj6Ao1oh>, <pytube.contrib.Playlist object: playlistId=PLYT4vq6pQVSuQ6ecJmh0GqfBNNXM-Brg6>, <pytube.contrib.Playlist object: playlistId=PLYT4vq6pQVSuLJ1s2M05T2C2YrcIIOHX6>, <pytube.contrib.Playlist object: playlistId=PLYT4vq6pQVSsqAudfP_I3kX2zrLB7xWAF>, <pytube.contrib.Playlist object: playlistId=PLYT4vq6pQVSs41obbOyNtR45yJT1e7jcm>, <pytube.contrib.Playlist object: playlistId=PLYT4vq6pQVSuBYlHFYkU6Qib9QE6QWGFi>, <pytube.contrib.Playlist object: playlistId=PLYT4vq6pQVSs6yFw3mmlCpOe73oVb1_wM>, <pytube.contrib.Playlist object: playlistId=PLYT4vq6pQVSuukCycDDhGhraQelJvAjrM>, <pytube.contrib.Playlist object: playlistId=PLYT4vq6pQVSvo53Vw-Zl5e3pPDZt8V2PE>, <pytube.contrib.Playlist object: playlistId=PLYT4vq6pQVSsIbApbrc1UDKxiXyz_54u7>, <pytube.contrib.Playlist object: playlistId=PLYT4vq6pQVSvXar5BURTTP4kMomUxUwfi>, <pytube.contrib.Playlist object: playlistId=PLYT4vq6pQVStIzhZujr5CqmxE_QQ3Yqoc>, <pytube.contrib.Playlist object: playlistId=PLYT4vq6pQVSvIozhlZimv-o51JlnElhej>, <pytube.contrib.Playlist object: playlistId=PLYT4vq6pQVSvyrBQ3fwQo8YxqJ64WRC3r>, <pytube.contrib.Playlist object: playlistId=PLYT4vq6pQVSs6LEk6hO87ma43yWY2fMs->, <pytube.contrib.Playlist object: playlistId=PLYT4vq6pQVSsr5I-m0SjAPANwq3WgRWLF>, <pytube.contrib.Playlist object: playlistId=PLYT4vq6pQVSvdbTsIbjlD-modHKfZAWmJ>, <pytube.contrib.Playlist object: playlistId=PLYT4vq6pQVSuCGuTAXm_8VNEyZ-lcwy5u>, <pytube.contrib.Playlist object: playlistId=PLYT4vq6pQVSsOhQ0w_RbdgvsvvCm9kxVf>, <pytube.contrib.Playlist object: playlistId=PLYT4vq6pQVStohX0gsx8iPGwdjDjIyrBt>, <pytube.contrib.Playlist object: playlistId=PLYT4vq6pQVSvEBjN5rMNxabUwtYqV8dpJ>, <pytube.contrib.Playlist object: playlistId=PLYT4vq6pQVSuSIKK13fQ8533JPyqH66kG>, <pytube.contrib.Playlist object: playlistId=PLYT4vq6pQVSv3zECGufMrCDXKX0Ouxzde>, <pytube.contrib.Playlist object: playlistId=PLYT4vq6pQVSvCtY4FYQs7XPJkOFXpoZwc>, <pytube.contrib.Playlist object: playlistId=PLYT4vq6pQVSvmoSc7tP6T1ufdmjclT1Or>, <pytube.contrib.Playlist object: playlistId=PLYT4vq6pQVSuPJg1uit9v8J3zXfCDSDj1>, <pytube.contrib.Playlist object: playlistId=PLYT4vq6pQVSv_jFjvsMuxr6poP4yBU0VE>, <pytube.contrib.Playlist object: playlistId=PLYT4vq6pQVSu7CWxNGURanz2JPaAO28Gt>, <pytube.contrib.Playlist object: playlistId=PLYT4vq6pQVSuiFwl8Vv4XmCpdBDc8HeO6>, <pytube.contrib.Playlist object: playlistId=PLYT4vq6pQVStlmcOadjw_1C63oZXKzSDX>, <pytube.contrib.Playlist object: playlistId=PLYT4vq6pQVSuYs4h13CnOWAoag0t22_A2>, <pytube.contrib.Playlist object: playlistId=PLYT4vq6pQVSssLjYLUBrRU1kD2zDzgv42>, <pytube.contrib.Playlist object: playlistId=PLYT4vq6pQVSsleGDBf_DEY1NJHWMlp9ef>, <pytube.contrib.Playlist object: playlistId=PLYT4vq6pQVSun4KvXWYbGw2GY1wPXkiof>, <pytube.contrib.Playlist object: playlistId=PLYT4vq6pQVSvNUcl1eoNElalB5DlKcJgZ>, <pytube.contrib.Playlist object: playlistId=PLYT4vq6pQVSvfGdP3MdKZegD8Ub_0pqPS>]

With this array you can iterate with each playlist object.



**You can get the YouTube objects for each playlist using:**::

        ch = Channel('https://www.youtube.com/@Alanwalkermusic')

        print(ch.playlists[0].videos)

Output::

    [<pytube.__main__.YouTube object: videoId=v6oZuqN85D4>, <pytube.__main__.YouTube object: videoId=R-YSFJoQvwA>, <pytube.__main__.YouTube object: videoId=ouEl3qTLc0M>, <pytube.__main__.YouTube object: videoId=tu4HfcmMn1E>, <pytube.__main__.YouTube object: videoId=tw-pNm4oaoY>, <pytube.__main__.YouTube object: videoId=_BFgzaqyd8w>, <pytube.__main__.YouTube object: videoId=IQDJ3nu45Tw>, <pytube.__main__.YouTube object: videoId=RTR0oVn75Zs>, <pytube.__main__.YouTube object: videoId=JQORMjyFhBg>, <pytube.__main__.YouTube object: videoId=5AKDVJq45R4>, <pytube.__main__.YouTube object: videoId=_T9J-NK6ctI>, <pytube.__main__.YouTube object: videoId=d4vtEEL89JA>, <pytube.__main__.YouTube object: videoId=OBYwA36WHiw>, <pytube.__main__.YouTube object: videoId=Epa17C5Fy5c>, <pytube.__main__.YouTube object: videoId=07Z-DojGMAw>]


**Or you can also get the URL of the videos from each playlist:**::

    ch = Channel('https://www.youtube.com/@Alanwalkermusic')

    print(ch.playlists[0].video_urls)


Output::

    ['https://www.youtube.com/watch?v=v6oZuqN85D4', 'https://www.youtube.com/watch?v=R-YSFJoQvwA', 'https://www.youtube.com/watch?v=ouEl3qTLc0M', 'https://www.youtube.com/watch?v=tu4HfcmMn1E', 'https://www.youtube.com/watch?v=tw-pNm4oaoY', 'https://www.youtube.com/watch?v=_BFgzaqyd8w', 'https://www.youtube.com/watch?v=IQDJ3nu45Tw', 'https://www.youtube.com/watch?v=RTR0oVn75Zs', 'https://www.youtube.com/watch?v=JQORMjyFhBg', 'https://www.youtube.com/watch?v=5AKDVJq45R4', 'https://www.youtube.com/watch?v=_T9J-NK6ctI', 'https://www.youtube.com/watch?v=d4vtEEL89JA', 'https://www.youtube.com/watch?v=OBYwA36WHiw', 'https://www.youtube.com/watch?v=Epa17C5Fy5c', 'https://www.youtube.com/watch?v=07Z-DojGMAw']

