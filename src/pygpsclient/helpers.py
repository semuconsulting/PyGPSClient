"""
helpers.py

PyGPSClient Helpers.

Collection of helper methods.

Created on 17 Apr 2021

:author: semuadmin
:copyright: 2020 SEMU Consulting
:license: BSD 3-Clause

"""

import os
from datetime import datetime, timedelta
from math import asin, atan, atan2, cos, degrees, pi, radians, sin, sqrt, trunc
from socket import AF_INET, SOCK_DGRAM, socket
from time import strftime
from tkinter import Entry
from tkinter.font import Font

from pynmeagps import WGS84_SMAJ_AXIS, haversine
from pyubx2 import (
    SET,
    SET_LAYER_RAM,
    TXN_NONE,
    UBX_CLASSES,
    UBX_MSGIDS,
    UBXMessage,
    attsiz,
    atttyp,
)
from requests import get

from pygpsclient.globals import (
    ERRCOL,
    FIXLOOKUP,
    GPSEPOCH0,
    MAX_SNR,
    PUBLICIP_URL,
    ROMVER_NEW,
    TIME0,
    Area,
    AreaXY,
    Point,
)
from pygpsclient.strings import NA

# validation type flags
MAXPORT = 65535
MAXALT = 10000.0  # meters arbitrary
MAXFLOAT = 2e20
MINFLOAT = -MAXFLOAT
VALBLANK = 1
VALNONBLANK = 2
VALINT = 4
VALFLOAT = 8
VALURL = 16
VALHEX = 32
VALDMY = 64
VALLEN = 128

# NTRIP enumerations
NMEA = {"0": "No GGA", "1": "GGA"}
AUTHS = {"N": "None", "B": "Basic", "D": "Digest"}
CARRIERS = {"0": "No", "1": "L1", "2": "L1,L2"}
SOLUTIONS = {"0": "Single", "1": "Network"}
POINTLIMIT = 500  # max number of shape points supported by MapQuest API


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

    r = g = b = 0
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
    elif 247 <= svid <= 253:
        gnssId = 7  # NAVIC
    else:
        gnssId = 0  # GPS
    return gnssId


def get_mp_info(srt: list) -> dict:
    """
    Get mountpoint information from sourcetable entry.

    :param list srt: sourcetable entry as list
    :return: dictionary of mountpoint info
    :rtype: dict or None if not available
    """

    try:
        return {
            "name": srt[0],
            "identifier": srt[1],
            "format": srt[2],
            "messages": srt[3],
            "carrier": CARRIERS.get(srt[4], srt[4]),
            "navs": srt[5],
            "network": srt[6],
            "country": srt[7],
            "lat": srt[8],
            "lon": srt[9],
            "gga": NMEA.get(srt[10], srt[10]),
            "solution": SOLUTIONS.get(srt[11], srt[11]),
            "generator": srt[12],
            "encrypt": srt[13],
            "auth": AUTHS.get(srt[14], srt[14]),
            "fee": srt[15],
            "bitrate": srt[16],
        }
    except IndexError:
        return None


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

    # regex = re.compile(
    #     # r"^(?:http|https)?://"  # http:// or https://
    #     r"^(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"  # domain...
    #     r"localhost|"  # localhost...
    #     r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
    #     r"(?::\d+)?"  # optional port
    #     r"(?:/?|[/?]\S+)$",
    #     re.IGNORECASE,
    # )

    # return re.match(regex, url) is not None
    return url not in (None, "")


def valid_entry(entry: Entry, valmode: int, low=MINFLOAT, high=MAXFLOAT) -> bool:
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
            highlightthickness=2, highlightbackground=ERRCOL, highlightcolor=ERRCOL
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
    elif atttyp(att) in ("IN", "HX"):  # NMEA int
        val = int(val)
    elif atttyp(att) in ("DE", "LA", "LN"):  # NMEA float
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

    return int.from_bytes(bitfield, "big") >> (lbb - position - length) & 2**length - 1


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


def dop2str(dop: float) -> str:
    """
    Convert Dilution of Precision float to descriptive string.

    :param float dop: dilution of precision as float
    :return: dilution of precision as string
    :rtype: str

    """

    if dop == 0:
        dops = "N/A"
    elif dop <= 1:
        dops = "Ideal"
    elif dop <= 2:
        dops = "Excellent"
    elif dop <= 5:
        dops = "Good"
    elif dop <= 10:
        dops = "Moderate"
    elif dop <= 20:
        dops = "Fair"
    else:
        dops = "Poor"
    return dops


def fontwidth(fnt: Font, txt: str = "W") -> int:
    """
    Get font width.

    :param Font fnt:font
    :param txt: reference text ("W")
    :return: font width in pixels
    :rtype: int
    """

    return Font.measure(fnt, txt)


def fontheight(fnt: Font) -> int:
    """
    Get font height.

    :param Font fnt: font
    :return: font height in pixels
    :rtype: int
    """

    return Font.metrics(fnt, "linespace")


def scale_font(
    width: int, basesize: int, txtwidth: int, maxsize: int = 0, fnt: Font = None
) -> tuple:
    """
    Scale font size to widget width.

    :param int width: widget width
    :param int bassiz: base font size
    :param int txtwidth: reference text width
    :param int maxsiz: max font size
    :param Font fnt: default font
    :return: tuple of scaled font, font height
    :rtype: tuple
    """

    fnt = Font(size=12) if fnt is None else fnt
    fs = basesize * width / fontwidth(fnt, "W" * txtwidth)
    fnt = Font(size=int(min(fs, maxsize))) if maxsize else Font(size=int(fs))
    return fnt, fontheight(fnt)


def setubxrate(app: object, mid: str, rate: int = 1, prot: str = "UBX") -> UBXMessage:
    """
    Set rate on specified UBX message on default port(s).

    Uses either CFG-MSG or CFG-VALSET command, depending on device ROM version.

    The port(s) this applies to are defined in the 'defaultport_s'
    configuration setting as a comma-separated string e.g. "USB,UART1".

    Rate is relative to navigation solution e.g.
    a rate of '4' means 'every 4th navigation solution'
    (higher = less frequent).

    :param object application: reference to calling application
    :param str mid: message identity e.g. "MON-SPAN"
    :param int rate: message rate (0 = off)
    :param str prot: message protocol ("UBX", "NMEA_ID", "PUBX_ID", "RTCM_3X_TYPE")
    :return: UBX set rate command
    :rtype: UBXMessage
    :raises: ValueError if unknown message identity
    """

    rates = {}
    msg = None
    # select which receiver ports to apply rate to
    prts = app.configuration.get("defaultport_s").split(",")

    # check device ROM version for configuration support
    romver = app.gnss_status.version_data.get("romversion", NA).replace(NA, "")
    if romver >= ROMVER_NEW:

        # new style message rate configuration using CFG-VALSET & configuration database keys:
        prot = prot + "_" if prot != "RTCM_3X_TYPE" else prot
        mid = mid.replace("-", "_")
        for prt in prts:
            if prt != "":
                cfgdata = [(f"CFG_MSGOUT_{prot}{mid}_{prt}", rate)]
                msg = UBXMessage.config_set(SET_LAYER_RAM, TXN_NONE, cfgdata)
                app.gnss_outqueue.put(msg.serialize())

    else:

        # old style message rate configuration usng CFG-MSG:
        for prt in prts:
            rates[prt] = rate

        msgclass = msgid = None
        for msgtype, msgnam in UBX_MSGIDS.items():
            if msgnam == mid:
                msgclass = msgtype[0]
                msgid = msgtype[1]
                break
        if msgclass is None or msgid is None:
            raise ValueError(f"Message ID {mid} unknown")

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

    return msg


def val2sphp(val: float, scale: float) -> tuple:
    """
    Convert a float value into separate
    standard and high precisions components,
    multiplied by a scaling factor to render them
    as integers.

    As required by e.g. UBX CFG-TMODE command.

    :param float val: value as float
    :param float scale: scaling factor e.g. 1e-7
    :return: tuple of (standard precision, high precision)
    :rtype: tuple
    """

    val = val / scale
    val_sp = trunc(val)
    val_hp = round((val - val_sp) * 100)
    return val_sp, val_hp


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


def ned2vector(n: float, e: float, d: float) -> tuple:
    """
    Convert N,E,D relative position to 2D heading and distance.

    :param float n: north coordinate
    :param float e: east coordinate
    :param float d: down coordinate
    :return: tuple of distance, heading
    :rtype: tuple
    """

    dis = sqrt(n**2 + e**2 + d**2)
    if n == 0 or e == 0:
        hdg = 0
    else:
        hdg = atan(e / n) * 180 / pi
        if hdg > 0:
            hdg += 180
        else:
            hdg += 360
    return dis, hdg


def isot2dt(tim: str) -> datetime:
    """
    Format datetime from ISO time element.

    :param str tim: iso time from trackpoint
    :return: datetime
    :rtype: datetime
    """

    if tim[-1] == "Z":  # strip timezone label
        tim = tim[0:-1]
    if tim[-4] == ".":  # has milliseconds
        tfm = "%Y-%m-%dT%H:%M:%S.%f"
    elif tim[-7] == ".":  # has microseconds
        tfm = "%Y-%m-%dT%H:%M:%S.%f"
    else:
        tfm = "%Y-%m-%dT%H:%M:%S"
    return datetime.strptime(tim, tfm).timestamp()


def publicip() -> str:
    """
    Get public IP address from ipinfo REST API.

    :return: Public IP address as string, or "N/A' if not available.
    """

    try:
        response = get(PUBLICIP_URL, verify=True, timeout=3)
        response.raise_for_status()
        return response.json().get("ip", "N/A")
    except Exception:  # pylint: disable=broad-exception-caught
        return "N/A"


def lanip() -> str:
    """
    Get LAN IP address via socket connection info.

    :return: LAN IP address as string, or "N/A' if not available.
    """

    with socket(AF_INET, SOCK_DGRAM) as sck:
        try:
            sck.connect(("8.8.8.8", 80))
            return sck.getsockname()[0]
        except Exception:  # pylint: disable=broad-exception-caught
            return "N/A"


def get_point_at_vector(
    start: Point,
    dist: float,
    bearing: float,
    radius: float = WGS84_SMAJ_AXIS,
) -> Point:
    """
    Get new point at vector from start position.

    :param Point start: starting position
    :param float dist: vector distance
    :param float bearing: vector bearing (true)
    :param float radius: optional radius of sphere, defaults to mean radius of earth
    :return: new position as lat/lon
    :rtype: Point
    """

    phi1 = radians(start.lat)
    lambda1 = radians(start.lon)
    br = radians(bearing)
    phi2 = asin(
        sin(phi1) * cos(dist / radius) + cos(phi1) * sin(dist / radius) * cos(br)
    )
    lambda2 = lambda1 + atan2(
        sin(br) * sin(dist / radius) * cos(phi1),
        cos(dist / radius) - sin(phi1) * sin(phi2),
    )
    return Point(degrees(phi2), degrees(lambda2))


def in_bounds(bounds: Area, point: Point) -> bool:
    """
    Check if given point is within canvas bounding box.

    :param Area bounds: bounding box
    :param Point point: point
    :return: true/false
    :rtype: bool
    """

    if bounds is None:
        return False

    return (
        point.lat >= bounds.lat1
        and point.lat <= bounds.lat2
        and point.lon >= bounds.lon1
        and point.lon <= bounds.lon2
    )


def reorder_range(valuerange: tuple, default) -> tuple:
    """
    Reorder range so default is first value (e.g. for
    spinbox objects).

    :param tuple valuerange: range
    :param object default: starting value
    :return: range starting with default
    :rtype: tuple
    """

    drange = valuerange
    lr = len(valuerange)
    for i, val in enumerate(valuerange):
        if val == default:
            drange = valuerange[i:lr] + valuerange[0:i]
            break
    return drange


def ll2xy(width: int, height: int, bounds: Area, position: Point) -> tuple:
    """
    Convert lat/lon to canvas x/y.

    :param int width: canvas width
    :param int height: canvas height
    :param Area bounds: lat/lon bounds of canvas
    :param Point coordinate: lat/lon
    :return: x,y canvas coordinates
    :rtype: tuple
    """

    lw = bounds.lon2 - bounds.lon1
    lh = bounds.lat2 - bounds.lat1
    x = (position.lon - bounds.lon1) / (lw / width)
    y = height - (position.lat - bounds.lat1) / (lh / height)
    return x, y


def xy2ll(width: int, height: int, bounds: Area, xy: tuple) -> Point:
    """
    Convert canvas x/y to lat/lon.

    :param int width: canvas width
    :param int height: canvas height
    :param Area bounds: lat/lon bounds of canvas
    :param tuple xy: canvas x/y coordinate
    :return: lat/lon
    :rtype: Point
    """

    lw = bounds.lon2 - bounds.lon1
    lh = bounds.lat2 - bounds.lat1
    x, y = xy
    lon = bounds.lon1 + x / (width / lw)
    lat = bounds.lat1 + (height - y) / (height / lh)
    return Point(lat, lon)


def data2xy(
    width: int,
    height: int,
    bounds: AreaXY,
    xdata: float,
    ydata: float,
    xoffset: float = 0,
    yoffset: float = 0,
) -> tuple:
    """
    Convert datapoint x,y to canvas x,y. Y is vertical axis.

    :param int width: canvas width
    :param int height: canvas height
    :param AreaXY bounds: x,y bounds of data
    :param float xdata: datapoint x
    :param float ydata: datapoint y
    :param float xoffset: canvas x offset
    :param float yoffset: canvas y offset
    :return: x,y canvas coordinates
    :rtype: tuple
    """
    # pylint: disable=too-many-arguments, too-many-positional-arguments

    try:
        lw = bounds.x2 - bounds.x1
        lh = bounds.y2 - bounds.y1
        x = (xdata - bounds.x1) / (lw / width)
        y = height - (ydata - bounds.y1) / (lh / height)
    except ZeroDivisionError:
        return 0, 0
    return x + xoffset, y + yoffset


def xy2data(
    width: int,
    height: int,
    bounds: AreaXY,
    x: int,
    y: int,
    xoffset: int = 0,
    yoffset: int = 0,
) -> tuple:
    """
    Convert canvas x,y to datapoint x,y. Y is vertical axis.

    :param int width: canvas width
    :param int height: canvas height
    :param AreaXY bounds: x,y bounds of data
    :param int x: canvas x coordinate
    :param int y: canvas y coordinate
    :param float xoffset: canvas x offset
    :param float yoffset: canvas y offset
    :return: xdata, ydata
    :rtype: tuple
    """
    # pylint: disable=too-many-arguments, too-many-positional-arguments

    try:
        lw = bounds.x2 - bounds.x1
        lh = bounds.y2 - bounds.y1
        datax = bounds.x1 + (x - xoffset) / (width / lw)
        datay = bounds.y1 + (height - (y - yoffset)) / (height / lh)
    except ZeroDivisionError:
        return 0, 0
    return datax, datay


def points2area(points: tuple) -> Area:
    """
    Convert 4 points to Area.

    Points in order (minlat, minlon, maxlat, maxlon)

    :param tuple points: tuple of points
    :raises TypeError: if less than 4 points provided
    :return: area
    :rtype Area
    """

    if len(points) != 4:
        raise ValueError("Exactly 4 points required")

    minlat = min(points[0], points[2])
    maxlat = max(points[0], points[2])
    minlon = min(points[1], points[3])
    maxlon = max(points[1], points[3])

    return Area(minlat, minlon, maxlat, maxlon)


def limittrack(track: list, limit: int = POINTLIMIT) -> list:
    """
    Limit number of points in track.

    :param list track: list of Points
    :param int limit: max points
    :return: limited list of Points
    """

    points = []
    stp = 1
    rng = len(track)
    while rng / stp > limit:
        stp += 1
    for i, p in enumerate(track):
        if i % stp == 0:
            points.append(p)
    return points


def get_grid(
    num: int = 10, start: int = 0, stop: int = 1, endpoint: bool = True
) -> tuple:
    """
    Generate linear grid steps for graphing widgets.

    :param int num: number of increments (10)
    :param int start: start point (0)
    :param int stop: end point (1)
    :param bool endpoint: include endpoint (True)
    :return: linear grid increments
    :rtype: tuple
    """

    def linspace(start, stop, num, endpoint):
        """Generator for linear grid"""
        num = int(num)
        start = start * 1.0
        stop = stop * 1.0

        if num == 1:
            yield round(stop, 4)
            return
        if endpoint:
            step = (stop - start) / (num - 1)
        else:
            step = (stop - start) / num

        for i in range(num):
            yield round(start + step * i, 4)

    return tuple(linspace(start, stop, num, endpoint))


def time2str(tim: float, sformat: str = "%H:%M:%S") -> str:
    """
    Convert time float to formatted string.

    :param float tim: time as float (seconds since 1970-01-01-00:00:00)
    :param str sformat: string format ("%H:%M:%S")
    :return: formated time string
    :rtype: str
    """

    dt = TIME0 + timedelta(seconds=tim)
    return dt.strftime(sformat)


def ubx2preset(msgs: tuple, desc: str = "") -> str:
    """
    Convert one or more UBXMessages to format suitable for adding to user-defined
    preset list `ubxpresets_l` in PyGPSClient *.json configuration files.

    The format is:
    "<description>, <talker>, <msgID>, <payload as hexadecimal string>, <msgmode>"

    e.g. "Set NMEA High Precision Mode, CFG, CFG-VALSET, 000100000600931001, 1"

    :param tuple msgs: UBXMessage or tuple of UBXmessages
    :param str desc: preset description
    :return: preset string
    :rtype: str
    """

    desc = desc.replace(",", " ")
    if not isinstance(msgs, tuple):
        msgs = (msgs,)
    preset = (
        f"{msgs[0].identity} {['GET','SET','POLL'][msgs[0].msgmode]}"
        if desc == ""
        else desc
    )
    for msg in msgs:
        preset += (
            f", {UBX_CLASSES[msg.msg_cls]}, {UBX_MSGIDS[msg.msg_cls + msg.msg_id]}, "
            f"{msg.payload.hex()}, {msg.msgmode}"
        )
    return preset


def nmea2preset(msgs: tuple, desc: str = "") -> str:
    """
    Convert one or more NMEAMessages to format suitable for adding to user-defined
    preset list `nmeapresets_l` in PyGPSClient *.json configuration files.

    The format is:
    "<description>; <talker>; <msgID>; <payload as comma separated list>; <msgmode>"

    e.g. "Configure Signals; P; QTMCFGSIGNAL; W,7,3,F,3F,7,1; 1"

    :param tuple msgs: NMEAmessage or tuple of NMEAmessages
    :param str desc: preset description
    :return: preset string
    :rtype: str
    """

    desc = desc.replace(";", " ")
    if not isinstance(msgs, tuple):
        msgs = (msgs,)
    preset = (
        f"{msgs[0].identity} {['GET','SET','POLL'][msgs[0].msgmode]}"
        if desc == ""
        else desc
    )
    for msg in msgs:
        preset += f"; {msg.talker}; {msg.msgID}; {','.join(msg.payload)}; {msg.msgmode}"
    return preset
