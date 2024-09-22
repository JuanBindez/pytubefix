#!/bin/bash

git add .
git commit -m 'Pytubefix 6.16.3 (#237)'
git push -u origin main
git tag v6.16.3
git push --tag
make clean
make upload