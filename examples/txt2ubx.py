"""
txt2ubx.py

Utility which converts u-center *.txt configuration files to binary *.ubx files. 

Two output files are produced:

*.get.ubx - contains GET (MON-VER and CFG-VALGET) messages mirroring the input file
*.set.ubx - contains SET (converted CFG-VALSET) messages which can be used to set configuration

The *.set.ubx file can be loaded into PyGPSClient's UBX Configuration Load/Save/record facility
and uploaded to the receiver.

Created on 27 Apr 2023

@author: semuadmin
"""

from pyubx2 import UBXMessage, escapeall, GET, SET

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
                        data = bytes.fromhex(parts[-1])
                        cls = data[0:1]
                        mid = data[1:2]
                        # lenb = data[2:4]
                        version = data[4:5]
                        layer = data[5:6]
                        position = data[6:8]
                        cfgdata = data[8:]
                        print(escapeall(cfgdata))
                        payload = version + layer + position + cfgdata
                        ubx = UBXMessage(cls, mid, GET, payload=payload)
                        outfile_get.write(ubx.serialize())
                        # only convert CFG-VALGET
                        if not (cls == b"\x06" and mid == b"\x8b"):
                            continue
                        layers = b"\x01" # bbr only
                        transaction = b"\x00" # not transactional
                        reserved0 = b"\x00"
                        payload = version + layers + transaction + reserved0 + cfgdata
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
