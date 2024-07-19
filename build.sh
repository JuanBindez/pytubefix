#!/bin/bash

git add .
git commit -m '6.3.4'
git push -u origin main
git tag v6.3.4
git push --tag
make clean
make upload