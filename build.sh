#!/bin/bash

git add .
git commit -m '8.1-rc1 (#284)'
git push -u origin dev
git tag v8.1rc1
git push --tag
make clean
make upload