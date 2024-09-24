#!/bin/bash

git add .
git commit -m 'Pytubefix 6.17.0 (#241)'
git push -u origin main
git tag v6.17.0
git push --tag
make clean
make upload