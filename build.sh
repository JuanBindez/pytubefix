#!/bin/bash

git add .
git commit -m 'Pytubefix 6.13.1 (#202)'
git push -u origin main
git tag v6.13.1
git push --tag
make clean
make upload