#!/bin/bash

git add .
git commit -m 'Pytubefix 7.3.1  (#268)'
git push -u origin main
git tag v7.3.1
git push --tag
make clean
make upload