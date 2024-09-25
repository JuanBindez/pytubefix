#!/bin/bash

git add .
git commit -m 'v7 rc1 (#244)'
git push -u origin dev
git tag v7.0-rc1
git push --tag
make clean
make upload