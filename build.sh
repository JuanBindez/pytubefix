#!/bin/bash

git add .
git commit -m 'merge Alfa -> Release_Candidate v6.5-rc1'
git push -u origin Release_Candidate
git tag v6.5-rc1
git push --tag
make clean
make upload