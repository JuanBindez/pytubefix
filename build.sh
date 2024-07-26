#!/bin/bash

git add .
git commit -m ' Pytubefix 6.5.3 -> (#134) '
git push -u origin main
git tag v6.5.3
git push --tag
make clean
make upload