#!/bin/bash

git add .
git commit -m 'update'
git push -u origin dev
git tag v5.7-rc2
git push --tag
make clean
make upload
