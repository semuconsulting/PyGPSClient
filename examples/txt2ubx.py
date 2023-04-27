"""
txt2ubx.py

Utility which converts u-center *.txt configuration files to binary *.ubx files. 

Two output files are produced:

*.get.ubx - contains GET (MON-VER and CFG-VALGET) messages mirroring the input file
*.set.ubx - contains SET (converted CFG-VALSET) messages which can be used to apply configuration


Created on 27 Apr 2023

@author: semuadmin
"""

from pyubx2 import UBXMessage, GET, SET


def txt2ubx(fname: str):
    """
    Convert txt configuration file to ubx

    :param fname str: txt config file name
    """

    with open(fname, "r", encoding="utf-8") as infile:
        with open(fname + ".get.ubx", "wb") as outfile_get:
            with open(fname + ".set.ubx", "wb") as outfile_set:
                read = 0
                write = 0
                errors = 0
                for line in infile:
                    try:
                        read += 1
                        parts = line.replace(" ", "").split("-")
                        payload = bytes.fromhex(parts[-1])
                        cls = payload[0:1]
                        mid = payload[1:2]
                        # lenb = payload[2:4]
                        ubx = UBXMessage(cls, mid, GET, payload=payload[4:])
                        outfile_get.write(ubx.serialize())
                        # only convert CFG-VALGET
                        if not (cls == b"\x06" and mid == b"\x8b"):
                            continue
                        version = payload[4:5]
                        # layer = payload[5:6]
                        # position = payload[6:8]
                        data = payload[8:]
                        layers = b"\x01\x00"  # bbr
                        transaction = b"\x00"  # not transactional
                        reserved0 = b"\x00"
                        payload = version + layers + transaction + reserved0 + data
                        # create a CFG-VALSET message from the input CFG-VALGET
                        ubx = UBXMessage(b"\x06", b"\x8a", SET, payload=payload)
                        outfile_set.write(ubx.serialize())
                        write += 1
                    except Exception as err:  # pylint: disable=broad-exception-caught
                        print(err)
                        errors += 1
                        continue

    print(f"{read} GET messages read, {write} SET messages written, {errors} errors")


txt2ubx("simpleRTK2B_FW132_Base-00.txt")
