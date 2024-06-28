#!/bin/bash

git add .
git commit -m 'Added ability to get video width and height -> by @CureSaba'
git push -u origin dev
git tag v5.7-rc1
git push --tag
make clean
make upload
