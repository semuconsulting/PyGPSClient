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
    config_nmea,
    config_disable_lc29h,
    config_disable_lg290p,
    config_disable_septentrio,
    config_disable_ublox,
    config_fixed_lc29h,
    config_fixed_lg290p,
    config_fixed_septentrio,
    config_fixed_ublox,
    config_svin_lc29h,
    config_svin_lg290p,
    config_svin_quectel,
    config_svin_septentrio,
    config_svin_ublox,
)


class ConfigsTest(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    def tearDown(self):
        pass

    def test_config_nmea(self):
        EXPECTED_RESULT = "<UBX(CFG-VALSET, version=0, ram=1, bbr=0, flash=0, action=0, reserved0=0, CFG_UART1OUTPROT_NMEA=0, CFG_UART1OUTPROT_UBX=1, CFG_MSGOUT_UBX_NAV_PVT_UART1=1, CFG_MSGOUT_UBX_NAV_DOP_UART1=1, CFG_MSGOUT_UBX_NAV_SAT_UART1=4)>"
        res = config_nmea(1, "UART1")
        self.assertEqual(str(res), EXPECTED_RESULT)

    def test_config_disable_lc29h(self):
        EXPECTED_RESULT = "[NMEAMessage('P','AIR062', 1, payload=['-1', '0']), NMEAMessage('P','AIR432', 1, payload=['-1']), NMEAMessage('P','AIR434', 1, payload=['0']), NMEAMessage('P','QTMSAVEPAR', 1, payload=[]), NMEAMessage('P','AIR005', 1, payload=[])]"
        res = config_disable_lc29h()
        self.assertEqual(str(res), EXPECTED_RESULT)

    def test_config_disable_lg290p(self):
        EXPECTED_RESULT = "[NMEAMessage('P','QTMCFGRCVRMODE', 1, payload=['W', '1']), NMEAMessage('P','QTMSAVEPAR', 1, payload=[]), NMEAMessage('P','QTMSRR', 1, payload=[])]"
        res = config_disable_lg290p()
        self.assertEqual(str(res), EXPECTED_RESULT)

    def test_config_disable_septentrio(self):
        EXPECTED_RESULT = "['SSSSSSSSSS\\r\\n', 'erst,soft,config\\r\\n']"
        res = config_disable_septentrio()
        self.assertEqual(str(res), EXPECTED_RESULT)

    def test_config_disable_ublox(self):
        EXPECTED_RESULT = "<UBX(CFG-VALSET, version=0, ram=1, bbr=0, flash=0, action=0, reserved0=0, CFG_TMODE_MODE=0)>"
        res = config_disable_ublox()
        self.assertEqual(str(res), EXPECTED_RESULT)

    def test_config_fixed_lc29h(self):
        EXPECTED_RESULT = "[NMEAMessage('P','AIR062', 1, payload=['0', '0']), NMEAMessage('P','AIR062', 1, payload=['1', '0']), NMEAMessage('P','AIR062', 1, payload=['2', '0']), NMEAMessage('P','AIR062', 1, payload=['3', '0']), NMEAMessage('P','AIR062', 1, payload=['4', '0']), NMEAMessage('P','AIR062', 1, payload=['5', '0']), NMEAMessage('P','AIR062', 1, payload=['6', '0']), NMEAMessage('P','AIR062', 1, payload=['7', '0']), NMEAMessage('P','AIR062', 1, payload=['8', '0']), NMEAMessage('P','AIR432', 1, payload=['1']), NMEAMessage('P','AIR434', 1, payload=['1']), NMEAMessage('P','QTMSAVEPAR', 1, payload=[]), NMEAMessage('P','AIR005', 1, payload=[])]"
        res = config_fixed_lc29h(3000, 37.23345, -115.81513, 15.00, "LLH")
        self.assertEqual(str(res), EXPECTED_RESULT)

    def test_config_fixed_lg290p(self):
        EXPECTED_RESULT = "[NMEAMessage('P','QTMCFGRCVRMODE', 1, payload=['W', '2']), NMEAMessage('P','QTMCFGRTCM', 1, payload=['W', '7', '0', '-90', '07', '06', '1', '0']), NMEAMessage('P','QTMCFGSVIN', 1, payload=['W', '2', '0', '30.0', '-2214085.0816407623', '-4576970.1248123', '3838061.656193887']), NMEAMessage('P','QTMSAVEPAR', 1, payload=[]), NMEAMessage('P','QTMSRR', 1, payload=[])]"
        res = config_fixed_lg290p(3000, 37.23345, -115.81513, 15.00, "LLH")
        self.assertEqual(str(res), EXPECTED_RESULT)

    def test_config_fixed_septentrio(self):
        EXPECTED_RESULT = "['SSSSSSSSSS\\r\\n', 'setDataInOut,COM1, ,RTCMv3\\r\\n', 'setRTCMv3Formatting,1234\\r\\n', 'setRTCMv3Output,COM1,RTCM1006+RTCM1033+RTCM1077+RTCM1087+RTCM1097+RTCM1107+RTCM1117+RTCM1127+RTCM1137+RTCM1230\\r\\n', 'setStaticPosGeodetic,Geodetic1,37.23345000,-115.81513000,15.0000\\r\\n', 'setPVTMode,Static, ,Geodetic1\\r\\n']"
        res = config_fixed_septentrio(3000, 37.23345, -115.81513, 15.00, "LLH")
        self.assertEqual(str(res), EXPECTED_RESULT)

    def test_config_fixed_ublox(self):
        EXPECTED_RESULT = "<UBX(CFG-VALSET, version=0, ram=1, bbr=0, flash=0, action=0, reserved0=0, CFG_TMODE_MODE=2, CFG_TMODE_POS_TYPE=1, CFG_TMODE_FIXED_POS_ACC=300000, CFG_TMODE_LAT=372334500, CFG_TMODE_LAT_HP=0, CFG_TMODE_LON=-1158151300, CFG_TMODE_LON_HP=0, CFG_TMODE_HEIGHT=1500, CFG_TMODE_HEIGHT_HP=0)>"
        res = config_fixed_ublox(3000, 37.23345, -115.81513, 15.00, "LLH")
        self.assertEqual(str(res), EXPECTED_RESULT)

    def test_config_svin_lc29h(self):
        EXPECTED_RESULT = "[NMEAMessage('P','AIR062', 1, payload=['0', '0']), NMEAMessage('P','AIR062', 1, payload=['1', '0']), NMEAMessage('P','AIR062', 1, payload=['2', '0']), NMEAMessage('P','AIR062', 1, payload=['3', '0']), NMEAMessage('P','AIR062', 1, payload=['4', '0']), NMEAMessage('P','AIR062', 1, payload=['5', '0']), NMEAMessage('P','AIR062', 1, payload=['6', '0']), NMEAMessage('P','AIR062', 1, payload=['7', '0']), NMEAMessage('P','AIR062', 1, payload=['8', '0']), NMEAMessage('P','AIR432', 1, payload=['1']), NMEAMessage('P','AIR434', 1, payload=['1']), NMEAMessage('P','QTMSAVEPAR', 1, payload=[]), NMEAMessage('P','AIR005', 1, payload=[])]"
        res = config_svin_lc29h(3000, 60)
        self.assertEqual(str(res), EXPECTED_RESULT)

    def test_config_svin_lg290p(self):
        EXPECTED_RESULT = "[NMEAMessage('P','QTMCFGRCVRMODE', 1, payload=['W', '2']), NMEAMessage('P','QTMCFGRTCM', 1, payload=['W', '7', '0', '-90', '07', '06', '1', '0']), NMEAMessage('P','QTMCFGSVIN', 1, payload=['W', '1', '60', '30.0', '0.0', '0.0', '0.0']), NMEAMessage('P','QTMSAVEPAR', 1, payload=[]), NMEAMessage('P','QTMSRR', 1, payload=[])]"
        res = config_svin_lg290p(3000, 60)
        self.assertEqual(str(res), EXPECTED_RESULT)

    def test_config_svin_quectel(self):
        EXPECTED_RESULT = (
            "<NMEA(PQTMCFGMSGRATE, status=W, msgname=PQTMSVINSTATUS, rate=1, msgver=1)>"
        )
        res = config_svin_quectel()
        self.assertEqual(str(res), EXPECTED_RESULT)

    def test_config_svin_septentrio(self):
        EXPECTED_RESULT = "['SSSSSSSSSS\\r\\n', 'setDataInOut, COM1, ,RTCMv3\\r\\n', 'setRTCMv3Formatting,1234\\r\\n', 'setRTCMv3Output,COM1,RTCM1006+RTCM1033+RTCM1077+RTCM1087+RTCM1097+RTCM1107+RTCM1117+RTCM1127+RTCM1137+RTCM1230\\r\\n', 'setPVTMode,Static, ,auto\\r\\n']"
        res = config_svin_septentrio(3000, 60)
        self.assertEqual(str(res), EXPECTED_RESULT)

    def test_config_svin_ublox(self):
        EXPECTED_RESULT = "<UBX(CFG-VALSET, version=0, ram=1, bbr=0, flash=0, action=0, reserved0=0, CFG_TMODE_MODE=1, CFG_TMODE_SVIN_ACC_LIMIT=300000, CFG_TMODE_SVIN_MIN_DUR=60)>"
        res = config_svin_ublox(3000, 60)
        self.assertEqual(str(res), EXPECTED_RESULT)
