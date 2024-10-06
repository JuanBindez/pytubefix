#!/bin/bash

git add .
git commit -m 'Pytubefix 7.3.0 (#266)'
git push -u origin main
git tag v7.3.0
git push --tag
make clean
make upload