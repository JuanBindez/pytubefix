#!/bin/bash

git add .
git commit -m 'Pytubefix 6.12.0 (#187)'
git push -u origin main
git tag v6.12.0
git push --tag
make clean
make upload