"""
test_configs.py

Static method tests for pygpsclient configuration handler.

Created on 3 Oct 2020

:author: semuadmin (Steve Smith)
:copyright: 2020 semuadmin
:license: BSD 3-Clause
"""

# pylint: disable=missing-docstring

import unittest

from pygpsclient.receiver_config_handler import (
    config_disable_quectel_lcseries,
    config_disable_quectel_lgseries,
    config_disable_septentrio,
    config_disable_unicore,
    config_disable_ublox,
    config_fixed_quectel_lcseries,
    config_fixed_quectel_lgseries,
    config_fixed_septentrio,
    config_fixed_unicore,
    config_fixed_ublox,
    config_svin_quectel_lcseries,
    config_svin_quectel_lgseries,
    config_svin_quectel,
    config_svin_septentrio,
    config_svin_unicore,
    config_svin_ublox,
)


class ConfigsTest(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    def tearDown(self):
        pass

    def test_config_disable_quectel_lcseries(self):
        # EXPECTED_RESULT = "[NMEAMessage('P','AIR062', 1, payload=['-1', '0']), NMEAMessage('P','AIR432', 1, payload=['-1']), NMEAMessage('P','AIR434', 1, payload=['0']), NMEAMessage('P','QTMSAVEPAR', 1, payload=[]), NMEAMessage('P','AIR005', 1, payload=[])]"
        EXPECTED_RESULT = [b'$PAIR062,-1,0*12\r\n', b'$PAIR432,-1*0F\r\n', b'$PAIR434,0*25\r\n', b'$PQTMSAVEPAR*5A\r\n', b'$PAIR005*3F\r\n']
        res = config_disable_quectel_lcseries()
        # print(res)
        self.assertEqual(res, EXPECTED_RESULT)

    def test_config_disable_quectel_lgseries(self):
        # EXPECTED_RESULT = "[NMEAMessage('P','QTMCFGRCVRMODE', 1, payload=['W', '1']), NMEAMessage('P','QTMSAVEPAR', 1, payload=[]), NMEAMessage('P','QTMSRR', 1, payload=[])]"
        EXPECTED_RESULT = [b'$PQTMCFGRCVRMODE,W,1*2A\r\n', b'$PQTMSAVEPAR*5A\r\n', b'$PQTMSRR*4B\r\n']
        res = config_disable_quectel_lgseries()
        # print(res)
        self.assertEqual(res, EXPECTED_RESULT)

    def test_config_disable_septentrio(self):
        # EXPECTED_RESULT = "['SSSSSSSSSS\\r\\n', 'erst,soft,config\\r\\n']"
        EXPECTED_RESULT =  [b'SSSSSSSSSS\r\n', b'setPVTMode, Rover, all, auto\r\n', b'setRTCMv3Output, COM1, none\r\n', b'setDataInOut, COM1, auto, SBF+NMEA\r\n', b'setNMEAOutput, Stream1, COM1, GGA+GSA+GLL+RMC+VTG, sec1\r\n', b'setNMEAOutput, Stream2, COM1, GSV, sec5\r\n']
        res = config_disable_septentrio()
        # print(res)
        self.assertEqual(res, EXPECTED_RESULT)

    def test_config_disable_unicore(self):
        # EXPECTED_RESULT = "['mode rover survey\\r\\n', 'rtcm1006 com1 0\\r\\n', 'rtcm1033 com1 0\\r\\n', 'rtcm1074 com1 0\\r\\n', 'rtcm1084 com1 0\\r\\n', 'rtcm1094 com1 0\\r\\n', 'rtcm1124 com1 0\\r\\n', 'saveconfig\\r\\n']"
        EXPECTED_RESULT = [b'unlog\r\n', b'gpgsa 1\r\n', b'gpgga 1\r\n', b'gpgll 1\r\n', b'gpgsv 4\r\n', b'gpvtg 1\r\n', b'gprmc 1\r\n', b'mode rover\r\n', b'config pvtalg multi\r\n', b'saveconfig\r\n']
        res = config_disable_unicore()
        # print(res)
        self.assertEqual(res, EXPECTED_RESULT)

    def test_config_disable_ublox(self):
        # EXPECTED_RESULT = "<UBX(CFG-VALSET, version=0, ram=1, bbr=0, flash=0, action=0, reserved0=0, CFG_TMODE_MODE=0)>"
        EXPECTED_RESULT = [b'\xb5b\x06\x8a\t\x00\x00\x01\x00\x00\x01\x00\x03 \x00\xbe\x7f', b'\xb5b\x06\x8aJ\x00\x00\x01\x00\x00\x8b\x00\x91 \x00\xb6\x02\x91 \x00\xc5\x02\x91 \x00\xbb\x02\x91 \x00\xcf\x02\x91 \x00\xd4\x02\x91 \x00\x1b\x03\x91 \x00\xd9\x02\x91 \x00\x06\x03\x91 \x00\x02\x00x\x10\x01\x01\x00x\x10\x01\t\x00\x91 \x00;\x00\x91 \x00\x18\x00\x91 \x00\x08\xc5', b'\xb5b\x06\x8aJ\x00\x00\x01\x00\x00\x89\x00\x91 \x00\xb4\x02\x91 \x00\xc3\x02\x91 \x00\xb9\x02\x91 \x00\xcd\x02\x91 \x00\xd2\x02\x91 \x00\x19\x03\x91 \x00\xd7\x02\x91 \x00\x04\x03\x91 \x00\x02\x00t\x10\x01\x01\x00t\x10\x01\x07\x00\x91 \x009\x00\x91 \x00\x16\x00\x91 \x00\xe8a']
        res = config_disable_ublox()
        # print(res)
        self.assertEqual(res, EXPECTED_RESULT)

    def test_config_fixed_quectel_lcseries(self):
        # EXPECTED_RESULT = "[NMEAMessage('P','AIR062', 1, payload=['0', '0']), NMEAMessage('P','AIR062', 1, payload=['1', '0']), NMEAMessage('P','AIR062', 1, payload=['2', '0']), NMEAMessage('P','AIR062', 1, payload=['3', '0']), NMEAMessage('P','AIR062', 1, payload=['4', '0']), NMEAMessage('P','AIR062', 1, payload=['5', '0']), NMEAMessage('P','AIR062', 1, payload=['6', '0']), NMEAMessage('P','AIR062', 1, payload=['7', '0']), NMEAMessage('P','AIR062', 1, payload=['8', '0']), NMEAMessage('P','AIR432', 1, payload=['1']), NMEAMessage('P','AIR434', 1, payload=['1']), NMEAMessage('P','QTMSAVEPAR', 1, payload=[]), NMEAMessage('P','AIR005', 1, payload=[])]"
        EXPECTED_RESULT = [b'$PAIR062,0,0*3E\r\n', b'$PAIR062,1,0*3F\r\n', b'$PAIR062,2,0*3C\r\n', b'$PAIR062,3,0*3D\r\n', b'$PAIR062,4,0*3A\r\n', b'$PAIR062,5,0*3B\r\n', b'$PAIR062,6,0*38\r\n', b'$PAIR062,7,0*39\r\n', b'$PAIR062,8,0*36\r\n', b'$PAIR432,1*22\r\n', b'$PAIR434,1*24\r\n', b'$PQTMSAVEPAR*5A\r\n', b'$PAIR005*3F\r\n']
        res = config_fixed_quectel_lcseries(3000, 37.23345, -115.81513, 15.00, "LLH")
        # print(res)
        self.assertEqual(res, EXPECTED_RESULT)

    def test_config_fixed_quectel_lgseries(self):
        # EXPECTED_RESULT = "[NMEAMessage('P','QTMCFGRCVRMODE', 1, payload=['W', '2']), NMEAMessage('P','QTMCFGRTCM', 1, payload=['W', '7', '0', '-90', '07', '06', '1', '0']), NMEAMessage('P','QTMCFGSVIN', 1, payload=['W', '2', '0', '30.0', '-2214085.0816407623', '-4576970.1248123', '3838061.656193887']), NMEAMessage('P','QTMSAVEPAR', 1, payload=[]), NMEAMessage('P','QTMSRR', 1, payload=[])]"
        EXPECTED_RESULT = [b'$PQTMCFGRCVRMODE,W,2*29\r\n', b'$PQTMCFGRTCM,W,7,0,-90,07,06,1,0*26\r\n', b'$PQTMCFGSVIN,W,2,0,30.0,-2214085.0816407623,-4576970.1248123,3838061.656193887*2E\r\n', b'$PQTMSAVEPAR*5A\r\n', b'$PQTMSRR*4B\r\n']
        res = config_fixed_quectel_lgseries(3000, 37.23345, -115.81513, 15.00, "LLH")
        # print(res)
        self.assertEqual(res, EXPECTED_RESULT)

    def test_config_fixed_septentrio(self):
        # EXPECTED_RESULT = "['SSSSSSSSSS\\r\\n', 'setDataInOut,COM1, ,RTCMv3\\r\\n', 'setRTCMv3Formatting,1234\\r\\n', 'setRTCMv3Output,COM1,RTCM1006+RTCM1033+RTCM1077+RTCM1087+RTCM1097+RTCM1107+RTCM1117+RTCM1127+RTCM1137+RTCM1230\\r\\n', 'setStaticPosGeodetic,Geodetic1,37.23345000,-115.81513000,15.0000\\r\\n', 'setPVTMode,Static, ,Geodetic1\\r\\n']"
        EXPECTED_RESULT = [b'SSSSSSSSSS\r\n', b'setDataInOut, COM1, auto,RTCMv3+SBF\r\n', b'setRTCMv3Formatting, 1234\r\n', b'setRTCMv3Output, COM1, RTCM1006+RTCM1013+RTCM1019+RTCM1020+RTCM1033+MSM7+RTCM1230\r\n', b'setRTCMv3Interval, MSM7+RTCM1230, 1\r\n', b'setRTCMv3Interval, RTCM1005|6+RTCM1013+RTCM1019+RTCM1020+RTCM1033, 5\r\n', b'setPVTMode, Static, all, auto\r\n', b'setStaticPosGeodetic, Geodetic1, 37.23345000,-115.81513000,15.0000\r\n', b'setPVTMode,Static, ,Geodetic1\r\n']
        res = config_fixed_septentrio(3000, 37.23345, -115.81513, 15.00, "LLH")
        # print(res)
        self.assertEqual(res, EXPECTED_RESULT)

    def test_config_fixed_unicore(self):
        # EXPECTED_RESULT = "['mode base 37.23345 -115.81513 15.0\\r\\n', 'rtcm1006 com1 10\\r\\n', 'rtcm1033 com1 10\\r\\n', 'rtcm1074 com1 1\\r\\n', 'rtcm1084 com1 1\\r\\n', 'rtcm1094 com1 1\\r\\n', 'rtcm1124 com1 1\\r\\n', 'saveconfig\\r\\n']"
        EXPECTED_RESULT = [b'unlog\r\n', b'mode base 37.23345 -115.81513 15.0\r\n', b'config pvtalg multi\r\n', b'rtcm1006 10\r\n', b'rtcm1033 10\r\n', b'rtcm1074 1\r\n', b'rtcm1084 1\r\n', b'rtcm1094 1\r\n', b'rtcm1124 1\r\n', b'saveconfig\r\n']
        res = config_fixed_unicore(3000, 37.23345, -115.81513, 15.00, "LLH")
        # print(res)
        self.assertEqual(res, EXPECTED_RESULT)

    def test_config_fixed_ublox(self):
        # EXPECTED_RESULT = "<UBX(CFG-VALSET, version=0, ram=1, bbr=0, flash=0, action=0, reserved0=0, CFG_TMODE_MODE=2, CFG_TMODE_POS_TYPE=1, CFG_TMODE_FIXED_POS_ACC=300000, CFG_TMODE_LAT=372334500, CFG_TMODE_LAT_HP=0, CFG_TMODE_LON=-1158151300, CFG_TMODE_LON_HP=0, CFG_TMODE_HEIGHT=1500, CFG_TMODE_HEIGHT_HP=0)>"
        EXPECTED_RESULT = [b'\xb5b\x06\x8a=\x00\x00\x01\x00\x00\x01\x00\x03 \x02\x02\x00\x03 \x01\x0f\x00\x03@\xe0\x93\x04\x00\t\x00\x03@\xa4_1\x16\x0c\x00\x03 \x00\n\x00\x03@|\x03\xf8\xba\r\x00\x03 \x00\x0b\x00\x03@\xdc\x05\x00\x00\x0e\x00\x03 \x00\xb67', b'\xb5b\x06\x8a6\x00\x00\x01\x00\x00\x8b\x00\x91 \x00\x02\x00x\x10\x00\xb6\x02\x91 \x01\xc5\x02\x91 \x05\xbb\x02\x91 \x01\xcf\x02\x91 \x01\xd4\x02\x91 \x01\x1b\x03\x91 \x01\xd9\x02\x91 \x01\x06\x03\x91 \x01\x06\x8e', b'\xb5b\x06\x8a6\x00\x00\x01\x00\x00\x89\x00\x91 \x00\x02\x00t\x10\x00\xb4\x02\x91 \x01\xc3\x02\x91 \x05\xb9\x02\x91 \x01\xcd\x02\x91 \x01\xd2\x02\x91 \x01\x19\x03\x91 \x01\xd7\x02\x91 \x01\x04\x03\x91 \x01\xf0\x16']
        res = config_fixed_ublox(3000, 37.23345, -115.81513, 15.00, "LLH")
        print(res)
        self.assertEqual(res, EXPECTED_RESULT)

    def test_config_svin_quectel_lcseries(self):
        # EXPECTED_RESULT = "[NMEAMessage('P','AIR062', 1, payload=['0', '0']), NMEAMessage('P','AIR062', 1, payload=['1', '0']), NMEAMessage('P','AIR062', 1, payload=['2', '0']), NMEAMessage('P','AIR062', 1, payload=['3', '0']), NMEAMessage('P','AIR062', 1, payload=['4', '0']), NMEAMessage('P','AIR062', 1, payload=['5', '0']), NMEAMessage('P','AIR062', 1, payload=['6', '0']), NMEAMessage('P','AIR062', 1, payload=['7', '0']), NMEAMessage('P','AIR062', 1, payload=['8', '0']), NMEAMessage('P','AIR432', 1, payload=['1']), NMEAMessage('P','AIR434', 1, payload=['1']), NMEAMessage('P','QTMSAVEPAR', 1, payload=[]), NMEAMessage('P','AIR005', 1, payload=[])]"
        EXPECTED_RESULT = [b'$PAIR062,0,0*3E\r\n', b'$PAIR062,1,0*3F\r\n', b'$PAIR062,2,0*3C\r\n', b'$PAIR062,3,0*3D\r\n', b'$PAIR062,4,0*3A\r\n', b'$PAIR062,5,0*3B\r\n', b'$PAIR062,6,0*38\r\n', b'$PAIR062,7,0*39\r\n', b'$PAIR062,8,0*36\r\n', b'$PAIR432,1*22\r\n', b'$PAIR434,1*24\r\n', b'$PQTMSAVEPAR*5A\r\n', b'$PAIR005*3F\r\n']
        res = config_svin_quectel_lcseries(3000, 60)
        # print(res)
        self.assertEqual(res, EXPECTED_RESULT)

    def test_config_svin_quectel_lgseries(self):
        # EXPECTED_RESULT = "[NMEAMessage('P','QTMCFGRCVRMODE', 1, payload=['W', '2']), NMEAMessage('P','QTMCFGRTCM', 1, payload=['W', '7', '0', '-90', '07', '06', '1', '0']), NMEAMessage('P','QTMCFGSVIN', 1, payload=['W', '1', '60', '30.0', '0.0', '0.0', '0.0']), NMEAMessage('P','QTMSAVEPAR', 1, payload=[]), NMEAMessage('P','QTMSRR', 1, payload=[])]"
        EXPECTED_RESULT = [b'$PQTMCFGRCVRMODE,W,2*29\r\n', b'$PQTMCFGRTCM,W,7,0,-90,07,06,1,0*26\r\n', b'$PQTMCFGSVIN,W,1,60,30.0,0.0,0.0,0.0*27\r\n', b'$PQTMSAVEPAR*5A\r\n', b'$PQTMSRR*4B\r\n']
        res = config_svin_quectel_lgseries(3000, 60)
        # print(res)
        self.assertEqual(res, EXPECTED_RESULT)

    def test_config_svin_quectel(self):
        # EXPECTED_RESULT = "<NMEA(PQTMCFGMSGRATE, status=W, msgname=PQTMSVINSTATUS, rate=1, msgver=1)>"
        EXPECTED_RESULT = b'$PQTMCFGMSGRATE,W,PQTMSVINSTATUS,1,1*58\r\n'
        res = config_svin_quectel()
        # print(res)
        self.assertEqual(res, EXPECTED_RESULT)

    def test_config_svin_septentrio(self):
        # EXPECTED_RESULT = "['SSSSSSSSSS\\r\\n', 'setDataInOut, COM1, ,RTCMv3\\r\\n', 'setRTCMv3Formatting,1234\\r\\n', 'setRTCMv3Output,COM1,RTCM1006+RTCM1033+RTCM1077+RTCM1087+RTCM1097+RTCM1107+RTCM1117+RTCM1127+RTCM1137+RTCM1230\\r\\n', 'setPVTMode,Static, ,auto\\r\\n']"
        EXPECTED_RESULT = [b'SSSSSSSSSS\r\n', b'setDataInOut, COM1, auto, RTCMv3+SBF\r\n', b'setRTCMv3Formatting, 1234\r\n', b'setRTCMv3Output, COM1, RTCM1006+RTCM1013+RTCM1019+RTCM1020+RTCM1033+MSM7+RTCM1230\r\n', b'setRTCMv3Interval, MSM7+RTCM1230, 1\r\n', b'setRTCMv3Interval, RTCM1005|6+RTCM1013+RTCM1019+RTCM1020+RTCM1033, 5\r\n', b'setPVTMode, Static, all, auto\r\n']
        res = config_svin_septentrio(3000, 60)
        # rint(res)
        self.assertEqual(res, EXPECTED_RESULT)

    def test_config_svin_unicore(self):
        # EXPECTED_RESULT = "['mode base time 60\\r\\n', 'rtcm1006 com1 10\\r\\n', 'rtcm1033 com1 10\\r\\n', 'rtcm1074 com1 1\\r\\n', 'rtcm1084 com1 1\\r\\n', 'rtcm1094 com1 1\\r\\n', 'rtcm1124 com1 1\\r\\n', 'saveconfig\\r\\n']"
        EXPECTED_RESULT = [b'unlog\r\n', b'mode base time 60\r\n', b'config pvtalg multi\r\n', b'rtcm1006 10\r\n', b'rtcm1033 10\r\n', b'rtcm1074 1\r\n', b'rtcm1084 1\r\n', b'rtcm1094 1\r\n', b'rtcm1124 1\r\n', b'saveconfig\r\n']
        res = config_svin_unicore(3000, 60)
        # print(res)
        self.assertEqual(res, EXPECTED_RESULT)

    def test_config_svin_ublox(self):
        # EXPECTED_RESULT = "<UBX(CFG-VALSET, version=0, ram=1, bbr=0, flash=0, action=0, reserved0=0, CFG_TMODE_MODE=1, CFG_TMODE_SVIN_ACC_LIMIT=300000, CFG_TMODE_SVIN_MIN_DUR=60)>"
        EXPECTED_RESULT = [b'\xb5b\x06\x8a\x19\x00\x00\x01\x00\x00\x01\x00\x03 \x01\x11\x00\x03@\xe0\x93\x04\x00\x10\x00\x03@<\x00\x00\x00)U', b'\xb5b\x06\x8a6\x00\x00\x01\x00\x00\x02\x00x\x10\x00\x8b\x00\x91 \x01\xb6\x02\x91 \x01\xc5\x02\x91 \x05\xbb\x02\x91 \x01\xcf\x02\x91 \x01\xd4\x02\x91 \x01\x1b\x03\x91 \x01\xd9\x02\x91 \x01\x06\x03\x91 \x01\x07=', b'\xb5b\x06\x8a6\x00\x00\x01\x00\x00\x02\x00t\x10\x00\x89\x00\x91 \x01\xb4\x02\x91 \x01\xc3\x02\x91 \x05\xb9\x02\x91 \x01\xcd\x02\x91 \x01\xd2\x02\x91 \x01\x19\x03\x91 \x01\xd7\x02\x91 \x01\x04\x03\x91 \x01\xf1\xbb']
        res = config_svin_ublox(3000, 60)
        # print(res)
        self.assertEqual(res, EXPECTED_RESULT)
