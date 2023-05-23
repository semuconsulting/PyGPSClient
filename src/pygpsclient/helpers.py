"""
PyGPSClient Helpers

Collection of helper methods

Created on 17 Apr 2021

:author: semuadmin
:copyright: SEMU Consulting © 2021
:license: BSD 3-Clause

"""

import os
import re
from datetime import datetime, timedelta
from math import cos, pi, sin
from time import strftime
from tkinter import Button, Entry, Label, Toplevel, W, font

from pynmeagps import haversine
from pyubx2 import SET, UBXMessage, attsiz, atttyp
from requests import get

from pygpsclient.globals import FIXLOOKUP, GPSEPOCH0, MAX_SNR
from pygpsclient.strings import NA

# validation type flags
MAXPORT = 65535
MAXALT = 10000.0  # meters arbitrary
VALBLANK = 1
VALNONBLANK = 2
VALINT = 4
VALFLOAT = 8
VALURL = 16
VALHEX = 32
VALDMY = 64
VALLEN = 128


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
    elevation = elevation * pi / 180
    azimuth = azimuth * pi / 180
    x = cos(azimuth) * cos(elevation)
    y = sin(azimuth) * cos(elevation)
    return (x, y)


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


def rgb2str(r: int, g: int, b: int) -> str:
    """
    Convert R,G,B values to RGB color string.

    :param int r: red value (0-255)
    :param int g: green value (0-255)
    :param int b: blue value (0-255)
    :return: RGB color string e.g. "#032a4e"
    :rtype: str
    """

    return f"#{r:02x}{g:02x}{b:02x}"


def str2rgb(col: str) -> tuple:
    """
    Convert RGB color string to R,G,B values.

    :param str col: RGB color string e.g. "#032a4e"
    :return: tuple of (r,g,b) as integers
    :rtype: tuple
    """

    r = int(col[1:3], 16)
    g = int(col[3:5], 16)
    b = int(col[5:7], 16)
    return (r, g, b)


def hsv2rgb(h: float, s: float, v: float) -> str:
    """
    Convert HSV values (in range 0-1) to RGB color string.

    :param float h: hue (0-1)
    :param float s: saturation (0-1)
    :param float v: value (0-1)
    :return: RGB color string e.g. "#032a4e"
    :rtype: str
    """

    v = int(v * 255)
    if s == 0.0:
        return rgb2str(v, v, v)
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

    return rgb2str(r, g, b)


def col2contrast(col: str) -> str:
    """
    Find best contrasting color against background
    using perceived luminance (human eye favors green color).

    :param str col: RGB color string e.g. "#032a4e"
    :return: "black' or "white"
    :rtype: str
    """

    r, g, b = str2rgb(col)
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    col = "black" if luminance > 0.5 else "white"
    return col


def snr2col(snr: int) -> str:
    """
    Convert satellite signal-to-noise ratio to a color
    high = green, low = red.

    :param int snr: signal to noise ratio as integer
    :return: RGB color string e.g. "#032a4e"
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


def get_mp_distance(lat: float, lon: float, mp: list) -> float:
    """
    Get distance to mountpoint from current location (if known).

    The sourcetable mountpoint entry is a list where index [0]
    is the name and indices [8] & [9] are the lat/lon. Not all
    sourcetable entries provide this information.

    :param float lat: current latitude
    :param float lon: current longitude
    :param list mp: sourcetable mountpoint entry
    :return: distance to mountpoint in km, or None if n/a
    :rtype: float or None
    """

    dist = None
    try:
        if len(mp) > 9:  # if location provided for this mountpoint
            lat2 = float(mp[8])
            lon2 = float(mp[9])
            dist = haversine(lat, lon, lat2, lon2)
    except (ValueError, TypeError):
        pass

    return dist


def check_latest(name: str) -> str:
    """
    Check for latest version of module on PyPi.

    :param str name: name of module to check
    :return: latest version e.g. "1.3.5"
    :rtype: str
    """

    try:
        return get(f"https://pypi.org/pypi/{name}/json", timeout=3).json()["info"][
            "version"
        ]
    except Exception:  # pylint: disable=broad-except
        return NA


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

    lookup = {
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

    return lookup.get(code, 0)


def validURL(url: str) -> bool:
    """
    Validate URL.

    :param str url: URL to check
    :return: valid True/False
    :rtype: bool
    """
    # pylint: disable=line-too-long

    regex = re.compile(
        # r"^(?:http|https)?://"  # http:// or https://
        r"^(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"  # domain...
        r"localhost|"  # localhost...
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
        r"(?::\d+)?"  # optional port
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )

    return re.match(regex, url) is not None


def valid_entry(entry: Entry, valmode: int, low=None, high=None) -> bool:
    """
    Validates tkinter entry field and highlights it if in error.

    :param Entry entry: tkinter entry widget
    :param int valmode: int representing validation type - can be OR'd
    :param object low: optional min value
    :param object high: optional max value
    :return: True/False
    :rtype: bool
    """

    valid = True
    try:
        if valmode & VALBLANK and entry.get() == "":  # blank ok
            valid = True
        else:
            if valmode & VALNONBLANK:  # non-blank
                valid = entry.get() != ""
            if valmode & VALINT:  # int in range
                valid = low < int(entry.get()) < high
            if valmode & VALFLOAT:  # float in range
                valid = low < float(entry.get()) < high
            if valmode & VALURL:  # valid URL
                valid = validURL(entry.get())
            if valmode & VALHEX:  # valid hexadecimal
                bytes.fromhex(entry.get())
            if valmode & VALDMY:  # valid date YYYYMMDD
                dat = entry.get()
                datetime(int(dat[0:4]), int(dat[4:6]), int(dat[6:8]))
            if valmode & VALLEN:  # valid length
                valid = low <= len(entry.get()) <= high
    except ValueError:
        valid = False

    # entry.config(bg=ENTCOL if valid else ERRCOL)
    if valid:
        entry.configure(highlightthickness=0)
    else:
        entry.configure(
            highlightthickness=1, highlightbackground="red", highlightcolor="red"
        )
    return valid


def stringvar2val(val: str, att: str) -> object:
    """
    Convert StringVar entry to appropriate attribute value type.

    :param str val: StringVar value
    :param str att: attribute type e.g. 'U004'
    :return: converted value
    :rtype: object (int, float or bytes)
    """

    if atttyp(att) in ("E", "I", "L", "U"):  # integer
        if val.find(".") != -1:  # ignore scaling decimals
            val = val[0 : val.find(".")]
        val = int(val)
    elif atttyp(att) == "X":  # bytes
        if val[0:2] in ("0x", "0X"):  # allow for hex representation
            mod = 16
        else:
            mod = 10
        val = int(val, mod).to_bytes(attsiz(att), "big")
    elif atttyp(att) == "C":  # char
        val = bytes(val, "utf-8")
    elif atttyp(att) == "R":  # float
        val = float(val)

    return val


def set_filename(path: str, mode: str, ext: str) -> tuple:
    """
    Return timestamped file name and fully qualified file path.

    :param path: the file path as str
    :param mode: the type of file being created ('data', 'track') as str
    :param ext: the file extension ('log', 'gpx') as str
    :return: fully qualified filename and path
    :rtype: tuple of (filename, filepath)
    """

    filename = f"pygps{mode}-{strftime('%Y%m%d%H%M%S')}.{ext}"
    filepath = os.path.join(path, filename)
    return filename, filepath


def date2wnotow(dat: datetime) -> tuple:
    """
    Get GPS Week number (Wno) and Time of Week (Tow)
    for given datetime.

    GPS Epoch 0 = 6th Jan 1980

    :param datetime dat: calendar date
    :return: tuple of (Wno, Tow)
    :rtype: tuple
    """

    wno = int((dat - GPSEPOCH0).days / 7)
    tow = ((dat.weekday() + 1) % 7) * 86400
    return wno, tow


def wnotow2date(wno: int, tow: int) -> datetime:
    """
    Get datetime from GPS Week number (Wno) and Time of Week (Tow).

    GPS Epoch 0 = 6th Jan 1980

    :param int wno: week number
    :param int tow: time of week
    :return: datetime
    :rtype: datetime
    """

    dat = GPSEPOCH0 + timedelta(days=wno * 7)
    dat += timedelta(seconds=tow)
    return dat


def bitsval(bitfield: bytes, position: int, length: int) -> int:
    """
    Get unisgned integer value of masked bits in bitfield.

    :param bytes bitfield: bytes
    :param int position: position in bitfield, from leftmost bit
    :param int length: length of masked bits
    :return: value
    :rtype: int
    """

    lbb = len(bitfield) * 8
    if position + length > lbb:
        return None

    return (
        int.from_bytes(bitfield, "big") >> (lbb - position - length) & 2**length - 1
    )


def parse_rxmspartnkey(msg: UBXMessage) -> list:
    """
    Extract dates and keys from RXM-SPARTNKEY message.

    :param UBXMessage msg: RXM-SPARTNKEY message
    :return: list of (key, valid from date) tuples
    :rtype: list
    """

    keys = []
    pos = 0
    for i in range(msg.numKeys):
        lkey = getattr(msg, f"keyLengthBytes_{i+1:02}")
        wno = getattr(msg, f"validFromWno_{i+1:02}")
        tow = getattr(msg, f"validFromTow_{i+1:02}")
        dat = wnotow2date(wno, tow)
        key = ""
        for n in range(0 + pos, lkey + pos):
            keyb = getattr(msg, f"key_{n+1:02}")
            key += f"{keyb:02x}"
        keys.append((key, dat))
        pos += lkey

    return keys


def bytes2unit(valb: int) -> tuple:
    """Format bytes as KB, MB, GB etc
    such that value < 100.

    :param int valb: bytes
    :return: tuple of (value, units)
    """

    if not isinstance(valb, (int, float)):
        return 0, NA

    BYTESUNITS = ["", "KB", "MB", "GB", "TB"]
    i = 0
    val = valb
    valu = BYTESUNITS[i]
    while val > 500:
        val = valb / (2 ** (i * 10))
        valu = BYTESUNITS[i]
        i += 1
        if i > 4:
            break
    return val, valu


def secs2unit(secs: int) -> tuple:
    """
    Format seconds as secs, mins, hours or days
    such that value is > 100.

    :param int secs: seconds
    :return: tuple of (value, units)
    :rtype: tuple
    """

    if not isinstance(secs, (int, float)):
        return 0, NA

    SECSUNITS = ["secs", "mins", "hrs", "days"]
    SECSDIV = [60, 3600, 86400]

    i = 0
    val = secs
    while val > 100:
        val = secs / SECSDIV[i]
        i += 1
        if i > 2:
            break
    return val, SECSUNITS[i]


def sizefont(height: int, lines: int, minfont: int) -> tuple:
    """
    Set font size according to number of text lines on widget
    of given height.

    :param int maxlines: max no of lines of text
    :param int minfont: min font size
    :returns: tuple of (font, fontheight)
    :rtype: tuple
    """

    fh = 0
    fs = minfont
    while fh * lines < height:
        fnt = font.Font(size=fs)
        fh = fnt.metrics("linespace")
        fs += 1
    return fnt, fh


def setubxrate(app: object, msgclass: int, msgid: int, rate: int = 1):
    """
    Set rate on specified UBX message on default port(s).

    The port(s) this applies to are defined in the 'defaultport'
    configuration setting as a string or list.

    Rate is relative to navigation solution e.g.
    a rate of '4' means 'every 4th navigation solution'
    (higher = less frequent).

    :param App app: calling application (PyGPSClient)
    :param int msgclass: msgClass
    :param int msgid: msgId
    :param int rate: message rate (0 = off)
    """

    if app is None:
        return

    rates = {}
    prts = app.app_config.get("defaultport", "USB")
    if isinstance(prts, str):
        prts = [
            prts,
        ]
    for prt in prts:
        rates[prt] = rate

    msg = UBXMessage(
        "CFG",
        "CFG-MSG",
        SET,
        msgClass=msgclass,
        msgID=msgid,
        rateDDC=rates.get("I2C", 0),
        rateUART1=rates.get("UART1", 0),
        rateUART2=rates.get("UART2", 0),
        rateUSB=rates.get("USB", 0),
        rateSPI=rates.get("SPI", 0),
    )
    app.gnss_outqueue.put(msg.serialize())
