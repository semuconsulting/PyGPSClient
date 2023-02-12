"""
Example use of the SPARTNReader class with benchmarking facility.

Reads binary file containing ONLY SPARTN messages
(e.g. from MQTT /pp/ip topic) and prints parsed data.

NB: the SPARTNReader and SPARTNMessage classes
are currently skeleton classes and do not perform
a full decode of SPARTN protocol messages.

Created on 12 Feb 2023

:author: semuadmin
:copyright: SEMU Consulting © 2023
:license: BSD 3-Clause
"""

from datetime import datetime
from platform import version as osver, python_version
from pygpsclient.spartnmessage import SPARTNReader
from pygpsclient._version import __version__ as VERSION

INFILE = "spartn_mqtt.log"
INFILELEN = 35
PROGBAR = False  # set to True to show benchmark progress bar


def progbar(i: int, lim: int, inc: int = 20):
    """
    Display progress bar on console.

    :param int i: iteration
    :param int lim: max iterations
    :param int inc: bar increments (20)
    """

    i = min(i, lim)
    pct = int(i * inc / lim)
    if not i % int(lim / inc):
        print(
            f"{int(pct*100/inc):02}% " + "\u2593" * pct + "\u2591" * (inc - pct),
            end="\r",
        )


cyc = 10000 if PROGBAR else 1
txnc = INFILELEN
txnt = txnc * cyc

print(
    f"\nOperating system: {osver()}",
    f"\nPython version: {python_version()}",
    f"\nPyGPSClienty version: {VERSION}",
    f"\nTest cycles: {cyc:,}",
    f"\nTxn per cycle: {txnc:,}",
)
start = datetime.now()
print(f"\nBenchmark test started at {start}")

for n in range(cyc):
    if PROGBAR:
        progbar(n, cyc)
    with open(INFILE, "rb") as stream:
        m = 0
        spr = SPARTNReader(stream)
        for raw_data, parsed_data in spr.iterate():
            if not PROGBAR:
                print(parsed_data)
            m += 1

end = datetime.now()
print(f"Benchmark test ended at {end}.")
duration = (end - start).total_seconds()
rate = round(txnt / duration, 2)

print(
    f"\n{txnt:,} messages processed in {duration:,.3f} seconds = {rate:,.2f} txns/second.\n"
)
