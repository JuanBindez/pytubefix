#!/bin/bash

git add .
git commit -m ' Fixed issue with use_oauth #111 '
git push -u origin use_oauth_patch
git tag v6.3-rc1
git push --tag
make clean
make upload