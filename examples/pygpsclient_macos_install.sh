#!/bin/zsh

# ZSH shell script to install PyGPSClient on MacOS
# environments (MacOS 13 or later running zsh shell).
#
# NB: Does NOT create an application launcher - use
# the MacOS Automator tool to create a bin/zsh shell app
# called PyGPSClient.app with the shell command:
# $HOME/pygpsclient/bin/pygpsclient
#
# Full installation instructions:
# https://github.com/semuconsulting/PyGPSClient
#
# Created by semuadmin on 20 Sep 2023.
# 
# exit on error
set -e

echo "PyGPSClient will be installed at $HOME/pygpsclient/bin"
VER=3.13.7
echo "Installing Python $VER from python.org ..."
curl https://www.python.org/ftp/python/$VER/python-$VER-macos11.pkg --output python-$VER-macos11.pkg
sudo installer -pkg python-$VER-macos11.pkg -target /

PYVER="$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')"
echo "Installed Python version is $PYVER"

echo "Creating virtual environment..."
cd $HOME
python3 -m venv pygpsclient
source pygpsclient/bin/activate
python3 -m pip install --upgrade pip pygpsclient
deactivate

echo "Adding directory to PATH..."
ZSHPROF1=$HOME/.zprofile
ZSHPROF2=$HOME/.zshrc
if test -f $ZSHPROF1
then
PROF=$ZSHPROF1
elif test -f $ZSHPROF2
then
PROF=$ZSHPROF2
fi
echo '# Path to PyGPSClient executable\nexport PATH="$HOME/pygpsclient/bin:$PATH"' >> $PROF
source $PROF

echo "Installation complete"
