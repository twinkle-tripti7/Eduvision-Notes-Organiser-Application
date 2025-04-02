#!/bin/bash
apt update && apt install -y tesseract-ocr
gunicorn app:app
