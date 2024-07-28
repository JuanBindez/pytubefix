#!/bin/bash

git add .
git commit -m 'Pytubefix 6.7.0 (#140)'
git push -u origin main
git tag v6.7.0
git push --tag
make clean
make upload