#!/bin/bash

git add .
git commit -m 'Pytubefix 6.15.0 (#209)'
git push -u origin main
git tag v6.15.0
git push --tag
make clean
make upload