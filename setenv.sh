#!/bin/bash

#Install py dependency
python3 -m pip install -r requirements.txt -t .python_packages/


#Set PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)/.python_packages/"
