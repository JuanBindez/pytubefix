#!/bin/bash

git add .
git commit -m 'pypi -> (#169 #170)'
git push -u origin dev
git tag v6.10-a1
git push --tag
make clean
make upload