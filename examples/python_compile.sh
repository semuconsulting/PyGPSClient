#!/bin/bash

# bash shell script to compile and install specified Python 3 version
# on Debian Linux platforms e.g. Ubuntu or Raspberry Pi OS.
#
# Remember to run chmod +x python_compile.sh to make this script executable.
#
# Source code:
# https://www.python.org/downloads/source/
# https://www.python.org/ftp/python/
#
# Build instructions:
# https://devguide.python.org/getting-started/setup-building/index.html#install-dependencies
# https://docs.python.org/3/using/unix.html#building-python
#
# Created by semuadmin on 20 Sep 2020.
# 
# exit on error
set -e

# set required Python major and minor version e.g. 3.10.10
PYVER="3.13.0"
# NB: uncomment this line to install this version alongside existing versions
# ALTINSTALL=1

# download and unzip source code
sudo apt install vim wget screen -y
wget https://www.python.org/ftp/python/${PYVER}/Python-${PYVER}.tgz
tar zvxf Python-${PYVER}.tgz

# enable the Debian source repos
SRCDEB="/etc/apt/sources.list"
SRCUBU="/etc/apt/sources.list.d/ubuntu.sources"
# Debian, including Raspberry Pi OS:
if test -f $SRCDEB
then
sudo sed -i -e 's/#deb-src/deb-src/g' $SRCDEB
fi
# Ubuntu, including 24.04 LTS:
if test -f $SRCUBU
then
sudo sed -i 's/^Types: deb$/Types: deb deb-src/' $SRCUBU 
fi

# install build dependencies
sudo apt update
sudo apt build-dep python3
sudo apt install build-essential gdb lcov pkg-config \
      libbz2-dev libffi-dev libgdbm-dev libgdbm-compat-dev liblzma-dev \
      libncurses5-dev libreadline6-dev libsqlite3-dev libssl-dev \
      lzma lzma-dev tk-dev uuid-dev zlib1g-dev -y

# compile, install and verify installed version
cd Python-${PYVER}
./configure --enable-optimizations
make
# make test
if [ -z ${ALTINSTALL+x} ]
then 
sudo make install
python3 -V
else
sudo make altinstall
python${PYVER%.*} -V
fi
