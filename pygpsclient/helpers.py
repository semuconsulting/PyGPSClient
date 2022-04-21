"""
PyGPSClient Helpers

Collection of helper methods

Created on 17 Apr 2021

:author: semuadmin
:copyright: SEMU Consulting © 2021
:license: BSD 3-Clause

"""
# pylint: disable=invalid-name

from subprocess import run as subrun
from sys import executable
from tkinter import Toplevel, Label, Button, W
from math import sin, cos, pi
from datetime import datetime, timedelta
from pygpsclient.globals import (
    MAX_SNR,
    DEVICE_ACCURACY,
    HDOP_RATIO,
    FIXLOOKUP,
)


class ConfirmBox(Toplevel):
    """
    Confirm action dialog class.
    Provides better consistency across different OS platforms
    than using messagebox.askyesno()

    Returns True if OK, False if Cancel
    """

    def __init__(self, parent, title, prompt):
        """
        Constructor

        :param parent: parent dialog
        :param string title: title
        :param string prompt: prompt to be displayed
        """

        self.__master = parent
        Toplevel.__init__(self, parent)
        self.title(title)  # pylint: disable=E1102
        self.resizable(False, False)
        Label(self, text=prompt, anchor=W).grid(
            row=0, column=0, columnspan=2, padx=3, pady=5
        )
        Button(self, command=self._on_ok, text="OK", width=8).grid(
            row=1, column=0, padx=3, pady=3
        )
        Button(self, command=self._on_cancel, text="Cancel", width=8).grid(
            row=1, column=1, padx=3, pady=3
        )
        self.lift()  # Put on top of
        self.grab_set()  # Make modal
        self._rc = False

        self._centre()

    def _on_ok(self, event=None):  # pylint: disable=unused-argument
        """
        OK button handler
        """

        self._rc = True
        self.destroy()

    def _on_cancel(self, event=None):  # pylint: disable=unused-argument
        """
        Cancel button handler
        """

        self._rc = False
        self.destroy()

    def _centre(self):
        """
        Centre dialog in parent
        """

        # self.update_idletasks()
        dw = self.winfo_width()
        dh = self.winfo_height()
        mx = self.__master.winfo_x()
        my = self.__master.winfo_y()
        mw = self.__master.winfo_width()
        mh = self.__master.winfo_height()
        self.geometry(f"+{int(mx + (mw/2 - dw/2))}+{int(my + (mh/2 - dh/2))}")

    def show(self):
        """
        Show dialog

        :return: True (OK) or False (Cancel)
        :rtype: bool
        """

        self.wm_deiconify()
        self.wait_window()
        return self._rc


def deg2rad(deg: float) -> float:
    """
    Convert degrees to radians.

    :param float deg: degrees
    :return: radians
    :rtype: float

    """

    if not isinstance(deg, (float, int)):
        return 0
    return deg * pi / 180


def cel2cart(elevation: float, azimuth: float) -> tuple:
    """
    Convert celestial coordinates (degrees) to Cartesian coordinates.

    :param float elevation: elevation
    :param float azimuth: azimuth
    :return: cartesian x,y coordinates
    :rtype: tuple

    """

    if not (isinstance(elevation, (float, int)) and isinstance(azimuth, (float, int))):
        return (0, 0)
    elevation = deg2rad(elevation)
    azimuth = deg2rad(azimuth)
    x = cos(azimuth) * cos(elevation)
    y = sin(azimuth) * cos(elevation)
    return (x, y)


def deg2dms(degrees: float, latlon: str) -> str:
    """
    Convert decimal degrees to degrees minutes seconds string.

    :param float degrees: degrees
    :return: degrees as d.m.s formatted string
    :rtype: str

    """

    if not isinstance(degrees, (float, int)):
        return ""
    negative = degrees < 0
    degrees = abs(degrees)
    minutes, seconds = divmod(degrees * 3600, 60)
    degrees, minutes = divmod(minutes, 60)
    if negative:
        sfx = "S" if latlon == "lat" else "W"
    else:
        sfx = "N" if latlon == "lat" else "E"
    return (
        str(int(degrees))
        + "\u00b0"
        + str(int(minutes))
        + "\u2032"
        + str(round(seconds, 3))
        + "\u2033"
        + sfx
    )


def deg2dmm(degrees: float, latlon: str) -> str:
    """
    Convert decimal degrees to degrees decimal minutes string.

    :param float degrees: degrees
    :param str latlon: "lat" or "lon"
    :return: degrees as dm.m formatted string
    :rtype: str

    """

    if not isinstance(degrees, (float, int)):
        return ""
    negative = degrees < 0
    degrees = abs(degrees)
    degrees, minutes = divmod(degrees * 60, 60)
    if negative:
        sfx = "S" if latlon == "lat" else "W"
    else:
        sfx = "N" if latlon == "lat" else "E"
    return str(int(degrees)) + "\u00b0" + str(round(minutes, 5)) + "\u2032" + sfx


def m2ft(meters: float) -> float:
    """
    Convert meters to feet.

    :param float meters: meters
    :return: feet
    :rtype: float

    """

    if not isinstance(meters, (float, int)):
        return 0
    return meters * 3.28084


def ft2m(feet: float) -> float:
    """
    Convert feet to meters.


    :param float feet: feet
    :return: elevation in meters
    :rtype: float

    """

    if not isinstance(feet, (float, int)):
        return 0
    return feet / 3.28084


def ms2kmph(ms: float) -> float:
    """
    Convert meters per second to kilometers per hour.

    :param float ms: m/s
    :return: speed in kmph
    :rtype: float

    """

    if not isinstance(ms, (float, int)):
        return 0
    return ms * 3.6


def ms2mph(ms: float) -> float:
    """
    Convert meters per second to miles per hour.

    :param float ms: m/s
    :return: speed in mph
    :rtype: float

    """

    if not isinstance(ms, (float, int)):
        return 0
    return ms * 2.23693674


def ms2knots(ms: float) -> float:
    """
    Convert meters per second to knots.

    :param float ms: m/s
    :return: speed in knots
    :rtype: float

    """

    if not isinstance(ms, (float, int)):
        return 0
    return ms * 1.94384395


def kmph2ms(kmph: float) -> float:
    """
    Convert kilometers per hour to meters per second.

    :param float kmph: kmph
    :return: speed in m/s
    :rtype: float

    """

    if not isinstance(kmph, (float, int)):
        return 0
    return kmph * 0.2777778


def knots2ms(knots: float) -> float:
    """
    Convert knots to meters per second.

    :param float knots: knots
    :return: speed in m/s
    :rtype: float

    """

    if not isinstance(knots, (float, int)):
        return 0
    return knots * 0.5144447324


def pos2iso6709(lat: float, lon: float, alt: float, crs: str = "WGS_84") -> str:
    """
    convert decimal degrees and alt to iso6709 format.

    :param float lat: latitude
    :param float lon: longitude
    :param float alt: altitude
    :param float crs: coordinate reference system (default = WGS_84)
    :return: position in iso6709 format
    :rtype: str

    """

    if not (
        isinstance(lat, (float, int))
        and isinstance(lon, (float, int))
        and isinstance(alt, (float, int))
    ):
        return ""
    lati = "-" if lat < 0 else "+"
    loni = "-" if lon < 0 else "+"
    alti = "-" if alt < 0 else "+"
    iso6709 = (
        lati
        + str(abs(lat))
        + loni
        + str(abs(lon))
        + alti
        + str(alt)
        + "CRS"
        + crs
        + "/"
    )
    return iso6709


def hsv2rgb(h: float, s: float, v: float) -> str:
    """
    Convert HSV values (in range 0-1) to RGB color string.

    :param float h: hue (0-1)
    :param float s: saturation (0-1)
    :param float v: value (0-1)
    :return: rgb color value e.g. "#032a4e"
    :rtype: str

    """

    v = int(v * 255)
    if s == 0.0:
        return f"#{v:02x}{v:02x}{v:02x}"
    i = int(h * 6.0)
    f = (h * 6.0) - i
    p = int(v * (1.0 - s))
    q = int(v * (1.0 - s * f))
    t = int(v * (1.0 - s * (1.0 - f)))
    i %= 6
    if i == 0:
        r, g, b = v, t, p
    if i == 1:
        r, g, b = q, v, p
    if i == 2:
        r, g, b = p, v, t
    if i == 3:
        r, g, b = p, q, v
    if i == 4:
        r, g, b = t, p, v
    if i == 5:
        r, g, b = v, p, q

    return f"#{r:02x}{g:02x}{b:02x}"


def snr2col(snr: int) -> str:
    """
    Convert satellite signal-to-noise ratio to a color
    high = green, low = red.

    :param int snr: signal to noise ratio as integer
    :return: rgb color string
    :rtype: str

    """

    return hsv2rgb(snr / (MAX_SNR * 2.5), 0.8, 0.8)


def svid2gnssid(svid) -> int:
    """
    Derive gnssId from svid numbering range.

    :param int svid: space vehicle ID
    :return: gnssId as integer
    :rtype: int

    """

    if 120 <= svid <= 158:
        gnssId = 1  # SBAS
    elif 211 <= svid <= 246:
        gnssId = 2  # Galileo
    elif (159 <= svid <= 163) or (33 <= svid <= 64):
        gnssId = 3  # Beidou
    elif 173 <= svid <= 182:
        gnssId = 4  # IMES
    elif 193 <= svid <= 202:
        gnssId = 5  # QZSS
    elif (65 <= svid <= 96) or svid == 255:
        gnssId = 6  # GLONASS
    else:
        gnssId = 0  # GPS
    return gnssId


def check_for_update(name: str) -> tuple:
    """
    Check for latest version of module on PyPi.

    :param: str name: name of module to check
    :return: (latest true/false, latest version)
    :rtype: tuple
    """

    ver = []
    for proc in (
        [executable, "-m", "pip", "show", name],
        [executable, "-m", "pip", "install", f"{name}==random"],
    ):
        ver.append(str(subrun(proc, capture_output=True, text=True, check=False)))

    ver[0] = ver[0].split("Version: ")[1].split("\\n")[0]  # current version
    ver[1] = ver[1].split(")\\nERROR:")[0].split(" ")[-1]  # latest version
    return (ver[0] == ver[1], ver[1])


def itow2utc(itow: int) -> datetime.time:
    """
    Convert UBX Time Of Week to UTC datetime

    (UTC = GPS - 18 seconds; correct as from 1/1/2017).
    :param int itow: UBX Time Of Week
    :return: UTC time hh.mm.ss
    :rtype: datetime.time
    """

    dt = datetime(1980, 1, 6) + timedelta(seconds=(itow / 1000) - 18)
    return dt.time()


def estimate_acc(dop: float) -> float:
    """
    Derive a graphic indication of positional accuracy (in m) based on the HDOP
    (Horizontal Dilution of Precision) value and the nominal native device
    accuracy (datasheet CEP)

    NB: this is a largely arbitrary estimate - there is no direct correlation
    between HDOP and accuracy based solely on generic NMEA data.
    The NMEA PUBX,00 or UBX NAV-POSLLH message types return an explicit estimate
    of horizontal and vertical accuracy and are the preferred source.

    :param float dop: horizontal dilution of precision
    :return: horizontal accuracy
    :rtype: float
    """

    return float(dop) * DEVICE_ACCURACY * HDOP_RATIO / 1000


def fix2desc(msgid: str, fix: object) -> str:
    """
    Get integer fix value for given message fix status.

    :param str msgid: UBX or NMEA message identity
    :param object fix: value representing fix type
    :return: descriptive fix status e.g. "3D"
    :rtype: str
    """

    return FIXLOOKUP.get(msgid + str(fix), "NO FIX")


def corrage2int(code: int) -> int:
    """
    Convert NAV-PVT lastCorrectionAge value to age in seconds.

    :param int code: diff age code from NAV-PVT
    :return: string indicating diff age in seconds
    :rtype: int
    """

    LOOKUP = {
        0: 0,
        1: 1,
        2: 2,
        3: 5,
        4: 10,
        5: 15,
        6: 20,
        7: 30,
        8: 45,
        9: 60,
        10: 90,
        11: 120,
    }

    return LOOKUP.get(code, 0)
