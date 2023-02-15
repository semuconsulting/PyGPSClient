"""
Created on 3 Oct 2020

Static method tests for pygpsclient.spartnmessage

@author: semuadmin
"""

import os
import unittest
from pygpsclient.spartnmessage import SPARTNReader


class StreamTest(unittest.TestCase):
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
            "<SPARTN(SPARTN-1X-OCB-GPS, msgType=0, nData=37, eaf=1, crcType=2, frameCrc=2, msgSubtype=0, timeTagtype=0, gnssTimeTag=3940, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=3, authInd=1, embAuthLen=0, crc=7556915)>",
            "<SPARTN(SPARTN-1X-OCB-GLO, msgType=0, nData=33, eaf=1, crcType=2, frameCrc=3, msgSubtype=1, timeTagtype=0, gnssTimeTag=14722, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=42, authInd=1, embAuthLen=0, crc=13784453)>",
            "<SPARTN(SPARTN-1X-OCB-GAL, msgType=0, nData=34, eaf=1, crcType=2, frameCrc=3, msgSubtype=2, timeTagtype=0, gnssTimeTag=3940, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=63, authInd=1, embAuthLen=0, crc=15726580)>",
            "<SPARTN(SPARTN-1X-OCB-GPS, msgType=0, nData=37, eaf=1, crcType=2, frameCrc=2, msgSubtype=0, timeTagtype=1, gnssTimeTag=413903145, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=4, authInd=1, embAuthLen=0, crc=6997525)>",
            "<SPARTN(SPARTN-1X-OCB-GLO, msgType=0, nData=33, eaf=1, crcType=2, frameCrc=3, msgSubtype=1, timeTagtype=1, gnssTimeTag=413913927, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=43, authInd=1, embAuthLen=0, crc=11358619)>",
            "<SPARTN(SPARTN-1X-OCB-GAL, msgType=0, nData=34, eaf=1, crcType=2, frameCrc=3, msgSubtype=2, timeTagtype=1, gnssTimeTag=413903145, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=0, authInd=1, embAuthLen=0, crc=16183954)>",
            "<SPARTN(SPARTN-1X-OCB-GPS, msgType=0, nData=37, eaf=1, crcType=2, frameCrc=2, msgSubtype=0, timeTagtype=0, gnssTimeTag=3950, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=5, authInd=1, embAuthLen=0, crc=9417614)>",
            "<SPARTN(SPARTN-1X-OCB-GLO, msgType=0, nData=33, eaf=1, crcType=2, frameCrc=3, msgSubtype=1, timeTagtype=0, gnssTimeTag=14732, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=44, authInd=1, embAuthLen=0, crc=2885277)>",
            "<SPARTN(SPARTN-1X-OCB-GAL, msgType=0, nData=34, eaf=1, crcType=2, frameCrc=3, msgSubtype=2, timeTagtype=0, gnssTimeTag=3950, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=1, authInd=1, embAuthLen=0, crc=7937704)>",
            "<SPARTN(SPARTN-1X-OCB-GPS, msgType=0, nData=37, eaf=1, crcType=2, frameCrc=2, msgSubtype=0, timeTagtype=0, gnssTimeTag=3955, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=6, authInd=1, embAuthLen=0, crc=2323099)>",
            "<SPARTN(SPARTN-1X-OCB-GLO, msgType=0, nData=33, eaf=1, crcType=2, frameCrc=3, msgSubtype=1, timeTagtype=0, gnssTimeTag=14737, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=45, authInd=1, embAuthLen=0, crc=6930276)>",
            "<SPARTN(SPARTN-1X-OCB-GAL, msgType=0, nData=34, eaf=1, crcType=2, frameCrc=3, msgSubtype=2, timeTagtype=0, gnssTimeTag=3955, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=2, authInd=1, embAuthLen=0, crc=1602694)>",
            "<SPARTN(SPARTN-1X-GAD, msgType=2, nData=191, eaf=1, crcType=2, frameCrc=14, msgSubtype=0, timeTagtype=0, gnssTimeTag=3960, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=63, authInd=1, embAuthLen=0, crc=13757653)>",
            "<SPARTN(SPARTN-1X-GAD, msgType=2, nData=50, eaf=1, crcType=2, frameCrc=2, msgSubtype=0, timeTagtype=0, gnssTimeTag=3960, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=0, authInd=1, embAuthLen=0, crc=11582036)>",
            "<SPARTN(SPARTN-1X-HPAC-GPS, msgType=1, nData=590, eaf=1, crcType=2, frameCrc=12, msgSubtype=0, timeTagtype=1, gnssTimeTag=413903160, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=52, authInd=1, embAuthLen=0, crc=7879592)>",
            "<SPARTN(SPARTN-1X-HPAC-GPS, msgType=1, nData=584, eaf=1, crcType=2, frameCrc=4, msgSubtype=0, timeTagtype=1, gnssTimeTag=413903160, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=53, authInd=1, embAuthLen=0, crc=5046464)>",
            "<SPARTN(SPARTN-1X-HPAC-GPS, msgType=1, nData=554, eaf=1, crcType=2, frameCrc=6, msgSubtype=0, timeTagtype=1, gnssTimeTag=413903160, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=54, authInd=1, embAuthLen=0, crc=14377135)>",
            "<SPARTN(SPARTN-1X-HPAC-GPS, msgType=1, nData=554, eaf=1, crcType=2, frameCrc=6, msgSubtype=0, timeTagtype=1, gnssTimeTag=413903160, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=55, authInd=1, embAuthLen=0, crc=5226642)>",
            "<SPARTN(SPARTN-1X-HPAC-GLO, msgType=1, nData=456, eaf=1, crcType=2, frameCrc=2, msgSubtype=1, timeTagtype=1, gnssTimeTag=413913942, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=11, authInd=1, embAuthLen=0, crc=4825390)>",
            "<SPARTN(SPARTN-1X-HPAC-GLO, msgType=1, nData=415, eaf=1, crcType=2, frameCrc=4, msgSubtype=1, timeTagtype=1, gnssTimeTag=413913942, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=12, authInd=1, embAuthLen=0, crc=2661822)>",
            "<SPARTN(SPARTN-1X-HPAC-GLO, msgType=1, nData=433, eaf=1, crcType=2, frameCrc=6, msgSubtype=1, timeTagtype=1, gnssTimeTag=413913942, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=13, authInd=1, embAuthLen=0, crc=4661009)>",
            "<SPARTN(SPARTN-1X-HPAC-GLO, msgType=1, nData=380, eaf=1, crcType=2, frameCrc=9, msgSubtype=1, timeTagtype=1, gnssTimeTag=413913942, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=14, authInd=1, embAuthLen=0, crc=6432064)>",
            "<SPARTN(SPARTN-1X-HPAC-GAL, msgType=1, nData=565, eaf=1, crcType=2, frameCrc=1, msgSubtype=2, timeTagtype=1, gnssTimeTag=413903160, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=15, authInd=1, embAuthLen=0, crc=9900363)>",
            "<SPARTN(SPARTN-1X-HPAC-GAL, msgType=1, nData=565, eaf=1, crcType=2, frameCrc=1, msgSubtype=2, timeTagtype=1, gnssTimeTag=413903160, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=16, authInd=1, embAuthLen=0, crc=3171880)>",
            "<SPARTN(SPARTN-1X-HPAC-GAL, msgType=1, nData=524, eaf=1, crcType=2, frameCrc=6, msgSubtype=2, timeTagtype=1, gnssTimeTag=413903160, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=17, authInd=1, embAuthLen=0, crc=3600973)>",
            "<SPARTN(SPARTN-1X-HPAC-GAL, msgType=1, nData=465, eaf=1, crcType=2, frameCrc=13, msgSubtype=2, timeTagtype=1, gnssTimeTag=413903160, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=18, authInd=1, embAuthLen=0, crc=11477640)>",
            "<SPARTN(SPARTN-1X-OCB-GPS, msgType=0, nData=218, eaf=1, crcType=2, frameCrc=8, msgSubtype=0, timeTagtype=1, gnssTimeTag=413903160, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=7, authInd=1, embAuthLen=0, crc=4538711)>",
            "<SPARTN(SPARTN-1X-OCB-GLO, msgType=0, nData=152, eaf=1, crcType=2, frameCrc=2, msgSubtype=1, timeTagtype=1, gnssTimeTag=413913942, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=46, authInd=1, embAuthLen=0, crc=8221523)>",
            "<SPARTN(SPARTN-1X-OCB-GAL, msgType=0, nData=191, eaf=1, crcType=2, frameCrc=11, msgSubtype=2, timeTagtype=1, gnssTimeTag=413903160, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=3, authInd=1, embAuthLen=0, crc=12340159)>",
            "<SPARTN(SPARTN-1X-OCB-GPS, msgType=0, nData=37, eaf=1, crcType=2, frameCrc=2, msgSubtype=0, timeTagtype=0, gnssTimeTag=3965, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=8, authInd=1, embAuthLen=0, crc=6970314)>",
            "<SPARTN(SPARTN-1X-OCB-GLO, msgType=0, nData=33, eaf=1, crcType=2, frameCrc=3, msgSubtype=1, timeTagtype=0, gnssTimeTag=14747, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=47, authInd=1, embAuthLen=0, crc=12368174)>",
            "<SPARTN(SPARTN-1X-OCB-GAL, msgType=0, nData=34, eaf=1, crcType=2, frameCrc=3, msgSubtype=2, timeTagtype=0, gnssTimeTag=3965, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=4, authInd=1, embAuthLen=0, crc=8851501)>",
            "<SPARTN(SPARTN-1X-OCB-GPS, msgType=0, nData=37, eaf=1, crcType=2, frameCrc=2, msgSubtype=0, timeTagtype=0, gnssTimeTag=3970, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=9, authInd=1, embAuthLen=0, crc=7627181)>",
            "<SPARTN(SPARTN-1X-OCB-GLO, msgType=0, nData=33, eaf=1, crcType=2, frameCrc=3, msgSubtype=1, timeTagtype=0, gnssTimeTag=14752, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=48, authInd=1, embAuthLen=0, crc=15490832)>",
            "<SPARTN(SPARTN-1X-OCB-GAL, msgType=0, nData=34, eaf=1, crcType=2, frameCrc=3, msgSubtype=2, timeTagtype=0, gnssTimeTag=3970, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=5, authInd=1, embAuthLen=0, crc=15632803)>",
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
