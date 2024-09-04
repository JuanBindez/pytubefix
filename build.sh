#!/bin/bash

git add .
git commit -m 'Pytubefix 6.15.1 (Fixed -> SyntaxError: f-string: unmatched '[' #213)'
git push -u origin main
git tag v6.15.1
git push --tag
make clean
make upload