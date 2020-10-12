'''
NMEA Protocol handler - handles all incoming standard and proprietary NMEA sentences

Uses pynmea2 library for parsing

Created on 30 Sep 2020

@author: semuadmin
'''

# pylint: disable=invalid-name
from time import time
from pynmea2 import parse as nmea_parse, ParseError, types, RMC, VTG, GSV, GGA, GSA, GLL
from pynmea2.types.proprietary.ubx import UBX00

from .globals import DEVICE_ACCURACY, HDOP_RATIO, SAT_EXPIRY
from .strings import NMEAVALERROR


class NMEAHandler():
    '''
    NMEAHandler class
    '''

    def __init__(self, app):
        '''
        Constructor.
        '''

        self.__app = app  # Reference to main application class
        self.__master = self.__app.get_master()  # Reference to root class (Tk)

        self._raw_data = None
        self._parsed_data = None
        self.gsv_data = []  # Holds array of current satellites in view from NMEA GSV sentences
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
        self.utc = ''
        self.sip = 0
        self.fix = '-'

    def process_data(self, data: bytes):
        '''
        Process NMEA message type
        '''

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
        if isinstance(parsed_data, GSA):  # GPS DOP (Dilution of Precision) and active satellites
            self._process_GSA(parsed_data)
        if isinstance(parsed_data, VTG):  # GPS Vector track and Speed over the Ground
            self._process_VTG(parsed_data)
        if isinstance(parsed_data, GSV):  # GPS Satellites in View
            self._process_GSV(parsed_data)
        if isinstance(parsed_data, UBX00):  # GPS Satellites in View
            self._process_UBX00(parsed_data)

        return self._parsed_data

    def _update_console(self, raw_data, parsed_data):
        '''
        Write the incoming data to the console in raw or parsed format.
        '''

        if self.__app.frm_settings.get_settings()['raw']:
            self.__app.frm_console.update_console(repr(raw_data))
        else:
            self.__app.frm_console.update_console(repr(parsed_data))

    def _process_RMC(self, data: types.talker):
        '''
        Process RMC sentence - Recommended minimum data for GPS.
        '''

        try:
            self.utc = data.timestamp
            (self.lat, self.lon) = self.nmea2latlon(data)
            self.speed = data.spd_over_grnd
            self.track = data.true_course
            self.__app.frm_banner.update_banner(time=self.utc, lat=self.lat,
                                                lon=self.lon, speed=self.speed,
                                                track=self.track)
            if self.__app.frm_settings.get_settings()['webmap']:
                self.__app.frm_mapview.update_map(lat=self.lat, lon=self.lon, static=False)
            else:
                self.__app.frm_mapview.update_map(lat=self.lat, lon=self.lon, static=True)
        except ValueError as err:
            self.__app.set_status(NMEAVALERROR.format(err), "red")

    def _process_GGA(self, data: types.talker):
        '''
        Process GGA sentence - GPS Fix Data.
        '''

        try:
            self.utc = data.timestamp
            self.sip = data.num_sats
            (self.lat, self.lon) = self.nmea2latlon(data)
            self.alt = data.altitude
            self.__app.frm_banner.update_banner(time=self.utc, lat=self.lat,
                                                lon=self.lon, alt=self.alt, sip=self.sip)
            if self.__app.frm_settings.get_settings()['webmap']:
                self.__app.frm_mapview.update_map(lat=self.lat, lon=self.lon, static=False)
            else:
                self.__app.frm_mapview.update_map(lat=self.lat, lon=self.lon, static=True)
        except ValueError as err:
            self.__app.set_status(NMEAVALERROR.format(err), "red")

    def _process_GLL(self, data: types.talker):
        '''
        Process GLL sentence - GPS Lat Lon.
        '''

        try:
            self.utc = data.timestamp
            (self.lat, self.lon) = self.nmea2latlon(data)
            self.__app.frm_banner.update_banner(time=self.utc, lat=self.lat, lon=self.lon)
            if self.__app.frm_settings.get_settings()['webmap']:
                self.__app.frm_mapview.update_map(lat=self.lat, lon=self.lon, static=False)
            else:
                self.__app.frm_mapview.update_map(lat=self.lat, lon=self.lon, static=True)
        except ValueError as err:
            self.__app.set_status(NMEAVALERROR.format(err), "red")

    def _process_GSA(self, data: types.talker):
        '''
        Process GSA sentence - GPS DOP (Dilution of Precision) and active satellites.
        '''

        self.pdop = float(data.pdop)
        self.hdop = float(data.hdop)
        self.vdop = float(data.vdop)
        if data.mode_fix_type == '3':
            fix = '3D'
        elif data.mode_fix_type == '2':
            fix = '2D'
        else:
            fix = 'NO FIX'

        if self.__app.frm_settings.get_settings()['webmap']:
            self.__app.frm_mapview.update_map(lat=self.lat, lon=self.lon, hacc=self.hacc,
                                              vacc=self.vacc, fix=fix, static=False)
        else:
            self.__app.frm_mapview.update_map(lat=self.lat, lon=self.lon, hacc=self.hacc,
                                              vacc=self.vacc, fix=fix, static=True)

        self.__app.frm_banner.update_banner(dop=self.pdop, hdop=self.hdop, vdop=self.vdop, fix=fix)

    def _process_GSV(self, data: types.talker):
        '''
        Process GSV sentences - GPS Satellites in View
        These come in batches of 1-4 sentences, each containing the positions
        of up to 4 satellites (16 satellites in total).
        Modern receivers can send multiple batches corresponding to different
        NMEA assigned 'ID' ranges (GPS 1-32, SBAS 33-64, GLONASS 65-96)
        '''

        self.gsv_data = []
        gsv_dict = {}
        now = time()

        try:
            if data.sv_prn_num_1 != '':
                gsv_dict[data.sv_prn_num_1] = (data.elevation_deg_1,
                                               data.azimuth_1, data.snr_1, now)
            if data.sv_prn_num_2 != '':
                gsv_dict[data.sv_prn_num_2] = (data.elevation_deg_2,
                                               data.azimuth_2, data.snr_2, now)
            if data.sv_prn_num_3 != '':
                gsv_dict[data.sv_prn_num_3] = (data.elevation_deg_3,
                                               data.azimuth_3, data.snr_3, now)
            if data.sv_prn_num_4 != '':
                gsv_dict[data.sv_prn_num_4] = (data.elevation_deg_4,
                                               data.azimuth_4, data.snr_4, now)
        except AttributeError:
            pass

        for key in gsv_dict:
            self.gsv_log[key] = gsv_dict[key]

        for key in self.gsv_log:
            elev, azim, snr, lastupdate = self.gsv_log[key]
            if now - lastupdate < SAT_EXPIRY:  # expire passed satellites
                self.gsv_data.append((key, elev, azim, snr))

        self.__app.frm_satview.update_sats(self.gsv_data)
        self.__app.frm_banner.update_banner(siv=len(self.gsv_data))
        self.__app.frm_graphview.update_graph(self.gsv_data, len(self.gsv_data))

    def _process_VTG(self, data: types.talker):
        '''
        Process VTG sentence - GPS Vector track and Speed over the Ground.
        '''

        try:
            self.track = data.true_track
            self.speed = data.spd_over_grnd_kmph
            self.__app.frm_banner.update_banner(speed=self.speed, track=self.track)
        except ValueError as err:
            self.__app.set_status(NMEAVALERROR.format(err), "red")

    def _process_UBX00(self, data: types.ubx.UBX00):
        '''
        Process UXB00 sentence - GPS Vector track and Speed over the Ground.
        '''

        try:
            self.hacc = float(data.h_acc)
            self.vacc = float(data.v_acc)
            self.__app.frm_banner.update_banner(hacc=self.hacc, vacc=self.vacc)
        except ValueError as err:
            self.__app.set_status(NMEAVALERROR.format(err), "red")

    @staticmethod
    def nmea2latlon(data: types.talker) -> (float, float):
        '''
        Convert parsed NMEA GGA sentence to decimal lat, lon
        '''

        if data.lat == '':
            lat = ''
        else:
            latdeg = float(data.lat[0:2])
            latmin = float(data.lat[2:])
            londeg = float(data.lon[0:3])
            lat = (latdeg + latmin / 60) * (-1 if data.lat_dir == 'S' else 1)
        if data.lon == '':
            lon = ''
        else:
            lonmin = float(data.lon[3:])
            lon = (londeg + lonmin / 60) * (-1 if data.lon_dir == 'W' else 1)
        return (lat, lon)

    @staticmethod
    def _estimate_acc(dop) -> float:
        '''
        Derive a graphic indication of positional accuracy (in m) based on the HDOP
        (Horizontal Dilution of Precision) value and the nominal native device
        accuracy (datasheet CEP)

        NB: this is a largely arbitrary estimate - there is no direct correlation
        between HDOP and accuracy based solely on generic NMEA data.
        The NMEA PUBX,00 or UBX NAV-POSLLH message types return an explicit estimate
        of horizontal and vertical accuracy and are the preferred source.
        '''

        return float(dop) * DEVICE_ACCURACY * HDOP_RATIO / 1000
