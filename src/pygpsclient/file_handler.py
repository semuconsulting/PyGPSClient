"""
file_handler.py

Filehandler class for PyGPSClient application.

This handles all the file i/o, including:
- binary gnss log file
- json configuration file save, load and validation
- datalog export
- gpx file export
- SPARTN key and crt files

Created on 16 Sep 2020

:author: semuadmin (Steve Smith)
:copyright: 2020 semuadmin
:license: BSD 3-Clause
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from tkinter import Frame, Toplevel, filedialog
from types import NoneType

from pyubx2 import hextable

from pygpsclient.globals import (
    CONFIGFILE,
    ERRCOL,
    FORMAT_BINARY,
    FORMAT_BOTH,
    FORMAT_HEXSTR,
    FORMAT_HEXTAB,
    FORMAT_PARSED,
    GPX_NS,
    GPX_TRACK_INTERVAL,
    HOME,
    XML_HDR,
)
from pygpsclient.helpers import set_filename
from pygpsclient.strings import CONFIGTITLE, GITHUB_URL, SAVETITLE

DEFEXT = ("all files", "*.*")


class FileHandler:
    """
    File handler class.
    """

    def __init__(self, app):
        """
        Constructor.

        :param Tk app: reference to main tkinter application
        """

        self.__app = app  # Reference to main application class
        self.logger = logging.getLogger(__name__)
        self._in_filepath = None
        self._in_filename = None
        self._logpath = None
        self._logname = None
        self._logfile = None
        self._trackpath = None
        self._databasepath = None
        self._trackname = None
        self._trackfile = None
        self._configpath = None
        self._configfile = None
        self._initdir = {}
        self._logsize = 0
        self._last_track_update = datetime.fromordinal(1)
        self._flushcount = 0

    def __del__(self):
        """
        Destructor - close any open files.
        """

        self.close_logfile()
        self.close_trackfile()

    def open_file(
        self,
        parent: Frame | Toplevel | NoneType,
        mode: str,
        exts: tuple = DEFEXT,
    ) -> Path | NoneType:
        """
        Generic routine to open specified file type.

        :param Frame | Toplevel | NoneType: parent: parent window
        :param str mode: type of file e.g. "config", "gpxtrack" etc.
        :param tuple exts: tuple of file types ("description", "ext")
        :return: fully qualified path to file, or None if user cancelled
        :rtype: Path | NoneType
        """

        fil = filedialog.askopenfilename(
            title=f"Open {mode.upper()} File",
            initialdir=self._initdir.get(mode, HOME),
            filetypes=exts,
            parent=parent,
        )
        if fil in ((), ""):
            return None  # User cancelled
        self._initdir[mode] = Path(fil).parent  # remember last directory
        return Path(fil)

    def load_config(
        self, filepath: Path | NoneType = CONFIGFILE
    ) -> tuple[Path | NoneType, dict | NoneType, str]:
        """
        Load configuration file. If filename is not provided, defaults
        to $HOME/pygpsclient.json, otherwise user is prompted for path.

        :param Path | NoneType filename: fully qualified filename, or None for prompt
        :return: filename, saved settings as dictionary and any error message
        :rtype: tuple[Path | NoneType, dict | NoneType, str]
        """

        try:
            if filepath is None:
                filepath = self.open_file(
                    None,
                    "config",
                    (
                        ("config files", "*.json"),
                        ("all files", "*.*"),
                    ),
                )
                if filepath is None:
                    return (None, None, "cancelled")  # User cancelled
            else:
                self._initdir["config"] = filepath.parent

            with open(filepath, "r", encoding="utf-8") as jsonfile:
                config = json.load(jsonfile)
        except (OSError, json.JSONDecodeError) as err:
            return (filepath, None, str(err))

        return (filepath, config, "")

    def save_config(self, config: dict, filepath: Path | NoneType = CONFIGFILE) -> str:
        """
        Save configuration file. If filename is not provided, defaults to
        $HOME/pygpsclient.json, otherwise user is prompted for filename.

        :param dict config: configuration settings as dictionary
        :param Path | NoneType filename: fully qualified path to config file, or None for default
        :return: return code "" = success, err str = failure
        :rtype: str
        """

        try:
            if filepath is None:
                filepath = CONFIGFILE
            filename = filedialog.asksaveasfilename(
                title=CONFIGTITLE,
                initialdir=filepath.parent,
                initialfile=filepath.name,
                filetypes=(
                    ("config files", "*.json"),
                    ("all files", "*.*"),
                ),
            )
            if filename in ((), ""):
                return "cancelled"  # User cancelled

            with open(filename, "w", encoding="utf-8") as file:
                cfgstr = json.dumps(config)
                file.write(cfgstr)
                return ""
        except (OSError, json.JSONDecodeError) as err:
            return str(err)

    def set_logfile_path(self, initdir=HOME) -> str | NoneType:
        """
        Set file path.

        :param str initdir: initial directory (HOME)
        :return: file path
        :rtype: str | NoneType
        """

        logpath = filedialog.askdirectory(
            title=SAVETITLE, initialdir=initdir, mustexist=True
        )
        if logpath in ((), ""):
            return None  # User cancelled
        self._logpath = logpath
        return self._logpath

    def open_logfile(self) -> int:
        """
        Open logfile.

        :return: 0 = error, 1 = ok
        :rtype: int
        """

        # pylint: disable=consider-using-with

        try:
            self._logpath = self.__app.configuration.get("logpath_s")
            self._logsize = 0
            _, self._logname = set_filename(self._logpath, "data", "log")
            self._logfile = open(self._logname, "a+b")
            return 1
        except FileNotFoundError as err:
            self.__app.set_status_label(f"{err}", ERRCOL)
            return 0

    def write_logfile(self, raw_data, parsed_data):
        """
        Append data to log file. Data will be converted to bytes.

        :param data: data to be logged
        """

        if self._logfile is None:
            if not self.open_logfile():
                return

        lfm = self.__app.configuration.get("logformat_s")
        maxsize = self.__app.configuration.get("logsize_n")
        data = []
        if lfm in (FORMAT_PARSED, FORMAT_BOTH):
            data.append(parsed_data)
        if lfm == FORMAT_BINARY:
            data.append(raw_data)
        if lfm == FORMAT_HEXSTR:
            data.append(raw_data.hex())
        if lfm in (FORMAT_HEXTAB, FORMAT_BOTH):
            data.append(hextable(raw_data))

        for datum in data:
            if not isinstance(datum, bytes):
                datum = (str(datum) + "\r").encode("utf-8")
            try:
                self._logfile.write(datum)
                self._logfile.flush()
                self._logsize += len(datum)
            except ValueError:
                pass

        if self._logsize > maxsize:
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

    def set_trackfile_path(self, initdir=HOME) -> str | NoneType:
        """
        Set track directory.

        :param str initdir: initial directory (HOME)
        :return: file path
        :rtype: str
        """

        trackpath = filedialog.askdirectory(
            title=SAVETITLE, initialdir=initdir, mustexist=True
        )
        if trackpath in ((), ""):
            return None  # User cancelled
        self._trackpath = trackpath
        return self._trackpath

    def open_trackfile(self) -> int:
        """
        Open track file and create GPX track header tags.

        :return: 0 = error, 1 = ok
        :rtype: int
        """

        # pylint: disable=consider-using-with

        try:
            self._trackpath = self.__app.configuration.get("trackpath_s")
            _, self._trackname = set_filename(self._trackpath, "track", "gpx")
            self._trackfile = open(self._trackname, "a", encoding="utf-8")
        except FileNotFoundError as err:
            self.__app.set_status_label(f"{err}", ERRCOL)
            return 0

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

        return 1

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
            if self._trackfile is not None:
                self._trackfile.write(trkpnt)
                self._trackfile.flush()
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

    def update_gpx_track(self):
        """
        Update GPX track with latest valid position readings.
        """

        gnss_status = self.__app.gnss_status
        # must have valid coords (apologies if you live on Null Island)
        if (
            isinstance(gnss_status.lat, str)
            or isinstance(gnss_status.lon, str)
            or (gnss_status.lat == 0 and gnss_status.lon == 0)
        ):
            return

        if datetime.now() > self._last_track_update + timedelta(
            seconds=GPX_TRACK_INTERVAL
        ):
            today = datetime.now()
            gpstime = gnss_status.utc
            trktime = datetime(
                today.year,
                today.month,
                today.day,
                gpstime.hour,
                gpstime.minute,
                gpstime.second,
                gpstime.microsecond,
            )
            time = f"{trktime.isoformat()}Z"
            if gnss_status.diff_corr:
                fix = "dgps"
            elif gnss_status.fix == "3D":
                fix = "3d"
            elif gnss_status.fix == "2D":
                fix = "2d"
            else:
                fix = "none"
            diff_age = gnss_status.diff_age
            diff_station = gnss_status.diff_station
            if diff_age in [None, "", 0] or diff_station in [None, "", 0]:
                self.add_trackpoint(
                    gnss_status.lat,
                    gnss_status.lon,
                    ele=gnss_status.alt,
                    time=time,
                    fix=fix,
                    sat=gnss_status.sip,
                    pdop=gnss_status.pdop,
                )
            else:
                self.add_trackpoint(
                    gnss_status.lat,
                    gnss_status.lon,
                    ele=gnss_status.alt,
                    time=time,
                    fix=fix,
                    sat=gnss_status.sip,
                    pdop=gnss_status.pdop,
                    ageofdgpsdata=diff_age,
                    dgpsid=diff_station,
                )

            self._last_track_update = datetime.now()

    def set_database_path(self, initdir: Path = HOME) -> str | NoneType:
        """
        Set database directory.

        :param Path initdir: initial directory (HOME)
        :return: file path or None
        :rtype: str | NoneType
        """

        databasepath = filedialog.askdirectory(
            title=SAVETITLE, initialdir=initdir, mustexist=True
        )
        if databasepath in ((), ""):
            return None  # User cancelled
        self._databasepath = databasepath
        return self._databasepath
