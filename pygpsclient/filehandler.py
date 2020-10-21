'''
Filehandler class for PyGPSClient application

This handles all the file i/o

Created on 16 Sep 2020

@author: semuadmin
'''

import os
from pathlib import Path
from time import strftime
from tkinter import filedialog

from .globals import MQAPIKEY, UBXPRESETS, MAXLOGLINES
from .strings import SAVETITLE, READTITLE

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
        self._filepath = None
        self._filename = None
        self._logfile = None
        self._lines = 0

    def load_apikey(self) -> str:
        '''
        Load MapQuest web map api key from user's home directory.
        '''

        filepath = os.path.join(HOME, MQAPIKEY)
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
        filepath = os.path.join(HOME, UBXPRESETS)
        try:
            with open(filepath, 'r') as file:
                for line in file:
                    presets.append(line)
        except OSError:
            presets = ''

        return presets

    def open_logfile_output(self) -> str:
        '''
        Set logfile directory and open logfile for output
        '''

        self._filepath = filedialog.askdirectory(title=SAVETITLE, initialdir=HOME,
                                       mustexist=True)
        if self._filepath == "":
            return None  # User cancelled
        self._filename = self._set_filename()
        self._logfile = open(self._filename, 'a+b')
        return self._filename

    def open_logfile_input(self) -> str:
        '''
        Set logfile name and open logfile for input
        '''

        self._filepath = filedialog.askopenfilename(title=READTITLE, initialdir=HOME,
                                          filetypes=(("log files", "*.log"),
                                                    ("all files", "*.*")))
        if self._filepath == "":
            return None  # User cancelled
        return self._filepath

    def write_logfile(self, data: bytes):
        '''
        Append binary data to log file
        '''

        self._logfile.write(data)
        self._lines += 1

        if self._lines > MAXLOGLINES:
            self.close_logfile()
            self._filename = self._set_filename()
            self._logfile = open(self._filename, 'a+b')

    def close_logfile(self):
        '''
        Close the logfile
        '''

        if self._logfile is not None:
            self._logfile.close()

    def _set_filename(self) -> str:
        '''
        Set log file name with timestamp
        '''

        self._lines = 0
        timestr = strftime("%Y%m%d%H%M%S")
        filename = os.path.join(self._filepath, 'pygpsdata-' + timestr + '.log')
        return filename
