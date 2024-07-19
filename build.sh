#!/bin/bash

git add .
git commit -m 'patch exceptions'
git push -u origin exceptions
git tag v6.3.4-rc1
git push --tag
make clean
make upload