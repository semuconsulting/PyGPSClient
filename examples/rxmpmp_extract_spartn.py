"""
rxmpmp_extract_spartn.py

Extract SPARTN messages from RXM-PMP payloads
output by NEO-D9S SPARTN correction receiver.

Created on 18 Frb 2023

:author: semuadmin
:copyright: SEMU Consulting © 203
:license: BSD 3-Clause
"""

from io import BytesIO
from pyubx2 import UBXReader
from pyspartn import SPARTNReader, SPARTNMessage

FILENAME = "D9S_RXM_PMP.ubx"

# Read each RXM-PMP message in the input file and
# accumulate userData into payload bytes
with open(FILENAME, "rb") as stream:
    ubr = UBXReader(stream)
    payload = b""
    m = 0
    for raw, parsed in ubr.iterate():
        if parsed.identity == "RXM-PMP":
            m += 1
            # print(parsed)
            for i in range(parsed.numBytesUserData):
                val = getattr(parsed, f"userData_{i+1:02}")
                payload += val.to_bytes(1, "big")

# Parse the accumulated payload bytes for SPARTN messages
try:
    spr = SPARTNReader(BytesIO(payload))
    n = 0
    for raw, parsed in spr.iterate():
        if isinstance(parsed, SPARTNMessage):
            print(parsed)
            n += 1
except AttributeError:  # truncated data
    pass

print(f"{n} SPARTN messages parsed from {m} RXM-PMP payloads")
