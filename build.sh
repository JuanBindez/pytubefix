#!/bin/bash

git add .
git commit -m '7.3-rc1 (#266)'
git push -u origin dev
git tag v7.3-rc1
git push --tag
make clean
make upload