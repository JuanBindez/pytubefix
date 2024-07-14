#!/bin/bash

git add .
git commit -m 'update'
git push -u origin dev
git tag v6.2-rc3
git push --tag
make clean
make upload