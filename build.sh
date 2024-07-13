#!/bin/bash

git add .
git commit -m 'Refactor: Remove problematic characters from video title

- Implemented a translation table using str.maketrans to replace problematic characters in the video title with an empty string.
- Characters removed include: /, :, *, ", <, >, and |.
- This change ensures that video titles are sanitized and free of characters that could cause issues in terminal commands or file system operations.
- Updated the title property to apply the translation table, ensuring consistent and safe formatting of video titles.

This update helps prevent errors related to invalid file names and potential security risks from unescaped characters.
'
git push -u origin dev
git tag v6.2-rc1
git push --tag
make clean
make upload