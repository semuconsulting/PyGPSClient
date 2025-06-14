"""
convert_ubx_preset.py

Illustration of how to convert a file containing a
series of binary UBX configuration (CFG-VALSET) messages
to a preset string suitable for copying-and-pasting
into the ubxpresets_l section of a PyGPSClient *.json
configuration file.

The example input file was created using the
CFG Configuration Load/Save/Record facility in PyGPSClient's
UBX Configuration Panel.

NB: Avoid embedded commas in description.

Usage:

python3 convert_ubx_preset.py infile="myinput.ubx" desc="mydesc"

Created by semuadmin on 20 Sep 2024.
"""

from sys import argv
from pygpsclient import ubx2preset
from pyubx2 import UBXReader, SET


def main(**kwargs):
    """
    Main routine.
    """

    infile = kwargs.get("infile", "pygpsconfig_x20p_enableubx.ubx")
    desc = kwargs.get("desc", "ZED-X20P Enable UBX & Disable NMEA")

    ubx = ()
    with open(infile, "rb") as stream:
        ubr = UBXReader(stream, msgmode=SET)
        for _, parsed in ubr:
            ubx += (parsed,)

    preset = ubx2preset(ubx, desc)

    print(f'Copy the following string into ubxpresets_l...\n\n"{preset}",')


if __name__ == "__main__":

    main(**dict(arg.split("=") for arg in argv[1:]))
