"""
sbf_handler.py

SBF Protocol handler - handles all incoming SBF messages

Parses individual SBF (proprietary Septentrio binary) messages
(using pysbf2 library) and adds selected attribute values to
the app.gnss_status data dictionary. This dictionary is then
used to periodically update the various user-selectable widget panels.

Created on 19 May 2025

:author: semuadmin (Steve Smith)
:copyright: 2020 semuadmin
:license: BSD 3-Clause
"""

import logging
from math import degrees
from time import time

from pynmeagps import bearing, ecef2llh, haversine, llh2ecef
from pysbf2 import SBFMessage, itow2utc

from pygpsclient.dialog_state import DLGTTTY
from pygpsclient.globals import ASCII, BSR
from pygpsclient.helpers import fix2desc, hdg2yaw, sbfsvid2svid
from pygpsclient.strings import NA

CARRSOLN = {
    4: 2,  # RTK-FIXED
    7: 2,  # RTK-FIXED
    5: 1,  # RTK-FLOAT
    8: 1,  # RTK-FLOAT
    2: 3,  # RTK
    6: 4,  # SBAS
    10: 5,  # PPP
}
DNUL = -20000000000  # -2 * 1e10
DNUS = 65535


class SBFHandler:
    """
    SBFHandler class
    """

    def __init__(self, app):
        """
        Constructor.

        :param Tk app: reference to main tkinter application
        """

        self.__app = app  # Reference to main application class
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

        try:
            if raw_data is None:
                return
            if self.__app.gnss_status.version_data["hwversion"] == NA:
                self.__app.gnss_status.version_data["hwversion"] = "Septentrio"
                self.__app.set_device_label(
                    self.__app.gnss_status.version_data["hwversion"]
                )
            # self.logger.debug(f"data received {parsed_data.identity}")
            if parsed_data.identity in ("PVTGeodetic", "NavGeod"):
                self._process_PVT_geodetic(parsed_data)
            elif parsed_data.identity in ("PVTCartesian", "NavCart"):
                self._process_PVT_cartesian(parsed_data)
            elif parsed_data.identity == "DOP":
                self._process_DOP(parsed_data)
            elif parsed_data.identity == "SatVisibility":
                self._process_SatVisibility(parsed_data)
            elif parsed_data.identity == "ReceiverStatus":
                self._process_ReceiverStatus(parsed_data)
            elif parsed_data.identity == "ReceiverSetup":
                self._process_ReceiverSetup(parsed_data)
            elif parsed_data.identity == "AttEuler":
                self._process_AttEuler(parsed_data)
            elif parsed_data.identity in ("BaseVectorGeod", "BaseVectorCart"):
                self._process_BaseVector(parsed_data)
        except Exception as err:  # pylint: disable=broad-exception-caught
            self.logger.exception(err)

    def _process_PVT_geodetic(self, data: SBFMessage):
        """
        Process PVT Geodetic sentence - Position Velocity Track Geodetic.

        :param SBFMessage data: PVT Geodetic message
        """

        self.__app.gnss_status.utc = itow2utc(data.TOW)  # datetime.time
        if data.Latitude != DNUL:
            self.__app.gnss_status.lat = degrees(data.Latitude)
        if data.Longitude != DNUL:
            self.__app.gnss_status.lon = degrees(data.Longitude)
        if data.Height != DNUL:  # HAE
            self.__app.gnss_status.hae = data.Height  # meters
        if DNUL not in (data.Height, data.Undulation):  # SEP
            self.__app.gnss_status.alt = data.Height - data.Undulation  # meters
        self._process_PVT_common(data)

    def _process_PVT_cartesian(self, data: SBFMessage):
        """
        Process PVT Cartesian sentence - Position Velocity Track Cartesian.

        :param SBFMessage data: PVT Cartesian message
        """

        self.__app.gnss_status.utc = itow2utc(data.TOW)  # datetime.time
        if DNUL not in (data.X, data.Y, data.Z):
            lat, lon, hae = ecef2llh(data.X, data.Y, data.Z)
            self.__app.gnss_status.lat = lat
            self.__app.gnss_status.lon = lon
            self.__app.gnss_status.hae = hae
            if data.Undulation != DNUL:  # SEP
                self.__app.gnss_status.alt = hae - data.Undulation  # meters
        self._process_PVT_common(data)

    def _process_PVT_common(self, data: SBFMessage):
        """
        Process common elements of PVT Geodetic and Cartesian messages.

        :param SBFMessage data: PVT Geodetic/Cartesian message
        """

        if data.NrSV != 255:
            self.__app.gnss_status.sip = data.NrSV
        if data.COG != DNUL:
            self.__app.gnss_status.track = data.COG
        self.__app.gnss_status.fix = fix2desc("PVTGeodetic", data.Type)
        if data.MeanCorrAge != 0:
            self.__app.gnss_status.diff_age = data.MeanCorrAge  # seconds
        self.__app.gnss_status.diff_station = data.ReferenceID
        if data.identity in ("NavCart", "NavGeod"):
            if data.PosHAcc != DNUS / 1000:
                self.__app.gnss_status.hacc = data.PosHAcc  # meters
            if data.PosVAcc != DNUS / 1000:
                self.__app.gnss_status.vacc = data.PosVAcc  # meters
            if data.PDOP != 0:
                self.__app.gnss_status.pdop = data.PDOP
        else:  # PVTCartesian, PVTGeodetic
            if data.HAccuracy != DNUS / 100:
                self.__app.gnss_status.hacc = data.HAccuracy  # meters
            if data.VAccuracy != DNUS / 100:
                self.__app.gnss_status.vacc = data.VAccuracy  # meters

    def _process_DOP(self, data: SBFMessage):
        """
        Process DOP sentence - Degrees of Precision.

        :param SBFMessage data: DOP message
        """

        if data.PDOP != 0:
            self.__app.gnss_status.pdop = data.PDOP
        if data.HDOP != 0:
            self.__app.gnss_status.hdop = data.HDOP
        if data.VDOP != 0:
            self.__app.gnss_status.vdop = data.VDOP
        if data.TDOP != 0:
            self.__app.gnss_status.tdop = data.TDOP

    def _process_SatVisibility(self, data: SBFMessage):
        """
        Process SatVisibility sentence - Satellite visibility.

        :param SBFMessage data: SatVisibility message
        """

        self.__app.gnss_status.gsv_data = {}
        num_siv = int(data.N)
        now = time()

        for i in range(num_siv):
            idx = f"_{i+1:02d}"
            gnssId, svid = sbfsvid2svid(getattr(data, "SVID" + idx))
            elev = getattr(data, "Elevation" + idx)
            azim = getattr(data, "Azimuth" + idx)
            self.__app.gnss_status.gsv_data[(gnssId, svid)] = (
                gnssId,
                svid,
                elev,
                azim,
                -30,  # NB: nominal value as cno not provided
                now,
            )

        self.__app.gnss_status.siv = len(self.__app.gnss_status.gsv_data)

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

        hwver = (
            data.ProductName.decode(ASCII, errors=BSR)
            .replace("\x00", "")
            .replace("amosaic", "mosaic")
            .replace("0mosaic", "mosaic")
        )
        self.__app.gnss_status.version_data["hwversion"] = f"Septentrio {hwver}"
        self.__app.gnss_status.version_data["swversion"] = (
            data.GNSSFWVersion.decode(ASCII, errors=BSR)
            .replace("\x00", "")
            .replace("Unknown", "")
        )
        self.__app.gnss_status.version_data["romversion"] = (
            data.RxVersion.decode(ASCII, errors=BSR)
            .replace("\x00", "")
            .replace("Unknown", "")
        )
        self.__app.gnss_status.version_data["gnss"] = NA
        self.__app.set_device_label(self.__app.gnss_status.version_data["hwversion"])

    def _process_AttEuler(self, data: SBFMessage):
        """
        Process AttEuler sentence.

        :param SBFMessage data: AttEuler message
        """

        ims = self.__app.gnss_status.imu_data
        ims["source"] = data.identity
        dnu = False
        if data.Roll == DNUL:
            ims["roll"] = 0
            dnu = True
        else:
            ims["roll"] = round(data.Roll, 4)
        if data.Pitch == DNUL:
            ims["pitch"] = 0
            dnu = True
        else:
            ims["pitch"] = round(data.Pitch, 4)
        if data.Heading == DNUL:
            ims["yaw"] = 0
            dnu = True
        else:
            ims["yaw"] = round(hdg2yaw(data.Heading), 4)
        ims["status"] = "DONOTUSE" if dnu else f"INFO: {data.Info}"

    def _process_BaseVector(self, data: SBFMessage):
        """
        Process BaseVector sentence - Relative position of rover.

        :param SBFMessage data: BaseVector parsed message
        """

        if self.__app.configuration.get("relposnedsettings_d")[
            "source_s"
        ] != "SBF BaseVector" or (
            self.__app.gnss_status.lat == 0 and self.__app.gnss_status.lon == 0
        ):
            return

        X1, Y1, Z1 = llh2ecef(
            self.__app.gnss_status.lat,
            self.__app.gnss_status.lon,
            self.__app.gnss_status.hae,
        )

        self.__app.gnss_status.rel_pos_source = "SBF BaseVector"
        self.__app.gnss_status.acc_heading = 0
        self.__app.gnss_status.acc_length = 0

        if data.N == 0:
            self.__app.gnss_status.rel_pos_heading = 0
            self.__app.gnss_status.rel_pos_length = 0
            self.__app.gnss_status.rel_pos_flags = [0] * 9
            return

        if data.identity == "BaseVectorGeod":
            if DNUL in (data.DeltaEast_01, data.DeltaNorth_01, data.DeltaUp_01):
                return
            X2, Y2, Z2 = (
                data.DeltaEast_01 + X1,
                data.DeltaNorth_01 + Y1,
                data.DeltaUp_01 + Z1,
            )
        else:  # BaseVectorCart
            if DNUL in (data.DeltaX_01, data.DeltaY_01, data.DeltaZ_01):
                return
            X2, Y2, Z2 = data.DeltaX_01 + X1, data.DeltaY_01 + Y1, data.DeltaZ_01 + Z1

        lat2, lon2, _ = ecef2llh(X2, Y2, Z2)
        distance = haversine(
            self.__app.gnss_status.lat, self.__app.gnss_status.lon, lat2, lon2
        )
        heading = bearing(
            lat2, lon2, self.__app.gnss_status.lat, self.__app.gnss_status.lon
        )
        if data.identity == "BaseVectorGeod":
            heading = (heading - 90) % 360
        self.__app.gnss_status.rel_pos_heading = heading
        self.__app.gnss_status.rel_pos_length = distance * 100000  # cm
        carrsoln = CARRSOLN.get(data.Type_01, 0)
        self.__app.gnss_status.rel_pos_flags = [
            int(data.Error_01 == 0),  # gnssFixOK,
            int(data.Type_01 in (2, 4, 5, 6, 7, 8, 10)),  # diffSoln,
            int(data.Error_01 == 0),  # relPosValid,
            carrsoln,  # carrSoln,
            int(data.Type_01 in (7, 8)),  # isMoving,
            0,  # refPosMiss,
            0,  # refObsMiss,
            int(data.Error_01 == 0),  # relPosHeadingValid,
            0,  # relPosNormalized,
        ]

    def process_lif(self, data: str):
        """
        Parse output of lstInternalFile,identification poll,
        - an XML construct of hardware and firmware data.

        :param str data: ASCII text response
        """

        def gettag(line: str, tag: str) -> str:
            st = line.find(tag) + len(tag) + 1
            return line[st : line.find('"', st)]

        hw = rom = sw = fw = ""
        for line in data.split("\n"):
            tag = "<hwplatform product="
            if tag in line:
                hw = "Septentrio " + gettag(line, tag)
            tag = "name="
            if tag in line:
                rom = gettag(line, tag)
            tag = "gnssfw version="
            if tag in line:
                sw = gettag(line, tag)
            tag = "<firmware version="
            if tag in line:
                fw = gettag(line, tag)
                fw += " " + gettag(line, "date=")

        if hw != "":
            self.__app.gnss_status.version_data["hwversion"] = hw
            self.__app.set_device_label(
                self.__app.gnss_status.version_data["hwversion"]
            )
        if fw != "":
            self.__app.gnss_status.version_data["fwversion"] = fw
        if sw != "":
            self.__app.gnss_status.version_data["swversion"] = sw
        if rom != "":
            self.__app.gnss_status.version_data["romversion"] = rom
        if self.__app.dialog(DLGTTTY):
            self.__app.dialog(DLGTTTY).frm_device_info.reset()
