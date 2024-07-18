#!/bin/bash

git add .
git commit -m 'pytubefix 6.3.3 -> #111 #112 #114'
git push -u origin main
git tag v6.3.3
git push --tag
make clean
make upload