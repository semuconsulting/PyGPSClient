"""
uni_handler.py

Unicore GNSS Protocol handler - handles all incoming UNI messages

Parses individual UNI (Unicore UM98n GNSS) messages (using pyunignss library)
and adds selected attribute values to the app.gnss_status
data dictionary. This dictionary is then used to periodically
update the various user-selectable widget panels.

Created on 27 Jan 2026

:author: semuadmin (Steve Smith)
:copyright: 2020 semuadmin
:license: BSD 3-Clause
"""

import logging
from time import time

from pyunigps import UNIMessage

from pygpsclient.helpers import fix2desc, wnotow2date

SATSINFO_GNSSID = {
    0: 0,  # GPS
    1: 6,  # GLONASS
    2: 1,  # SBAS
    3: 2,  # GAL
    4: 3,  # BDS
    5: 5,  # QZSS
    6: 7,  # IRNSS
}

SATELLITE_GNSSID = {
    0: 0,  # GPS
    1: 6,  #  GLONASS
    2: 1,  #  SBAS
    5: 2,  #  GALILEO
    6: 3,  #  BEIDOU
    7: 5,  #  QZSS
    9: 7,  #  NAVIC
}


class UNIHandler:
    """
    UNIHandler class
    """

    def __init__(self, app):
        """
        Constructor.

        :param Frame app: reference to main tkinter application
        """

        self.__app = app  # Reference to main application class
        self.__master = self.__app.appmaster  # Reference to root class (Tk)
        self.logger = logging.getLogger(__name__)

        self._raw_data = None
        self._parsed_data = None

    # pylint: disable=unused-argument
    def process_data(self, raw_data: bytes, parsed_data: UNIMessage):
        """
        Process relevant UNI message types

        :param bytes raw_data: raw data
        :param UNIMessage parsed_data: parsed data
        """

        if raw_data is None:
            return
        # self.logger.debug(f"data received {parsed_data.identity}")
        self.__app.gnss_status.utc = wnotow2date(
            parsed_data.wno, int(parsed_data.tow / 1000), parsed_data.leapsecond
        )  # datetime.time
        if parsed_data.identity in ("BESTNAV", "BESTNAVH"):
            self._process_BESTNAV(parsed_data)
        elif parsed_data.identity in ("PVTSLT",):
            self._process_PVTSLT(parsed_data)
        elif parsed_data.identity in (
            "ADRNAV",
            "ADRNAVH",
            "PPPNAV",
            "SPPNAV",
            "SPPNAVH",
        ):
            self._process_ADRNAV(parsed_data)
        elif parsed_data.identity in ("SATSINFO",):
            self._process_SATSINFO(parsed_data)
        elif parsed_data.identity in ("SATELLITE",):
            self._process_SATELLITE(parsed_data)
        elif parsed_data.identity in ("STADOP", "ADRDOP", "PPPDOP"):
            self._process_STADOP(parsed_data)

    def _process_pos(self, lat: float, lon: float, hmsl: float, undulation: float):
        """
        Process lat/lon/hmsl/hae.

        :param float lat: lat
        :param float lon: lon
        :param float hmsl: hmsl in meters
        :param float undulation: separation in meters
        """

        self.__app.gnss_status.lat = lat
        self.__app.gnss_status.lon = lon
        self.__app.gnss_status.alt = hmsl
        self.__app.gnss_status.hae = hmsl + undulation

    def _process_fix(self, postype: int):
        """
        Process fix type.

        :param int postype: attribute representing fix type
        """

        self.__app.gnss_status.fix = fix2desc("BESTNAV", postype)
        self.__app.gnss_status.diff_corr = ("RTK" in self.__app.gnss_status.fix) or (
            "PPP" in self.__app.gnss_status.fix
        )

    def _process_BESTNAV(self, data: UNIMessage):
        """
        Process BESTNAV sentence -  Navigation position velocity time solution.

        :param UNIMessage data: BESTNAV parsed message
        """

        self._process_pos(data.lat, data.lon, data.hmsl, data.undulation)
        self._process_fix(data.postype)
        self.__app.gnss_status.sip = data.numsolnsvs
        self.__app.gnss_status.diff_age = data.diffage
        self.__app.gnss_status.speed = data.horspd
        self.__app.gnss_status.track = data.trkgnd
        self.__app.gnss_status.diff_station = data.stationid

    def _process_PVTSLT(self, data: UNIMessage):
        """
        Process PVTSLT sentence -  Navigation position velocity time solution.

        :param UNIMessage data: PVTSLT parsed message
        """

        self._process_pos(
            data.psrposlat, data.psrposlon, data.psrposhmsl, data.undulation
        )
        self._process_fix(data.psrpostype)
        self.__app.gnss_status.sip = data.psrpossolnsvs
        self.__app.gnss_status.speed = data.psrvelground
        self.__app.gnss_status.track = data.headingdegree
        self.__app.gnss_status.pdop = data.pdop
        self.__app.gnss_status.hdop = data.hdop
        self.__app.gnss_status.diff_age = data.bestpos_diffage

    def _process_ADRNAV(self, data: UNIMessage):
        """
        Process ADRNAV, PPPNAV, SPPNAV sentences.

        :param UNIMessage data: ADRNAV/PPPNAV/SPPNAV parsed message
        """

        self._process_pos(data.lat, data.lon, data.hmsl, data.undulation)
        self._process_fix(data.postype)

    def _process_SATSINFO(self, data: UNIMessage):
        """
        Process SATSINFO sentences - Space Vehicle Information for all
        GNSS constellations.

        :param UNIMessage data: SATSINFO parsed message
        """

        self.__app.gnss_status.gsv_data = {}
        num_siv = int(data.numsat)
        now = time()

        for i in range(num_siv):
            idx = f"_{i+1:02d}"
            gnssId = SATSINFO_GNSSID[getattr(data, "sysstatus" + idx + "_01")]
            svid = getattr(data, "prn" + idx)
            elev = getattr(data, "elev" + idx)
            azim = getattr(data, "azi" + idx)
            cno = getattr(data, "cno" + idx + "_01")
            self.__app.gnss_status.gsv_data[(gnssId, svid)] = (
                gnssId,
                svid,
                elev,
                azim,
                cno,
                now,
            )

        self.__app.gnss_status.siv = len(self.__app.gnss_status.gsv_data)

    def _process_SATELLITE(self, data: UNIMessage):
        """
        Process SATELLITE sentences - Space Vehicle Information for a
        specific GNSS constellation (7 in total).

        :param UNIMessage data: SATSINFO parsed message
        """

        gnssId = SATELLITE_GNSSID[getattr(data, "gnss")]
        for gnss, prn in list(self.__app.gnss_status.gsv_data.keys()):
            if gnss == gnssId:
                self.__app.gnss_status.gsv_data.pop((gnss, prn))

        num_siv = int(data.numsat)
        now = time()
        for i in range(num_siv):
            idx = f"_{i+1:02d}"
            svid = getattr(data, "prn" + idx)
            elev = getattr(data, "elv" + idx)
            azim = getattr(data, "azi" + idx)
            cno = 0  # cno not available from this message
            self.__app.gnss_status.gsv_data[(gnssId, svid)] = (
                gnssId,
                svid,
                elev,
                azim,
                cno,
                now,
            )

        self.__app.gnss_status.siv = len(self.__app.gnss_status.gsv_data)

    def _process_STADOP(self, data: UNIMessage):
        """
        Process STADOP/ADRDOP/PPPDOP sentences - DOP Information.

        :param UNIMessage data: STADOP/ADRDOP/PPPDOP parsed message
        """

        self.__app.gnss_status.pdop = data.pdop
        self.__app.gnss_status.hdop = data.hdop
        self.__app.gnss_status.vdop = data.vdop
