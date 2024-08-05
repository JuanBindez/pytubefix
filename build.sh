#!/bin/bash

git add .
git commit -m 'Pytubefix 6.8.1 (#146 #147)'
git push -u origin main
git tag v6.8.1
git push --tag
make clean
make upload