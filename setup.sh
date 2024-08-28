#!/bin/bash

# Create a virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate the virtual environment
source venv/bin/activate

# Upgrade pip in the virtual environment
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# Deactivate the virtual environment
deactivate