#!/bin/bash

git add .
git commit -m '6.15rc1 Released'
git push -u origin rc
git tag v6.15-rc1
git push --tag
make clean
make upload