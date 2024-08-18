#!/bin/bash

git add .
git commit -m 'test oauth_verifier 6.13 release candidate'
git push -u origin rc
git tag v6.13-rc1
git push --tag
make clean
make upload