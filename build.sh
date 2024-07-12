#!/bin/bash

git add .
git commit -m 'pytubefix 6.1.2'
git push -u origin main
git tag v6.1.2
git push --tag
make clean
make upload