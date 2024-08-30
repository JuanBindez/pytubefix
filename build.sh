#!/bin/bash

git add .
git commit -m 'update'
git push -u origin rc
git tag v6.14-rc1
git push --tag
make clean
make upload