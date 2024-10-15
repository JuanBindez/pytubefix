#!/bin/bash

git add .
git commit -m 'Pytubefix 8.1.1 (#284)'
git push -u origin main
git tag v8.1.1
git push --tag
make clean
make upload