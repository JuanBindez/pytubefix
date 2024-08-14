#!/bin/bash

git add .
git commit -m 'Refactor code to ensure compatibility with Python 3.7

- Replaced the 'int | None' type annotation with 'Optional[int]' to support older Python versions.
- Imported 'Optional' from the 'typing' module.
'
git push -u origin dev
git tag v6.11-rc1
git push --tag
make clean
make upload