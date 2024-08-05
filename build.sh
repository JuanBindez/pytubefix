#!/bin/bash

git add .
git commit -m '6.9 Alfa 1'
git push -u origin dev
git tag v6.9-a1
git push --tag
make clean
make upload