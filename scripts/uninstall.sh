#!/bin/bash
pip uninstall aws-creds

if [ -f ".installed_files" ]; then
    xargs rm -rf < .installed_files
fi

pip uninstall aws-creds