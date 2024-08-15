#!/bin/bash

git add .
git commit -m 'Pytubefix 6.11.0 (#178)'
git push -u origin main
git tag v6.11.0
git push --tag
make clean
make upload