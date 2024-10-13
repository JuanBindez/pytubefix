#!/bin/bash

git add .
git commit -m '8.0.0 (#277 #278 #280 #281 #282)'
git push -u origin main
git tag v8.0.0
git push --tag
make clean
make upload