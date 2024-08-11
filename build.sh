#!/bin/bash

git add .
git commit -m 'seach docs update'
git push -u origin search_docs_update
git tag v6.10-a2
git push --tag
make clean
make upload