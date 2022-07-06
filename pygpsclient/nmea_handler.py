"""
NMEA Protocol handler - handles all incoming standard and proprietary NMEA sentences

Uses pynmea2 library for parsing

Created on 30 Sep 2020

:author: semuadmin
:copyright: SEMU Consulting © 2020
:license: BSD 3-Clause
"""
# pylint: disable=invalid-name

from time import time
from pynmeagps import NMEAMessage
from pygpsclient.globals import SAT_EXPIRY
from pygpsclient.helpers import knots2ms, kmph2ms, fix2desc


class NMEAHandler:
    """
    NMEA handler class.
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
        )  # Holds array of current satellites in view from NMEA GSV sentences
        self.gsv_log = {}  # Holds cumulative log of all satellites seen

    def process_data(self, raw_data: bytes, parsed_data: object):
        """
        Process relevant NMEA message types

        :param bytes raw_data: raw_data
        :param NMEAMessage parsed_data: parsed data
        """
        # pylint: disable=no-member

        try:
            if raw_data is None:
                return

            if parsed_data.msgID == "RMC":  # Recommended minimum data for GPS
                self._process_RMC(parsed_data)
            elif parsed_data.msgID == "GGA":  # GPS Fix Data
                self._process_GGA(parsed_data)
            elif parsed_data.msgID == "GLL":  # GPS Lat Lon Data
                self._process_GLL(parsed_data)
            elif parsed_data.msgID == "GNS":  # GNSS Fix Data
                self._process_GNS(parsed_data)
            elif parsed_data.msgID == "GSA":  # GPS DOP (Dilution of Precision)
                self._process_GSA(parsed_data)
            elif parsed_data.msgID == "VTG":  # GPS Vector track and Speed over Ground
                self._process_VTG(parsed_data)
            elif parsed_data.msgID == "GSV":  # GPS Satellites in View
                self._process_GSV(parsed_data)
            elif parsed_data.msgID == "ZDA":  # ZDA Time
                self._process_ZDA(parsed_data)
            # proprietary GPS Lat/Lon & Acc
            elif parsed_data.msgID == "UBX" and parsed_data.msgId == "00":
                self._process_UBX00(parsed_data)

        except ValueError:
            pass

    def _process_RMC(self, data: NMEAMessage):
        """
        Process RMC sentence - Recommended minimum data for GPS.

        :param pynmeagps.NMEAMessage data: parsed RMC sentence
        """

        self.__app.gnss_status.utc = data.time  # datetime.time
        self.__app.gnss_status.lat = data.lat
        self.__app.gnss_status.lon = data.lon
        self.__app.gnss_status.fix = fix2desc("RMC", data.posMode)
        # only works for NMEA 4.10 and later...
        # if data.posMode in ["F", "R"]:
        #     self.__app.gnss_status.diff_corr = 1
        if data.spd != "":
            self.__app.gnss_status.speed = knots2ms(data.spd)  # convert to m/s
        if data.cog != "":
            self.__app.gnss_status.track = data.cog

    def _process_GGA(self, data: NMEAMessage):
        """
        Process GGA sentence - GPS Fix Data.

        :param pynmeagps.NMEAMessage data: parsed GGA sentence
        """

        self.__app.gnss_status.utc = data.time  # datetime.time
        self.__app.gnss_status.sip = data.numSV
        self.__app.gnss_status.lat = data.lat
        self.__app.gnss_status.lon = data.lon
        self.__app.gnss_status.alt = data.alt
        self.__app.gnss_status.sep = data.sep
        self.__app.gnss_status.fix = fix2desc("GGA", data.quality)
        self.__app.gnss_status.diff_corr = 0 if data.diffAge == "" else 1
        self.__app.gnss_status.diff_age = data.diffAge
        self.__app.gnss_status.diff_station = data.diffStation

    def _process_GLL(self, data: NMEAMessage):
        """
        Process GLL sentence - GPS Lat Lon.

        :param pynmeagps.NMEAMessage data: parsed GLL sentence
        """

        self.__app.gnss_status.utc = data.time  # datetime.time
        self.__app.gnss_status.lat = data.lat
        self.__app.gnss_status.lon = data.lon
        self.__app.gnss_status.fix = fix2desc("GLL", data.posMode)
        # only works for NMEA 4.10 and later...
        # self.__app.gnss_status.diff_corr = 1 if data.posMode == "D" else 0

    def _process_GNS(self, data: NMEAMessage):
        """
        Process GNS sentence - GNSS Fix

        :param pynmeagps.NMEAMessage data: parsed GNS sentence
        """

        self.__app.gnss_status.utc = data.time  # datetime.time
        self.__app.gnss_status.lat = data.lat
        self.__app.gnss_status.lon = data.lon
        self.__app.gnss_status.sip = data.numSV
        self.__app.gnss_status.hdop = data.HDOP
        self.__app.gnss_status.alt = data.alt
        # GNS has four posMode values, one for each GNSS
        # for dgps status, we pick the 'best' one
        posMode = "N"
        for val in ["R", "F", "D", "E", "A"]:
            if data.posMode.find(val) >= 0:
                posMode = val
                break
        # only works for NMEA 4.10 and later...
        # if posMode in ["R", "F"]:
        #     self.__app.gnss_status.diff_corr = 1
        self.__app.gnss_status.diff_age = data.diffAge
        self.__app.gnss_status.diff_corr = 0 if data.diffAge == "" else 1
        self.__app.gnss_status.diff_station = data.diffStation
        self.__app.gnss_status.fix = fix2desc("GNS", posMode)

    def _process_GSA(self, data: NMEAMessage):
        """
        Process GSA sentence - GPS DOP (Dilution of Precision) and active satellites.

        :param pynmeagps.NMEAMessage data: parsed GSA sentence
        """

        self.__app.gnss_status.pdop = data.PDOP
        self.__app.gnss_status.hdop = data.HDOP
        self.__app.gnss_status.vvdop = data.VDOP
        # doesn't support RTK fix modes so ignored...
        # self.__app.gnss_status.fix = fix2desc("GSA", data.navMode)

    def _process_GSV(self, data: NMEAMessage):
        """
        Process GSV sentences - GPS Satellites in View
        These come in batches of 1-4 sentences, each containing the positions
        of up to 4 satellites (16 satellites in total).
        Modern receivers can send multiple batches corresponding to different
        GNSS constellations (GPS 1-32, SBAS 33-64, GLONASS 65-96 etc.).

        :param pynmeagps.NMEAMessage data: parsed GSV sentence
        """
        # pylint: disable=consider-using-dict-items

        show_unused = self.__app.frm_settings.show_unused
        self.gsv_data = []
        gsv_dict = {}
        now = time()
        if data.talker == "GA":
            gnss = 2  # Galileo
        elif data.talker == "GB":
            gnss = 3  # Beidou (only available in MMEA 4.11)
        elif data.talker == "GL":
            gnss = 6  # GLONASS
        else:
            gnss = 0  # GPS, SBAS, QZSS

        try:
            if data.svid_01 != "":
                svid = data.svid_01
                key = str(gnss) + "-" + str(svid)
                gsv_dict[key] = (
                    gnss,
                    svid,
                    data.elv_01,
                    data.az_01,
                    str(data.cno_01),
                    now,
                )
            if data.svid_02 != "":
                svid = data.svid_02
                key = str(gnss) + "-" + str(svid)
                gsv_dict[key] = (
                    gnss,
                    svid,
                    data.elv_02,
                    data.az_02,
                    str(data.cno_02),
                    now,
                )
            if data.svid_03 != "":
                svid = data.svid_03
                key = str(gnss) + "-" + str(svid)
                gsv_dict[key] = (
                    gnss,
                    svid,
                    data.elv_03,
                    data.az_03,
                    str(data.cno_03),
                    now,
                )
            if data.svid_04 != "":
                svid = data.svid_04
                key = str(gnss) + "-" + str(svid)
                gsv_dict[key] = (
                    gnss,
                    svid,
                    data.elv_04,
                    data.az_04,
                    str(data.cno_04),
                    now,
                )
        except AttributeError:
            pass

        for key in gsv_dict:
            self.gsv_log[key] = gsv_dict[key]

        for key in self.gsv_log:
            gnssId, svid, elev, azim, snr, lastupdate = self.gsv_log[key]
            if snr in ("", "0", 0) and not show_unused:  # omit unused sats
                continue
            if now - lastupdate < SAT_EXPIRY:  # expire passed sats
                self.gsv_data.append((gnssId, svid, elev, azim, snr))

        self.__app.gnss_status.siv = len(self.gsv_data)
        self.__app.gnss_status.gsv_data = self.gsv_data

    def _process_VTG(self, data: NMEAMessage):
        """
        Process VTG sentence - GPS Vector track and Speed over the Ground.

        :param pynmeagps.NMEAMessage data: parsed VTG sentence
        """

        self.__app.gnss_status.track = data.cogt
        if data.sogk is not None:
            self.__app.gnss_status.speed = kmph2ms(data.sogk)  # convert to m/s
        self.__app.gnss_status.fix = fix2desc("VTG", data.posMode)
        # only works for NMEA 4.10 and later...
        # self.__app.gnss_status.diff_corr = 1 if data.posMode == "D" else 0

    def _process_ZDA(self, data: NMEAMessage):
        """
        Process ZDA sentence - GPS Time.

        :param pynmeagps.NMEAMessage data: parsed ZDA sentence
        """

        self.__app.gnss_status.utc = data.time

    def _process_UBX00(self, data: NMEAMessage):
        """
        Process UXB00 sentence - GPS Vector track and Speed over the Ground.

        :param pynmeagps.NMEAMessage data: parsed UBX,00 sentence
        """

        self.__app.gnss_status.lat = data.lat
        self.__app.gnss_status.lon = data.lon
        # self.__app.gnss_status.alt = data.altRef height above datum, not SL
        self.__app.gnss_status.speed = data.SOG
        self.__app.gnss_status.track = data.COG
        self.__app.gnss_status.pdop = data.PDOP
        self.__app.gnss_status.hdop = data.HDOP
        self.__app.gnss_status.vdop = data.VDOP
        self.__app.gnss_status.hacc = data.hAcc
        self.__app.gnss_status.vacc = data.vAcc
        self.__app.gnss_status.sip = data.numSVs
