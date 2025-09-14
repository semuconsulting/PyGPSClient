#!/bin/bash

# bash shell script to compile and install libspatialite
# (mod_spatialite.so) on platforms which do not include a suitable
# binary in their standard repos (e.g. Raspberry Pi OS).
#
# Remember to run chmod +x libspatialite_compile.sh to make this script executable.
#
# Source code:
# https://www.gaia-gis.it/gaia-sins/libspatialite-sources/libspatialite-5.1.0.tar.gz
#
# Created by semuadmin on 27 Sep 2023.
# 
# exit on error
set -e

# install build dependencies (we'll omit the freexl dependency)
sudo apt install libspatial-dev
# download and unzip source code
wget https://www.gaia-gis.it/gaia-sins/libspatialite-sources/libspatialite-5.1.0.tar.gz
tar zxvf libspatialite-5.1.0.tar.gz
cd libspatialite-5.1.0
# compile source and install - this will take several minutes
./configure --build=aarch64-unknown-linux-gnu --enable-freexl=no
make
sudo make install-strip

# typically installs mod_spatialite.so to /usr/local/lib, which
# must be added to the LD_LIBRARY_PATH environment variable:
#
export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH

# make this permanent via your .bashrc or .zshrc shell profile
