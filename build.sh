#!/bin/bash

git add .
git commit -m 'update'
git push -u origin Alfa
git tag v6.5.3-a2
git push --tag
make clean
make upload