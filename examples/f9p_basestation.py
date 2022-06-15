"""
f9p_basestation.py

Example showing how to configure a u-blox ZED-F9P
receiver to operate in RTK Base Station mode (either
Survey-In or Fixed Timing Mode). This can be used to
complement PyGPSClient's NTRIP Caster functionality.

It also optionally formats a user-defined preset
configuration message string suitable for copying
and pasting into the PyGPSClient ubxpresets file.

Created on 26 Apr 2022

:author: semuadmin
:copyright: SEMU Consulting © 2022
:license: BSD 3-Clause
"""

from math import trunc
from serial import Serial
from pyubx2 import UBXMessage

TMODE_SVIN = 1
TMODE_FIXED = 2


def send_msg(serial_out: Serial, ubx: UBXMessage):
    """
    Send config message to receiver.
    """

    print("Sending configuration message to receiver...")
    print(ubx)
    serial_out.write(ubx.serialize())


def config_rtcm(port_type: str) -> UBXMessage:
    """
    Configure which RTCM3 messages to output.
    """

    print("\nFormatting RTCM MSGOUT CFG-VALSET message...")
    layers = 1  # 1 = RAM, 2 = BBR, 4 = Flash (can be OR'd)
    transaction = 0
    cfg_data = []
    for rtcm_type in (
        "1005",
        "1077",
        "1087",
        "1097",
        "1127",
        "1230",
        "4072_0",
        "4072_1",
    ):
        cfg = f"CFG_MSGOUT_RTCM_3X_TYPE{rtcm_type}_{port_type}"
        cfg_data.append([cfg, 1])

    ubx = UBXMessage.config_set(layers, transaction, cfg_data)

    if SHOW_PRESET:
        print(
            "Set ZED-F9P RTCM3 MSGOUT Basestation, "
            f"CFG, CFG_VALSET, {ubx.payload.hex()}, 1\n"
        )

    return ubx


def config_svin(port_type: str, acc_limit: int, svin_min_dur: int) -> UBXMessage:
    """
    Configure Survey-In mode with specied accuracy limit.
    """

    print("\nFormatting SVIN TMODE CFG-VALSET message...")
    tmode = TMODE_SVIN
    layers = 1
    transaction = 0
    acc_limit = int(round(acc_limit / 0.1, 0))
    cfg_data = [
        ("CFG_TMODE_MODE", tmode),
        ("CFG_TMODE_SVIN_ACC_LIMIT", acc_limit),
        ("CFG_TMODE_SVIN_MIN_DUR", svin_min_dur),
        (f"CFG_MSGOUT_UBX_NAV_SVIN_{port_type}", 1),
    ]

    ubx = UBXMessage.config_set(layers, transaction, cfg_data)

    if SHOW_PRESET:
        print(
            "Set ZED-F9P to Survey-In Timing Mode Basestation, "
            f"CFG, CFG_VALSET, {ubx.payload.hex()}, 1\n"
        )

    return ubx


def config_fixed(acc_limit: int, lat: float, lon: float, height: float) -> UBXMessage:
    """
    Configure Fixed mode with specified coordinates.
    """

    print("\nFormatting FIXED TMODE CFG-VALSET message...")
    tmode = TMODE_FIXED
    pos_type = 1  # LLH (as opposed to ECEF)
    layers = 1
    transaction = 0
    acc_limit = int(round(acc_limit / 0.1, 0))

    # separate standard and high precision parts of lat / lon
    # and apply scaling factors
    lat_7dp = trunc(lat * 1e7) / 1e7
    lat_hp = lat - lat_7dp
    lat = int(round(lat_7dp / 1e-7, 0))
    lat_hp = int(round(lat_hp / 1e-9, 0))
    lon_7dp = trunc(lon * 1e7) / 1e7
    lon_hp = lon - lon_7dp
    lon = int(round(lon_7dp / 1e-7, 0))
    lon_hp = int(round(lon_hp / 1e-9, 0))

    height = int(height)
    cfg_data = [
        ("CFG_TMODE_MODE", tmode),
        ("CFG_TMODE_POS_TYPE", pos_type),
        ("CFG_TMODE_FIXED_POS_ACC", acc_limit),
        ("CFG_TMODE_HEIGHT_HP", 0),
        ("CFG_TMODE_HEIGHT", height),
        ("CFG_TMODE_LAT", lat),
        ("CFG_TMODE_LAT_HP", lat_hp),
        ("CFG_TMODE_LON", lon),
        ("CFG_TMODE_LON_HP", lon_hp),
    ]

    ubx = UBXMessage.config_set(layers, transaction, cfg_data)

    if SHOW_PRESET:
        print(
            "Set ZED-F9P to Fixed Timing Mode Basestation, "
            f"CFG, CFG_VALSET, {ubx.payload.hex()}, 1\n"
        )

    return ubx


if __name__ == "__main__":

    # Amend as required...
    PORT = "/dev/tty.usbmodem141101"
    PORT_TYPE = "USB"  # choose from "USB", "UART1", "UART2"
    BAUD = 38400
    TIMEOUT = 5
    SHOW_PRESET = True  # hide or show PyGPSClient preset string

    TMODE = TMODE_SVIN  # "TMODE_SVIN" or 1 = Survey-In, "TMODE_FIXED" or 2 = Fixed
    ACC_LIMIT = 200  # accuracy in mm

    # only used if TMODE = 1 ...
    SVIN_MIN_DUR = 90  # seconds

    # only used if TMODE = 2 ...
    ARP_LAT = 37.012345678
    ARP_LON = -115.012345678
    ARP_HEIGHT = 137000  # cm

    print(f"Configuring receiver on {PORT} @ {BAUD:,} baud.\n")
    with Serial(PORT, BAUD, timeout=TIMEOUT) as stream:

        # configure RTCM3 outputs
        msg = config_rtcm(PORT_TYPE)
        send_msg(stream, msg)

        # configure either Survey-In or Fixed Timing Mode
        if TMODE == TMODE_SVIN:
            msg = config_svin(PORT_TYPE, ACC_LIMIT, SVIN_MIN_DUR)
        else:
            msg = config_fixed(ACC_LIMIT, ARP_LAT, ARP_LON, ARP_HEIGHT)
        send_msg(stream, msg)
