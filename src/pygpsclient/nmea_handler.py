"""
nmea_handler.py

NMEA Protocol handler - handles all incoming standard and
proprietary NMEA sentences.

Parses individual NMEA sentences (using pynmeagps library)
and adds selected attribute values to the app.gnss_status
data dictionary. This dictionary is then used to periodically
update the various user-selectable widgets.

Created on 30 Sep 2020

:author: semuadmin
:copyright: 2020 SEMU Consulting
:license: BSD 3-Clause
"""

import logging
from math import degrees
from time import time

from pynmeagps import NMEAMessage
from pyubx2 import itow2utc

from pygpsclient.globals import SAT_EXPIRY
from pygpsclient.helpers import fix2desc, kmph2ms, knots2ms, svid2gnssid
from pygpsclient.strings import DLGTNMEA


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
        self.__master = self.__app.appmaster  # Reference to root class (Tk)
        self.logger = logging.getLogger(__name__)

        self._raw_data = None
        self._parsed_data = None
        # Holds array of current satellites in view from NMEA GSV sentences
        self.gsv_data = {}
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
            # self.logger.debug(f"data received {parsed_data.identity}")
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
            # proprietary GPS Lat/Lon & Acc
            elif parsed_data.msgID == "UBX" and parsed_data.msgId == "03":
                self._process_UBX03(parsed_data)
            elif parsed_data.msgID == "QTMVERNO":  # LG290P hardware version
                self._process_QTMVERNO(parsed_data)
            elif parsed_data.msgID == "QTMVER":  # LG290P hardware version
                self._process_QTMVER(parsed_data)
            elif parsed_data.msgID == "QTMPVT":  # LG290P pos, vel, trk
                self._process_QTMPVT(parsed_data)
            elif parsed_data.msgID[0:3] == "QTM" and hasattr(parsed_data, "status"):
                self._process_QTMACK(parsed_data)
            elif parsed_data.msgID == "QTMSVINSTATUS":  # LG290P SVIN status
                self._process_QTMSVINSTATUS(parsed_data)
            elif parsed_data.msgID == "FMI":  # Feyman IM19 IMU status
                self._process_FMI(parsed_data)

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
        if hasattr(data, "posMode"):  # NMEA >= 2.3
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
        self.__app.gnss_status.hae = data.sep + data.alt
        self.__app.gnss_status.hdop = data.HDOP
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
        self.__app.gnss_status.vdop = data.VDOP
        # doesn't support RTK fix modes so ignored...
        # self.__app.gnss_status.fix = fix2desc("GSA", data.navMode)

    def _process_GSV(self, data: NMEAMessage):
        """
        Process GSV sentences - GPS Satellites in View
        These come in batches of 1-4 sentences, each containing the positions
        of up to 4 satellites (16 satellites in total).
        Modern receivers can send multiple batches corresponding to different
        GNSS constellations (GPS 1-32, SBAS 33-64, GLONASS 65-96 etc.).

        This function collates all received GSV data into a single gsv_data array,
        removing any signals that have not been seen for more than a specified
        number of seconds (set in SAT_EXPIRY). This array is then used to
        populate the graphview and skyview widgets.

        :param pynmeagps.NMEAMessage data: parsed GSV sentence
        """

        show_unused = self.__app.configuration.get("unusedsat_b")
        self.gsv_data = {}
        gsv_dict = {}
        now = time()
        if data.talker == "GA":
            gnss = 2  # Galileo
        elif data.talker in ("GB", "BD"):
            gnss = 3  # Beidou (only available in MMEA 4.11)
        elif data.talker == "GL":
            gnss = 6  # GLONASS
        elif data.talker == "GI":
            gnss = 7  # NAVIC
        else:
            gnss = 0  # GPS, SBAS, QZSS

        for i in range(4):
            idx = f"_{i+1:02d}"
            svid = getattr(data, "svid" + idx, "")
            if svid != "":
                key = f"{gnss}-{svid}"
                gsv_dict[key] = (
                    gnss,
                    svid,
                    getattr(data, "elv" + idx),
                    getattr(data, "az" + idx),
                    str(getattr(data, "cno" + idx)),
                    now,
                )

        for key, value in gsv_dict.items():
            self.gsv_log[key] = value

        for key, (gnssId, svid, elev, azim, cno, lastupdate) in self.gsv_log.items():
            if cno in ("", "0", 0) and not show_unused:  # omit unused sats
                continue
            if now - lastupdate < SAT_EXPIRY:  # expire passed sats
                self.gsv_data[key] = (gnssId, svid, elev, azim, cno)

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
        Process UXB00 sentence - Lat/Long position data.

        :param pynmeagps.NMEAMessage data: parsed UBX,00 sentence
        """

        self.__app.gnss_status.lat = data.lat
        self.__app.gnss_status.lon = data.lon
        # self.__app.gnss_status.alt = data.altRef height above datum, not SL
        self.__app.gnss_status.speed = data.SOG
        self.__app.gnss_status.track = data.COG
        self.__app.gnss_status.hdop = data.HDOP
        self.__app.gnss_status.vdop = data.VDOP
        self.__app.gnss_status.hacc = data.hAcc
        self.__app.gnss_status.vacc = data.vAcc
        self.__app.gnss_status.sip = data.numSVs

    def _process_UBX03(self, data: NMEAMessage):
        """
        Process UXB03 sentence - NMEA Satellite Status.

        NB: this message appears to use the legacy NMEA 2.n
        SVID numbering scheme. This may conflict with GSV
        satellite data if both message types are enabled.

        :param pynmeagps.NMEAMessage data: parsed UBX,03 sentence
        """
        # pylint: disable=consider-using-dict-items

        show_unused = self.__app.configuration.get("unusedsat_b")
        self.gsv_data = {}
        for i in range(data.numSv):
            idx = f"_{i+1:02d}"
            svid = getattr(data, "svid" + idx)
            gnss = svid2gnssid(svid)
            elev = getattr(data, "ele" + idx)
            azim = getattr(data, "azi" + idx)
            cno = str(getattr(data, "cno" + idx))
            # fudge to make PUBX03 svid numbering consistent with GSV
            if gnss == 2 and svid > 210:  # Galileo
                svid -= 210
            if gnss == 3 and svid > 32:  # Beidou
                svid -= 32
            if cno in ("", "0", 0) and not show_unused:  # omit unused sats
                continue
            self.gsv_data[f"{gnss}-{svid}"] = (gnss, svid, elev, azim, cno)

        self.__app.gnss_status.siv = len(self.gsv_data)
        self.__app.gnss_status.gsv_data = self.gsv_data

    def _process_QTMVERNO(self, data: NMEAMessage):
        """
        Process QTMVERNO sentence - Quectel Hardware Version.

        :param pynmeagps.NMEAMessage data: parsed QTMVERNO sentence
        """

        verdata = {}
        verdata["swversion"] = "N/A"
        verdata["hwversion"] = data.verstr
        verdata["fwversion"] = f"{data.builddate}-{data.buildtime}"
        verdata["romversion"] = "N/A"
        self.__app.gnss_status.version_data = verdata

        if self.__app.dialog(DLGTNMEA) is not None:
            self.__app.dialog(DLGTNMEA).update_pending(data)

    def _process_QTMVER(self, data: NMEAMessage):
        """
        Process QTMVER sentence - Quectel Hardware Version.
        This gets sent whenever receiver is restarted.

        :param pynmeagps.NMEAMessage data: parsed QTMVER sentence
        """

        self._process_QTMVERNO(data)

        # notify socket server frame that receiver has restarted...
        if self.__app.frm_settings.frm_socketserver is not None:
            self.__app.frm_settings.frm_socketserver.update_pending(data)

    def _process_QTMPVT(self, data: NMEAMessage):
        """
        Process QTMPVT sentence - Quectel PVT.

        :param pynmeagps.NMEAMessage data: parsed QTMPVT sentence
        """

        self.__app.gnss_status.utc = itow2utc(data.tow)
        self.__app.gnss_status.lat = data.lat
        self.__app.gnss_status.lon = data.lon
        self.__app.gnss_status.speed = data.spd
        self.__app.gnss_status.track = data.hdg
        self.__app.gnss_status.hdop = data.hdop
        self.__app.gnss_status.pdop = data.pdop
        self.__app.gnss_status.alt = data.alt
        self.__app.gnss_status.hae = data.sep + data.alt
        self.__app.gnss_status.sip = data.numsv
        self.__app.gnss_status.fix = ["NO FIX", "NO FIX", "2D", "3D"][data.fixtype]

    def _process_QTMACK(self, data: NMEAMessage):
        """
        Process QTM acknowledgement.

        :param pynmeagps.NMEAMessage data: parsed QTM*acknowledgement
        """

        if self.__app.dialog(DLGTNMEA) is not None:
            self.__app.dialog(DLGTNMEA).update_pending(data)

    def _process_QTMSVINSTATUS(self, data: NMEAMessage):
        """
        Process QTMSVINSTATUS sentence - Survey In Status.

        :param NMEAMessage data:QTMSVINSTATUS parsed message
        """

        valid = 1 if data.valid == 2 else 0
        active = data.valid == 1
        if self.__app.frm_settings.frm_socketserver is not None:
            self.__app.frm_settings.frm_socketserver.svin_countdown(
                data.obs, valid, active
            )

    def _process_FMI(self, data: NMEAMessage):
        """
        Process GMFMI sentence - Feyman IM19 IMU status.

        Roll, Pitch and Yaw are in radians.

        :param NMEAMessage data: GPFMI message
        """

        try:  # cater for pynmeagps<1.0.50
            self.__app.gnss_status.utc = data.time  # datetime.time
            self.__app.gnss_status.lat = data.lat
            self.__app.gnss_status.lon = data.lon
            self.__app.gnss_status.alt = data.alt
            self.__app.gnss_status.sip = data.numSV
            self.__app.gnss_status.diff_age = data.diffAge
            ims = self.__app.gnss_status.imu_data
            ims["source"] = data.identity
            ims["roll"] = round(degrees(data.roll), 4)
            ims["pitch"] = round(degrees(data.pitch), 4)
            ims["yaw"] = round(degrees(data.yaw), 4)
            ims["status"] = data.status
        except (KeyError, AttributeError):
            pass
