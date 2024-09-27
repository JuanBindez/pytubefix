#!/bin/bash

git add .
git commit -m '7.1-rc2 (#246 #249 #253)'
git push -u origin dev
git tag v7.1-rc2
git push --tag
make clean
make upload