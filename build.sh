#!/bin/bash

git add .
git commit -m 'Pytubefix 7.2.2 (#255 #258 #259 #260)'
git push -u origin main
git tag v7.2.2
git push --tag
make clean
make upload