#!/bin/bash

git add .
git commit -m 'Pytubefix 6.14.0 (#204 #207)'
git push -u origin main
git tag v6.14.0
git push --tag
make clean
make upload