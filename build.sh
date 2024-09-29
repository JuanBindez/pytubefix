#!/bin/bash

git add .
git commit -m 'Pytubefix 7.1.3 (#246 #249 #253 #254)'
git push -u origin main
git tag v7.1.3
git push --tag
make clean
make upload