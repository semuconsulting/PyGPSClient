#!/bin/bash

# bash shell script to install PyGPSClient on Raspberry Pi and
# other similar Debian Linux environments
#
# Should work for most vanilla Debian environments with Python>=3.9
# but is probably not 100% foolproof - use at own risk
#
# NB: NOT for use on Windows or MacOS!
#
# Remember to run chmod +x pygpsclient_debian_install.sh to make this script executable.
#
# Full installation instructions:
# https://github.com/semuconsulting/PyGPSClient
#
# Created by semuadmin on 20 Sep 2023.
# 
# exit on error
set -e

PYVER="$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')"

echo "Installed Python version is $PYVER"

read -p "Enter user name: " user
echo "PyGPSClient will be installed at /home/$USER/pygpsclient/bin"

echo "Installing dependencies..."
sudo apt install python3-pip python3-tk python3-pil python3-pil.imagetk \
     libjpeg-dev zlib1g-dev tk-dev python3-rasterio
     
echo "Setting user permissions..."
sudo usermod -a -G tty $USER

echo "Creating virtual environment..."
cd /home/$USER
python3 -m venv pygpsclient
source pygpsclient/bin/activate
python3 -m pip install --upgrade pygpsclient
deactivate

echo "Adding desktop launch icon..."
cat > /home/$USER/.local/share/applications/pygpsclient.desktop <<EOF
[Desktop Entry]
Type=Application
Terminal=false
Name=PyGPSClient
Icon=/home/$USER/pygpsclient/lib/python$PYVER/site-packages/pygpsclient/resources/pygpsclient.ico
Exec=/home/$USER/pygpsclient/bin/pygpsclient
EOF

echo "Adding directory to PATH..."
BASHPROF=/home/$USER/.bashrc
ZSHPROF=/home/$USER/.profile
if test -f $BASHPROF
then
sed -i '$aexport PATH="/home/$USER/pygpsclient/bin:$PATH"' $BASHPROF
source $BASHPROF
fi
if test -f $ZSHPROF
then
sed -i '$aexport PATH="/home/$USER/pygpsclient/bin:$PATH"' $ZSHPROF
source $ZSHPROF
fi

echo "Installation complete"
