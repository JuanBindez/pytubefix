#!/usr/bin/env python
"""This module contains setup instructions for pytube."""

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
