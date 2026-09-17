"""
test_tk.py

Static method tests for Tk methods

NB: THESE TESTS WILL FAIL IN A HEADLESS NON-WINDOW ENVIRONMENT

Created on 5 Nov 2025

:author: semuadmin (Steve Smith)
:copyright: 2020 semuadmin
:license: BSD 3-Clause
"""

# pylint: disable=missing-docstring

import unittest

from tkinter import Entry, Tk, TclError
from pygpsclient.globals import (
    VALBLANK,
    VALNONBLANK,
    VALNONSPACE,
    VALINT,
    VALFLOAT,
    VALURL,
    VALHEX,
    VALDMY,
    VALLEN,
    VALREGEX,
    VALCUSTOM,
)
from pygpsclient.helpers import validate

NMEAPREREGEX = r"^(?:(?:[^;]+;){3}\s?[0-2];?)+$"

class TkTest(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    def tearDown(self):
        pass

    def testEntryValidate(self):

        def customfunc(val) -> bool:

            try:
                return 5 < int(val) < 12
            except ValueError:
                return False

        try:

            root = Tk()
            Entry.validate = validate
            ent = Entry(root)
            ent.insert(0, "333")
            self.assertTrue(ent.validate(VALINT))
            ent.insert(0, "xxx")
            self.assertFalse(ent.validate(VALINT))
            ent = Entry(root)
            ent.insert(0, "1.2")
            self.assertTrue(ent.validate(VALFLOAT))
            ent.insert(0, "xxx")
            self.assertFalse(ent.validate(VALFLOAT))
            ent.insert(0, "xxx")
            self.assertTrue(ent.validate(VALNONBLANK))
            ent = Entry(root)
            ent.insert(0, "")
            self.assertFalse(ent.validate(VALNONBLANK))
            ent.insert(0, "aabb")
            self.assertTrue(ent.validate(VALHEX))
            ent.insert(0, "xxxx")
            self.assertFalse(ent.validate(VALHEX))
            ent.insert(0, "20030412")
            self.assertTrue(ent.validate(VALDMY))
            ent.insert(0, "20039999")
            self.assertFalse(ent.validate(VALDMY))
            ent = Entry(root)
            ent.insert(0, "xxx")
            self.assertTrue(ent.validate(VALNONSPACE))
            ent = Entry(root)
            ent.insert(0, "     ")
            self.assertFalse(ent.validate(VALNONSPACE))
            ent = Entry(root)
            ent.insert(0, "")
            self.assertTrue(ent.validate(VALBLANK))
            self.assertFalse(ent.validate(VALURL))
            ent.insert(0, "localhost")
            self.assertTrue(ent.validate(VALURL))
            self.assertTrue(ent.validate(VALLEN, 8, 9))
            self.assertFalse(ent.validate(VALLEN, 3, 4))
            ent.delete(0 ,'end')
            ent.insert(0, "P; QTMCFGUART; W,115200; 1")
            self.assertTrue(ent.validate(VALREGEX, regex=NMEAPREREGEX))
            ent.delete(0 ,'end')
            ent.insert(0, "P; QTMCFGUART; W,115200; 1;P; QTMCFGUART; W,230400; 1;P; QTMCFGUART; W,460800; 1")
            self.assertTrue(ent.validate(VALREGEX, regex=NMEAPREREGEX))
            ent.delete(0 ,'end')
            ent.insert(0, "P; QTMCFGUART; W,115200; 1;P; QTMCFGUART; W,230400; 4;P; QTMCFGUART; W,460800; 1")
            self.assertFalse(ent.validate(VALREGEX, regex=NMEAPREREGEX))
            ent.delete(0 ,'end')
            ent.insert(0, "P; QTMCFGUART; W,115200; 4")
            self.assertFalse(ent.validate(VALREGEX, regex=NMEAPREREGEX))
            ent.delete(0 ,'end')
            ent.insert(0, "P, QTMCFGUART, W,115200, 1")
            self.assertFalse(ent.validate(VALREGEX, regex=NMEAPREREGEX))
            ent.delete(0 ,'end')
            ent.insert(0, "")
            self.assertFalse(ent.validate(VALREGEX, regex=NMEAPREREGEX))
            ent.delete(0 ,'end')
            ent.insert(0, '9')
            self.assertTrue(ent.validate(VALCUSTOM, func=customfunc))
            ent.delete(0 ,'end')
            ent.insert(0, '18')
            self.assertFalse(ent.validate(VALCUSTOM, func=customfunc))
            ent.delete(0 ,'end')
            ent.insert(0, 'D')
            self.assertFalse(ent.validate(VALCUSTOM, func=customfunc))

        except TclError as err:
            if str(err) == "no display name and no $DISPLAY environment variable":
                print(f"{err}\nCan't execute this test without Window environment")
            else:
                raise TclError from err
