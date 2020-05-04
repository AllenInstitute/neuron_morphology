#!/bin/bash

set -euo pipefail

python -m venv lambda-venv
source lambda-venv/bin/activate
pip install --no-deps --no-cache-dir . -r pipeline/build_stage/lambda_requirements.txt 
pip uninstall -y setuptools pip

find lambda-venv/lib/python3.*/site-packages/ -follow -type f -regextype posix-extended -regex '.*\.((a)|(pyc))' -delete

cd lambda-venv/lib/python3.*/site-packages/
zip -r9 ${OLDPWD}/lambda-package .
cd ${OLDPWD}

echo `du -hs lambda-venv/lib/python3.*/site-packages`
echo `du -hs lambda-package.zip`
