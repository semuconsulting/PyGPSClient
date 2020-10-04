'''
UBX Protocol handler

Uses pyubx2 library for parsing

Created on 30 Sep 2020

@author: semuadmin
'''

from pyubx2.ubxmessage import UBXMessage


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
        # pylint: disable=no-member, line-too-long
        pdat = UBXMessage.parse(data, False)

        if pdat.identity == 'NAV-POSLLH':
            print(f"NAV-POSLLH: lat {pdat.lat/10**7}, lon {pdat.lon/10**7}, alt {pdat.hMSL/10**3} m, hAcc {pdat.HAcc/10**3} m")
        if pdat.identity == 'NAV-VELNED':
            print(f"NAV-VELNED: ground speed {pdat.gSpeed/10**2} m/s, heading {int(round(pdat.heading/10**5))} degrees")
        if data or pdat:
            self._update_console(data, pdat)

        return pdat

    def _update_console(self, raw_data, parsed_data):
        '''
        Write the incoming data to the console in raw or parsed format.
        '''

        if self.__app.frm_settings.get_settings()['raw']:
            self.__app.frm_console.update_console(str(raw_data))
        else:
            self.__app.frm_console.update_console(str(parsed_data))
