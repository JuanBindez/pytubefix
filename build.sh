#!/bin/bash

git add .
git commit -m 'Pytubefix 7.4.0 (#269)'
git push -u origin main
git tag v7.4.0
git push --tag
make clean
make upload