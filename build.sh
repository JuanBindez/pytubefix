#!/bin/bash

git add .
git commit -m 'update'
git push -u origin Release_Candidate
git tag v6.6-rc1
git push --tag
make clean
make upload