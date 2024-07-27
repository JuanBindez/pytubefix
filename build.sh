#!/bin/bash

git add .
git commit -m 'Pytubefix 6.6.3 -> (#137)'
git push -u origin main
git tag v6.6.3
git push --tag
make clean
make upload