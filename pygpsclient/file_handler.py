"""
Filehandler class for PyGPSClient application

This handles all the file i/o

Created on 16 Sep 2020

:author: semuadmin
:copyright: SEMU Consulting © 2020
:license: BSD 3-Clause
"""
# pylint: disable=unspecified-encoding

import os
from datetime import datetime
from pathlib import Path
from time import strftime
from tkinter import filedialog
from pyubx2 import hextable

from pygpsclient.globals import (
    MQAPIKEY,
    COLORTAGS,
    UBXPRESETS,
    MAXLOGLINES,
    XML_HDR,
    GPX_NS,
    GITHUB_URL,
    FORMATS,
)
from pygpsclient.strings import SAVETITLE, READTITLE

HOME = str(Path.home())


class FileHandler:
    """
    File handler class.
    """

    def __init__(self, app):
        """
        Constructor.

        :param Frame app: reference to main tkinter application
        """

        self.__app = app  # Reference to main application class
        self.__master = self.__app.get_master()  # Reference to root class (Tk)
        self._in_filepath = None
        self._in_filename = None
        self._logpath = None
        self._logname = None
        self._infile = None
        self._logfile = None
        self._trackpath = None
        self._trackname = None
        self._trackfile = None
        self._lines = 0

    def __del__(self):
        """
        Destructor - close any open files.
        """

        self.close_logfile()
        self.close_trackfile()

    def load_apikey(self) -> str:
        """
        Load MapQuest web map api key from environment variable or
        key file in user's home directory.

        :return: apikey
        :rtype: str
        """

        # load from env variable if set
        apikey = os.getenv("MQAPIKEY")
        if apikey is not None:
            return apikey

        # otherwise load from file
        filepath = os.path.join(HOME, MQAPIKEY)
        try:
            with open(filepath, "r") as file:
                apikey = file.read()
        except OSError:
            # Error message will be displayed on mapview widget if invoked
            apikey = ""

        return apikey

    def load_colortags(self) -> list:
        """
        Load user defined colortags from file.

        Expects file in format:
        string1;color1
        string2;color2
        etc.

        :return: list of colortags
        :rtype: list
        """

        ctags = []
        filepath = os.path.join(HOME, COLORTAGS)
        try:
            with open(filepath, "r") as file:
                for line in file:
                    ctag = line.split(";")
                    if len(ctag) == 2:
                        if ctag[0][0:1] != "#":  # ignore comments
                            tag = ctag[0].strip(" \n")
                            col = ctag[1].strip(" \n")
                            ctags.append((tag, col))
        except OSError:
            pass

        return ctags

    def load_user_presets(self) -> str:
        """
        Load user configuration message presets from user's home directory.

        :return: user presets
        :rtype: str
        """

        presets = []
        filepath = os.path.join(HOME, UBXPRESETS)
        try:
            with open(filepath, "r") as file:
                for line in file:
                    presets.append(line)
        except OSError:
            presets = ""

        return presets

    def _set_filename(self, path: str, mode: str, ext: str) -> str:
        """
        Return fully qualified and timestamped file name.

        :param path: the file path as str
        :param mode: the type of file being created ('data', 'track') as str
        :param ext: the file extension ('log', 'gpx') as str
        :return: fully qualified filename
        :rtype: str
        """

        self._lines = 0
        timestr = strftime("%Y%m%d%H%M%S")
        filename = os.path.join(path, f"pygps{mode}-" + timestr + f".{ext}")
        return filename

    def set_logfile_path(self) -> str:
        """
        Set file path.

        :return: file path
        :rtype: str
        """

        self._logpath = filedialog.askdirectory(
            title=SAVETITLE, initialdir=HOME, mustexist=True
        )
        if self._logpath in ((), ""):
            return None  # User cancelled
        return self._logpath

    def open_logfile(self):
        """
        Open logfile.
        """

        self._logname = self._set_filename(self._logpath, "data", "log")
        self._logfile = open(self._logname, "a+b")

    def open_infile(self) -> str:
        """
        Open input file for streaming.

        :return: input ile path
        :rtype: str
        """

        self._in_filepath = filedialog.askopenfilename(
            title=READTITLE,
            initialdir=HOME,
            filetypes=(
                ("datalog files", "*.log"),
                ("u-center logs", "*.ubx"),
                ("all files", "*.*"),
            ),
        )
        if self._in_filepath in ((), ""):
            return None  # User cancelled
        return self._in_filepath

    def write_logfile(self, raw_data, parsed_data):
        """
        Append data to log file. Data will be converted to bytes.

        :param data: data to be logged
        """

        if self._logfile is None:
            return

        data = []
        if self.__app.frm_settings.logformat in (
            FORMATS[0],
            FORMATS[4],
        ):  # parsed, parsed + hex tabular
            data.append(parsed_data)
        if self.__app.frm_settings.logformat == FORMATS[1]:  # binary
            data.append(raw_data)
        if self.__app.frm_settings.logformat == FORMATS[2]:  # hex string
            data.append(raw_data.hex())
        if self.__app.frm_settings.logformat in (
            FORMATS[3],
            FORMATS[4],
        ):  # hex tabular, parsed + hex tabular
            data.append(hextable(raw_data))

        for datum in data:
            if not isinstance(datum, bytes):
                datum = (str(datum) + "\r").encode("utf-8")
            try:
                self._logfile.write(datum)
                self._lines += 1
            except ValueError:
                pass

        if self._lines > MAXLOGLINES:
            self.close_logfile()
            self.open_logfile()

    def close_logfile(self):
        """
        Close the logfile.
        """

        try:
            if self._logfile is not None:
                self._logfile.close()
        except IOError:
            pass

    def set_trackfile_path(self) -> str:
        """
        Set track directory.

        :return: file path
        :rtype: str
        """

        self._trackpath = filedialog.askdirectory(
            title=SAVETITLE, initialdir=HOME, mustexist=True
        )
        if self._trackpath in ((), ""):
            return None  # User cancelled
        return self._trackpath

    def open_trackfile(self):
        """
        Open track file and create GPX track header tags.
        """

        self._trackname = self._set_filename(self._trackpath, "track", "gpx")
        self._trackfile = open(self._trackname, "a")

        date = datetime.now().isoformat() + "Z"
        gpxtrack = (
            XML_HDR + "<gpx " + GPX_NS + ">"
            "<metadata>"
            f'<link href="{GITHUB_URL}"><text>PyGPSClient</text></link>'
            f"<time>{date}</time>"
            "</metadata>"
            "<trk><name>GPX track from PyGPSClient</name>"
            "<desc>GPX track from PyGPSClient</desc><trkseg>"
        )

        try:
            self._trackfile.write(gpxtrack)
        except ValueError:
            pass

    def add_trackpoint(self, lat: float, lon: float, **kwargs):
        """
        Creates GPX track point from provided parameters.

        :param float lat: latitude
        :param float lon: longitude
        :param kwargs: optional gpx tags as series of key value pairs
        """

        if not (isinstance(lat, (float, int)) and isinstance(lon, (float, int))):
            return

        trkpnt = f'<trkpt lat="{lat}" lon="{lon}">'

        # these are the permissible elements in the GPX schema for wptType
        # http://www.topografix.com/GPX/1/1/#type_wptType
        for tag in (
            "ele",
            "time",
            "magvar",
            "geoidheight",
            "name",
            "cmt",
            "desc",
            "src",
            "link",
            "sym",
            "type",
            "fix",
            "sat",
            "hdop",
            "vdop",
            "pdop",
            "ageofdgpsdata",
            "dgpsid",
            "extensions",
        ):
            if tag in kwargs:
                val = kwargs[tag]
                trkpnt += f"<{tag}>{val}</{tag}>"

        trkpnt += "</trkpt>"

        try:
            self._trackfile.write(trkpnt)
        except (IOError, ValueError):
            pass

    def close_trackfile(self):
        """
        Create GPX track trailer tags and close track file.
        """

        gpxtrack = "</trkseg></trk></gpx>"
        try:
            if self._trackfile is not None:
                self._trackfile.write(gpxtrack)
                self._trackfile.close()
        except (IOError, ValueError):
            pass
