"""
Created on 3 Oct 2020

Static method tests for pygpsclient.spartnmessage

@author: semuadmin
"""

import os
import unittest
from pygpsclient.spartnmessage import SPARTNReader


class StaticTest(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        dirname = os.path.dirname(__file__)
        self.streamSPARTN = open(os.path.join(dirname, "spartn_mqtt.log"), "rb")

    def tearDown(self):
        self.streamSPARTN.close()

    def testSPARTNLOG(
        self,
    ):  # test stream of SPARTN messages
        EXPECTED_RESULTS = (
            "<SPARTN(SPARTN-1X-OCB-GPS, msgType=0, msgSubtype=0, nData=37, eaf=1, crcType=2, frameCrc=2, timeTagtype=0, gnssTimeTag=3940, solutionId=5, solutionProcId=11)>",
            "<SPARTN(SPARTN-1X-OCB-GLO, msgType=0, msgSubtype=1, nData=33, eaf=1, crcType=2, frameCrc=3, timeTagtype=0, gnssTimeTag=14722, solutionId=5, solutionProcId=11)>",
            "<SPARTN(SPARTN-1X-OCB-GAL, msgType=0, msgSubtype=2, nData=34, eaf=1, crcType=2, frameCrc=3, timeTagtype=0, gnssTimeTag=3940, solutionId=5, solutionProcId=11)>",
            "<SPARTN(SPARTN-1X-OCB-GPS, msgType=0, msgSubtype=0, nData=37, eaf=1, crcType=2, frameCrc=2, timeTagtype=1, gnssTimeTag=413903145, solutionId=5, solutionProcId=11)>",
            "<SPARTN(SPARTN-1X-OCB-GLO, msgType=0, msgSubtype=1, nData=33, eaf=1, crcType=2, frameCrc=3, timeTagtype=1, gnssTimeTag=413913927, solutionId=5, solutionProcId=11)>",
            "<SPARTN(SPARTN-1X-OCB-GAL, msgType=0, msgSubtype=2, nData=34, eaf=1, crcType=2, frameCrc=3, timeTagtype=1, gnssTimeTag=413903145, solutionId=5, solutionProcId=11)>",
            "<SPARTN(SPARTN-1X-OCB-GPS, msgType=0, msgSubtype=0, nData=37, eaf=1, crcType=2, frameCrc=2, timeTagtype=0, gnssTimeTag=3950, solutionId=5, solutionProcId=11)>",
            "<SPARTN(SPARTN-1X-OCB-GLO, msgType=0, msgSubtype=1, nData=33, eaf=1, crcType=2, frameCrc=3, timeTagtype=0, gnssTimeTag=14732, solutionId=5, solutionProcId=11)>",
            "<SPARTN(SPARTN-1X-OCB-GAL, msgType=0, msgSubtype=2, nData=34, eaf=1, crcType=2, frameCrc=3, timeTagtype=0, gnssTimeTag=3950, solutionId=5, solutionProcId=11)>",
            "<SPARTN(SPARTN-1X-OCB-GPS, msgType=0, msgSubtype=0, nData=37, eaf=1, crcType=2, frameCrc=2, timeTagtype=0, gnssTimeTag=3955, solutionId=5, solutionProcId=11)>",
            "<SPARTN(SPARTN-1X-OCB-GLO, msgType=0, msgSubtype=1, nData=33, eaf=1, crcType=2, frameCrc=3, timeTagtype=0, gnssTimeTag=14737, solutionId=5, solutionProcId=11)>",
            "<SPARTN(SPARTN-1X-OCB-GAL, msgType=0, msgSubtype=2, nData=34, eaf=1, crcType=2, frameCrc=3, timeTagtype=0, gnssTimeTag=3955, solutionId=5, solutionProcId=11)>",
            "<SPARTN(SPARTN-1X-GAD, msgType=2, msgSubtype=0, nData=191, eaf=1, crcType=2, frameCrc=14, timeTagtype=0, gnssTimeTag=3960, solutionId=5, solutionProcId=11)>",
            "<SPARTN(SPARTN-1X-GAD, msgType=2, msgSubtype=0, nData=50, eaf=1, crcType=2, frameCrc=2, timeTagtype=0, gnssTimeTag=3960, solutionId=5, solutionProcId=11)>",
            "<SPARTN(SPARTN-1X-HPAC-GPS, msgType=1, msgSubtype=0, nData=590, eaf=1, crcType=2, frameCrc=12, timeTagtype=1, gnssTimeTag=413903160, solutionId=5, solutionProcId=11)>",
            "<SPARTN(SPARTN-1X-HPAC-GPS, msgType=1, msgSubtype=0, nData=584, eaf=1, crcType=2, frameCrc=4, timeTagtype=1, gnssTimeTag=413903160, solutionId=5, solutionProcId=11)>",
            "<SPARTN(SPARTN-1X-HPAC-GPS, msgType=1, msgSubtype=0, nData=554, eaf=1, crcType=2, frameCrc=6, timeTagtype=1, gnssTimeTag=413903160, solutionId=5, solutionProcId=11)>",
            "<SPARTN(SPARTN-1X-HPAC-GPS, msgType=1, msgSubtype=0, nData=554, eaf=1, crcType=2, frameCrc=6, timeTagtype=1, gnssTimeTag=413903160, solutionId=5, solutionProcId=11)>",
            "<SPARTN(SPARTN-1X-HPAC-GLO, msgType=1, msgSubtype=1, nData=456, eaf=1, crcType=2, frameCrc=2, timeTagtype=1, gnssTimeTag=413913942, solutionId=5, solutionProcId=11)>",
            "<SPARTN(SPARTN-1X-HPAC-GLO, msgType=1, msgSubtype=1, nData=415, eaf=1, crcType=2, frameCrc=4, timeTagtype=1, gnssTimeTag=413913942, solutionId=5, solutionProcId=11)>",
            "<SPARTN(SPARTN-1X-HPAC-GLO, msgType=1, msgSubtype=1, nData=433, eaf=1, crcType=2, frameCrc=6, timeTagtype=1, gnssTimeTag=413913942, solutionId=5, solutionProcId=11)>",
            "<SPARTN(SPARTN-1X-HPAC-GLO, msgType=1, msgSubtype=1, nData=380, eaf=1, crcType=2, frameCrc=9, timeTagtype=1, gnssTimeTag=413913942, solutionId=5, solutionProcId=11)>",
            "<SPARTN(SPARTN-1X-HPAC-GAL, msgType=1, msgSubtype=2, nData=565, eaf=1, crcType=2, frameCrc=1, timeTagtype=1, gnssTimeTag=413903160, solutionId=5, solutionProcId=11)>",
            "<SPARTN(SPARTN-1X-HPAC-GAL, msgType=1, msgSubtype=2, nData=565, eaf=1, crcType=2, frameCrc=1, timeTagtype=1, gnssTimeTag=413903160, solutionId=5, solutionProcId=11)>",
            "<SPARTN(SPARTN-1X-HPAC-GAL, msgType=1, msgSubtype=2, nData=524, eaf=1, crcType=2, frameCrc=6, timeTagtype=1, gnssTimeTag=413903160, solutionId=5, solutionProcId=11)>",
            "<SPARTN(SPARTN-1X-HPAC-GAL, msgType=1, msgSubtype=2, nData=465, eaf=1, crcType=2, frameCrc=13, timeTagtype=1, gnssTimeTag=413903160, solutionId=5, solutionProcId=11)>",
            "<SPARTN(SPARTN-1X-OCB-GPS, msgType=0, msgSubtype=0, nData=218, eaf=1, crcType=2, frameCrc=8, timeTagtype=1, gnssTimeTag=413903160, solutionId=5, solutionProcId=11)>",
            "<SPARTN(SPARTN-1X-OCB-GLO, msgType=0, msgSubtype=1, nData=152, eaf=1, crcType=2, frameCrc=2, timeTagtype=1, gnssTimeTag=413913942, solutionId=5, solutionProcId=11)>",
            "<SPARTN(SPARTN-1X-OCB-GAL, msgType=0, msgSubtype=2, nData=191, eaf=1, crcType=2, frameCrc=11, timeTagtype=1, gnssTimeTag=413903160, solutionId=5, solutionProcId=11)>",
            "<SPARTN(SPARTN-1X-OCB-GPS, msgType=0, msgSubtype=0, nData=37, eaf=1, crcType=2, frameCrc=2, timeTagtype=0, gnssTimeTag=3965, solutionId=5, solutionProcId=11)>",
            "<SPARTN(SPARTN-1X-OCB-GLO, msgType=0, msgSubtype=1, nData=33, eaf=1, crcType=2, frameCrc=3, timeTagtype=0, gnssTimeTag=14747, solutionId=5, solutionProcId=11)>",
            "<SPARTN(SPARTN-1X-OCB-GAL, msgType=0, msgSubtype=2, nData=34, eaf=1, crcType=2, frameCrc=3, timeTagtype=0, gnssTimeTag=3965, solutionId=5, solutionProcId=11)>",
            "<SPARTN(SPARTN-1X-OCB-GPS, msgType=0, msgSubtype=0, nData=37, eaf=1, crcType=2, frameCrc=2, timeTagtype=0, gnssTimeTag=3970, solutionId=5, solutionProcId=11)>",
            "<SPARTN(SPARTN-1X-OCB-GLO, msgType=0, msgSubtype=1, nData=33, eaf=1, crcType=2, frameCrc=3, timeTagtype=0, gnssTimeTag=14752, solutionId=5, solutionProcId=11)>",
            "<SPARTN(SPARTN-1X-OCB-GAL, msgType=0, msgSubtype=2, nData=34, eaf=1, crcType=2, frameCrc=3, timeTagtype=0, gnssTimeTag=3970, solutionId=5, solutionProcId=11)>",
        )

        i = 0
        raw = 0
        spr = SPARTNReader(self.streamSPARTN)
        for raw, parsed in spr.iterate():
            if raw is not None:
                self.assertEqual(str(parsed), EXPECTED_RESULTS[i])
                i += 1


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
