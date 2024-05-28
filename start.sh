#!/bin/bash

SCRIPT_PATH=$(readlink -f "$0")
PROJECT_ROOT=$(dirname "$SCRIPT_PATH")
export PYTHONPATH=$PROJECT_ROOT:$PYTHONPATH

poetry run python app/main.py
