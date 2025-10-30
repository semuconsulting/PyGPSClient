"""
Created on 3 Oct 2020

Static method tests for pygpsclient.helpers

@author: semuadmin
"""

# pylint: disable=line-too-long, invalid-name, missing-docstring, no-member

from subprocess import run, PIPE
import sys
import unittest
from io import StringIO


class StreamTest(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    def tearDown(self):
        pass

    def testpygpsclient(self):
        res = run(["pygpsclient", "-h"], stdout=PIPE, check=False)
        res = res.stdout.decode("utf-8")
        self.assertEqual(res[0:18], "usage: pygpsclient")


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
