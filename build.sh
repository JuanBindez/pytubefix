#!/bin/bash

git add .
git commit -m 'pytubefix 5.7.0'
git push -u origin main
git tag v5.7.0
git push --tag
make clean
make upload