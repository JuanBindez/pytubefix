#!/bin/bash

git add .
git commit -m 'Pytubefix 6.9.1 (#151 #152)'
git push -u origin main
git tag v6.9.1
git push --tag
make clean
make upload