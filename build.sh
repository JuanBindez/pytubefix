#!/bin/bash

git add .
git commit -m 'fixed and added new functionality #171 #172'
git push -u origin Release_Candidate
git tag v6.10-rc3
git push --tag
make clean
make upload