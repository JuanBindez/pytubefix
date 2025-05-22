.. _proxy:

Proxy
=====

**YouTube may block or limit access from a specific IP address, especially if it detects a large number of requests in a short period of time. Using a proxy helps mask the original IP address, avoiding blocking.**


.. code:: python

    from pytubefix import YouTube

    proxy = {
        "http": "socks5://proxy_address",
        "https": "socks5://proxy_address"
        }

    url = "url"
    
    yt = YouTube(url, proxies=proxy)
    print(yt.title)
    
    ys = yt.streams.get_highest_resolution()
    ys.download()
