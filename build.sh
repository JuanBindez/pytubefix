#!/bin/bash

git add .
git commit -m 'Pytubefix 6.10.2 (#169 #170 #173)'
git push -u origin main
git tag v6.10.2
git push --tag
make clean
make upload