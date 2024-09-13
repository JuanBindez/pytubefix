#!/bin/bash

git add .
git commit -m 'Pytubefix 6.16.1 (#218 #223)'
git push -u origin main
git tag v6.16.1
git push --tag
make clean
make upload