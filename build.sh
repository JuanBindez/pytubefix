#!/bin/bash

git add .
git commit -m 'cli -> dev -> v6.4-rc3'
git push -u origin dev
git tag v6.4-rc3
git push --tag
make clean
make upload