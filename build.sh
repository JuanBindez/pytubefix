#!/bin/bash

git add .
git commit -m ' Fix empty chapter list bug #131 '
git push -u origin Release_Candidate
git tag v6.5.2-rc1
git push --tag
make clean
make upload