#!/bin/bash

git add .
git commit -m '5.8.0'
git push -u origin dev
git tag v5.8.0
git push --tag
make clean
make upload
