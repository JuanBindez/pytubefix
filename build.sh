#!/bin/bash

git add .
git commit -m 'Pytubefix 6.15.4 (#216 #217)'
git push -u origin main
git tag v6.15.4
git push --tag
make clean
make upload