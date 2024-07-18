#!/bin/bash

git add .
git commit -m 'merge use_pathlib -> dev 6.3-rc4'
git push -u origin dev
git tag v6.3-rc4
git push --tag
make clean
make upload