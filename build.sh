#!/bin/bash

git add .
git commit -m 'merge dev -> Error_handling 6.3-rc5'
git push -u origin Error_handling
git tag v6.3-rc5
git push --tag
make clean
make upload