#!/bin/bash

python setup.py sdist bdist_wheel
twine check dist/*

if [[ $1 == "publish" ]]
then
    echo "Publishing to pip"
    twine upload
else
    echo "Publishing to pip test"
    twine upload --repository-url https://test.pypi.org/legacy/ dist/*
fi
