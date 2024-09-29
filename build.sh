#!/bin/bash

git add .
git commit -m '7.1-rc3 (#246 #249 #253 #254)'
git push -u origin dev
git tag v7.1-rc3
git push --tag
make clean
make upload