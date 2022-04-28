"""
Created on 3 Oct 2020

Static method tests for pygpsclient.helpers

@author: semuadmin
"""

import unittest

from pygpsclient.helpers import (
    deg2rad,
    deg2dmm,
    deg2dms,
    m2ft,
    ms2kmph,
    ms2knots,
    ms2mph,
    ft2m,
    kmph2ms,
    knots2ms,
    pos2iso6709,
    hsv2rgb,
    snr2col,
    svid2gnssid,
    cel2cart,
    itow2utc,
    corrage2int,
    fix2desc,
    estimate_acc,
    validURL,
)


class StaticTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testdeg2rad(self):
        res = deg2rad(147)
        self.assertAlmostEqual(res, 2.565634, 5)

    def testcel2cart(self):
        (elev, azim) = cel2cart(34, 128)
        self.assertAlmostEqual(elev, -0.510406, 5)
        self.assertAlmostEqual(azim, 0.653290, 5)

    def testdeg2dms(self):
        res = deg2dms(53.346, "lat")
        self.assertEqual(res, ("53°20′45.6″N"))

    def testdeg2dmm(self):
        res = deg2dmm(-2.5463, "lon")
        self.assertEqual(res, ("2°32.778′W"))

    def testm2ft(self):
        res = m2ft(39.234)
        self.assertAlmostEqual(res, 128.720476, 5)

    def testft2m(self):
        res = ft2m(124.063)
        self.assertAlmostEqual(res, 37.814401, 5)

    def testms2kmph(self):
        res = ms2kmph(3.654)
        self.assertAlmostEqual(res, 13.154400, 5)

    def testms2mph(self):
        res = ms2mph(3.654)
        self.assertAlmostEqual(res, 8.173766, 5)

    def testms2knots(self):
        res = ms2knots(3.654)
        self.assertAlmostEqual(res, 7.102805, 5)

    def testkmph2ms(self):
        res = kmph2ms(3.654)
        self.assertAlmostEqual(res, 1.015000, 5)

    def testknots2ms(self):
        res = knots2ms(3.654)
        self.assertAlmostEqual(res, 1.879781, 5)

    def testpos2iso6709(self):
        res = pos2iso6709(53.12, -2.165, 35)
        self.assertEqual(res, "+53.12-2.165+35CRSWGS_84/")

    def testhsv2rgb(self):
        res = hsv2rgb(0.5, 0.2, 0.9)
        self.assertEqual(res, "#b7e5e5")

    def testsnr2col(self):
        res = snr2col(38)
        self.assertEqual(res, "#77cc28")

    def testsvid2gnss(self):
        EXPECTED_RESULT = [0, 3, 6, 1, 4, 5, 2]
        svids = (28, 50, 72, 140, 180, 200, 220)
        for i, svid in enumerate(svids):
            res = svid2gnssid(svid)
            self.assertEqual(res, EXPECTED_RESULT[i])

    def testfix2desc(self):
        EXPECTED_RESULT = ["3D", "RTK FIXED", "RTK FLOAT", "3D", "NO FIX"]
        codes = (("GGA", 1), ("GGA", 4), ("RMC", "F"), ("GLL", "A"), ("GGA", 0))
        for i, code in enumerate(codes):
            fix, msg = code
            res = fix2desc(fix, msg)
            self.assertEqual(res, EXPECTED_RESULT[i])

    def testcorrage2int(self):
        EXPECTED_RESULT = [0, 5, 20, 60, 120, 0]
        fixes = (0, 3, 6, 9, 11, 15)
        for i, fix in enumerate(fixes):
            res = corrage2int(fix)
            self.assertEqual(res, EXPECTED_RESULT[i])

    def testvalidURL(self):
        res = validURL("localhost")
        self.assertEqual(res, True)
        res = validURL("tcpserver.com")
        self.assertEqual(res, True)
        res = validURL("192.168.0.72")
        self.assertEqual(res, True)
        res = validURL("192.168,0.72")
        self.assertEqual(res, False)
        res = validURL("sdfffasdff")
        self.assertEqual(res, False)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
