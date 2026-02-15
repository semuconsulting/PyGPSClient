#!/bin/bash

# Bash shell script to install PyGPSClient on 64-bit Arch-based
# Linux environments.
#
# Change shebang /bin/bash to /bin/zsh if running from zsh shell.
# NB: NOT for use on Windows or MacOS!
#
# Remember to run chmod +x pygpsclient_arch_install.sh to make this script executable.
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

echo "PyGPSClient will be installed at $HOME/pygpsclient/bin"

echo "Installing dependencies..."
sudo pacman -S tk libspatialite
     
echo "Setting user permissions for /dev/tty* devices..."
sudo usermod -aG uucp $USER

echo "Creating virtual environment..."
cd $HOME
python3 -m venv pygpsclient
source pygpsclient/bin/activate
python3 -m pip install --upgrade pip pygpsclient rasterio
deactivate

echo "Adding desktop launch icon..."
# the LD_LIBRARY_PATH env setting allows PyGPSClient to find the 
# mod_spatialite.so module, which is typically installed in this location
# you can set other env variables in a similar fashion if required
mkdir -p $HOME/.local/share/applications
cat > $HOME/.local/share/applications/pygpsclient.desktop <<EOF
[Desktop Entry]
Type=Application
Terminal=false
Name=PyGPSClient
Icon=$HOME/pygpsclient/lib/python$PYVER/site-packages/pygpsclient/resources/pygpsclient.ico
Exec=env LD_LIBRARY_PATH=/usr/local/lib $HOME/pygpsclient/bin/pygpsclient
EOF

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
sed -i '$a# Path to PyGPSClient executable\nexport PATH="${HOME}/pygpsclient/bin:${PATH}"' $PROF
source $PROF # this will throw an error if running as bash script in zsh shell

echo "Installation complete"
echo "You may need to restart before accessing /dev/tty*"
