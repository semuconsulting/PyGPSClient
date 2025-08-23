"""
Created on 3 Oct 2020

Static method tests for pygpsclient.helpers

@author: semuadmin
"""

# pylint: disable=missing-docstring

import unittest
from datetime import datetime

from pynmeagps import SET, NMEAMessage
from pyubx2 import UBXMessage, UBXReader

from pygpsclient.configuration import Configuration
from pygpsclient.globals import Area, AreaXY, Point, TrackPoint
from pygpsclient.helpers import (
    area_in_bounds,
    bitsval,
    bytes2unit,
    cel2cart,
    col2contrast,
    corrage2int,
    data2xy,
    date2wnotow,
    dop2str,
    fix2desc,
    ft2m,
    get_grid,
    get_mp_distance,
    get_mp_info,
    get_point_at_vector,
    get_track_bounds,
    haversine,
    hsv2rgb,
    isot2dt,
    kmph2ms,
    knots2ms,
    lanip,
    ll2xy,
    m2ft,
    ms2kmph,
    ms2knots,
    ms2mph,
    ned2vector,
    nmea2preset,
    normalise_area,
    parse_rxmspartnkey,
    point_in_bounds,
    pos2iso6709,
    publicip,
    reorder_range,
    secs2unit,
    snr2col,
    str2rgb,
    stringvar2val,
    svid2gnssid,
    time2str,
    ubx2preset,
    val2sphp,
    validURL,
    wnotow2date,
    xy2data,
    xy2ll,
)
from pygpsclient.mapquest import (
    compress_track,
    format_mapquest_request,
    mapq_compress,
    mapq_decompress,
)
from pygpsclient.widget_state import (
    DEFAULT,
    FRAME,
    MENU,
    VISIBLE,
    WidgetState,
)


class DummyFileHandler:

    def load_config(self, filename):
        if filename == "bad.json":
            return filename, {"xcheckforupdate_b": 0}, ""
        return filename, {"checkforupdate_b": 0}, ""


class DummyApp:  # Dummy App class

    def __init__(self):

        self.appmaster = "appmaster"
        self.widget_state = WidgetState()
        self.file_handler = DummyFileHandler()


class StaticTest(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    def tearDown(self):
        pass

    def testconfiguration(self):

        cfg = Configuration(DummyApp())
        self.assertEqual(cfg.get("bpsrate_n"), 9600)
        self.assertEqual(cfg.get("lbandclientdrat_n"), 2400)
        self.assertEqual(cfg.get("userport_s"), "")
        self.assertEqual(cfg.get("spartnport_s"), "")
        self.assertEqual(len(cfg.settings), 140)
        kwargs = {"userport": "/dev/ttyACM0", "spartnport": "/dev/ttyACM1"}
        cfg.loadcli(**kwargs)
        self.assertEqual(cfg.get("userport_s"), "/dev/ttyACM0")
        self.assertEqual(cfg.get("spartnport_s"), "/dev/ttyACM1")
        cfg.set("userport_s", "/dev/ttyACM2")
        cfg.set("spartnport_s", "/dev/ttyACM3")
        self.assertEqual(cfg.get("userport_s"), "/dev/ttyACM2")
        self.assertEqual(cfg.get("spartnport_s"), "/dev/ttyACM3")

    def testloadfile(self):

        cfg = Configuration(DummyApp())
        res = cfg.loadfile("bad.json")
        self.assertEqual(
            res, ("bad.json", f'Unrecognised setting "xcheckforupdate_b": 0')
        )
        res = cfg.loadfile("good.json")
        self.assertEqual(res, ("good.json", ""))

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
        res = validURL(None)
        self.assertEqual(res, False)
        res = validURL("")
        self.assertEqual(res, False)
        # res = validURL("192.168,0.72")
        # self.assertEqual(res, False)
        # res = validURL("sdfffasdff")
        # self.assertEqual(res, False)

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
        # print(pnts)
        for i, pnt in enumerate(pnts):
            self.assertAlmostEqual(pnt, points[i], PREC)

    def testcompresstrack(self):
        points = [
            Point(53.4245, -2.18663),
            Point(52.1274, -2.2284),
            Point(51.6603, -2.5285),
            Point(50.9377, -2.0006),
            Point(53.2004, -2.1511),
        ]
        encoded = compress_track(points)
        self.assertEqual(encoded, "gvw{dBjwmdCvkdnArqpAvho[fciQnibk@w`f_@wibiCf}dH")
        encoded = compress_track(points, limit=3)
        self.assertEqual(encoded, "gvw{dBjwmdCnutjBzuzSg__}Aob`V")

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
            # print(res)
            self.assertEqual(res, bres[i])

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

    def testval2sphp(self):  # test val2sphp
        slist = [(54.123456789, 1e-7), (-2.2498765437, 1e-7), (145.123456789, 1e-2)]
        sres = [(541234567, 89), (-22498765, -44), (14512, 35)]
        for i, b in enumerate(slist):
            val, scale = b
            res = val2sphp(val, scale)
            self.assertEqual(res, sres[i])

    def testwidgetgrid(self):  # ensure widgets.py is correctly defined
        app = DummyApp()
        NoneType = type(None)
        for wdg, wdict in app.widget_state.state.items():
            self.assertIsInstance(wdg, str),
            self.assertIsInstance(wdict.get(MENU, True), bool),
            self.assertIsInstance(wdict.get(DEFAULT, False), bool),
            self.assertIsInstance(wdict[FRAME], str),
            self.assertEqual(wdict["frm"][0:4], "frm_"),
            self.assertIsInstance(wdict[VISIBLE], bool),

    def testned2vector(self):  # test ned2vector
        relPosN = -879166 + 0 * 1e-2
        relPosE = -6068417 + 3.9 * 1e-2
        relPosD = 29273 + 2.4 * 1e-2
        dis, hdg = ned2vector(relPosN, relPosE, relPosD)
        self.assertEqual(int(dis), 6131841)
        self.assertAlmostEqual(hdg, 261.7566, 4)
        relPosN = 267987 + 5.1 * 1e-2
        relPosE = -8849794 + 0 * 1e-2
        relPosD = 58193 + 9 * 1e-2
        dis, hdg = ned2vector(relPosN, relPosE, relPosD)
        self.assertEqual(int(dis), 8854041)
        self.assertAlmostEqual(hdg, 271.7345, 4)
        relPosN = 0
        relPosE = -8849794 + 0 * 1e-2
        relPosD = 58193 + 9 * 1e-2
        dis, hdg = ned2vector(relPosN, relPosE, relPosD)
        self.assertEqual(int(dis), 8849985)
        self.assertAlmostEqual(hdg, 0, 4)

    def testgetmpinfo(self):  # test get_mp_info
        EXPECTED_RESULT = {
            "name": "ACACU",
            "identifier": "Curug",
            "format": "RTCM 3.2",
            "messages": "1005(31),1074(1),1084(1),1094(1)",
            "carrier": "L1,L2",
            "navs": "GPS+GLO+GAL",
            "network": "SNIP",
            "country": "SRB",
            "lat": "45.47",
            "lon": "20.06",
            "gga": "GGA",
            "solution": "Single",
            "generator": "sNTRIP",
            "encrypt": "none",
            "auth": "Basic",
            "fee": "N",
            "bitrate": "3120",
        }
        srt = (
            "ACACU",
            "Curug",
            "RTCM 3.2",
            "1005(31),1074(1),1084(1),1094(1)",
            "2",
            "GPS+GLO+GAL",
            "SNIP",
            "SRB",
            "45.47",
            "20.06",
            "1",
            "0",
            "sNTRIP",
            "none",
            "B",
            "N",
            "3120",
            "",
        )
        res = get_mp_info(srt)
        self.assertEqual(res, EXPECTED_RESULT)
        res = get_mp_info([])
        self.assertEqual(res, None)

    def testpublicip(self):
        res = publicip()
        # print(res)
        if res != "N/A":
            self.assertRegex(res, r"^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)\.?\b){4}$")

    def testlanip(self):
        res = lanip()
        # print(res)
        self.assertRegex(res, r"^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)\.?\b){4}$")

    def testiso2dt(self):  # test secs2unit
        tims = [
            "2023-12-11T14:55:08.730000Z",
            "2023-12-11T14:55:08.730000",
            "2023-12-11T14:55:08.730Z",
            "2023-12-11T14:55:08.730",
            "2023-12-11T14:55:08",
        ]
        dts = [
            "1702306508.73",
            "1702306508.73",
            "1702306508.73",
            "1702306508.73",
            "1702306508.0",
        ]
        for i, t in enumerate(tims):
            res = isot2dt(t)
            # print(res)
            self.assertEqual(str(res), dts[i])

    def testgetpointatvector(self):
        res = get_point_at_vector(Point(51.23, -2.41), 23.65, 123.45)
        self.assertAlmostEqual(res.lat, 51.22988289442865, 4)
        self.assertAlmostEqual(res.lon, -2.4097169220939443, 4)
        res = get_point_at_vector(Point(-12.645, 34.867), 145.1745, 56.27846)
        self.assertAlmostEqual(res.lat, -12.644276003524272, 4)
        self.assertAlmostEqual(res.lon, 34.868111659923926, 4)

    def testpointinbounds(self):
        res = point_in_bounds(Area(51.23, -2.41, 51.45, -2.13), Point(23.65, 45.123))
        self.assertEqual(res, False)
        res = point_in_bounds(Area(51.23, -2.41, 51.45, -2.13), Point(51.24, -2.39))
        self.assertEqual(res, True)

    def testareainbounds(self):
        res = area_in_bounds(Area(51.23, -2.41, 51.45, -2.13), Area(52, -3, 53, -2))
        self.assertEqual(res, False)
        res = area_in_bounds(
            Area(51.23, -2.41, 51.45, -2.13), Area(51.24, -2.39, 51.44, -2.15)
        )
        self.assertEqual(res, True)

    def testll2xy(self):
        bounds = Area(53, -2, 54, -1)
        (x, y) = ll2xy(600, 400, bounds, Point(53.5, -1.5))
        self.assertEqual(x, 300, 5)
        self.assertEqual(y, 200, 5)
        (x, y) = ll2xy(600, 400, bounds, Point(53.52345, -1.81264))
        self.assertAlmostEqual(x, 112.416, 5)
        self.assertAlmostEqual(y, 190.620, 5)

    def testxy2ll(self):
        bounds = Area(53, -2, 54, -1)
        pos = xy2ll(600, 400, bounds, (300, 200))
        self.assertEqual(pos.lat, 53.5, 5)
        self.assertEqual(pos.lon, -1.5, 5)
        pos = xy2ll(600, 400, bounds, (112.416, 190.620))
        self.assertAlmostEqual(pos.lat, 53.52345, 5)
        self.assertAlmostEqual(pos.lon, -1.81264, 5)

    def testdata2xy(self):
        bounds = AreaXY(-2, 53, -1, 54)
        x, y = data2xy(600, 400, bounds, -1.5, 53.5)
        self.assertEqual(x, 300, 5)
        self.assertEqual(y, 200, 5)
        x, y = data2xy(600, 400, bounds, -1.81264, 53.52345)
        self.assertAlmostEqual(x, 112.416, 5)
        self.assertAlmostEqual(y, 190.620, 5)
        x, y = data2xy(600, 400, bounds, -1.81264, 53.52345, 7, 5)
        self.assertAlmostEqual(x, 119.416, 5)
        self.assertAlmostEqual(y, 195.620, 5)

    def testxy2data(self):
        bounds = AreaXY(-2, 53, -1, 54)
        dx, dy = xy2data(600, 400, bounds, 300, 200)
        self.assertEqual(dx, -1.5, 5)
        self.assertEqual(dy, 53.5, 5)
        dx, dy = xy2data(600, 400, bounds, 112.416, 190.620)
        self.assertAlmostEqual(dx, -1.81264, 5)
        self.assertAlmostEqual(dy, 53.52345, 5)
        dx, dy = xy2data(600, 400, bounds, 119.416, 195.620, 7, 5)
        self.assertAlmostEqual(dx, -1.81264, 5)
        self.assertAlmostEqual(dy, 53.52345, 5)

    def testnormalise_area(self):
        points = (53, -2, 54, -1)
        res = normalise_area(points)
        self.assertEqual(res, Area(53, -2, 54, -1))
        points = (54, -2, 53, -1)
        res = normalise_area(points)
        self.assertEqual(res, Area(53, -2, 54, -1))
        points = (53, -1, 54, -2)
        res = normalise_area(points)
        self.assertEqual(res, Area(53, -2, 54, -1))
        points = (53, -2, 54)
        with self.assertRaises(ValueError) as context:
            res = normalise_area(points)
            self.assertTrue("Exactly 4 points required" in str(context.exception))

    def testreorderrange(self):
        rng1 = (1, 2, 5, 10, 20, 50, 100)
        res1 = (5, 10, 20, 50, 100, 1, 2)
        rng2 = ("apples", "oranges", "pears")
        res2 = ("pears", "apples", "oranges")
        self.assertEqual(reorder_range(rng1, 5), res1)
        self.assertEqual(reorder_range(rng2, "pears"), res2)
        self.assertEqual(reorder_range(rng1, 44), rng1)
        self.assertEqual(reorder_range(rng2, "limes"), rng2)

    def testformat_mapquest_request(self):
        EXPECTED_RESULT1 = "https://www.mapquestapi.com/staticmap/v5/map?key=abcdefghijklmnop&type=map&size=600,400&zoom=3&scalebar=true|bottom"
        EXPECTED_RESULT2 = "https://www.mapquestapi.com/staticmap/v5/map?key=abcdefghijklmnop&type=map&size=600,400&boundingBox=50,30,40,40&margin=0&scalebar=true|bottom"
        EXPECTED_RESULT3 = "https://www.mapquestapi.com/staticmap/v5/map?key=abcdefghijklmnop&type=map&size=600,400&zoom=3&scalebar=true|bottom"
        res = format_mapquest_request(
            "abcdefghijklmnop", "map", 600, 400, 3, (Point(45, 34),), None, 5.345
        )
        # print(res)
        self.assertEqual(res, EXPECTED_RESULT1)
        res = format_mapquest_request(
            "abcdefghijklmnop",
            "map",
            600,
            400,
            3,
            (Point(45, 34),),
            Area(40, 30, 50, 40),
            5.345,
        )
        # print(res)
        self.assertEqual(res, EXPECTED_RESULT2)
        res = format_mapquest_request(
            "abcdefghijklmnop",
            "map",
            600,
            400,
            3,
            (Point(45, 34), Point(45.2, 34.3), Point(46, 35)),
            None,
            5.345,
        )
        # print(res)
        self.assertEqual(res, EXPECTED_RESULT3)

    def testgetgrid(self):
        res = get_grid(7)
        self.assertEqual(res, (0.0, 0.1667, 0.3333, 0.5, 0.6667, 0.8333, 1.0))
        res = get_grid()
        self.assertEqual(
            res,
            (0.0, 0.1111, 0.2222, 0.3333, 0.4444, 0.5556, 0.6667, 0.7778, 0.8889, 1.0),
        )
        res = get_grid(13)
        self.assertEqual(
            res,
            (
                0.0,
                0.0833,
                0.1667,
                0.25,
                0.3333,
                0.4167,
                0.5,
                0.5833,
                0.6667,
                0.75,
                0.8333,
                0.9167,
                1.0,
            ),
        )
        res = get_grid(13, 0, 100, False)
        self.assertEqual(
            res,
            (
                0.0,
                7.6923,
                15.3846,
                23.0769,
                30.7692,
                38.4615,
                46.1538,
                53.8462,
                61.5385,
                69.2308,
                76.9231,
                84.6154,
                92.3077,
            ),
        )

    def testtime2str(self):
        res = time2str(1732547672)
        self.assertEqual(res, "15:14:32")
        res = time2str(1732547874.264534, "%H:%M:%S.%f")
        self.assertEqual(res, "15:17:54.264534")
        res = time2str(1732461337.123412, "%a, %d %b %Y %H:%M:%S +0000")
        self.assertEqual(res, "Sun, 24 Nov 2024 15:15:37 +0000")

    def testneam2preset(self):
        msg = NMEAMessage("P", "QTMHOT", SET)
        self.assertEqual(nmea2preset(msg), "PQTMHOT SET; P; QTMHOT; ; 1")
        msg1 = NMEAMessage(
            "P", "QTMCFGUART", SET, portid=1, baudrate=115200, databit=8, stopbit=1
        )
        msg2 = NMEAMessage(
            "P", "QTMCFGUART", SET, portid=2, baudrate=460800, databit=8, stopbit=1
        )
        self.assertEqual(
            nmea2preset(msg1, "Configure UART Port"),
            "Configure UART Port; P; QTMCFGUART; W,1,115200,8,0,1,0; 1",
        )
        self.assertEqual(
            nmea2preset((msg1, msg2), "Configure UART Ports"),
            "Configure UART Ports; P; QTMCFGUART; W,1,115200,8,0,1,0; 1; P; QTMCFGUART; W,2,460800,8,0,1,0; 1",
        )

    def testubx2preset(self):
        msg1 = UBXMessage(
            "CFG",
            "CFG-GNSS",
            SET,
            parsebitfield=False,
            numTrkChHw=2,
            numTrkChUse=4,
            numConfigBlocks=2,
            gnssId_01=0,
            resTrkCh_01=4,
            maxTrkCh_01=32,
            flags_01=b"\x01\x00\x04\x00",
            gnssId_02=6,
            resTrkCh_02=3,
            maxTrkCh_02=24,
            flags_02=b"\x00\x00\x40\x00",
        )
        msg2 = UBXMessage(
            "CFG",
            "CFG-GNSS",
            SET,
            parsebitfield=False,
            numTrkChHw=2,
            numTrkChUse=4,
            numConfigBlocks=2,
            gnssId_01=0,
            resTrkCh_01=4,
            maxTrkCh_01=32,
            flags_01=b"\x01\x00\x04\x00",
            gnssId_02=5,
            resTrkCh_02=3,
            maxTrkCh_02=24,
            flags_02=b"\x00\x00\x40\x00",
        )
        self.assertEqual(
            ubx2preset(msg1, "Configure GNSS"),
            "Configure GNSS, CFG, CFG-GNSS, 0002040200042000010004000603180000004000, 1",
        )
        self.assertEqual(
            ubx2preset((msg1, msg2), "Configure GNSS"),
            "Configure GNSS, CFG, CFG-GNSS, 0002040200042000010004000603180000004000, 1, CFG, CFG-GNSS, 0002040200042000010004000503180000004000, 1",
        )

    def testdop2str(self):
        dops = [
            "N/A",
            "Ideal",
            "Ideal",
            "Excellent",
            "Excellent",
            "Good",
            "Moderate",
            "Fair",
            "Poor",
        ]
        i = 0
        for dop in (0, 0.9, 1, 1.4, 2, 5, 10, 20, 30):
            res = dop2str(dop)
            self.assertEqual(res, dops[i])
            i += 1

    def testtrackbounds(self):
        track = [
            TrackPoint(
                lat=53.367779,
                lon=-1.815559,
                tim=1432993248.436,
                ele=295.0,
                spd=6.715710540781448,
            ),
            TrackPoint(
                lat=53.367763,
                lon=-1.815568,
                tim=1432993249.444,
                ele=295.0,
                spd=6.711882545529664,
            ),
            TrackPoint(
                lat=53.367691,
                lon=-1.815627,
                tim=1432993254.612,
                ele=297.0,
                spd=6.2148578220195745,
            ),
            TrackPoint(
                lat=53.367678,
                lon=-1.81564,
                tim=1432993255.365,
                ele=296.0,
                spd=8.064486989308314,
            ),
            TrackPoint(
                lat=53.367599,
                lon=-1.815695,
                tim=1432993265.43,
                ele=298.0,
                spd=3.4061951929567766,
            ),
            TrackPoint(
                lat=53.36759,
                lon=-1.815702,
                tim=1432993266.428,
                ele=299.0,
                spd=3.9833901087479853,
            ),
            TrackPoint(
                lat=53.367503,
                lon=-1.815736,
                tim=1432993272.462,
                ele=300.0,
                spd=5.933328376978552,
            ),
            TrackPoint(
                lat=53.367487,
                lon=-1.815725,
                tim=1432993273.432,
                ele=301.0,
                spd=7.142276157762976,
            ),
            TrackPoint(
                lat=53.367508,
                lon=-1.815593,
                tim=1432993280.436,
                ele=301.0,
                spd=4.663893711961502,
            ),
            TrackPoint(
                lat=53.367507,
                lon=-1.815571,
                tim=1432993281.437,
                ele=302.0,
                spd=5.262069550081461,
            ),
            TrackPoint(
                lat=53.367462,
                lon=-1.815451,
                tim=1432993288.36,
                ele=306.0,
                spd=4.895293914921759,
            ),
            TrackPoint(
                lat=53.367455,
                lon=-1.815433,
                tim=1432993289.528,
                ele=307.0,
                spd=4.394047941517249,
            ),
            TrackPoint(
                lat=53.36746,
                lon=-1.815304,
                tim=1432993295.4,
                ele=304.0,
                spd=5.264155466815996,
            ),
            TrackPoint(
                lat=53.367463,
                lon=-1.815283,
                tim=1432993296.446,
                ele=304.0,
                spd=4.928306385908393,
            ),
            TrackPoint(
                lat=53.367495,
                lon=-1.815155,
                tim=1432993310.396,
                ele=303.0,
                spd=2.3788542131221404,
            ),
            TrackPoint(
                lat=53.367496,
                lon=-1.815138,
                tim=1432993311.444,
                ele=302.0,
                spd=3.890445235062791,
            ),
        ]
        bounds, center = get_track_bounds(track)
        self.assertEqual(
            bounds, Area(lat1=53.367455, lon1=-1.815736, lat2=53.367779, lon2=-1.815138)
        )
        self.assertAlmostEqual(center.lat, 53.367617, 7)
        self.assertAlmostEqual(center.lon, -1.815437, 7)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
