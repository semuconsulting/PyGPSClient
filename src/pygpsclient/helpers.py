"""
helpers.py

Collection of helper methods and tkinter class extensions.

Created on 17 Apr 2021

:author: semuadmin (Steve Smith)
:copyright: 2020 semuadmin
:license: BSD 3-Clause

"""

from datetime import datetime, timedelta
from math import (
    asin,
    atan,
    atan2,
    cos,
    degrees,
    pi,
    radians,
    sin,
    sqrt,
    trunc,
)
from os import path
from socket import AF_INET, SOCK_DGRAM, socket
from time import strftime
from tkinter import (
    BooleanVar,
    DoubleVar,
    Entry,
    IntVar,
    Spinbox,
    StringVar,
    Tk,
)
from tkinter.font import Font
from typing import Literal

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
    M2FT,
    M2KM,
    M2MIL,
    M2NMIL,
    MAX_SNR,
    MAXFLOAT,
    MINFLOAT,
    MPS2KNT,
    MPS2KPH,
    MPS2MPH,
    PUBLICIP_URL,
    ROMVER_NEW,
    SCREENSCALE,
    TIME0,
    UI,
    UIK,
    UMK,
    VALBLANK,
    VALBOOL,
    VALDMY,
    VALFLOAT,
    VALHEX,
    VALINT,
    VALLEN,
    VALNONBLANK,
    VALNONSPACE,
    VALURL,
    Area,
    Point,
)
from pygpsclient.strings import NA

# validation type flags
MAXPORT = 65535
MAXALT = 10000.0  # meters arbitrary

# NTRIP enumerations
NMEA = {"0": "No GGA", "1": "GGA"}
AUTHS = {"N": "None", "B": "Basic", "D": "Digest"}
CARRIERS = {"0": "No", "1": "L1", "2": "L1,L2"}
SOLUTIONS = {"0": "Single", "1": "Network"}


def validate(self: Entry, valmode: int, low=MINFLOAT, high=MAXFLOAT) -> bool:
    """
    Extends tkinter.Entry class to add parameterised validation
    and error highlighting.

    :param Entry self: tkinter entry widget instance
    :param int valmode: int representing validation type - can be OR'd
    :param object low: optional min value
    :param object high: optional max value
    :return: True/False
    :rtype: bool
    """

    valid = True
    try:
        val = self.get()
        if valmode == VALBLANK and val == "":
            valid = True  # blank ok
        elif valmode == VALNONBLANK:  # non-blank
            valid = val != "" and not val.isspace()
        elif valmode == VALNONSPACE:  # non-blank
            valid = not val.isspace()
        elif valmode == VALINT:  # int in range
            valid = low < int(val) < high
        elif valmode == VALBOOL:  # boolean
            valid = val in ("0", "1", 1, 0)
        elif valmode == VALFLOAT:  # float in range
            valid = low < float(val) < high
        elif valmode == VALURL:  # valid URL
            # none of the clever RFC 3986 regexes
            # seem to work 100% of the time
            valid = val != "" and not val.isspace()
        elif valmode == VALHEX:  # valid hexadecimal
            bytes.fromhex(val)
        elif valmode == VALDMY:  # valid date YYYYMMDD
            datetime(int(val[0:4]), int(val[4:6]), int(val[6:8]))
        elif valmode == VALLEN:  # valid length
            valid = low <= len(val) <= high
    except ValueError:
        valid = False

    if valid:
        self.configure(highlightthickness=0)
    else:
        self.configure(
            highlightthickness=2, highlightbackground=ERRCOL, highlightcolor=ERRCOL
        )
    return valid


for wdg in (Entry, Spinbox):
    wdg.validate = validate


def trace_update(
    self: IntVar | StringVar | DoubleVar | BooleanVar,
    mode: Literal["array", "read", "write", "unset"],
    callback: object,
    add: bool = True,
) -> str:
    """
    Extends tkinter.*Var classes with trace_update method.

    :param str mode: 'array', 'read', 'write' or 'unset'
    :param function callback: callback
    :param bool add: add (True) or remove (False) trace
    :return: status
    :rtype: str
    """

    if add:
        return self.trace_add(mode, callback)
    if len(self.trace_info()) > 0:
        return self.trace_remove(mode, self.trace_info()[0][1])
    return None


for var in (BooleanVar, DoubleVar, IntVar, StringVar):
    var.trace_update = trace_update

# ****************************************************************
# End of Custom Class Extensions
# ****************************************************************


def area_in_bounds(
    bounds: Area,
    extents: Area,
) -> bool:
    """
    Check if extent is within bounds.

    :param Area bounds: bounding box
    :param Area extents: extents
    :return: true/false
    :rtype: bool
    """

    if bounds is None:
        return False

    return (
        extents.lat1 >= bounds.lat1
        and extents.lat2 <= bounds.lat2
        and extents.lon1 >= bounds.lon1
        and extents.lon2 <= bounds.lon2
    )


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


def brew_installed() -> bool:
    """
    Check if Python installed under Homebrew.

    Some Python/tkinter installations under Homebrew cause
    a critical segmentation error when shell subprocesses
    are invoked.

    :return: yes/no
    :rtype: bool
    """

    return path.isfile("/opt/homebrew/bin/python3")


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


def check_lowres(master: Tk, dim: tuple) -> tuple:
    """
    Check if dialog dimensions exceed effective screen resolution.

    :param tkinter.Tk master: reference to root
    :param tuple dim: dialog dimensions in pixels (height, width)
    :return: low resolution yes/no and effective resolution
    :rtype: tuple (boolean, (screen height/width))
    """

    sh, sw = screenres(master)
    dh, dw = dim
    if sh < dh or sw < dw:
        maxh, maxw = sh, sw
        lowres = True
    else:
        maxh, maxw = dh, dw
        lowres = False
    return lowres, (maxh, maxw)


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
    return "black" if luminance > 0.5 else "white"


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


def fix2desc(msgid: str, fix: object) -> str:
    """
    Get integer fix value for given message fix status.

    :param str msgid: UBX or NMEA message identity
    :param object fix: value representing fix type
    :return: descriptive fix status e.g. "3D"
    :rtype: str
    """

    return FIXLOOKUP.get(msgid + str(fix), "NO FIX")


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


def get_range(val: float, rng: tuple):
    """
    Find first value in range which exceeds specified value.

    :param float val: value
    :param tuple rng: range
    """
    return rng[next(x[0] for x in enumerate(rng) if x[1] > val)]


def get_track_bounds(track: list) -> tuple:
    """
    Get bounds and centre point of track list.

    :param list track: list of TrackPoints
    :return: bounds of track, center point
    :rtype: (Area, Point)
    """

    minlat = minlon = 400
    maxlat = maxlon = -400
    for pnt in track:
        minlat = min(minlat, pnt.lat)
        minlon = min(minlon, pnt.lon)
        maxlat = max(maxlat, pnt.lat)
        maxlon = max(maxlon, pnt.lon)
    return Area(minlat, minlon, maxlat, maxlon), Point(
        (maxlat + minlat) / 2, (maxlon + minlon) / 2
    )


def get_units(units: str) -> tuple:
    """
    Get speed and elevation units and conversions.
    Default is metric - meters and meters per second.

    :param str unit: unit
    :return: tuple of (dst_u, dst_c, ele_u, ele_C, spd_u, spd_c)
    :rtype: tuple
    """

    if units == UI:
        dst_u = "miles"
        dst_c = M2MIL
        ele_u = "ft"
        ele_c = M2FT
        spd_u = "mph"
        spd_c = MPS2MPH
    elif units == UIK:
        dst_u = "naut miles"
        dst_c = M2NMIL
        ele_u = "ft"
        ele_c = M2FT
        spd_u = "knt"
        spd_c = MPS2KNT
    elif units == UMK:
        dst_u = "km"
        dst_c = M2KM
        ele_u = "m"
        ele_c = 1
        spd_u = "kph"
        spd_c = MPS2KPH
    else:  # UMM
        dst_u = "m"
        dst_c = 1
        ele_u = "m"
        ele_c = 1
        spd_u = "m/s"
        spd_c = 1

    return dst_u, dst_c, ele_u, ele_c, spd_u, spd_c


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


def isot2dt(tim: str) -> float:
    """
    Format datetime from ISO time element.

    :param str tim: iso time from trackpoint
    :return: timestamp
    :rtype: float
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


def makeval(val: object, default: object = 0.0) -> object:
    """
    Force value to be same type as default.

    :param object val: value
    :param object default: default value
    :return: value or default
    :rtype: object
    """

    if (not isinstance(val, type(default))) or (
        val == "" and default != val and isinstance(default, str)
    ):
        return default
    return val


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


def nmea2preset(msgs: tuple, desc: str = "") -> str:
    """
    Convert one or more NMEAMessages to format suitable for adding to user-defined
    preset list `nmeapresets_l` in PyGPSClient .json configuration files.

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


def normalise_area(points: tuple) -> Area:
    """
    Convert 4 points to Area in correct order (minlat, minlon, maxlat, maxlon).

    :param tuple points: tuple of lat1, lon1, lat2, lon2
    :return: area
    :rtype: Area
    :raises TypeError: if less than 4 points provided
    """

    if len(points) != 4:
        raise ValueError("Exactly 4 points required")

    minlat = min(points[0], points[2])
    maxlat = max(points[0], points[2])
    minlon = min(points[1], points[3])
    maxlon = max(points[1], points[3])

    return Area(minlat, minlon, maxlat, maxlon)


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


def point_in_bounds(bounds: Area, point: Point) -> bool:
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
    fs = basesize * width / fnt.measure("W" * txtwidth)
    fnt = Font(size=int(min(fs, maxsize))) if maxsize else Font(size=int(fs))
    return fnt, fnt.metrics("linespace")


def screenres(master: Tk, scale: float = SCREENSCALE) -> tuple:
    """
    Get effective screen resolution.

    :param tkinter.Tk master: reference to root
    :param float scale: screen scaling factor
    :return: adjusted screen resolution in pixels (height, width)
    :rtype: tuple
    """

    return (master.winfo_screenheight() * scale, master.winfo_screenwidth() * scale)


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


def set_filename(fpath: str, mode: str, ext: str) -> tuple:
    """
    Return timestamped file name and fully qualified file path.

    :param fpath: the file path as str
    :param mode: the type of file being created ('data', 'track') as str
    :param ext: the file extension ('log', 'gpx') as str
    :return: fully qualified filename and path
    :rtype: tuple of (filename, filepath)
    """

    filename = f"pygps{mode}-{strftime('%Y%m%d%H%M%S')}.{ext}"
    filepath = path.join(fpath, filename)
    return filename, filepath


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
    romver = app.gnss_status.version_data.get("romversion", NA)
    if romver in (NA, "") or romver >= ROMVER_NEW:

        # new style message rate configuration using CFG-VALSET & configuration database keys:
        prot = prot + "_" if prot != "RTCM_3X_TYPE" else prot
        mid = mid.replace("-", "_")
        for prt in prts:
            if prt != "":
                cfgdata = [(f"CFG_MSGOUT_{prot}{mid}_{prt}", rate)]
                msg = UBXMessage.config_set(SET_LAYER_RAM, TXN_NONE, cfgdata)
                app.send_to_device(msg.serialize())

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
        app.send_to_device(msg.serialize())

    return msg


def snr2col(snr: int) -> str:
    """
    Convert satellite signal-to-noise ratio to a color
    high = green, low = red.

    :param int snr: signal to noise ratio as integer
    :return: RGB color string e.g. "#032a4e"
    :rtype: str

    """

    return hsv2rgb(snr / (MAX_SNR * 2.5), 0.8, 0.8)


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


def stringvar2val(val: str, att: str) -> object:
    """
    Convert StringVar entry to appropriate attribute value type.

    :param str val: StringVar value
    :param str att: attribute type e.g. 'U004'
    :return: converted value
    :rtype: object (int, float or bytes)
    """

    if att in ("DE", "LA", "LN"):  # NMEA float
        val = float(val)
    elif att in ("CH", "DT", "HX", "LAD", "LND", "TM"):  # NMEA str, hex
        pass
    elif att == "IN":  # NMEA int
        val = int(val)
    elif atttyp(att) in ("E", "I", "L", "U"):  # integer
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


def unused_sats(data: dict) -> int:
    """
    Get number of 'unused' sats in gnss_data.gsv_data.

    :param dict data: {(gnssid,svid}: (gnssId, svid, elev, azim, cno, last_updated)}
    :return: number of sats where cno = 0
    :rtype: int
    """

    return sum(1 for (_, _, _, _, cno, _) in data.values() if cno == 0)


def ubx2preset(msgs: tuple, desc: str = "") -> str:
    """
    Convert one or more UBXMessages to format suitable for adding to user-defined
    preset list `ubxpresets_l` in PyGPSClient .json configuration files.

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
    if lw == 0 or lh == 0:
        return None
    x, y = xy
    lon = bounds.lon1 + x / (width / lw)
    lat = bounds.lat1 + (height - y) / (height / lh)
    return Point(lat, lon)
