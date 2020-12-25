"""
PyGPSClient Globals

Collection of global constants and helper methods

Created on 14 Sep 2020

@author: semuadmin
"""
# pylint: disable=invalid-name, line-too-long

import os
from math import sin, cos, pi
from serial import PARITY_NONE, PARITY_EVEN, PARITY_ODD, PARITY_MARK, PARITY_SPACE
from pynmea2 import types

DIRNAME = os.path.dirname(__file__)
ICON_APP = os.path.join(DIRNAME, "resources/iconmonstr-location-27-32.png")
ICON_CONN = os.path.join(DIRNAME, "resources/iconmonstr-link-8-24.png")
ICON_DISCONN = os.path.join(DIRNAME, "resources/iconmonstr-link-10-24.png")
ICON_POS = os.path.join(DIRNAME, "resources/iconmonstr-location-1-24.png")
ICON_SEND = os.path.join(DIRNAME, "resources/iconmonstr-arrow-12-24.png")
ICON_EXIT = os.path.join(DIRNAME, "resources/iconmonstr-door-6-24.png")
ICON_PENDING = os.path.join(DIRNAME, "resources/iconmonstr-time-6-24.png")
ICON_CONFIRMED = os.path.join(DIRNAME, "resources/iconmonstr-check-mark-8-24.png")
ICON_WARNING = os.path.join(DIRNAME, "resources/iconmonstr-warning-1-24.png")
ICON_UBXCONFIG = os.path.join(DIRNAME, "resources/iconmonstr-gear-2-24.png")
ICON_LOGREAD = os.path.join(DIRNAME, "resources/iconmonstr-note-37-24.png")
IMG_WORLD = os.path.join(DIRNAME, "resources/world.png")
BTN_CONNECT = "\u25b6"  # text on "Connected" button
BTN_DISCONNECT = "\u2587"  # text on "Disconnected" button

GITHUB_URL = "https://github.com/semuconsulting/PyGPSClient"
XML_HDR = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
GPX_NS = " ".join(
    (
        'xmlns="http://www.topografix.com/GPX/1/1"',
        'creator="PyGPSClient" version="1.1"',
        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"',
        'xsi:schemaLocation="http://www.topografix.com/GPX/1/1',
        'http://www.topografix.com/GPX/1/1/gpx.xsd"',
    )
)
MAPURL = "https://www.mapquestapi.com/staticmap/v5/map?key={}&locations={},{}&zoom={}&defaultMarker=marker-sm-616161-ff4444&shape=radius:{}|weight:1|fill:ccffff50|border:88888850|{},{}&size={},{}"
MAP_UPDATE_INTERVAL = (
    60  # how frequently the mapquest api is called to update the web map
)
SAT_EXPIRY = 10  # how long passed satellites are kept in the sky and graph views
MAX_SNR = 60  # upper limit of graphview snr axis
DEVICE_ACCURACY = 2.5  # nominal GPS device accuracy (CEP) in meters
HDOP_RATIO = 20  # arbitrary calibration of accuracy against HDOP
PORTIDS = ("0 I2C", "1 UART1", "2 UART2", "3 USB", "4 SPI")
ANTSTATUS = ("INIT", "DONTKNOW", "OK", "SHORT", "OPEN")
ANTPOWER = ("OFF", "ON", "DONTKNOW")
# array of default serial device descriptors
KNOWNGPS = ("GPS", "gps", "GNSS", "gnss", "Garmin", "garmin", "U-Blox", "u-blox")
BAUDRATES = (115200, 57600, 38400, 19200, 9600, 4800)
PARITIES = {
    "Even": PARITY_EVEN,
    "Odd": PARITY_ODD,
    "Mark": PARITY_MARK,
    "Space": PARITY_SPACE,
    "None": PARITY_NONE,
}
# serial port timeout; lower is better for app response
# but you may lose packets on high latency connections
SERIAL_TIMEOUT = 0.2
MQAPIKEY = "mqapikey"
UBXPRESETS = "ubxpresets"
MAXLOGLINES = 10000  # maximum number of 'lines' per datalog file
NMEA_PROTOCOL = 0
UBX_PROTOCOL = 1
MIXED_PROTOCOL = 2
DISCONNECTED = 0
CONNECTED = 1
CONNECTED_FILE = 2
NOPORTS = 3
WIDGETU1 = (250, 250)
WIDGETU2 = (350, 250)
WIDGETU3 = (950, 350)
BGCOL = "gray24"  # default widget background color
FGCOL = "white"  # default widget foreground color
ENTCOL = "azure"  # default valid data entry field background color
ERRCOL = "pink"  # default invalid data entry field background color
INFCOL = "steelblue3"  # readonly info field text color
READONLY = "readonly"
ERROR = "ERR!"
DDD = "DD.D"
DMM = "DM.M"
DMS = "D.M.S"
UMM = "Metric m/s"
UMK = "Metric kmph"
UI = "Imperial mph"
UIK = "Imperial knots"
ADVOFF = "\u25bc"
ADVON = "\u25b2"

# ubx config widget confirmation flags
UBX_MONVER = 0
UBX_MONHW = 1
UBX_CFGPRT = 2
UBX_CFGMSG = 3
UBX_CFGVAL = 4
UBX_PRESET = 5

GLONASS_NMEA = True  # use GLONASS NMEA SVID (65-96) rather than slot (1-24)
GNSS_LIST = {
    0: ("GPS", "royalblue"),
    1: ("SBA", "orange"),
    2: ("GAL", "green4"),
    3: ("BEI", "purple"),
    4: ("IME", "violet"),
    5: ("QZS", "yellow"),
    6: ("GLO", "indianred"),
}

# List of tags to highlight in console
TAGS = [
    ("ACK-ACK", "green2"),
    ("ACK-NAK", "orange red"),
    ("CFG-MSG", "cyan"),
    ("CFG-VALGET", "deepskyblue"),
    ("DTM", "deepskyblue"),
    ("GAQ", "pink"),
    ("GBQ", "pink"),
    ("GBS", "pink"),
    ("GGA", "orange"),
    ("GLL", "orange"),
    ("GLQ", "pink"),
    ("GNQ", "pink"),
    ("GNS", "orange"),
    ("GQQ", "pink"),
    ("GRS", "yellow"),
    ("GSA", "green2"),
    ("GST", "mediumpurple2"),
    ("GSV", "yellow"),
    ("INF-ERROR", "red2"),
    ("INF-NOTICE", "deepskyblue"),
    ("INF-WARNING", "orange"),
    ("LOG", "skyblue1"),
    ("MON", "skyblue1"),
    ("NAV-ATT", "yellow"),
    ("NAV-AOPSTATUS", "yellow"),
    ("NAV-CLOCK", "cyan"),
    ("NAV-COV", "yellow"),
    ("NAV-DGPS", "yellow"),
    ("NAV-DOP", "mediumpurple2"),
    ("NAV-EELL", "yellow"),
    ("NAV-EOE", "yellow"),
    ("NAV-GEOFENCE", "yellow"),
    ("NAV-HPPOSECEF", "orange"),
    ("NAV-HPPOSLLH", "orange"),
    ("NAV-ODO", "deepskyblue"),
    ("NAV-ORB", "yellow"),
    ("NAV-POSECEF", "orange"),
    ("NAV-POSLLH", "orange"),
    ("NAV-PVT", "orange"),
    ("NAV-SAT", "yellow"),
    ("NAV-SBAS", "yellow"),
    ("NAV-SIG", "yellow"),
    ("NAV-SLAS", "yellow"),
    ("NAV-SOL", "green2"),
    ("NAV-STATUS", "green2"),
    ("NAV-SVINFO", "yellow"),
    ("NAV-TIMEBDS", "cyan"),
    ("NAV-TIMEGAL", "cyan"),
    ("NAV-TIMEGLO", "cyan"),
    ("NAV-TIMEGPS", "cyan"),
    ("NAV-TIMELS", "cyan"),
    ("NAV-TIMEQZSS", "cyan"),
    ("NAV-TIMEUTC", "cyan"),
    ("NAV-VELECEF", "deepskyblue"),
    ("NAV-VELNED", "deepskyblue"),
    ("RLM", "pink"),
    ("RMC", "orange"),
    ("RXM", "skyblue1"),
    ("TXT", "lightgrey"),
    ("UBX", "lightblue1"),
    ("UBX00", "aquamarine2"),
    ("UBX03", "yellow"),
    ("UBX04", "cyan"),
    ("UBX05", "orange"),
    ("UBX06", "orange"),
    ("VLW", "deepskyblue"),
    ("VTG", "deepskyblue"),
    ("ZDA", "cyan"),
    ("xb5b", "lightblue1"),
]


def deg2rad(deg: float) -> float:
    """
    Convert degrees to radians

    :param float deg: degrees
    :return radians
    :rtype float
    """

    if not isinstance(deg, (float, int)):
        return 0
    return deg * pi / 180


def cel2cart(elevation: float, azimuth: float) -> (float, float):
    """
    Convert celestial coordinates (degrees) to Cartesian coordinates

    :param float elevation
    :param float azimuth
    :return cartesian x,y coordinates
    :rtype tuple
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
    Convert decimal degrees to degrees minutes seconds string

    :param float degrees
    :return degrees as d.m.s formatted string
    :rtype str
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
    Convert decimal degrees to degrees decimal minutes string

    :param float: degrees
    :param str: latlon: whether degrees refer to lat or lon
    :return degrees as dm.m formatted string
    :rtype str
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
    Convert meters to feet

    :param float meters
    :return feet
    :rtype float
    """

    if not isinstance(meters, (float, int)):
        return 0
    return meters * 3.28084


def ft2m(feet: float) -> float:
    """
    Convert feet to meters


    :param float feet
    :return elevation in meters
    :rtype float
    """

    if not isinstance(feet, (float, int)):
        return 0
    return feet / 3.28084


def ms2kmph(ms: float) -> float:
    """
    Convert meters per second to kilometers per hour

    :param float ms
    :return speed in kmph
    :rtype float
    """

    if not isinstance(ms, (float, int)):
        return 0
    return ms * 3.6


def ms2mph(ms: float) -> float:
    """
    Convert meters per second to miles per hour

    :param float ms
    :return speed in mph
    :rtype float
    """

    if not isinstance(ms, (float, int)):
        return 0
    return ms * 2.23693674


def ms2knots(ms: float) -> float:
    """
    Convert meters per second to knots

    :param float: ms
    :return speed in knots
    :rtype float
    """

    if not isinstance(ms, (float, int)):
        return 0
    return ms * 1.94384395


def kmph2ms(kmph: float) -> float:
    """
    Convert kilometers per hour to meters per second

    :param float: kmph
    :return speed in m/s
    :rtype float
    """

    if not isinstance(kmph, (float, int)):
        return 0
    return kmph * 0.2777778


def knots2ms(knots: float) -> float:
    """
    Convert knots to meters per second

    :param float: knots
    :return speed in m/s
    :rtype float
    """

    if not isinstance(knots, (float, int)):
        return 0
    return knots * 0.5144447324


def pos2iso6709(lat: float, lon: float, alt: float, crs: str = "WGS_84") -> str:
    """
    convert decimal degrees and alt to iso6709 format

    :param float lat
    :param float lon
    :param float alt: altitude
    :param float crs: coordinate reference system
    :return position in iso6709 format
    :rtype str
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

    :param float h: hue
    :param float s: saturation
    :param float v: value
    :return rgb color value
    :rtype str
    """

    if s == 0.0:
        v = int(v * 255)
        return v, v, v
    i = int(h * 6.0)
    f = (h * 6.0) - i
    p = v * (1.0 - s)
    q = v * (1.0 - s * f)
    t = v * (1.0 - s * (1.0 - f))
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

    rgb = int(r * 255), int(g * 255), int(b * 255)
    return "#%02x%02x%02x" % rgb


def snr2col(snr: int) -> str:
    """
    Convert satellite signal-to-noise ratio to a color
    high = green, low = red

    :param int snr: signal to noise ratio as integer
    :return rgb color string
    :rtype str
    """

    return hsv2rgb(snr / (MAX_SNR * 2.5), 0.8, 0.8)


def nmea2latlon(data: types.talker) -> (float, float):
    """
    Convert parsed NMEA sentence to decimal lat, lon

    :param pynmea2.types.talker data: parsed NMEA sentence
    :return (lat, lon)
    :rtype tuple
    """

    if data.lat == "":
        lat = ""
    else:
        latdeg = float(data.lat[0:2])
        latmin = float(data.lat[2:])
        londeg = float(data.lon[0:3])
        lat = (latdeg + latmin / 60) * (-1 if data.lat_dir == "S" else 1)
    if data.lon == "":
        lon = ""
    else:
        lonmin = float(data.lon[3:])
        lon = (londeg + lonmin / 60) * (-1 if data.lon_dir == "W" else 1)
    return (lat, lon)


def svid2gnssid(svid) -> int:
    """
    Derive gnssId from svid numbering range

    :param int svid
    :return gnssId
    :rtype int
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
