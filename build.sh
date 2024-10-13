#!/bin/bash

git add .
git commit -m '8.0-rc5 (#277 #278 #280 #281 #282)'
git push -u origin dev
git tag v8.0-rc5
git push --tag
make clean
make upload