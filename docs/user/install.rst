.. _install:

Installation of pytubenow
======================

This guide assumes you already have python and pip installed.

To install pytubenow, run the following command in your terminal::

    $ pip install pytubenow

Get the Source Code
-------------------

pytubenow is actively developed on GitHub, where the source is `available <https://github.com/pytubenow/pytubenow>`_.

You can either clone the public repository::

    $ git clone git://github.com/pytubenow/pytubenow.git

Or, download the `tarball <https://github.com/pytubenow/pytubenow/tarball/master>`_::

    $ curl -OL https://github.com/pytubenow/pytubenow/tarball/master
    # optionally, zipball is also available (for Windows users).

Once you have a copy of the source, you can embed it in your Python package, or install it into your site-packages by running::

    $ cd pytubenow
    $ python -m pip install .
