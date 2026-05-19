#!/bin/bash

set -e

VERSION=10
MINOR=7
PATCH=2
EXTRAVERSION=""
COMMIT="(#630 #631)

Fixes: #627
"
BRANCH="main"

if [[ -z $PATCH ]]; then
    PATCH=""
else
    PATCH=".$PATCH"
fi

if [[ $EXTRAVERSION == *"-rc"* ]]; then
    FULL_VERSION="$VERSION.$MINOR$PATCH$EXTRAVERSION"
else

    if [[ -z $EXTRAVERSION ]]; then
        FULL_VERSION="$VERSION.$MINOR$PATCH"
    else
        FULL_VERSION="$VERSION.$MINOR$PATCH.$EXTRAVERSION"
    fi
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