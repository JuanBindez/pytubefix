#!/bin/bash

git add .
git commit -m 'Pytubefix 6.9.2 (#159)'
git push -u origin main
git tag v6.9.2
git push --tag
make clean
make upload