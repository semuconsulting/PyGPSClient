"""
Created on 3 Oct 2020

Static method tests for pygpsclient.helpers

@author: semuadmin
"""
# pylint: disable=missing-docstring

import unittest
from datetime import datetime

from pyubx2 import UBXReader
from pygpsclient.widgets import widget_grid

from pygpsclient.helpers import (
    bitsval,
    bytes2unit,
    cel2cart,
    col2contrast,
    corrage2int,
    date2wnotow,
    fix2desc,
    ft2m,
    get_mp_distance,
    haversine,
    hsv2rgb,
    kmph2ms,
    knots2ms,
    m2ft,
    ms2kmph,
    ms2knots,
    ms2mph,
    parse_rxmspartnkey,
    pos2iso6709,
    secs2unit,
    snr2col,
    str2rgb,
    stringvar2val,
    svid2gnssid,
    validURL,
    wnotow2date,
)
from pygpsclient.mapquest import mapq_compress, mapq_decompress


class StaticTest(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    def tearDown(self):
        pass

    def testcel2cart(self):
        (elev, azim) = cel2cart(34, 128)
        self.assertAlmostEqual(elev, -0.510406, 5)
        self.assertAlmostEqual(azim, 0.653290, 5)
        res = cel2cart("xxx", "xxx")
        self.assertEqual(res, (0, 0))

    def testm2ft(self):
        res = m2ft(39.234)
        self.assertAlmostEqual(res, 128.720476, 5)
        res = m2ft("xxx")
        self.assertEqual(res, 0)

    def testft2m(self):
        res = ft2m(124.063)
        self.assertAlmostEqual(res, 37.814401, 5)
        res = ft2m("xxx")
        self.assertEqual(res, 0)

    def testms2kmph(self):
        res = ms2kmph(3.654)
        self.assertAlmostEqual(res, 13.154400, 5)
        res = ms2kmph("xxx")
        self.assertEqual(res, 0)

    def testms2mph(self):
        res = ms2mph(3.654)
        self.assertAlmostEqual(res, 8.173766, 5)
        res = ms2mph("xxx")
        self.assertEqual(res, 0)

    def testms2knots(self):
        res = ms2knots(3.654)
        self.assertAlmostEqual(res, 7.102805, 5)
        res = ms2knots("xxx")
        self.assertEqual(res, 0)

    def testkmph2ms(self):
        res = kmph2ms(3.654)
        self.assertAlmostEqual(res, 1.015000, 5)
        res = kmph2ms("xxx")
        self.assertEqual(res, 0)

    def testknots2ms(self):
        res = knots2ms(3.654)
        self.assertAlmostEqual(res, 1.879781, 5)
        res = knots2ms("xxx")
        self.assertEqual(res, 0)

    def testpos2iso6709(self):
        res = pos2iso6709(53.12, -2.165, 35)
        self.assertEqual(res, "+53.12-2.165+35CRSWGS_84/")
        res = pos2iso6709("", -2.165, 35)
        self.assertEqual(res, "")

    def testhsv2rgb(self):
        res = hsv2rgb(0.5, 0.2, 0.9)
        self.assertEqual(res, "#b7e5e5")
        res = hsv2rgb(0.5, 0.0, 0.9)
        self.assertEqual(res, "#e5e5e5")

    def testhsv2rgb2(self):
        EXPECTED_RESULTS = [
            "#e5b7b7",
            "#e5e5b7",
            "#b7e5b7",
            "#b7e5e5",
            "#b7b7e5",
            "#e5b7e5",
        ]
        for i in range(6):
            h = i / 6
            res = hsv2rgb(h, 0.2, 0.9)
            self.assertEqual(res, EXPECTED_RESULTS[i])

    def teststr2rgb(self):
        res = str2rgb("#b7e5e5")
        self.assertEqual(res, (183, 229, 229))
        res = str2rgb("#e5e5e5")
        self.assertEqual(res, (229, 229, 229))

    def testsnr2col(self):
        res = snr2col(38)
        self.assertEqual(res, "#77cc28")

    def testsvid2gnss(self):
        EXPECTED_RESULT = [0, 3, 6, 1, 4, 5, 2]
        svids = (28, 50, 72, 140, 180, 200, 220)
        for i, svid in enumerate(svids):
            res = svid2gnssid(svid)
            self.assertEqual(res, EXPECTED_RESULT[i])

    def testcol2contrast(self):
        res = col2contrast("#ff0000")
        self.assertEqual(res, "white")
        res = col2contrast("#dddddd")
        self.assertEqual(res, "black")

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

    def testhaversine(self):
        res = haversine(51.23, -2.41, 34.205, 56.34)
        self.assertAlmostEqual(res, 5010.721853179245, 4)
        res = haversine(-12.645, 34.867, 145.1745, -56.27846)
        self.assertAlmostEqual(res, 10715.370876703888, 4)

    def testgetmpdistance(self):
        mp = [
            "TKC-EGA",
            "Wrens, GA",
            "RTCM 3.2",
            "1005(1),1074(1),1084(1),1094(1),1124(1),1230(1)",
            "",
            "GPS+GLO+GAL+BDS",
            "SNIP",
            "USA",
            "33.31",
            "-82.44",
            "1",
            "0",
            "sNTRIP",
            "none",
            "N",
            "N",
            "4200",
            "",
        ]
        res = get_mp_distance(34.123, 14.6743, mp)
        self.assertAlmostEqual(res, 8588.391732771786, 4)
        mp = [
            "tobetsu-tsujino",
            "Tobetsu",
            "RTCM 3.2",
            "1005(1),1077(1),1087(1),1127(1),1230(10)",
            "",
            "GPS+GLO+BDS",
            "SNIP",
            "JPN",
            "43.22",
            "141.52",
            "1",
            "0",
            "sNTRIP",
            "none",
            "N",
            "N",
            "8300",
            "",
        ]
        res = get_mp_distance(-34.123, -8.6743, mp)
        self.assertAlmostEqual(res, 17274.381937035745, 4)

    def teststringvar2val(self):
        vals = [
            ("53", "U001"),
            ("-513", "I002"),
            ("53.123", "R004"),
            ("GB", "C002"),
            ("0x1f1f0000", "X004"),
        ]
        ress = [53, -513, 53.123, b"GB", b"\x1f\x1f\x00\x00"]
        for i, (val, att) in enumerate(vals):
            res = stringvar2val(val, att)
            self.assertEqual(ress[i], res)

    def testdate2wnotow(self):
        dats = [
            (2023, 1, 1),
            (2005, 11, 5),
            (2020, 8, 20),
            (2014, 3, 16),
            (2023, 5, 21),
            (2023, 5, 27),
        ]
        vals = [
            (2243, 0),
            (1347, 518400),
            (2119, 345600),
            (1784, 0),
            (2263, 0),
            (2263, 518400),
        ]
        for i, dat in enumerate(dats):
            y, m, d = dat
            self.assertEqual(date2wnotow(datetime(y, m, d)), vals[i])

    def testwnotow2date(self):
        vals = [
            (2243, 0),
            (1347, 518400),
            (2119, 345600),
            (1784, 0),
            (2263, 0),
            (2263, 518400),
        ]
        dats = [
            "2023-01-01 00:00:00",
            "2005-11-05 00:00:00",
            "2020-08-20 00:00:00",
            "2014-03-16 00:00:00",
            "2023-05-21 00:00:00",
            "2023-05-27 00:00:00",
        ]
        for i, (wno, tow) in enumerate(vals):
            self.assertEqual(str(wnotow2date(wno, tow)), dats[i])
        (wno, tow) = date2wnotow(datetime(2020, 4, 12))
        self.assertEqual(wnotow2date(wno, tow), datetime(2020, 4, 12))

    def testbitsval(self):
        bits = [(7, 1), (8, 8), (22, 2), (24, 4), (40, 16)]
        EXPECTED_RESULT = [1, 8, 3, 15, None]

        bm = b"\x01\x08\x03\xf0\xff"
        for i, (ps, ln) in enumerate(bits):
            res = bitsval(bm, ps, ln)
            self.assertEqual(res, EXPECTED_RESULT[i])

    def testparserxm(self):
        EXPECTED_RESULT = [
            ("0c00", datetime(1988, 3, 1, 7, 40)),
            ("290900", datetime(1988, 7, 4, 2, 40)),
        ]
        RXM_SPARTNKEY = b"\xb5b\x026\x19\x00\x01\x02\x00\x00\x00\x02+\x00\xd0Y\xc8\r\x00\x03+\x00\x00\xdfl\x0e\x0c\x00)\t\x00D;"
        msg = UBXReader.parse(RXM_SPARTNKEY)
        res = parse_rxmspartnkey(msg)
        self.assertEqual(res, EXPECTED_RESULT)

    def testmapqcompress(self):
        PREC = 6
        points = [
            53.4245,
            -2.18663,
            52.1274,
            -2.2284,
            51.6603,
            -2.5285,
            50.9377,
            -2.0006,
            53.2004,
            -2.1511,
        ]
        encoded = mapq_compress(points, PREC)
        self.assertEqual(encoded, "gvw{dBjwmdCvkdnArqpAvho[fciQnibk@w`f_@wibiCf}dH")
        pnts = mapq_decompress(encoded, PREC)
        print(pnts)
        for i, pnt in enumerate(pnts):
            self.assertAlmostEqual(pnt, points[i], PREC)

    def testbytes2unit(self):  # test bytes2unit
        blist = [123, 5365, 97467383, 1982864663735305, 15234, 3, 0]
        bres = [
            (123, ""),
            (5.2392578125, "KB"),
            (92.95213985443115, "MB"),
            (1803.4049060000189, "TB"),
            (14.876953125, "KB"),
            (3, ""),
            (0, ""),
        ]
        for i, b in enumerate(blist):
            res = bytes2unit(b)
            print(res)
            # self.assertEqual(res, bres[i])

    def testsecs2unit(self):  # test secs2unit
        slist = [123, 5365, 97467383, 103, 15234, 3]
        sres = [
            (2.05, "mins"),
            (89.41666666666667, "mins"),
            (1128.094710648148, "days"),
            (1.7166666666666666, "mins"),
            (4.2316666666666665, "hrs"),
            (3, "secs"),
        ]
        for i, b in enumerate(slist):
            res = secs2unit(b)
            self.assertEqual(res, sres[i])

    def testwidgetgrid(self):  # ensure widgets.py is correctly defined
        NoneType = type(None)
        for wdg, wdict in widget_grid.items():
            self.assertIsInstance(wdg, str),
            self.assertIsInstance(wdict["menu"], (int, NoneType)),
            self.assertIsInstance(wdict["default"], bool),
            self.assertIsInstance(wdict["frm"], str),
            self.assertEqual(wdict["frm"][0:4], "frm_"),
            self.assertIsInstance(wdict["visible"], bool),


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
