#!/bin/bash

# Ensure we're in the project directory
cd "$(dirname "$0")"

# Use Replit's Python to install packages
python3 -m pip install --user -r requirements.txt

# Run the Python script
python3 main.py