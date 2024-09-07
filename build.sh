#!/bin/bash

git add .
git commit -m 'Pytubefix 6.15.2 (#215)'
git push -u origin main
git tag v6.15.2
git push --tag
make clean
make upload