#!/bin/bash

git add .
git commit -m 'Improved check_availability #106'
git push -u origin dev
git tag v6.2-rc2
git push --tag
make clean
make upload