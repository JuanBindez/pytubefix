#!/bin/bash

git add .
git commit -m 'Pytubefix 6.6.2 -> (#134 #135 #136)'
git push -u origin main
git tag v6.6.2
git push --tag
make clean
make upload