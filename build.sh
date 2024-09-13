#!/bin/bash

git add .
git commit -m 'rc2'
git push -u origin dev
git tag v6.16-rc2
git push --tag
make clean
make upload