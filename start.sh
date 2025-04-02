#!/bin/bash
apt update && apt install -y tesseract-ocr libc-bin
export LD_LIBRARY_PATH=/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH
gunicorn -w 4 -b 0.0.0.0:8080 auth:app
