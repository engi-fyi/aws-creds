#!/bin/bash
rm -rf build/
rm -rf dist/
rm -rf aws_creds.egg-info/
python3 setup.py sdist bdist_wheel