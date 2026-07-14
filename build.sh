#!/bin/bash

set -e

VERSION=10
MINOR=10
PATCH=1
EXTRAVERSION=""
COMMIT="(#656)

Tested-by: Justin 'Muggwomp' Corey <justincorey@mindgarden.cc>
Fixes:#653
"
BRANCH="main"

if [[ -n "${PATCH-}" ]]; then
    PATCH=".$PATCH"
fi

FULL_VERSION="$VERSION.$MINOR$PATCH"

if [[ $EXTRAVERSION == *"-rc"* ]]; then
    FULL_VERSION+="$EXTRAVERSION"
elif [[ -n $EXTRAVERSION ]]; then
    FULL_VERSION+=".$EXTRAVERSION"
fi

git add .
git commit -s -m "$FULL_VERSION $COMMIT"
git push -u origin $BRANCH
git tag v$FULL_VERSION
git push --tags

rm -fr build/
rm -fr dist/
rm -fr .eggs/
find . -name '*.egg-info' -exec rm -fr {} +
find . -name '*.egg' -exec rm -f {} +
find . -name '*.DS_Store' -exec rm -f {} +

find . -name '*.pyc' -exec rm -f {} +
find . -name '*.pyo' -exec rm -f {} +
find . -name '*~' -exec rm -f {} +
find . -name '__pycache__' -exec rm -fr {} +

pip install twine build
python -m build
twine upload dist/*

echo "Build $FULL_VERSION completed successfully!"