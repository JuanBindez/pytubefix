#!/bin/bash

git add .
git commit -m 'Pytubefix 7.0.0 (#244)'
git push -u origin main
git tag v7.0.0
git push --tag
make clean
make upload