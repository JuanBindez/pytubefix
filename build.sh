#!/bin/bash

git add .
git commit -m 'pytubefix 6.4.2 -> #120 #121'
git push -u origin main
git tag v6.4.2
git push --tag
make clean
make upload