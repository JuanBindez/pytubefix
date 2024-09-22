#!/bin/bash

git add .
git commit -m 'rc-1 6.17'
git push -u origin dev
git tag v6.17-rc1
git push --tag
make clean
make upload