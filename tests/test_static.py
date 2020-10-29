'''
Created on 3 Oct 2020

Static method tests for pygpsclient.globals

@author: semuadmin
'''

import unittest

from pygpsclient.globals import *


class StaticTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testdeg2rad(self):
        res = deg2rad(147)
        self.assertEqual(res, 2.5656340004316647)

    def testcel2cart(self):
        res = cel2cart(34, 128)
        self.assertEqual(res, (-0.5104064950196395, 0.6532905223173859))

    def testdeg2dms(self):
        res = deg2dms(53.346, 'lat')
        self.assertEqual(res, ('53°20′45.6″N'))

    def testdeg2dmm(self):
        res = deg2dmm(-2.5463, 'lon')
        self.assertEqual(res, ('2°32.778′W'))

    def testm2ft(self):
        res = m2ft(39.234)
        self.assertEqual(res, 128.72047656)

    def testft2m(self):
        res = ft2m(124.063)
        self.assertEqual(res, 37.81440118993916)

    def testms2kmph(self):
        res = ms2kmph(3.654)
        self.assertEqual(res, 13.1544)

    def testms2mph(self):
        res = ms2mph(3.654)
        self.assertEqual(res, 8.17376684796)

    def testms2knots(self):
        res = ms2knots(3.654)
        self.assertEqual(res, 7.1028057933)

    def testkmph2ms(self):
        res = kmph2ms(3.654)
        self.assertEqual(res, 1.0150000812)

    def testknots2ms(self):
        res = knots2ms(3.654)
        self.assertEqual(res, 1.8797810521896)

    def testpos2iso6709(self):
        res = pos2iso6709(53.12, -2.165, 35)
        self.assertEqual(res, '+53.12-2.165+35CRSWGS_84/')


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
