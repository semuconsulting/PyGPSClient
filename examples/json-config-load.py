"""
json-config-load.py

Illustrates how to load SPARTN decryption parameters
from ThingStream JSON file.

Execute from /examples folder.

Created on 12 Feb 2023

:author: semuadmin
:copyright: SEMU Consulting © 2023
:license: BSD 3-Clause
"""

from pygpsclient.spartn_json_config import SpartnJsonConfig

CLIENTID = "dummy123-1234-1234-1234-abcdefghijkl"
FILENAME = "device-{}-ucenter-config.json"


if __name__ == "__main__":
    filename = FILENAME.format(CLIENTID)
    print(f"Loading configuration from {filename}...\n")
    spc = SpartnJsonConfig(clientid=CLIENTID)
    spc.loadconfig(filename)
    (curr_key, curr_start, curr_end) = spc.current_key
    (next_key, next_start, next_end) = spc.next_key

    (curr_start, curr_end, next_start, next_end) = [
        d.strftime("%Y%m%d") for d in (curr_start, curr_end, next_start, next_end)
    ]

    print(f"Server: {spc.server}")
    print(f"Topics: {spc.topics}")
    print(f"Current key: {curr_key},  valid from {curr_start} to {curr_end}")
    print(f"Next key: {next_key},  valid from {next_start} to {next_end}")
