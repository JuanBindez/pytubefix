#!/bin/bash

git add .
git commit -m 'tests v6.4-rc1'
git push -u origin OAuth
git tag v6.4-rc1
git push --tag
make clean
make upload