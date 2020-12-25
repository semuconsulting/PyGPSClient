"""
NMEA Protocol handler - handles all incoming standard and proprietary NMEA sentences

Uses pynmea2 library for parsing

Created on 30 Sep 2020

@author: semuadmin
"""
# pylint: disable=invalid-name

from time import time
from datetime import datetime
from pynmea2 import parse as nmea_parse, ParseError, types, RMC, VTG, GSV, GGA, GSA, GLL
from pynmea2.types.proprietary.ubx import UBX00

from .globals import (
    DEVICE_ACCURACY,
    HDOP_RATIO,
    SAT_EXPIRY,
    knots2ms,
    kmph2ms,
    nmea2latlon,
)
from .strings import NMEAVALERROR


class NMEAHandler:
    """
    NMEAHandler class
    """

    def __init__(self, app):
        """
        Constructor.

        :param object app: reference to main tkinter application
        """

        self.__app = app  # Reference to main application class
        self.__master = self.__app.get_master()  # Reference to root class (Tk)

        self._raw_data = None
        self._parsed_data = None
        self._record_track = False
        self.gsv_data = (
            []
        )  # Holds array of current satellites in view from NMEA GSV sentences
        self.gsv_log = {}  # Holds cumulative log of all satellites seen
        self.lon = 0
        self.lat = 0
        self.alt = 0
        self.track = 0
        self.speed = 0
        self.pdop = 0
        self.hdop = 0
        self.vdop = 0
        self.hacc = 0
        self.vacc = 0
        self.utc = ""
        self.sip = 0
        self.fix = "-"

    def process_data(self, data: bytes):
        """
        Process NMEA message type

        :param bytes data: parsed NMEA sentence
        """

        try:
            parsed_data = nmea_parse(data)
        except ParseError:
            # Parsing errors at this point are typically due to NMEA and UBX
            # protocols getting garbled in the input stream. It only happens
            # rarely so we ignore them and carry on.
            return None

        if data or parsed_data:
            self._update_console(data, parsed_data)

        if isinstance(parsed_data, RMC):  # Recommended minimum data for GPS
            self._process_RMC(parsed_data)
        if isinstance(parsed_data, GGA):  # GPS Fix Data
            self._process_GGA(parsed_data)
        if isinstance(parsed_data, GLL):  # GLL Lat Lon Data
            self._process_GLL(parsed_data)
        if isinstance(
            parsed_data, GSA
        ):  # GPS DOP (Dilution of Precision) and active satellites
            self._process_GSA(parsed_data)
        if isinstance(parsed_data, VTG):  # GPS Vector track and Speed over the Ground
            self._process_VTG(parsed_data)
        if isinstance(parsed_data, GSV):  # GPS Satellites in View
            self._process_GSV(parsed_data)
        if isinstance(parsed_data, UBX00):  # GPS Satellites in View
            self._process_UBX00(parsed_data)

        return self._parsed_data

    def _update_console(self, raw_data: bytes, parsed_data: types.talker):
        """
        Write the incoming data to the console in raw or parsed format.

        :param bytes raw_data: raw data
        :param pynmea2.types.talker parsed_data: parsed data
        """

        if self.__app.frm_settings.get_settings()["raw"]:
            self.__app.frm_console.update_console(repr(raw_data))
        else:
            self.__app.frm_console.update_console(repr(parsed_data))

    def _process_RMC(self, data: types.talker):
        """
        Process RMC sentence - Recommended minimum data for GPS.

        :param pynmea2.types.talker data: parsed RMC sentence
        """

        try:
            self.utc = data.timestamp
            (self.lat, self.lon) = nmea2latlon(data)
            if data.spd_over_grnd != "None":
                self.speed = knots2ms(data.spd_over_grnd)  # convert to m/s
            self.track = data.true_course
            self.__app.frm_banner.update_banner(
                time=self.utc,
                lat=self.lat,
                lon=self.lon,
                speed=self.speed,
                track=self.track,
            )

            self.__app.frm_mapview.update_map(self.lat, self.lon, self.hacc)

        except ValueError as err:
            self.__app.set_status(NMEAVALERROR.format(err), "red")

    def _process_GGA(self, data: types.talker):
        """
        Process GGA sentence - GPS Fix Data.

        :param pynmea2.types.talker data: parsed GGA sentence
        """

        try:
            self.utc = data.timestamp
            self.sip = data.num_sats
            (self.lat, self.lon) = nmea2latlon(data)
            self.alt = data.altitude
            self.__app.frm_banner.update_banner(
                time=self.utc, lat=self.lat, lon=self.lon, alt=self.alt, sip=self.sip
            )

            self.__app.frm_mapview.update_map(self.lat, self.lon, self.hacc)

            if (
                self.__app.frm_settings.get_settings()["recordtrack"]
                and self.lat != ""
                and self.lon != ""
            ):
                tim = self.ts2utc(data.timestamp)
                ele = 0 if self.alt == "None" else self.alt
                self.__app.file_handler.add_trackpoint(
                    self.lat, self.lon, ele=ele, time=tim, sat=self.sip
                )
        except ValueError as err:
            self.__app.set_status(NMEAVALERROR.format(err), "red")

    def _process_GLL(self, data: types.talker):
        """
        Process GLL sentence - GPS Lat Lon.

        :param pynmea2.types.talker data: parsed GLL sentence
        """

        try:
            self.utc = data.timestamp
            (self.lat, self.lon) = nmea2latlon(data)
            self.__app.frm_banner.update_banner(
                time=self.utc, lat=self.lat, lon=self.lon
            )

            self.__app.frm_mapview.update_map(self.lat, self.lon, self.hacc)

        except ValueError as err:
            self.__app.set_status(NMEAVALERROR.format(err), "red")

    def _process_GSA(self, data: types.talker):
        """
        Process GSA sentence - GPS DOP (Dilution of Precision) and active satellites.

        :param pynmea2.types.talker data: parsed GSA sentence
        """

        self.pdop = float(data.pdop)
        self.hdop = float(data.hdop)
        self.vdop = float(data.vdop)
        if data.mode_fix_type == "3":
            fix = "3D"
        elif data.mode_fix_type == "2":
            fix = "2D"
        else:
            fix = "NO FIX"

        self.__app.frm_mapview.update_map(self.lat, self.lon, self.hacc)

        self.__app.frm_banner.update_banner(
            dop=self.pdop, hdop=self.hdop, vdop=self.vdop, fix=fix
        )

    def _process_GSV(self, data: types.talker):
        """
        Process GSV sentences - GPS Satellites in View
        These come in batches of 1-4 sentences, each containing the positions
        of up to 4 satellites (16 satellites in total).
        Modern receivers can send multiple batches corresponding to different
        NMEA assigned 'ID' ranges (GPS 1-32, SBAS 33-64, GLONASS 65-96 etc.)

        :param pynmea2.types.talker data: parsed GSV sentence
        """

        show_zero = self.__app.frm_settings.get_settings()["zerosignal"]
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
            if data.sv_prn_num_1 != "":
                svid = data.sv_prn_num_1
                key = str(gnss) + "-" + svid
                gsv_dict[key] = (
                    gnss,
                    svid,
                    data.elevation_deg_1,
                    data.azimuth_1,
                    data.snr_1,
                    now,
                )
            if data.sv_prn_num_2 != "":
                svid = data.sv_prn_num_2
                key = str(gnss) + "-" + svid
                gsv_dict[key] = (
                    gnss,
                    svid,
                    data.elevation_deg_2,
                    data.azimuth_2,
                    data.snr_2,
                    now,
                )
            if data.sv_prn_num_3 != "":
                svid = data.sv_prn_num_3
                key = str(gnss) + "-" + svid
                gsv_dict[key] = (
                    gnss,
                    svid,
                    data.elevation_deg_3,
                    data.azimuth_3,
                    data.snr_3,
                    now,
                )
            if data.sv_prn_num_4 != "":
                svid = data.sv_prn_num_4
                key = str(gnss) + "-" + svid
                gsv_dict[key] = (
                    gnss,
                    svid,
                    data.elevation_deg_4,
                    data.azimuth_4,
                    data.snr_4,
                    now,
                )
        except AttributeError:
            pass

        for key in gsv_dict:
            self.gsv_log[key] = gsv_dict[key]

        for key in self.gsv_log:
            gnssId, svid, elev, azim, snr, lastupdate = self.gsv_log[key]
            if snr in ("", "0", 0) and not show_zero:  # omit sats with zero signal
                continue
            if now - lastupdate < SAT_EXPIRY:  # expire passed satellites
                self.gsv_data.append((gnssId, svid, elev, azim, snr))

        self.__app.frm_satview.update_sats(self.gsv_data)
        self.__app.frm_banner.update_banner(siv=len(self.gsv_data))
        self.__app.frm_graphview.update_graph(self.gsv_data, len(self.gsv_data))

    def _process_VTG(self, data: types.talker):
        """
        Process VTG sentence - GPS Vector track and Speed over the Ground.

        :param pynmea2.types.talker data: parsed VTG sentence
        """

        try:
            self.track = data.true_track
            if data.spd_over_grnd_kmph is not None:
                self.speed = kmph2ms(data.spd_over_grnd_kmph)  # convert to m/s
            self.__app.frm_banner.update_banner(speed=self.speed, track=self.track)
        except ValueError as err:
            self.__app.set_status(NMEAVALERROR.format(err), "red")

    def _process_UBX00(self, data: types.ubx.UBX00):
        """
        Process UXB00 sentence - GPS Vector track and Speed over the Ground.

        :param pynmea2.types.talker data: parsed UBX,00 sentence
        """

        try:
            self.hacc = float(data.h_acc)
            self.vacc = float(data.v_acc)
            self.__app.frm_banner.update_banner(hacc=self.hacc, vacc=self.vacc)

        except ValueError as err:
            self.__app.set_status(NMEAVALERROR.format(err), "red")

    @staticmethod
    def _estimate_acc(dop: float) -> float:
        """
        Derive a graphic indication of positional accuracy (in m) based on the HDOP
        (Horizontal Dilution of Precision) value and the nominal native device
        accuracy (datasheet CEP)

        NB: this is a largely arbitrary estimate - there is no direct correlation
        between HDOP and accuracy based solely on generic NMEA data.
        The NMEA PUBX,00 or UBX NAV-POSLLH message types return an explicit estimate
        of horizontal and vertical accuracy and are the preferred source.

        :param float dop: horizontal dilution of precision
        :return horizontal accuracy
        :rtype float
        """

        return float(dop) * DEVICE_ACCURACY * HDOP_RATIO / 1000

    @staticmethod
    def ts2utc(timestamp) -> str:
        """
        Convert NMEA timestamp to utc time

        :param str timestamp: NMEA timestamp from pynmea2
        :return utc time
        :rtype str
        """

        t = datetime.now()
        s = (
            str(t.year)
            + "-"
            + str(t.month)
            + "-"
            + str(t.day)
            + "T"
            + str(timestamp)
            + "Z"
        )
        return s
