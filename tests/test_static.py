'''
Created on 3 Oct 2020

Static method tests for pygpsclient.globals

@author: semuadmin
'''

import unittest
from pytest import approx

from pygpsclient.globals import *


class StaticTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testdeg2rad(self):
        res = deg2rad(147)
        assert res == approx(2.565634)

    def testcel2cart(self):
        (elev, azim) = cel2cart(34, 128)
        assert elev == approx(-0.510406)
        assert azim == approx(0.653290)

    def testdeg2dms(self):
        res = deg2dms(53.346, 'lat')
        self.assertEqual(res, ('53°20′45.6″N'))

    def testdeg2dmm(self):
        res = deg2dmm(-2.5463, 'lon')
        self.assertEqual(res, ('2°32.778′W'))

    def testm2ft(self):
        res = m2ft(39.234)
        assert res == approx(128.720476)

    def testft2m(self):
        res = ft2m(124.063)
        assert res == approx(37.814401)

    def testms2kmph(self):
        res = ms2kmph(3.654)
        assert res == approx(13.154400)

    def testms2mph(self):
        res = ms2mph(3.654)
        assert res == approx(8.173766)

    def testms2knots(self):
        res = ms2knots(3.654)
        assert res == approx(7.102805)

    def testkmph2ms(self):
        res = kmph2ms(3.654)
        assert res == approx(1.015000)

    def testknots2ms(self):
        res = knots2ms(3.654)
        assert res == approx(1.879781)

    def testpos2iso6709(self):
        res = pos2iso6709(53.12, -2.165, 35)
        self.assertEqual(res, '+53.12-2.165+35CRSWGS_84/')


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
