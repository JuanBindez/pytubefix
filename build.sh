#!/bin/bash

git add .
git commit -m '7.2-rc1 (#255 #258 #259)'
git push -u origin dev
git tag v7.2-rc1
git push --tag
make clean
make upload