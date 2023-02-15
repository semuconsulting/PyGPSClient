"""
Example use of the SPARTNReader class.

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

from pygpsclient.spartnmessage import SPARTNReader

INFILE = "spartn_mqtt.log"

i = 0
with open(INFILE, "rb") as stream:
    spr = SPARTNReader(stream)
    for raw_data, parsed_data in spr.iterate():
        print(parsed_data)
        i += 1

print(f"\n{i} SPARTN messages read from input file")
