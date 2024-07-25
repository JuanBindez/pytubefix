#!/bin/bash

git add .
git commit -m 'Refactor video count extraction to handle dynamic JSON structures

- Replaced direct access to 'videosCountText' with recursive search in `find_videos_info` method.
- Updated `length` property to use the new `find_videos_info` method for extracting video count.
- Added error handling and default return value 'Unknown' in case of missing data or exceptions.
'
git push -u origin channel_length
git tag v6.5.3-a1
git push --tag
make clean
make upload