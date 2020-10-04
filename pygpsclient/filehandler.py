'''
Filehandler class for PyGPSClient application

This handles all the file i/o

Created on 16 Sep 2020

@author: semuadmin
'''

import os


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
        Load MapQuest web map api key from PyGPSCLient application directory.
        '''

        dirname = os.path.dirname(__file__)
        filepath = os.path.join(dirname, "..", 'apikey')
        try:
            with open(filepath, 'r') as file:
                apikey = file.read()
            # print("apikey _reading: ", apikey)
        except OSError:
            # Error message will be displayed on mapview widget if invoked
            # print("Error reading apikey {}".format(err))
            apikey = ''

        return apikey
