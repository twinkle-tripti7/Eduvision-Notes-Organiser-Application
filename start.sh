#!/bin/bash
echo "Installing Tesseract..."
# Install Tesseract using Nix
nix-env -iA nixpkgs.tesseract

# Get the installed Tesseract path
export TESSERACT_PATH=$(which tesseract)
echo "Tesseract installed at: $TESSERACT_PATH"

pip install -r requirements.txt

# Download and install GLIBC 2.38
mkdir /glibc
cd /glibc
wget http://ftp.gnu.org/gnu/libc/glibc-2.38.tar.gz
tar -xvzf glibc-2.38.tar.gz
cd glibc-2.38
mkdir build
cd build
../configure --prefix=/opt/glibc-2.38
make -j$(nproc)
make install

# Use the new GLIBC version
export LD_LIBRARY_PATH=/opt/glibc-2.38/lib:$LD_LIBRARY_PATH
gunicorn -w 4 -b 0.0.0.0:8080 auth:app
