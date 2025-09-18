#!/bin/bash

# bash shell script to compile and install libspatialite
# (mod_spatialite.so) on Debian Linux platforms which do not
# include a suitable binary in their standard repos
# (e.g. Raspberry Pi OS).
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

# install build dependencies if required and available (we'll omit the freexl dependency)
sudo apt install libspatial-dev || true
sudo apt install libproj-dev || true
sudo apt install libgdal-dev || true
sudo apt install libgeos-dev || true
# download and unzip source code
wget https://www.gaia-gis.it/gaia-sins/libspatialite-sources/libspatialite-5.1.0.tar.gz
tar zxvf libspatialite-5.1.0.tar.gz
cd libspatialite-5.1.0
# compile source and install - this will take several minutes
# aarch64-unknown-linux-gnu is appropriate for ARM-based SBC platforms like RPi
./configure --build=aarch64-unknown-linux-gnu --enable-freexl=no
make
sudo make install-strip

# typically installs mod_spatialite.so to /usr/local/lib, which
# must be added to the LD_LIBRARY_PATH environment variable:
#
export LD_LIBRARY_PATH=/usr/local/lib

# make this permanent via your .bashrc or .zshrc shell profile
echo "Adding directory to PATH..."
BASHPROF1=$HOME/.profile
BASHPROF2=$HOME/.bashrc
ZSHPROF1=$HOME/.zprofile
ZSHPROF2=$HOME/.zshrc
if test -f $BASHPROF1
then
PROF=$BASHPROF1
elif test -f $BASHPROF2
then
PROF=$BASHPROF2
fi
if test -f $ZSHPROF1
then
PROF=$ZSHPROF1
elif test -f $ZSHPROF2
then
PROF=$ZSHPROF2
fi
sed -i '$a# Path to mod_spatialite.so\nexport LD_LIBRARY_PATH=/usr/local/lib' $PROF
source $PROF # this will throw an error if running as bash script in zsh shell
