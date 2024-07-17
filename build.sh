#!/bin/bash

git add .
git commit -m 'merge branch use_oauth_path -> dev'
git push -u origin dev
git tag v6.3-rc2
git push --tag
make clean
make upload