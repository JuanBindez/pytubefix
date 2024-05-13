.. _keymoments:

Extracting key moments
=========================

**Test**::

        from pytubefix import YouTube

        yt = YouTube("https://www.youtube.com/watch?v=-xNR_1WJQ-E")
        print(yt.key_moments)

Output::

        [
        <KeyMoment: Time Query | 0:00:12>, 
        <KeyMoment: Constructing Space | 0:00:15>, 
        <KeyMoment: Loosing / recovering the ball | 0:00:20>
        ]



**Support for both key moments**::

        from pytubefix import YouTube

        yt = YouTube("https://www.youtube.com/watch?v=rSKMYc1CQHE")
        print(yt.replayed_heatmap)

Output::

    [
    {'start_seconds': 0.0,
    'duration': 28.72,
    'norm_intensity': 0.7744516981592584},
    {'start_seconds': 28.72,
    'duration': 28.72,
    'norm_intensity': 0.5055251629407894},
    {'start_seconds': 57.44,
    'duration': 28.72,
    'norm_intensity': 0.3365084886794003},
    ......
    ]