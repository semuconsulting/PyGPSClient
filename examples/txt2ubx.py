"""
txt2ubx.py

Simple illustration of how to convert *.txt UBX 
configuration files into binary *.ubx format suitable
for sending to a u-blox receiver.

It automatically converts CFG-VALGET messages to CFG_VALSET
messages and discards and informational MON-VER messages.

Created on 23 Aug 2022

@author: semuadmin
"""

from pyubx2 import calc_checksum, msgstr2bytes, val2bytes, UBX_HDR, U2


def txt2ubx(fname: str):
    """
    Convert txt configuration file to ubx

    :param fname str: txt config file name
    """

    with open(fname, "r", encoding="utf-8") as infile:
        with open(fname + ".ubx", "wb") as outfile:
            read = 0
            write = 0
            errors = 0
            for line in infile:
                try:
                    read += 1
                    parts = line.replace(" ", "").split("-")
                    (cls, mid) = msgstr2bytes(parts[0], f"{parts[0]}-{parts[1]}")
                    if cls == b"\x0a":
                        continue  # discard MON messages
                    if cls == b"\x06" and mid == b"\x8b":
                        mid = b"\x8a"  # convert CFG-VALGET to CFG-VALSET
                    payload = bytes.fromhex(parts[-1])
                    paylen = val2bytes(len(payload), U2)
                    cksum = calc_checksum(cls + mid + paylen + payload)
                    ubx = UBX_HDR + cls + mid + paylen + payload + cksum
                    outfile.write(ubx)
                    write += 1
                except Exception as err:  # pylint: disable=broad-exception-caught
                    print(err)
                    errors += 1
                    continue

    print(f"{read} messages read, {write} messages written, {errors} errors")


txt2ubx("simpleRTK2B_FW113_Base-00.txt")
