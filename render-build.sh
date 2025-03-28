#!/usr/bin/env bash

# Install Tesseract
apt-get update && apt-get install -y tesseract-ocr

# Install project dependencies
pip install -r requirements.txt
