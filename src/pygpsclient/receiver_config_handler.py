"""
receiver_config_handler.py

Methods to create UBX, NMEA or TTY configuration messages
for various GNSS receivers.

Created on 5 Nov 2025

:author: semuadmin (Steve Smith)
:copyright: 2020 semuadmin
:license: BSD 3-Clause
"""

# pylint: disable=unused-argument

from pynmeagps import NMEAMessage, llh2ecef
from pyubx2 import SET, SET_LAYER_RAM, TXN_NONE, UBXMessage

from pygpsclient.helpers import val2sphp


def config_nmea(state: int, port_type: str = "USB") -> UBXMessage:
    """
    Enable or disable NMEA messages at port level and use minimum UBX
    instead (NAV-PRT, NAV_SAT, NAV_DOP).

    :param int state: 1 = disable NMEA, 0 = enable NMEA
    :param str port_type: port that rcvr is connected on
    """

    nmea_state = 0 if state else 1
    layers = 1
    transaction = 0
    cfg_data = []
    cfg_data.append((f"CFG_{port_type}OUTPROT_NMEA", nmea_state))
    cfg_data.append((f"CFG_{port_type}OUTPROT_UBX", 1))
    cfg_data.append((f"CFG_MSGOUT_UBX_NAV_PVT_{port_type}", state))
    cfg_data.append((f"CFG_MSGOUT_UBX_NAV_DOP_{port_type}", state))
    cfg_data.append((f"CFG_MSGOUT_UBX_NAV_SAT_{port_type}", state * 4))

    return UBXMessage.config_set(layers, transaction, cfg_data)


def config_disable_ublox() -> UBXMessage:
    """
    Disable base station mode for u-blox receivers.

    :return: UBXMessage
    :rtype: UBXMessage
    """

    layers = SET_LAYER_RAM
    transaction = TXN_NONE
    cfg_data = [
        ("CFG_TMODE_MODE", 0),
    ]

    return UBXMessage.config_set(layers, transaction, cfg_data)


def config_disable_lg290p() -> list:
    """
    Disable base station mode for Quectel LG290P receivers.

    NB: A 'feature' of Quectel firmware is that some command sequences
    require multiple restarts before taking effect.

    :return: list of NMEAMessage(s)
    :rtype: list
    """

    msgs = []
    msgs.append(NMEAMessage("P", "QTMCFGRCVRMODE", SET, rcvrmode=1))
    msgs.append(NMEAMessage("P", "QTMSAVEPAR", SET))
    msgs.append(NMEAMessage("P", "QTMSRR", SET))
    return msgs


def config_disable_lc29h() -> list:
    """
    Disable base station mode for Quectel LC29H receivers.

    :return: list of NMEAMessage(s)
    :rtype: list
    """

    msgs = []
    msgs.append(NMEAMessage("P", "AIR062", SET, type=-1))
    msgs.append(NMEAMessage("P", "AIR432", SET, mode=-1))
    msgs.append(NMEAMessage("P", "AIR434", SET, enabled=0))
    msgs.append(NMEAMessage("P", "QTMSAVEPAR", SET))
    msgs.append(NMEAMessage("P", "AIR005", SET))
    return msgs


def config_disable_septentrio() -> list:
    """
    Disable base station mode for Septentrio receivers.

    :return: ASCII TTY commands
    :rtype: list
    """

    msgs = []
    # msgs.append("SSSSSSSSSS\r\n")
    msgs.append("SSSSSSSSSS\r\n")
    msgs.append("erst,soft,config\r\n")
    return msgs


def config_svin_ublox(acc_limit: int, svin_min_dur: int) -> UBXMessage:
    """
    Configure Survey-In mode with specified accuracy limit for u-blox receivers.

    :param int acc_limit: accuracy limit in cm
    :param int svin_min_dur: survey minimimum duration
    :return: UBXMessage
    :rtype: UBXMessage
    """

    layers = SET_LAYER_RAM
    transaction = TXN_NONE
    acc_limit = int(acc_limit * 100)  # convert to 0.1 mm
    cfg_data = [
        ("CFG_TMODE_MODE", 1),
        ("CFG_TMODE_SVIN_ACC_LIMIT", acc_limit),
        ("CFG_TMODE_SVIN_MIN_DUR", svin_min_dur),
    ]

    return UBXMessage.config_set(layers, transaction, cfg_data)


def config_svin_lg290p(acc_limit: int, svin_min_dur: int) -> list:
    """
    Configure Survey-In mode with specified accuracy limit for Quectel LG290P receivers.

    NB: A 'feature' of Quectel firmware is that some command sequences
    require multiple restarts before taking effect.

    :param int acc_limit: accuracy limit in cm
    :param int svin_min_dur: survey minimimum duration
    :return: list of NMEAMessage(s)
    :rtype: list
    """

    msgs = []
    msgs.append(NMEAMessage("P", "QTMCFGRCVRMODE", SET, rcvrmode=2))
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
        )
    )
    msgs.append(
        NMEAMessage(
            "P",
            "QTMCFGSVIN",
            SET,
            svinmode=1,
            cfgcnt=svin_min_dur,
            acclimit=acc_limit / 100,  # m
        )
    )
    msgs.append(NMEAMessage("P", "QTMSAVEPAR", SET))
    msgs.append(NMEAMessage("P", "QTMSRR", SET))
    return msgs


def config_svin_lc29h(acc_limit: int, svin_min_dur: int) -> list:
    """
    Configure Survey-In mode with specified accuracy limit for Quectel LC29H receivers.

    NB: A 'feature' of Quectel firmware is that some command sequences
    require multiple restarts before taking effect.

    :param int acc_limit: accuracy limit in cm
    :param int svin_min_dur: survey minimimum duration
    :return: list of NMEAMessage(s)
    :rtype: list
    """

    msgs = []
    for i in range(9):
        msgs.append(NMEAMessage("P", "AIR062", SET, type=i, rate=0))
    msgs.append(NMEAMessage("P", "AIR432", SET, mode=1))
    msgs.append(NMEAMessage("P", "AIR434", SET, enabled=1))
    msgs.append(NMEAMessage("P", "QTMSAVEPAR", SET))
    msgs.append(NMEAMessage("P", "AIR005", SET))
    return msgs


def config_svin_septentrio(acc_limit: int, svin_min_dur: int) -> list:
    """
    Configure Survey-In mode with specified accuracy limit for Septentrio receivers.

    :param int acc_limit: accuracy limit in cm
    :param int svin_min_dur: survey minimimum duration
    :return: ASCII TTY commands
    :rtype: list
    """

    msgs = []
    msgs.append("SSSSSSSSSS\r\n")
    msgs.append("setDataInOut, COM1, ,RTCMv3\r\n")
    msgs.append("setRTCMv3Formatting,1234\r\n")
    msgs.append(
        "setRTCMv3Output,COM1,RTCM1006+RTCM1033+RTCM1077+RTCM1087+"
        "RTCM1097+RTCM1107+RTCM1117+RTCM1127+RTCM1137+RTCM1230\r\n"
    )
    msgs.append("setPVTMode,Static, ,auto\r\n")
    return msgs


def config_fixed_ublox(
    acc_limit: int, lat: float, lon: float, height: float, posmode: str
) -> UBXMessage:
    """
    Configure Fixed mode with specified coordinates for u-blox receivers.

    :param int acc_limit: accuracy limit in cm
    :param float lat: lat or X in m
    :param float lon: lon or Y in m
    :param float height: height or Z in m
    :param str posmode: "LLH" or "ECEF"
    :return: UBXMessage
    :rtype: UBXMessage
    """

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

    return UBXMessage.config_set(layers, transaction, cfg_data)


def config_fixed_lg290p(
    acc_limit: int, lat: float, lon: float, height: float, posmode: str
) -> list:
    """
    Configure Fixed mode with specified coordinates for Quectel LG290P receivers.

    NB: A 'feature' of Quectel firmware is that some command sequences
    require multiple restarts before taking effect.

    :param int acc_limit: accuracy limit in cm
    :param float lat: lat or X in m
    :param float lon: lon or Y in m
    :param float height: height or Z in m
    :param str posmode: "LLH" or "ECEF"
    :return: list of NMEAMessage(s)
    :rtype: list
    """

    if posmode == "LLH":
        ecef_x, ecef_y, ecef_z = llh2ecef(lat, lon, height)
    else:  # ECEF
        ecef_x, ecef_y, ecef_z = lat, lon, height

    msgs = []
    msgs.append(NMEAMessage("P", "QTMCFGRCVRMODE", SET, rcvrmode=2))
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
        )
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
        )
    )
    msgs.append(NMEAMessage("P", "QTMSAVEPAR", SET))
    msgs.append(NMEAMessage("P", "QTMSRR", SET))
    return msgs


def config_fixed_lc29h(
    acc_limit: int, lat: float, lon: float, height: float, posmode: str
) -> list:
    """
    Configure Fixed mode with specified coordinates for Quectel LC29H receivers.

    :param int acc_limit: accuracy limit in cm
    :param float lat: lat or X in m
    :param float lon: lon or Y in m
    :param float height: height or Z in m
    :param str posmode: "LLH" or "ECEF"
    :return: list of NMEAMessage(s)
    :rtype: list
    """

    msgs = []
    for i in range(9):
        msgs.append(NMEAMessage("P", "AIR062", SET, type=i, rate=0))
    msgs.append(NMEAMessage("P", "AIR432", SET, mode=1))
    msgs.append(NMEAMessage("P", "AIR434", SET, enabled=1))
    msgs.append(NMEAMessage("P", "QTMSAVEPAR", SET))
    msgs.append(NMEAMessage("P", "AIR005", SET))
    return msgs


def config_fixed_septentrio(
    acc_limit: int, lat: float, lon: float, height: float, posmode: str
) -> list:
    """
    Configure Fixed mode with specified coordinates for Septentrio receivers.

    :param int acc_limit: accuracy limit in cm
    :param float lat: lat or X in m
    :param float lon: lon or Y in m
    :param float height: height or Z in m
    :param str posmode: "LLH" or "ECEF"
    :return: ASCII TTY commands
    :rtype: list
    """

    msgs = []
    msgs.append("SSSSSSSSSS\r\n")
    msgs.append("setDataInOut,COM1, ,RTCMv3\r\n")
    msgs.append("setRTCMv3Formatting,1234\r\n")
    msgs.append(
        "setRTCMv3Output,COM1,RTCM1006+RTCM1033+RTCM1077+RTCM1087+"
        "RTCM1097+RTCM1107+RTCM1117+RTCM1127+RTCM1137+RTCM1230\r\n"
    )
    msgs.append(f"setStaticPosGeodetic,Geodetic1,{lat:.8f},{lon:.8f},{height:.4f}\r\n")
    msgs.append("setPVTMode,Static, ,Geodetic1\r\n")
    return msgs


def config_svin_quectel() -> NMEAMessage:
    """
    Configure SVIN enable message for Quectel receivers.

    :return: command
    :rtype: NMEAMessage
    """

    return NMEAMessage(
        "P",
        "QTMCFGMSGRATE",
        SET,
        msgname="PQTMSVINSTATUS",
        rate=1,
        msgver=1,
    )
