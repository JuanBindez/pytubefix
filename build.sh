#!/bin/bash

git add .
git commit -m '8.0-rc2 (#277 #278 #279 #280)'
git push -u origin dev
git tag v8.0-rc2
git push --tag
make clean
make upload