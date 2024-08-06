#!/bin/bash

git add .
git commit -m '6.9 RC 1'
git push -u origin Release_Candidate
git tag v6.9-rc1
git push --tag
make clean
make upload