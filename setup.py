#!/usr/bin/env python
"""This module contains setup instructions for pytubefix."""

"""
MIT License

Copyright (c) 2023 Juan Bindez <juanbindez780@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import codecs
import os

from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

with open(os.path.join(here, "pytubefix", "version.py")) as fp:
    exec(fp.read())

setup(name = "pytubefix",
      version = __version__,  # noqa: F821
      author = "Juan Bindez",
      author_email = "juanbindez780@gmail.com",
      packages = ["pytubefix", "pytubefix.contrib"],
      package_data = {"": ["LICENSE"],},
      url = "https://github.com/juanbindez/pytubefix",
      license = "MIT license",
      entry_points = {
        "console_scripts": [
          "pytubefix = pytubefix.cli:main"],},
      classifiers = [
            "Development Status :: 5 - Production/Stable",
            "Environment :: Console",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: MIT License",
            "Natural Language :: English",
            "Operating System :: OS Independent",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
            "Programming Language :: Python :: 3.11",
            "Programming Language :: Python",
            "Topic :: Internet",
            "Topic :: Multimedia :: Video",
            "Topic :: Software Development :: Libraries :: Python Modules",
            "Topic :: Terminals",
            "Topic :: Utilities",
        ],
      description = ("Python 3 library for downloading YouTube Videos."),
      include_package_data = True,
      long_description_content_type = "text/markdown",
      long_description = long_description,
      zip_safe = True,
      python_requires = ">=3.7",
      project_urls = {
        "Bug Reports": "https://github.com/juanbindez/pytubefix/issues",
        "Read the Docs": "https://github.com/JuanBindez/pytubefix/tree/main/docs/user",
      },
      keywords = ["youtube", "download", "video", "stream",],)
