#!/bin/bash

git add .
git commit -m '6.12 rc1'
git push -u origin dev
git tag v6.12-rc1
git push --tag
make clean
make upload