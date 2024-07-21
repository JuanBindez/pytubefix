#!/bin/bash

git add .
git commit -m 'pytubefix 6.5.1 ->  #122 18a4dee8e958d41e05fb7c618d194acc5e75c1cf'
git push -u origin main
git tag v6.5.1
git push --tag
make clean
make upload