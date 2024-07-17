#!/bin/bash

git add .
git commit -m 'merge dev -> use_pathlib'
git push -u origin use_pathlib
git tag v6.3-rc3
git push --tag
make clean
make upload