.. _info:

Info
====

This can be useful for debugging or logging purposes, as it allows developers to quickly 
check the environment in which the code is being executed. It helps ensure that the correct 
versions of Python and Pytubefix are being used, and can also assist in identifying any 
compatibility issues between the system and the application.::
    >>> from pytubefix import info
    >>> 
    >>> print(info())
    {'OS': {'linux'}, 'Python': {'3.11.6 (main, Apr 10 2024, 17:26:07) [GCC 13.2.0]'}, 'Pytubefix': {'7.3.1'}}
    >>> 

to get just the operating system::
    >>> from pytubefix import info
    >>> 
    >>> system_info = info()
    >>> 
    >>> print(f"Operational System: {system_info['OS']}")
    Operational System: linux
    >>> 
    >>>

to use only the pytubefix version::
    >>> from pytubefix import info
    >>> 
    >>> system_info = info()
    >>> 
    >>> print(f"Pytubefix Version: {system_info['Pytubefix']}")
    Pytubefix Version: 7.3.1
    >>> 

