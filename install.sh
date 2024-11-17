#!/usr/bin/env bash
echo "you need python3.10 or lower to run this"

python3 -m venv venv

source venv/bin/activate

pip install -r requirements.txt