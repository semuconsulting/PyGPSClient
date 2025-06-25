"""
sbf_handler.py

SBF Protocol handler - handles all incoming SBF messages

Parses individual UBX messages (using pysbf2 library)
and adds selected attribute values to the app.gnss_status
data dictionary. This dictionary is then used to periodically
update the various user-selectable widget panels.

Created on 19 May 2025

:author: semuadmin
:copyright: 2020 SEMU Consulting
:license: BSD 3-Clause
"""

import logging
from math import degrees

from pysbf2 import SBFMessage, itow2utc

from pygpsclient.globals import ASCII, BSR
from pygpsclient.helpers import fix2desc

DNUL = -2 * (10**10)
DNUS = 65535


class SBFHandler:
    """
    SBFHandler class
    """

    def __init__(self, app):
        """
        Constructor.

        :param Frame app: reference to main tkinter application
        """

        self.__app = app  # Reference to main application class
        self.__master = self.__app.appmaster  # Reference to root class (Tk)
        self.logger = logging.getLogger(__name__)

        self._cdb = 0
        self._raw_data = None
        self._parsed_data = None
        # Holds array of current satellites
        self.gsv_data = {}

    def process_data(self, raw_data: bytes, parsed_data: object):
        """
        Process relevant UBX message types

        :param bytes raw_data: raw data
        :param UBXMessage parsed_data: parsed data
        """

        if raw_data is None:
            return
        # self.logger.debug(f"data received {parsed_data.identity}")
        if parsed_data.identity == "PVTGeodetic":
            self._process_PVTGeodetic(parsed_data)
        elif parsed_data.identity == "ReceiverStatus":
            self._process_ReceiverStatus(parsed_data)
        elif parsed_data.identity == "ReceiverSetup":
            self._process_ReceiverSetup(parsed_data)

    def _process_PVTGeodetic(self, data: SBFMessage):
        """
        Process PVTGeodetic sentence - Position Velocity Track Geodetic.

        :param SBFMessage data: PVTGeodetic message
        """

        self.__app.gnss_status.utc = itow2utc(data.TOW)  # datetime.time
        if data.Latitude != DNUL:
            self.__app.gnss_status.lat = degrees(data.Latitude)
        if data.Longitude != DNUL:
            self.__app.gnss_status.lon = degrees(data.Longitude)
        if data.Height != DNUL:
            self.__app.gnss_status.hae = data.Height  # meters
        if data.HAccuracy != DNUS:
            self.__app.gnss_status.hacc = data.HAccuracy / 100  # meters
        if data.VAccuracy != DNUS:
            self.__app.gnss_status.vacc = data.VAccuracy / 100  # meters
        if data.NrSV != 255:
            self.__app.gnss_status.sip = data.NrSV
        if data.COG != DNUL:
            self.__app.gnss_status.track = data.COG
        self.__app.gnss_status.fix = fix2desc("PVTGeodetic", data.Type)
        if data.MeanCorrAge != 0:
            self.__app.gnss_status.diff_age = data.MeanCorrAge / 100  # seconds
        self.__app.gnss_status.diff_station = data.ReferenceID

    def _process_ReceiverStatus(self, data: SBFMessage):
        """
        Process ReceiverStatus sentence.

        :param SBFMessage data: ReceiverStatus message
        """

        sysdata = {}
        sysdata["cpuLoad"] = data.CPULoad
        sysdata["runTime"] = data.UpTime
        sysdata["tempValue"] = data.Temperature - 100  # offset by 100
        self.__app.gnss_status.sysmon_data = sysdata

    def _process_ReceiverSetup(self, data: SBFMessage):
        """
        Process ReceiverSetups sentence.

        :param SBFMessage data: ReceiverSetup message
        """

        verdata = {}
        verdata["hwversion"] = data.ProductName.decode(ASCII, errors=BSR).replace(
            "\x00", ""
        )
        verdata["fwversion"] = data.RxVersion.decode(ASCII, errors=BSR).replace(
            "\x00", ""
        )
        verdata["romversion"] = data.GNSSFWVersion.decode(ASCII, errors=BSR).replace(
            "\x00", ""
        )
        self.__app.gnss_status.version_data = verdata
