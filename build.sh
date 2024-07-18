#!/bin/bash

git add .
git commit -m 'merge Error_handlin -> dev 6.3-rc6'
git push -u origin dev
git tag v6.3-rc6
git push --tag
make clean
make upload