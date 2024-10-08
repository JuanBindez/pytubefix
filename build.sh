#!/bin/bash

git add .
git commit -m '7.4-rc1 (#269)'
git push -u origin dev
git tag v7.4-rc1
git push --tag
make clean
make upload