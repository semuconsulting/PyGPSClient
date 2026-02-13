"""
receiver_config_handler.py

Methods to create UBX, NMEA or TTY configuration messages
for various GNSS receivers.

NB: THESE SHOULD ALL RETURN `bytes` OR `list[bytes]`.

Created on 5 Nov 2025

:author: semuadmin (Steve Smith)
:copyright: 2020 semuadmin
:license: BSD 3-Clause
"""

# pylint: disable=unused-argument, too-many-arguments, too-many-positional-arguments

from pynmeagps import NMEAMessage, llh2ecef
from pyubx2 import SET, SET_LAYER_RAM, TXN_NONE, UBXMessage

from pygpsclient.globals import ASCII, BSR
from pygpsclient.helpers import val2sphp

BASE_SVIN = "SURVEY IN"
RTCMTYPES = {
    "1002": 1,
    "1006": 5,
    "1010": 1,
    "1077": 1,
    "1087": 1,
    "1097": 1,
    "1127": 1,
    "1230": 1,
}


def config_disable_ublox(disablenmea: bool = False) -> list[bytes]:
    """
    Disable base station mode for u-blox receivers.

    :param bool disablenmea: disable NMEA sentences
    :return: list of serialized UBXMessage(s)
    :rtype: list[bytes]exit
    """

    dn = 1 if disablenmea else 0
    msgs = []
    layers = SET_LAYER_RAM
    transaction = TXN_NONE
    msgs.append(
        UBXMessage.config_set(layers, transaction, [("CFG_TMODE_MODE", 0)]).serialize()
    )
    for port_type in ("USB", "UART1"):
        cfg_data = []
        cfg = f"CFG_MSGOUT_UBX_NAV_SVIN_{port_type}"
        cfg_data.append((cfg, 0))
        for rtcm_type, _ in RTCMTYPES.items():
            cfg = f"CFG_MSGOUT_RTCM_3X_TYPE{rtcm_type}_{port_type}"
            cfg_data.append((cfg, 0))
        cfg_data.append((f"CFG_{port_type}OUTPROT_NMEA", 0 if dn else 1))
        cfg_data.append((f"CFG_{port_type}OUTPROT_UBX", 1))
        cfg_data.append((f"CFG_MSGOUT_UBX_NAV_PVT_{port_type}", dn))
        cfg_data.append((f"CFG_MSGOUT_UBX_NAV_DOP_{port_type}", dn))
        cfg_data.append((f"CFG_MSGOUT_UBX_NAV_SAT_{port_type}", dn * 4))
        msgs.append(UBXMessage.config_set(layers, transaction, cfg_data).serialize())
    return msgs


def config_disable_lg290p(disablenmea: bool = False) -> list[bytes]:
    """
    Disable base station mode for Quectel LGSERIES receivers.

    NB: A 'feature' of Quectel firmware is that some command sequences
    require multiple restarts before taking effect.

    :param bool disablenmea: disable NMEA sentences
    :return: list of serialized NMEAMessage(s)
    :rtype: list[bytes]
    """

    msgs = []
    msgs.append(NMEAMessage("P", "QTMCFGRCVRMODE", SET, rcvrmode=1).serialize())
    msgs.append(NMEAMessage("P", "QTMSAVEPAR", SET).serialize())
    msgs.append(NMEAMessage("P", "QTMSRR", SET).serialize())
    return msgs


def config_disable_lc29h(disablenmea: bool = False) -> list[bytes]:
    """
    Disable base station mode for Quectel LCSERIES receivers.

    :param bool disablenmea: disable NMEA sentences
    :return: list of serialized NMEAMessage(s)
    :rtype: list[bytes]
    """

    msgs = []
    if not disablenmea:
        msgs.append(
            NMEAMessage("P", "AIR062", SET, type=-1).serialize()
        )  # default NMEA
    msgs.append(NMEAMessage("P", "AIR432", SET, mode=-1).serialize())  # disable RTCM
    msgs.append(NMEAMessage("P", "AIR434", SET, enabled=0).serialize())  # disable 1005
    msgs.append(NMEAMessage("P", "QTMSAVEPAR", SET).serialize())
    msgs.append(NMEAMessage("P", "AIR005", SET).serialize())  # warm start
    return msgs


def config_disable_septentrio(disablenmea: bool = False) -> list:
    """
    Disable base station mode for Septentrio receivers.

    :param bool disablenmea: disable NMEA sentences
    :return: ASCII TTY commands
    :rtype: list
    """

    msgs = []
    msgs.append(b"SSSSSSSSSS\r\n")
    msgs.append(b"erst,soft,config\r\n")
    return msgs


def config_disable_unicore(disablenmea: bool = False) -> list:
    """
    Disable base station mode for Unicore receivers.

    :param bool disablenmea: disable NMEA sentences
    :return: ASCII TTY commands
    :rtype: list
    """

    msgs = []
    msgs.append(b"unlog\r\n")
    if disablenmea:
        msgs.append(b"PVTSLNB 1\r\n")
        msgs.append(b"SATSINFOB 4\r\n")
        msgs.append(b"BESTNAVB 1\r\n")
        msgs.append(b"STADOPB 1\r\n")
    else:
        msgs.append(b"gpgsa 1\r\n")
        msgs.append(b"gpgga 1\r\n")
        msgs.append(b"gpgll 1\r\n")
        msgs.append(b"gpgsv 4\r\n")
        msgs.append(b"gpvtg 1\r\n")
        msgs.append(b"gprmc 1\r\n")
    msgs.append(b"mode rover\r\n")
    msgs.append(b"config pvtalg multi\r\n")
    msgs.append(b"saveconfig\r\n")
    return msgs


def config_svin_ublox(
    acc_limit: int, svin_min_dur: int, disablenmea: bool = True
) -> list[bytes]:
    """
    Configure Survey-In mode with specified accuracy limit for u-blox receivers.

    :param bool disablenmea: disable NMEA sentences
    :param int acc_limit: accuracy limit in cm
    :param int svin_min_dur: survey minimimum duration
    :return: list of serialized UBXMessage(s)
    :rtype: list[bytes]
    """

    dn = 1 if disablenmea else 0
    msgs = []
    layers = SET_LAYER_RAM
    transaction = TXN_NONE
    acc_limit = int(acc_limit * 100)  # convert to 0.1 mm
    cfg_data = [
        ("CFG_TMODE_MODE", 1),
        ("CFG_TMODE_SVIN_ACC_LIMIT", acc_limit),
        ("CFG_TMODE_SVIN_MIN_DUR", svin_min_dur),
    ]
    msgs.append(UBXMessage.config_set(layers, transaction, cfg_data).serialize())
    for port_type in ("USB", "UART1"):
        cfg_data = []
        cfg_data.append((f"CFG_{port_type}OUTPROT_NMEA", 0 if dn else 1))
        cfg = f"CFG_MSGOUT_UBX_NAV_SVIN_{port_type}"
        cfg_data.append((cfg, 1))
        for rtcm_type, mrate in RTCMTYPES.items():
            cfg = f"CFG_MSGOUT_RTCM_3X_TYPE{rtcm_type}_{port_type}"
            cfg_data.append((cfg, mrate))
        msgs.append(UBXMessage.config_set(layers, transaction, cfg_data).serialize())

    return msgs


def config_svin_lg290p(
    acc_limit: int, svin_min_dur: int, disablenmea: bool = True
) -> list[bytes]:
    """
    Configure Survey-In mode with specified accuracy limit for Quectel LGSERIES receivers.

    NB: A 'feature' of Quectel firmware is that some command sequences
    require multiple restarts before taking effect.

    :param bool disablenmea: disable NMEA sentences
    :param int acc_limit: accuracy limit in cm
    :param int svin_min_dur: survey minimimum duration
    :return: list of serialized NMEAMessage(s)
    :rtype: list[bytes]
    """

    msgs = []
    msgs.append(NMEAMessage("P", "QTMCFGRCVRMODE", SET, rcvrmode=2).serialize())
    msgs.append(
        NMEAMessage(
            "P",
            "QTMCFGRTCM",
            SET,
            msmtype=7,  # MSM 7 types e.g. 1077
            msmmode=0,
            msmelevthd=-90,
            reserved1="07",
            reserved2="06",
            ephmode=1,
            ephinterval=0,
        ).serialize()
    )
    msgs.append(
        NMEAMessage(
            "P",
            "QTMCFGSVIN",
            SET,
            svinmode=1,
            cfgcnt=svin_min_dur,
            acclimit=acc_limit / 100,  # m
        ).serialize()
    )
    msgs.append(NMEAMessage("P", "QTMSAVEPAR", SET).serialize())
    msgs.append(NMEAMessage("P", "QTMSRR", SET).serialize())
    return msgs


def config_svin_lc29h(
    acc_limit: int, svin_min_dur: int, disablenmea: bool = True
) -> list[bytes]:
    """
    Configure Survey-In mode with specified accuracy limit for Quectel LCSERIES receivers.

    NB: A 'feature' of Quectel firmware is that some command sequences
    require multiple restarts before taking effect.

    :param bool disablenmea: disable NMEA sentences
    :param int acc_limit: accuracy limit in cm
    :param int svin_min_dur: survey minimimum duration
    :return: list of serialized NMEAMessage(s)
    :rtype: list[bytes]
    """

    msgs = []
    if disablenmea:
        for i in range(9):
            msgs.append(
                NMEAMessage("P", "AIR062", SET, type=i, rate=0).serialize()
            )  # disable NMEA
    msgs.append(NMEAMessage("P", "AIR432", SET, mode=1).serialize())  # enable RTCM
    msgs.append(NMEAMessage("P", "AIR434", SET, enabled=1).serialize())  # enable 1005
    msgs.append(NMEAMessage("P", "QTMSAVEPAR", SET).serialize())
    msgs.append(NMEAMessage("P", "AIR005", SET).serialize())  # warm start
    return msgs


def config_svin_quectel() -> bytes:
    """
    Configure SVIN enable message for Quectel receivers.

    :return: serialized NMEAMessage
    :rtype: bytes
    """

    return NMEAMessage(
        "P",
        "QTMCFGMSGRATE",
        SET,
        msgname="PQTMSVINSTATUS",
        rate=1,
        msgver=1,
    ).serialize()


def config_svin_septentrio(
    acc_limit: int, svin_min_dur: int, disablenmea: bool = True
) -> list[bytes]:
    """
    Configure Survey-In mode with specified accuracy limit for Septentrio receivers.

    :param bool disablenmea: disable NMEA sentences
    :param int acc_limit: accuracy limit in cm
    :param int svin_min_dur: survey minimimum duration
    :return: ASCII TTY commands
    :rtype: list[bytes]
    """

    msgs = []
    msgs.append(b"SSSSSSSSSS\r\n")
    msgs.append(b"setDataInOut, COM1, ,RTCMv3\r\n")
    msgs.append(b"setRTCMv3Formatting,1234\r\n")
    msgs.append(
        b"setRTCMv3Output,COM1,RTCM1006+RTCM1033+RTCM1077+RTCM1087+"
        b"RTCM1097+RTCM1107+RTCM1117+RTCM1127+RTCM1137+RTCM1230\r\n"
    )
    msgs.append(b"setPVTMode,Static, ,auto\r\n")
    return msgs


def config_svin_unicore(
    acc_limit: int, svin_min_dur: int, disablenmea: bool = True
) -> list[bytes]:
    """
    Configure Survey-In mode with specified accuracy limit for Unicore receivers.

    :param bool disablenmea: disable NMEA sentences
    :param int acc_limit: accuracy limit in cm
    :param int svin_min_dur: survey minimimum duration
    :return: ASCII TTY commands
    :rtype: list[bytes]
    """

    msgs = []
    if disablenmea:
        msgs.append(b"unlog\r\n")
    msgs.append(f"mode base time {svin_min_dur}\r\n".encode(ASCII, errors=BSR))
    msgs.append(b"config pvtalg multi\r\n")
    msgs.append(b"rtcm1006 10\r\n")
    msgs.append(b"rtcm1033 10\r\n")
    msgs.append(b"rtcm1074 1\r\n")
    msgs.append(b"rtcm1084 1\r\n")
    msgs.append(b"rtcm1094 1\r\n")
    msgs.append(b"rtcm1124 1\r\n")
    msgs.append(b"saveconfig\r\n")
    return msgs


def config_fixed_ublox(
    acc_limit: int,
    lat: float,
    lon: float,
    height: float,
    posmode: str,
    disablenmea: bool = True,
) -> list[bytes]:
    """
    Configure Fixed mode with specified coordinates for u-blox receivers.

    :param bool disablenmea: disable NMEA sentences
    :param int acc_limit: accuracy limit in cm
    :param float lat: lat or X in m
    :param float lon: lon or Y in m
    :param float height: height or Z in m
    :param str posmode: "LLH" or "ECEF"
    :return: list of serialized UBXMessage(s)
    :rtype: list[bytes]
    """

    dn = 1 if disablenmea else 0
    msgs = []
    layers = SET_LAYER_RAM
    transaction = TXN_NONE
    acc_limit = int(acc_limit * 100)  # convert to 0.1 mm
    if posmode == "LLH":
        lat_sp, lat_hp = val2sphp(lat, 1e-7)
        lon_sp, lon_hp = val2sphp(lon, 1e-7)
        height_sp, height_hp = val2sphp(height, 0.01)
        cfg_data = [
            ("CFG_TMODE_MODE", 2),
            ("CFG_TMODE_POS_TYPE", 1),
            ("CFG_TMODE_FIXED_POS_ACC", acc_limit),
            ("CFG_TMODE_LAT", lat_sp),
            ("CFG_TMODE_LAT_HP", lat_hp),
            ("CFG_TMODE_LON", lon_sp),
            ("CFG_TMODE_LON_HP", lon_hp),
            ("CFG_TMODE_HEIGHT", height_sp),
            ("CFG_TMODE_HEIGHT_HP", height_hp),
        ]
    else:  # ECEF
        x_sp, x_hp = val2sphp(lat, 0.01)
        y_sp, y_hp = val2sphp(lon, 0.01)
        z_sp, z_hp = val2sphp(height, 0.01)
        cfg_data = [
            ("CFG_TMODE_MODE", 2),
            ("CFG_TMODE_POS_TYPE", 0),
            ("CFG_TMODE_FIXED_POS_ACC", acc_limit),
            ("CFG_TMODE_ECEF_X", x_sp),
            ("CFG_TMODE_ECEF_X_HP", x_hp),
            ("CFG_TMODE_ECEF_Y", y_sp),
            ("CFG_TMODE_ECEF_Y_HP", y_hp),
            ("CFG_TMODE_ECEF_Z", z_sp),
            ("CFG_TMODE_ECEF_Z_HP", z_hp),
        ]
    msgs.append(UBXMessage.config_set(layers, transaction, cfg_data).serialize())
    for port_type in ("USB", "UART1"):
        cfg_data = []
        cfg = f"CFG_MSGOUT_UBX_NAV_SVIN_{port_type}"
        cfg_data.append((cfg, 0))
        cfg_data.append((f"CFG_{port_type}OUTPROT_NMEA", 0 if dn else 1))
        for rtcm_type, mrate in RTCMTYPES.items():
            cfg = f"CFG_MSGOUT_RTCM_3X_TYPE{rtcm_type}_{port_type}"
            cfg_data.append((cfg, mrate))
        msgs.append(UBXMessage.config_set(layers, transaction, cfg_data).serialize())

    return msgs


def config_fixed_lg290p(
    acc_limit: int,
    lat: float,
    lon: float,
    height: float,
    posmode: str,
    disablenmea: bool = True,
) -> list[bytes]:
    """
    Configure Fixed mode with specified coordinates for Quectel LGSERIES receivers.

    NB: A 'feature' of Quectel firmware is that some command sequences
    require multiple restarts before taking effect.

    :param bool disablenmea: disable NMEA sentences
    :param int acc_limit: accuracy limit in cm
    :param float lat: lat or X in m
    :param float lon: lon or Y in m
    :param float height: height or Z in m
    :param str posmode: "LLH" or "ECEF"
    :return: list of serialized NMEAMessage(s)
    :rtype: list[bytes]
    """

    if posmode == "LLH":
        ecef_x, ecef_y, ecef_z = llh2ecef(lat, lon, height)
    else:  # ECEF
        ecef_x, ecef_y, ecef_z = lat, lon, height

    msgs = []
    msgs.append(NMEAMessage("P", "QTMCFGRCVRMODE", SET, rcvrmode=2).serialize())
    msgs.append(
        NMEAMessage(
            "P",
            "QTMCFGRTCM",
            SET,
            msmtype=7,  # MSM 7 types e.g. 1077
            msmmode=0,
            msmelevthd=-90,
            reserved1="07",
            reserved2="06",
            ephmode=1,
            ephinterval=0,
        ).serialize()
    )
    msgs.append(
        NMEAMessage(
            "P",
            "QTMCFGSVIN",
            SET,
            svinmode=2,
            cfgcnt=0,
            acclimit=acc_limit / 100,  # m
            ecefx=ecef_x,
            ecefy=ecef_y,
            ecefz=ecef_z,
        ).serialize()
    )
    msgs.append(NMEAMessage("P", "QTMSAVEPAR", SET).serialize())
    msgs.append(NMEAMessage("P", "QTMSRR", SET).serialize())
    return msgs


def config_fixed_lc29h(
    acc_limit: int,
    lat: float,
    lon: float,
    height: float,
    posmode: str,
    disablenmea: bool = True,
) -> list[bytes]:
    """
    Configure Fixed mode with specified coordinates for Quectel LCSERIES receivers.

    :param bool disablenmea: disable NMEA sentences
    :param int acc_limit: accuracy limit in cm
    :param float lat: lat or X in m
    :param float lon: lon or Y in m
    :param float height: height or Z in m
    :param str posmode: "LLH" or "ECEF"
    :return: list of serialized NMEAMessage(s)
    :rtype: list[bytes]
    """

    msgs = []
    if disablenmea:
        for i in range(9):
            msgs.append(
                NMEAMessage("P", "AIR062", SET, type=i, rate=0).serialize()
            )  # disable NMEA
    msgs.append(NMEAMessage("P", "AIR432", SET, mode=1).serialize())  # enable RTCM
    msgs.append(NMEAMessage("P", "AIR434", SET, enabled=1).serialize())  # enable 1005
    msgs.append(NMEAMessage("P", "QTMSAVEPAR", SET).serialize())
    msgs.append(NMEAMessage("P", "AIR005", SET).serialize())  # warm start
    return msgs


def config_fixed_septentrio(
    acc_limit: int,
    lat: float,
    lon: float,
    height: float,
    posmode: str,
    disablenmea: bool = True,
) -> list[bytes]:
    """
    Configure Fixed mode with specified coordinates for Septentrio receivers.

    :param bool disablenmea: disable NMEA sentences
    :param int acc_limit: accuracy limit in cm
    :param float lat: lat or X in m
    :param float lon: lon or Y in m
    :param float height: height or Z in m
    :param str posmode: "LLH" or "ECEF"
    :return: ASCII TTY commands
    :rtype: list[bytes]
    """

    msgs = []
    msgs.append(b"SSSSSSSSSS\r\n")
    msgs.append(b"setDataInOut,COM1, ,RTCMv3\r\n")
    msgs.append(b"setRTCMv3Formatting,1234\r\n")
    msgs.append(
        b"setRTCMv3Output,COM1,RTCM1006+RTCM1033+RTCM1077+RTCM1087+"
        b"RTCM1097+RTCM1107+RTCM1117+RTCM1127+RTCM1137+RTCM1230\r\n"
    )
    msgs.append(
        f"setStaticPosGeodetic,Geodetic1,{lat:.8f},{lon:.8f},{height:.4f}\r\n".encode(
            ASCII, errors=BSR
        )
    )
    msgs.append(b"setPVTMode,Static, ,Geodetic1\r\n")
    return msgs


def config_fixed_unicore(
    acc_limit: int,
    lat: float,
    lon: float,
    height: float,
    posmode: str,
    disablenmea: bool = True,
) -> list[bytes]:
    """
    Configure Fixed mode with specified coordinates for Unicore receivers.

    :param bool disablenmea: disable NMEA sentences
    :param int acc_limit: accuracy limit in cm
    :param float lat: lat or X in m
    :param float lon: lon or Y in m
    :param float height: height or Z in m
    :param str posmode: "LLH" or "ECEF"
    :return: ASCII TTY commands
    :rtype: list[bytes]
    """

    msgs = []
    if disablenmea:
        msgs.append(b"unlog\r\n")
    msgs.append(f"mode base {lat} {lon} {height}\r\n".encode(ASCII, errors=BSR))
    msgs.append(b"config pvtalg multi\r\n")
    msgs.append(b"rtcm1006 10\r\n")
    msgs.append(b"rtcm1033 10\r\n")
    msgs.append(b"rtcm1074 1\r\n")
    msgs.append(b"rtcm1084 1\r\n")
    msgs.append(b"rtcm1094 1\r\n")
    msgs.append(b"rtcm1124 1\r\n")
    msgs.append(b"saveconfig\r\n")
    return msgs
