#!/bin/bash

VERSION=8
MINOR=3
PATCH=0
EXTRAVERSION=""

NOTES="(#308 #309 #310)"
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
git commit -m "$FULL_VERSION $NOTES"
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