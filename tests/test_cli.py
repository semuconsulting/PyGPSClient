"""
test_cli.py

Static method tests for CLI entry points.

Created on 3 Oct 2020

:author: semuadmin (Steve Smith)
:copyright: 2020 semuadmin
:license: BSD 3-Clause
"""

# pylint: disable=line-too-long, invalid-name, missing-docstring, no-member

from subprocess import run, PIPE
import unittest


class StreamTest(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    def tearDown(self):
        pass

    def testpygpsclient(self):
        try:
            res = run(["pygpsclient", "-h"], stdout=PIPE, check=False)
            res = res.stdout.decode("utf-8")
            self.assertEqual(res[0:18], "usage: pygpsclient")
        except FileNotFoundError:
            print("Install pygpsclient binary and rerun test")


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
