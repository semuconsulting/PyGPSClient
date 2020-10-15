'''
Filehandler class for PyGPSClient application

This handles all the file i/o

Created on 16 Sep 2020

@author: semuadmin
'''

import os
from pathlib import Path

HOME = str(Path.home())


class FileHandler():
    '''
    File handler class.
    '''

    def __init__(self, app, *args, **kwargs):
        '''
        Constructor.
        '''

        self.__app = app  # Reference to main application class
        self.__master = self.__app.get_master()  # Reference to root class (Tk)

    def load_apikey(self) -> str:
        '''
        Load MapQuest web map api key from user's home directory.
        '''

        filepath = os.path.join(HOME, 'mqapikey')
        try:
            with open(filepath, 'r') as file:
                apikey = file.read()
        except OSError:
            # Error message will be displayed on mapview widget if invoked
            apikey = ''

        return apikey

    def load_user_presets(self) -> str:
        '''
        Load user configuration message presets from user's home directory.
        '''

        presets = []
        filepath = os.path.join(HOME, 'ubxpresets')
        try:
            with open(filepath, 'r') as file:
                for line in file:
                    presets.append(line)
        except OSError:
            presets = ''

        return presets
