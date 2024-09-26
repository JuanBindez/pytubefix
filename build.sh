#!/bin/bash

git add .
git commit -m '7.1-rc1 (#246 #249)'
git push -u origin dev
git tag v7.1-rc1
git push --tag
make clean
make upload