"""
UBX Protocol handler

Uses pyubx2 library for parsing

Created on 30 Sep 2020

:author: semuadmin
:copyright: SEMU Consulting © 2020
:license: BSD 3-Clause
"""
# pylint: disable=invalid-name

from pyubx2 import UBXMessage, itow2utc
from pygpsclient.globals import GLONASS_NMEA
from pygpsclient.helpers import svid2gnssid, fix2desc, corrage2int


class UBXHandler:
    """
    UBXHandler class
    """

    def __init__(self, app):
        """
        Constructor.

        :param Frame app: reference to main tkinter application
        """

        self.__app = app  # Reference to main application class
        self.__master = self.__app.get_master()  # Reference to root class (Tk)

        self._raw_data = None
        self._parsed_data = None
        self.gsv_data = (
            []
        )  # Holds array of current satellites in view from NMEA GSV or UBX NAV-SVINFO sentences

    def process_data(self, raw_data: bytes, parsed_data: object):
        """
        Process relevant UBX message types

        :param bytes raw_data: raw data
        :param UBXMessage parsed_data: parsed data
        """

        if raw_data is None:
            return

        if parsed_data.identity[0:3] in ("ACK", "CFG"):
            self._update_ubxconfig(parsed_data)
        elif parsed_data.identity in ("MON-VER", "MON-HW"):
            self._update_ubxconfig(parsed_data)
        elif parsed_data.identity in ("NAV-POSLLH", "NAV-HPPOSLLH"):
            self._process_NAV_POSLLH(parsed_data)
        elif parsed_data.identity in ("NAV-PVT", "NAV2-PVT"):
            self._process_NAV_PVT(parsed_data)
        elif parsed_data.identity == "NAV-VELNED":
            self._process_NAV_VELNED(parsed_data)
        elif parsed_data.identity in ("NAV-SAT", "NAV2-SAT"):
            self._process_NAV_SAT(parsed_data)
        elif parsed_data.identity in ("NAV-STATUS", "NAV2-STATUS)"):
            self._process_NAV_STATUS(parsed_data)
        elif parsed_data.identity == "NAV-SVINFO":
            self._process_NAV_SVINFO(parsed_data)
        elif parsed_data.identity == "NAV-SOL":
            self._process_NAV_SOL(parsed_data)
        elif parsed_data.identity in ("NAV-DOP", "NAV2-DOP"):
            self._process_NAV_DOP(parsed_data)
        elif parsed_data.identity == "HNR-PVT":
            self._process_HNR_PVT(parsed_data)
        elif parsed_data.identity == "RXM-RTCM":
            self._process_RXM_RTCM(parsed_data)

    def _update_ubxconfig(self, msg: UBXMessage):
        """
        Update UBX Config dialog status.

        :param UBXMessage msg: UBX config message
        """

        if self.__app.dlg_ubxconfig is not None:
            self.__app.dlg_ubxconfig.update_pending(msg)

    def _process_NAV_POSLLH(self, data: UBXMessage):
        """
        Process NAV-(HP)POSLLH sentence - Latitude, Longitude, Height.

        :param UBXMessage data: NAV-(HP)POSLLH parsed message
        """

        self.__app.gnss_status.utc = itow2utc(data.iTOW)  # datetime.time
        self.__app.gnss_status.lat = data.lat
        self.__app.gnss_status.lon = data.lon
        self.__app.gnss_status.alt = data.hMSL / 1000  # meters
        self.__app.gnss_status.hacc = data.hAcc / 1000  # meters
        self.__app.gnss_status.vacc = data.vAcc / 1000  # meters

    def _process_NAV_PVT(self, data: UBXMessage):
        """
        Process NAV-PVT sentence -  Navigation position velocity time solution.

        :param UBXMessage data: NAV-PVT parsed message
        """

        self.__app.gnss_status.utc = itow2utc(data.iTOW)  # datetime.time
        self.__app.gnss_status.lat = data.lat
        self.__app.gnss_status.lon = data.lon
        self.__app.gnss_status.alt = data.hMSL / 1000  # meters
        self.__app.gnss_status.hacc = data.hAcc / 1000  # meters
        self.__app.gnss_status.vacc = data.vAcc / 1000  # meters
        self.__app.gnss_status.pdop = data.pDOP
        self.__app.gnss_status.sip = data.numSV
        self.__app.gnss_status.speed = data.gSpeed / 1000  # m/s
        self.__app.gnss_status.track = data.headMot
        self.__app.gnss_status.fix = fix2desc("NAV-PVT", data.fixType)
        self.__app.gnss_status.diff_corr = data.difSoln
        if data.lastCorrectionAge != 0:
            self.__app.gnss_status.diff_age = corrage2int(data.lastCorrectionAge)

    def _process_NAV_VELNED(self, data: UBXMessage):
        """
        Process NAV-VELNED sentence - Velocity Solution in North East Down format.

        :param UBXMessage data: NAV-VELNED parsed message
        """

        self.__app.gnss_status.track = data.heading
        self.__app.gnss_status.speed = data.gSpeed / 100  # m/s

    def _process_NAV_SAT(self, data: UBXMessage):
        """
        Process NAV-SAT sentences - Space Vehicle Information.

        NB: For consistency with NMEA GSV and UBX NAV-SVINFO message types,
        this uses the NMEA SVID numbering range for GLONASS satellites
        (65 - 96) rather than the Slot ID (1-24) by default.
        To change this, set the GLONASS_NMEA flag in globals.py to False.

        :param UBXMessage data: NAV-SAT parsed message
        """

        self.gsv_data = []
        num_siv = int(data.numSvs)

        for i in range(num_siv):
            idx = f"_{i+1:02d}"
            gnssId = getattr(data, "gnssId" + idx)
            svid = getattr(data, "svId" + idx)
            # use NMEA GLONASS numbering (65-96) rather than slotID (1-24)
            if gnssId == 6 and svid < 25 and svid != 255 and GLONASS_NMEA:
                svid += 64
            elev = getattr(data, "elev" + idx)
            azim = getattr(data, "azim" + idx)
            cno = getattr(data, "cno" + idx)
            if cno == 0 and not self.__app.frm_settings.show_unused:  # omit unused sats
                continue
            self.gsv_data.append((gnssId, svid, elev, azim, cno))

        self.__app.gnss_status.siv = len(self.gsv_data)
        self.__app.gnss_status.gsv_data = self.gsv_data

    def _process_NAV_STATUS(self, data: UBXMessage):
        """
        Process NAV-STATUS sentences - Status Information.

        :param UBXMessage data: NAV-STATUS parsed message
        """

        self.__app.gnss_status.diff_corr = data.diffSoln
        # self.__app.gnss_status.diff_age = "<60"
        self.__app.gnss_status.fix = fix2desc("NAV-STATUS", data.gpsFix)

    def _process_NAV_SVINFO(self, data: UBXMessage):
        """
        Process NAV-SVINFO sentences - Space Vehicle Information.

        NB: Since UBX Gen8 this message is deprecated in favour of NAV-SAT

        :param UBXMessage data: NAV-SVINFO parsed message
        """

        self.gsv_data = []
        num_siv = int(data.numCh)

        for i in range(num_siv):
            idx = f"_{i+1:02d}"
            svid = getattr(data, "svid" + idx)
            gnssId = svid2gnssid(svid)  # derive gnssId from svid
            elev = getattr(data, "elev" + idx)
            azim = getattr(data, "azim" + idx)
            cno = getattr(data, "cno" + idx)
            if cno == 0 and not self.__app.frm_settings.show_unused:  # omit unused sats
                continue
            self.gsv_data.append((gnssId, svid, elev, azim, cno))

        self.__app.gnss_status.gsv_data = self.gsv_data

    def _process_NAV_SOL(self, data: UBXMessage):
        """
        Process NAV-SOL sentence - Navigation Solution.

        :param UBXMessage data: NAV-SOL parsed message
        """

        self.__app.gnss_status.pdop = data.pDOP
        self.__app.gnss_status.sip = data.numSV
        self.__app.gnss_status.fix = fix2desc("NAV-SOL", data.gpsFix)

    def _process_NAV_DOP(self, data: UBXMessage):
        """
        Process NAV-DOP sentence - Dilution of Precision.

        :param UBXMessage data: NAV-DOP parsed message
        """

        self.__app.gnss_status.pdop = data.pDOP
        self.__app.gnss_status.hdop = data.hDOP
        self.__app.gnss_status.vdop = data.vDOP

    def _process_HNR_PVT(self, data: UBXMessage):
        """
        Process HNR-PVT sentence -  High Rate Navigation position velocity time solution.

        :param UBXMessage data: HNR-PVT parsed message
        """

        self.__app.gnss_status.utc = itow2utc(data.iTOW)  # datetime.time
        self.__app.gnss_status.lat = data.lat
        self.__app.gnss_status.lon = data.lon
        self.__app.gnss_status.alt = data.hMSL / 1000  # meters
        self.__app.gnss_status.hacc = data.hAcc / 1000  # meters
        self.__app.gnss_status.vacc = data.vAcc / 1000  # meters
        self.__app.gnss_status.speed = data.gSpeed / 1000  # m/s
        self.__app.gnss_status.track = data.headMot
        self.__app.gnss_status.fix = fix2desc("HNR-PVT", data.gpsFix)
        self.__app.gnss_status.diff_corr = data.diffSoln

    def _process_RXM_RTCM(self, data: UBXMessage):
        """
        Process RXM-RTCM sentences - Status Information.

        :param UBXMessage data: RXM-RTCM parsed message
        """

        self.__app.gnss_status.diff_corr = data.msgUsed >= 1
        self.__app.gnss_status.diff_station = data.refStation
