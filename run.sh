#!/bin/bash

# Install dependencies
pip install flask transformers torch requests beautifulsoup4 gunicorn

# Start the Flask app using gunicorn
exec gunicorn --bind 0.0.0.0:8080 main:app