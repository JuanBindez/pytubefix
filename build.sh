#!/bin/bash

git add .
git commit -m 'pytubefix 6.0.0 ->   Fixed "get_throttling_function_name: could not find match for multiple" and other improvements #94 '
git push -u origin main
git tag v6.0.0
git push --tag
make clean
make upload