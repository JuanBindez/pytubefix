#!/bin/bash

git add .
git commit -m 'Fix type annotation for compatibility with Python versions earlier than 3.10

Changed the type annotation of 'token_file' from str | None to Optional[str] in the __init__ method to ensure compatibility with Python versions prior to 3.10.
'
git push -u origin Alfa
git tag v6.5-a1
git push --tag
make clean
make upload