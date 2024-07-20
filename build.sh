#!/bin/bash

git add .
git commit -m 'merge OAuth -> cli -> v6.4-rc2'
git push -u origin cli
git tag v6.4-rc2
git push --tag
make clean
make upload