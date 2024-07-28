#!/bin/bash

git add .
git commit -m 'merge -> playlist_oauth_feature -> Alfa'
git push -u origin Alfa
git tag v6.7-a1
git push --tag
make clean
make upload