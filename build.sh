#!/bin/bash

git add .
git commit -m 'Update download method docstring to include problematic_characters parameter

- Added documentation for the `problematic_characters` parameter in the `download` method docstring.
- Clarified that `problematic_characters` specifies characters to be removed from the filename to prevent issues with file naming.
- Adjusted the Note section to reflect the new behavior when `problematic_characters` is provided.'

git push -u origin problematic_characters
git tag v6.10-a3
git push --tag
make clean
make upload