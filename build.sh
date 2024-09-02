#!/bin/bash

git add .
git commit -m '6.15a1 Released'
git push -u origin PoToken
git tag v6.15-a1
git push --tag
make clean
make upload