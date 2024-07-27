#!/bin/bash

git add .
git commit -m 'merge chapters_data_patch1 -> Release_Candidate (#137)'
git push -u origin Release_Candidate
git tag v6.6.3-rc1
git push --tag
make clean
make upload