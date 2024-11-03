.. _install:

Installation of pytubefix
======================

This guide assumes you already have python and pip installed.

To install pytubefix, run the following command in your terminal::

    $ pip install pytubefix

Get the Source Code
-------------------

pytubefix is actively developed on GitHub, where the source is `available <https://github.com/JuanBindez/pytubefix>`_.

You can either clone the public repository::

    $ git clone git://github.com/JuanBindez/pytubefix.git

Or, download the `tarball <https://github.com/JuanBindez/pytubefix/tarball/master>`_::

    $ curl -OL https://github.com/JuanBindez/pytubefix/tarball/master
    # optionally, zipball is also available (for Windows users).

Once you have a copy of the source, you can embed it in your Python package, or install it into your site-packages by running::

    $ cd pytubefix
    $ python -m pip install .
