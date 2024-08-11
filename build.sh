#!/bin/bash

git add .
git commit -m 'merge dev -> Release_Candidate'
git push -u origin Release_Candidate
git tag v6.10-rc1
git push --tag
make clean
make upload