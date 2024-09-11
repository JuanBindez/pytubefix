#!/bin/bash

git add .
git commit -m 'merge -> interrupt_checker -> dev'
git push -u origin dev
git tag v6.16-rc1
git push --tag
make clean
make upload