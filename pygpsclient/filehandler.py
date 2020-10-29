'''
Filehandler class for PyGPSClient application

This handles all the file i/o

Created on 16 Sep 2020

@author: semuadmin
'''

import os
from datetime import datetime
from pathlib import Path
from time import strftime
from tkinter import filedialog

from .globals import MQAPIKEY, UBXPRESETS, MAXLOGLINES, XML_HDR, GPX_NS, GITHUB_URL
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
        self._datalog_filepath = None
        self._datalog_filename = None
        self._logfile = None
        self._track_filepath = None
        self._track_filename = None
        self._trkfile = None
        self._lines = 0

    def __del__(self):
        '''
        Destructor - close any open files
        '''

        self.close_logfile()
        self.close_trackfile()

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

    def _set_filename(self, path, mode, ext) -> str:
        '''
        Return fully qualified and timestamped file name
        '''

        self._lines = 0
        timestr = strftime("%Y%m%d%H%M%S")
        filename = os.path.join(path, f'pygps{mode}-' + timestr + f'.{ext}')
        return filename

    def open_logfile_output(self) -> str:
        '''
        Set logfile directory and open logfile for output
        '''

        self._datalog_filepath = filedialog.askdirectory(title=SAVETITLE, initialdir=HOME,
                                       mustexist=True)
        if self._datalog_filepath == "":
            return None  # User cancelled
        self._datalog_filename = self._set_filename(self._datalog_filepath, 'data', 'log')
        self._logfile = open(self._datalog_filename, 'a+b')
        return self._datalog_filename

    def open_logfile_input(self) -> str:
        '''
        Set logfile name and open logfile for input
        '''

        self._datalog_filepath = filedialog.askopenfilename(title=READTITLE, initialdir=HOME,
                                          filetypes=(("log files", "*.log"),
                                                    ("all files", "*.*")))
        if self._datalog_filepath == "":
            return None  # User cancelled
        return self._datalog_filepath

    def write_logfile(self, data: bytes):
        '''
        Append binary data to log file
        '''

        self._logfile.write(data)
        self._lines += 1

        if self._lines > MAXLOGLINES:
            self.close_logfile()
            self._datalog_filename = self._set_filename(self._datalog_filepath, 'data', 'log')
            self._logfile = open(self._datalog_filename, 'a+b')

    def close_logfile(self):
        '''
        Close the logfile
        '''

        if self._logfile is not None:
            self._logfile.close()

    def set_trackfile_path(self) -> str:
        '''
        Set track directory
        '''

        self._track_filepath = filedialog.askdirectory(title=SAVETITLE, initialdir=HOME,
                                       mustexist=True)
        if self._track_filepath == "":
            return None  # User cancelled
#         self._track_filename = self._set_filename(self._track_filepath, 'track', 'gpx')
#         self._trkfile = open(self._track_filename, 'a')
#         return self._track_filename
        return self._track_filepath

    def open_trackfile(self):
        '''
        Open track file and create GPX track header tags
        '''

        self._track_filename = self._set_filename(self._track_filepath, 'track', 'gpx')
        self._trkfile = open(self._track_filename, 'a')

        date = datetime.now().isoformat() + 'Z'
        gpxtrack = (XML_HDR + '<gpx ' + GPX_NS + '>'
        '<metadata>'
        f'<link href="{GITHUB_URL}"><text>PyGPSClient</text></link>'
        f'<time>{date}</time>'
        '</metadata>'
        '<trk><name>GPX track from PyGPSClient</name>'
        '<desc>GPX track from PyGPSClient</desc><trkseg>')

        self._trkfile.write(gpxtrack)

    def add_trackpoint(self, lat: float, lon: float, **kwargs):
        '''
        Creates GPX track point from provided parameters
        '''

        if not (isinstance(lat, (float, int)) and isinstance(lon, (float, int))):
            return

        trkpnt = f'<trkpt lat="{lat}" lon="{lon}">'

        for tag in ('ele', 'time', 'magvar', 'geoidheight', 'name', 'cmt', 'desc', 'src',
                    'link', 'sym', 'type', 'fix', 'sat', 'hdop', 'vdop', 'pdop'):
            if tag in kwargs:
                val = kwargs[tag]
                trkpnt += f'<{tag}>{val}</{tag}>'

        trkpnt += '</trkpt>'

        self._trkfile.write(trkpnt)

    def close_trackfile(self):
        '''
        Create GPX track trailer tags and close track file
        '''

        gpxtrack = '</trkseg></trk></gpx>'
        self._trkfile.write(gpxtrack)
        self._trkfile.close()
