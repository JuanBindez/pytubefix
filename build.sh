#!/bin/bash

git add .
git commit -m 'pytubefix 6.2.2 -> b2ac8550da2b73421bde43838b96d7cace979c29 caec2a4f28206de68af082ba3e1e22da3e849879'
git push -u origin main
git tag v6.2.2
git push --tag
make clean
make upload