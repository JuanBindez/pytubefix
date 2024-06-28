#!/bin/bash

git add .
git commit -m 'pytubefix 5.6.3'
git push -u origin main
git tag v5.6.3
git push --tag
make clean
make upload
