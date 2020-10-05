'''
UBX Protocol handler

Uses pyubx2 library for parsing

Created on 30 Sep 2020

@author: semuadmin
'''

from datetime import datetime, timedelta

from pyubx2.ubxmessage import UBXMessage

import pyubx2.exceptions as ube


def itow2utc(iTOW: int) -> str:
    '''
    `Convert UBX iTOW to UTC time
    '''

    utc = datetime(1980, 1, 6) + timedelta(seconds=(iTOW / 1000) - (35 - 19))
    return utc.time()


class UBXHandler():
    '''
    UBXHandler class
    '''

    def __init__(self, app):
        '''
        Constructor.
        '''

        self.__app = app  # Reference to main application class
        self.__master = self.__app.get_master()  # Reference to root class (Tk)

    def process_data(self, data: bytes) -> UBXMessage:
        '''
        Process UBX message type
        '''

        parsed_data = UBXMessage.parse(data, False)

        if parsed_data.identity == 'NAV-POSLLH':
            self._process_NAV_LLH(parsed_data)
        if parsed_data.identity == 'NAV-VELNED':
            self._process_NAV_VELNED(parsed_data)
        if parsed_data.identity == 'NAV-SVINFO':
            self._process_NAV_SVINFO(parsed_data)
        if parsed_data.identity == 'NAV-SOL':
            self._process_NAV_SOL(parsed_data)
        if parsed_data.identity == 'NAV-DOP':
            self._process_NAV_DOP(parsed_data)
        if data or parsed_data:
            self._update_console(data, parsed_data)

        return parsed_data

    def _update_console(self, raw_data, parsed_data):
        '''
        Write the incoming data to the console in raw or parsed format.
        '''

        if self.__app.frm_settings.get_settings()['raw']:
            self.__app.frm_console.update_console(str(raw_data))
        else:
            self.__app.frm_console.update_console(str(parsed_data))

    def _process_NAV_LLH(self, data: UBXMessage):
        '''
        Process NAV-LLH sentence - Latitude, Longitude, Height.
        '''

        try:
            self.utc = itow2utc(data.iTOW)
            self.lat = data.lat / 10 ** 7
            self.lon = data.lon / 10 ** 7
            self.alt = data.hMSL / 10 ** 3
            self.hacc = data.HAcc / 10 ** 3
            self.vacc = data.vAcc / 10 ** 3
            self.__app.frm_banner.update_banner(time=self.utc, lat=self.lat,
                                                lon=self.lon, alt=self.alt,
                                                hacc=self.hacc, vacc=self.vacc)

            if self.__app.frm_settings.get_settings()['webmap']:
                self.__app.frm_mapview.update_map(self.lat, self.lon, self.hacc,
                                                  self.vacc, '3D', False)
            else:
                self.__app.frm_mapview.update_map(self.lat, self.lon, self.hacc,
                                                  self.vacc, '3D', True)
        except ValueError as err:
            #self.__app.set_status(ube.UBXMessageError(err), "red")
            pass

    def _process_NAV_VELNED(self, data: UBXMessage):
        '''
        Process NAV-VELNED sentence - Velocity Solution in North East Down format.
        '''

        try:
            self.track = str(data.heading)
            self.speed = str(data.gspeed)
            self.__app.frm_banner.update_banner(speed=self.speed, track=self.track)
        except ValueError as err:
            #self.__app.set_status(ube.UBXMessageError(err), "red")
            pass

    def _process_NAV_SVINFO(self, data: UBXMessage):
        '''
        Process NAV-SVINFO sentences - Space Vehicle Information.
        '''

        try:
            self.gsv_data = []
            num_siv = int(data.numCh)
            self.__app.frm_banner.update_banner(siv=num_siv)

            for i in range(num_siv):
                idx = "_{0:0=2d}".format(i + 1)
                # TODO is there an easier/better way to do this without exec()?:
                exec("if data.svid" + str(idx) + " < 100: " + \
                     "self.gsv_data.append((data.svid" + str(idx) + \
                     ", data.elev" + str(idx) + \
                     ", data.azim" + str(idx) + ", data.cno" + str(idx) + "))")
            self.__app.frm_satview.update_sats(self.gsv_data)
            self.__app.frm_graphview.update_graph(self.gsv_data)
        except ValueError as err:
            #self.__app.set_status(ube.UBXMessageError(err), "red")
            pass

    def _process_NAV_SOL(self, data: UBXMessage):
        '''
        Process NAV-SOL sentence - Navigation Solution.
        '''

        try:
            self.pdop = str(data.pDOP / 10 ** 2)
            self.sip = str(data.numSV)
            if data.gpsFix == 3:
                fix = '3D'
            elif data.gpsFix == 2:
                fix = '2D'
            else:
                fix = 'NO FIX'

            self.__app.frm_banner.update_banner(dop=self.pdop, fix=fix, sip=self.sip)
        except ValueError as err:
            #self.__app.set_status(ube.UBXMessageError(err), "red")
            pass

    def _process_NAV_DOP(self, data: UBXMessage):
        '''
        Process NAV-DOP sentence - Dilution of Precision.
        '''

        try:
            self.pdop = str(data.pDOP / 10 ** 2)
            self.hdop = str(data.hDOP / 10 ** 2)
            self.vdop = str(data.vDOP / 10 ** 2)

            self.__app.frm_banner.update_banner(dop=self.pdop, hdop=self.hdop, vdop=self.vdop)
        except ValueError as err:
            #self.__app.set_status(ube.UBXMessageError(err), "red")
            pass
