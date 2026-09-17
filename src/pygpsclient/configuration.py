"""
configuration.py

Class holding all PyGPSClient configuration settings.

Created on 18 Apr 2025

:author: semuadmin (Steve Smith)
:copyright: 2020 semuadmin
:license: BSD 3-Clause
"""

# pylint: disable=logging-format-interpolation

import logging
from os import getenv
from types import NoneType
from typing import Any

from pygnssutils import (
    PYGNSSUTILS_CRT,
    PYGNSSUTILS_CRTPATH,
    PYGNSSUTILS_PEM,
    PYGNSSUTILS_PEMPATH,
)
from pyubx2 import GET
from serial import PARITY_NONE

from pygpsclient import version
from pygpsclient.globals import (
    CUSTOM,
    DDD,
    DEFAULT_PASSWORD,
    DEFAULT_USER,
    ERRCOL,
    FORMAT_BINARY,
    FORMAT_PARSED,
    GUI_UPDATE_INTERVAL,
    MAXLOGSIZE,
    MIN_GUI_UPDATE_INTERVAL,
    OKCOL,
    RCVR_CONNECTION,
    SOCKCLIENT_HOST,
    SOCKCLIENT_PORT,
    SOCKSERVER_HOST,
    SOCKSERVER_NTRIP_PORT,
    SOCKSERVER_PORT,
    TRACK,
    UBLOX_ZEDF9,
    UMM,
    WORLD,
)
from pygpsclient.init_presets import INIT_PRESETS
from pygpsclient.mapquest_handler import MAP_UPDATE_INTERVAL
from pygpsclient.serverconfig_dialog import BASE_SVIN
from pygpsclient.strings import (
    LOADCONFIGBAD,
    LOADCONFIGNK,
    LOADCONFIGNONE,
    LOADCONFIGOK,
    LOADCONFIGRESAVE,
)
from pygpsclient.widget_state import MAXCOLSPAN, VISIBLE

INITMARKER = "INIT_PRESETS"
PRE_L = "presets_l"


class Configuration:
    """
    Configuration class for PyGPSClient.

    Contains, in order of precedence:

        1. settings updated by user via GUI
        2. settings provided by CLI keyword arguments
        3. settings provided by environment variables
        4. settings imported from json file
        5. default setting values

    """

    def __init__(self, app):
        """
        Set up initial configuration.

        :param Tk app: reference to main tkinter application
        :param str filename: configuration file name
        """

        self.__app = app  # Reference to main application class
        self.logger = logging.getLogger(__name__)

        # Set initial default configuration
        self._settings = {
            "version_s": version,
            "screengeom_s": "",  # screen geometry in tkinter format f"{w}x{h}+{x}+{y}"
            "showsettings_b": 1,
            "docksettings_b": 1,
            **self.widget_config,
            "checkforupdate_b": 0,
            "transient_dialog_b": 1,  # whether pop-up dialogs are on top of main app window
            "resizeable_dialog_b": 0,  # whether pop-up dialogs are all resizeable
            "guiupdateinterval_f": GUI_UPDATE_INTERVAL,  # GUI widget update interval in seconds
            "mapupdateinterval_n": MAP_UPDATE_INTERVAL,  # MAPQUEST map update interval in seconds
            "defaultport_s": RCVR_CONNECTION,
            "nmeaprot_b": 1,
            "ubxprot_b": 1,
            "rtcmprot_b": 1,
            "sbfprot_b": 0,
            "qgcprot_b": 0,
            "uniprot_b": 0,
            "spartnprot_b": 0,
            "mqttprot_b": 1,
            "ttyprot_b": 0,
            "metaprot_b": 0,
            "ttycrlf_b": 1,
            "ttyecho_b": 0,
            "ttydelay_b": 1,
            "degreesformat_s": DDD,
            "colortag_b": 0,
            "units_s": UMM,
            "autoscroll_b": 1,
            "maxlines_n": 100,
            "maxcolumns_n": MAXCOLSPAN,  # maximum number of user-selectable widget columns
            "filedelay_n": 20,  # milliseconds
            "consoleformat_s": FORMAT_PARSED,
            "maptype_s": WORLD,
            "mapzoom_n": 10,
            "mapzoom_disabled_b": 0,  # whether offline maps zooming is disabled
            "gpxmaptype_s": CUSTOM,
            "gpxmapzoom_n": 10,
            "gpxtype_s": TRACK,
            "mqapikey_s": "<=== YOUR MAPQUEST API KEY  ===>",
            "showtrack_b": 0,
            "legend_b": 1,
            "unusedsat_b": 0,
            "datalog_b": 0,
            "logformat_s": FORMAT_BINARY,
            "logpath_s": "",
            "logsize_n": MAXLOGSIZE,
            "recordtrack_b": 0,
            "trackpath_s": "",
            "database_b": 0,
            "databasepath_s": "",
            "tlspempath_s": PYGNSSUTILS_PEM,
            "tlscrtpath_s": PYGNSSUTILS_CRT,
            # serial port settings from frm_serial
            "serialport_s": "/dev/ttyACM0",
            "bpsrate_n": 9600,
            "databits_n": 8,
            "stopbits_f": 1.0,
            "parity_s": PARITY_NONE,
            "rtscts_b": 0,
            "xonxoff_b": 0,
            "timeout_f": 0.1,
            "msgmode_n": GET,
            "userport_s": "",
            "inactivity_timeout_n": 0,
            # socket client settings from frm_socketclient
            "sockclienthost_s": SOCKCLIENT_HOST,
            "sockclientport_n": SOCKCLIENT_PORT,
            "sockclienthttps_b": 0,
            "sockclientselfsign_b": 0,
            "sockclientprotocol_s": "TCP IPv4",
            # socket server settings from server dialog
            "sockserver_b": 0,
            "sockhost_s": SOCKSERVER_HOST,
            "sockport_n": SOCKSERVER_PORT,
            "sockportntrip_n": SOCKSERVER_NTRIP_PORT,
            "sockmode_b": 0,
            "sockhttps_b": 0,
            "ntripcasterbasemode_s": BASE_SVIN,
            "ntripcasterrcvrtype_s": UBLOX_ZEDF9,
            "ntripcasteracclimit_f": 100.0,
            "ntripcasterduration_n": 60,
            "ntripcasterposmode_s": "LLH",
            "ntripcasterfixedlat_f": 0.0,
            "ntripcasterfixedlon_f": 0.0,
            "ntripcasterfixedalt_f": 0.0,
            "ntripcasterdisablenmea_b": 0,
            "ntripcasteruser_s": DEFAULT_USER,
            "ntripcasterpassword_s": DEFAULT_PASSWORD,
            # NTRIP client settings from pygnssutils.GNSSNTRIPClient
            "ntripclientserver_s": "rtk2go.com",
            "ntripclientport_n": SOCKSERVER_NTRIP_PORT,
            "ntripclienthttps_b": 0,
            "ntripclientselfsign_b": 0,
            "ntripclientprotocol_s": "IPv4",
            "ntripclientflowinfo_n": 0,
            "ntripclientscopeid_n": 0,
            "ntripclientmountpoint_s": "",
            "ntripclientversion_s": "2.0",
            "ntripclientdatatype_s": "RTCM",
            "ntripclientuser_s": DEFAULT_USER,
            "ntripclientpassword_s": DEFAULT_PASSWORD,
            "ntripclientggainterval_n": -1,
            "ntripclientggamode_b": 1,
            "ntripclientreflat_f": 0.0,
            "ntripclientreflon_f": 0.0,
            "ntripclientrefalt_f": 0.0,
            "ntripclientrefsep_f": 0.0,
            "spartndecode_b": 0,
            "spartnkey_s": "abcd1234abcd1234abcd1234abcd1234",
            "spartnbasedate_n": -1,
            "relposnedsettings_d": {
                "source_s": "NAV-RELPOSNED",
            },
            "scattersettings_d": {
                "scatterautorange_b": 1,
                "scattercenter_s": "Average",
                "scatterinterval_n": 1,
                "scatterscale_n": 1,
                "scatterlat_f": 0.0,
                "scatterlon_f": 0.0,
            },
            "imusettings_d": {
                "range_n": 180,
                "option_s": "N/A",  # reserved for future use
            },
            "chartsettings_d": {
                "numchn_n": 4,
                "timrng_n": 240,
                "maxpoints_n": 1000,
            },
            f"ubx{PRE_L}": [],
            f"nmea{PRE_L}": [],
            f"tty{PRE_L}": [],
            "usermaps_l": [],
            "colortags_l": [],
        }

    def loadfile(self, filename: str | NoneType = None) -> tuple:
        """
        Load configuration from json file.

        :param str | NoneType filename: config file name
        :return: tuple of filename and err message (or "" if OK)
        :rtype: tuple
        """

        fname, config, err = self.__app.file_handler.load_config(filename)
        key = ""
        val = 0
        resave = False
        if err == "":  # load succeeded
            for key, val in config.items():
                if key == "version_s" and val != version:
                    resave = True
                key = key.replace("mgtt", "mqtt")  # tolerate "mgtt" typo
                if key == "guiupdateinterval_f":  # disallow excessive value
                    val = max(MIN_GUI_UPDATE_INTERVAL, val)
                try:
                    self.set(key, val)
                except KeyError:  # ignore unrecognised setting
                    self.logger.info(LOADCONFIGNK.format(key, val))
                    resave = True
                    continue
        else:
            if err == "cancelled":  # user cancelled
                return filename, err
            if "No such file or directory" in err:
                err = LOADCONFIGNONE.format(fname)
            else:
                err = LOADCONFIGBAD.format(fname, err)

        if err == "":  # config valid
            rs = LOADCONFIGRESAVE if resave else ""
            self.__app.set_status_label(LOADCONFIGOK.format(fname, rs), OKCOL)
        else:
            self.__app.set_status_label(err, ERRCOL)

        return fname, err

    def savefile(self, filename: str | NoneType = None) -> str:
        """
        Save configuration to json file.

        :param str | NoneType filename: config file name
        :return: error code, or "" if OK
        :rtype: str
        """

        self.set("version_s", version)
        return self.__app.file_handler.save_config(self.settings, filename)

    def loadcli(self, **kwargs):
        """
        Load settings from CLI keyword arguments or environment variables.

        :param dict kwargs: CLI keyword arguments
        """

        arg = kwargs.pop("userport", getenv("PYGPSCLIENT_USERPORT", None))
        if arg is not None:
            self.set("userport_s", arg)
        arg = kwargs.pop("spartnport", getenv("PYGPSCLIENT_SPARTNPORT", None))
        if arg is not None:
            self.set("spartnport_s", arg)
        arg = kwargs.pop("mqapikey", getenv("MQAPIKEY", None))
        if arg is not None:
            self.set("mqapikey_s", arg)
        arg = kwargs.pop("mqttclientid", getenv("MQTTCLIENTID", None))
        if arg is not None:
            self.set("mqttclientid_s", arg)
        arg = kwargs.pop("spartnkey", getenv("MQTTKEY", None))
        if arg is not None:
            self.set("spartnkey_s", arg)
        arg = kwargs.pop("spartnbasedate", getenv("SPARTNBASEDATE", None))
        if arg is not None:
            self.set("spartnbasedate_n", int(arg))
        arg = kwargs.pop("mqttclientregion", getenv("MQTTCLIENTREGION", None))
        if arg is not None:
            self.set("mqttclientregion_s", arg)
        arg = kwargs.pop("mqttclientmode", getenv("MQTTCLIENTMODE", None))
        if arg is not None:
            self.set("mqttclientmode_n", int(arg))
        arg = kwargs.pop("ntripcasteruser", getenv("NTRIPCASTER_USER", None))
        if arg is not None:
            self.set("ntripcasteruser_s", arg)
        arg = kwargs.pop("ntripcasterpassword", getenv("NTRIPCASTER_PASSWORD", None))
        if arg is not None:
            self.set("ntripcasterpassword_s", arg)
        arg = kwargs.pop("tlspempath", getenv(PYGNSSUTILS_PEMPATH, PYGNSSUTILS_PEM))
        if arg is not None:
            self.set("tlspempath_s", arg)
        arg = kwargs.pop("tlscrtpath", getenv(PYGNSSUTILS_CRTPATH, PYGNSSUTILS_CRT))
        if arg is not None:
            self.set("tlscrtpath_s", arg)

    def set(self, name: str, value: Any):
        """
        Set individual value.

        :param str name: name of setting
        :param Any value: value of setting
        :raises: KeyError if setting does not exist
        """

        _ = self.settings[name]
        self.settings[name] = value
        # self.logger.debug(f"{name=} {value=}")

    def get(self, name: str) -> Any:
        """
        Get individual value.

        :param str name: name of setting
        :return: setting value
        :rtype: Any
        :raises: KeyError if setting does not exist
        """

        return self.settings[name]

    def init_presets(self, mode: str):
        """
        (Re-)Initialise user-defined presets list.

        :param str mode: "ubx", "nmea" or "tty"
        """

        presets = f"{mode}{PRE_L}"
        init_presets = INIT_PRESETS.get(presets, [])
        lp = len(self.get(presets))
        init = False
        if lp == 0:
            init = True
        elif lp > 0 and self.get(presets)[0] == INITMARKER:
            self.get(presets).pop(0)
            init = True
        if init:
            self.set(
                presets,
                init_presets + self.get(presets),
            )

    @property
    def settings(self) -> dict:
        """
        Getter for settings

        :return: settings dictionary
        :rtype: dict
        """

        return self._settings

    @property
    def widget_config(self) -> dict:
        """
        Getter for widget configuration.

        :return: widget visible state
        :rtype: dict
        """

        return {
            key: vals[VISIBLE] for key, vals in self.__app.widget_state.state.items()
        }
