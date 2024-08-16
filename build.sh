#!/bin/bash

git add .
git commit -m '6.12 rc2'
git push -u origin rc
git tag v6.12-rc2
git push --tag
make clean
make upload