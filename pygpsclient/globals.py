'''

Collection of global constants and helper methods

Created on 14 Sep 2020

@author: semuadmin
'''

import os
from math import sin, cos, pi
from serial import PARITY_NONE, PARITY_EVEN, PARITY_ODD, PARITY_MARK, PARITY_SPACE

VERSION = "0.1.5"

DIRNAME = os.path.dirname(__file__)
ICON_APP = os.path.join(DIRNAME, 'resources/iconmonstr-location-27-32.png')
ICON_CONN = os.path.join(DIRNAME, 'resources/iconmonstr-link-8-24.png')
ICON_DISCONN = os.path.join(DIRNAME, 'resources/iconmonstr-link-10-24.png')
ICON_GO = os.path.join(DIRNAME, 'resources/iconmonstr-media-control-4-32.png')
ICON_STOP = os.path.join(DIRNAME, 'resources/iconmonstr-media-control-12-32.png')
ICON_POS = os.path.join(DIRNAME, 'resources/iconmonstr-location-1-24.png')
ICON_SEND = os.path.join(DIRNAME, 'resources/iconmonstr-arrow-12-24.png')
ICON_EXIT = os.path.join(DIRNAME, 'resources/iconmonstr-door-6-24.png')
IMG_WORLD = os.path.join(DIRNAME, 'resources/world.png')
BTN_CONNECT = "\u25b6"  # text on "Connected" button
BTN_DISCONNECT = "\u2587"  # text on "Disconnected" button

MAPURL = "https://www.mapquestapi.com/staticmap/v5/map?key={}&locations={},{}&zoom={}&defaultMarker=marker-sm-616161-ff4444&shape=radius:{}|weight:1|fill:ccffff50|border:88888850|{},{}&size={},{}"
MAP_UPDATE_INTERVAL = 60
DEVICE_ACCURACY = 2.5  # nominal GPS device accuracy (CEP) in meters
HDOP_RATIO = 20  # arbitrary calibration of accuracy against HDOP
KNOWNGPS = ('GPS', 'gps', 'GNSS', 'gnss', 'Garmin', 'garmin', 'U-Blox', 'u-blox')
BAUDRATES = (115200, 57600, 38400, 19200, 9600, 4800)
PARITIES = {"Even":PARITY_EVEN, "Odd": PARITY_ODD, "Mark": PARITY_MARK, "Space": PARITY_SPACE, "None": PARITY_NONE}
SERIAL_TIMEOUT = .5

NMEA_PROTOCOL = 0
UBX_PROTOCOL = 1
MIXED_PROTOCOL = 2

DISCONNECTED = 0
CONNECTED = 1
NOPORTS = 2
WIDGETU1 = (250, 250)
WIDGETU2 = (350, 250)
WIDGETU3 = (950, 350)
BGCOL = "gray24"  # default widget background color
FGCOL = "white"  # default widget foreground color
ENTCOL = "azure"  # default data entry field background color
READONLY = "readonly"
ADVOFF = "\u25bc"
ADVON = "\u25b2"
ERROR = "ERR!"
DDD = "DD.D"
DMM = "DM.M"
DMS = "D.M.S"
UMM = "Metric m/s"
UMK = "Metric kmph"
UI = "Imperial mph"
UIK = "Imperial knots"

# List of tags to highlight in console
TAGS = [("DTM", "deepskyblue"), ("GBS", "pink"), \
        ("GGA", "orange"), ("GSV", "yellow"), ("GLL", "orange"), ("TXT", "lightgrey"), \
        ("GSA", "green2"), ("RMC", "orange"), ("VTG", "deepskyblue"), ("lat", "lightblue1"), \
        ("lon", "lightblue1"), ("lat_dir", "lightblue1"), ("lon_dir", "lightblue1"), \
        ("altitude", "lightblue1"), ("pdop", "lightblue1"), ("UBX", "lightblue1"), \
        ("UBX00", "aquamarine2"), ("UBX03", "yellow"), ("UBX04", "cyan"), ("UBX05", "orange"), \
        ("UBX06", "orange"), \
        ("vdop", "lightblue1"), ("hdop", "lightblue1"), ("h_acc", "lightblue1"), \
        ("v_acc", "lightblue1"), ("spd_over_grnd_kmph", "lightblue1"), \
        ("true_track", "lightblue1"), ("mode_fix_type", "lightblue1"), \
        ("datum", "lightblue1"), ("ACK-ACK", "green2"), ("ACK-NAK", "orange red"), \
        ("CFG-MSG", "cyan"), ("xb5b", "lightblue1"), ("NAV-SOL", "green2"), ("NAV-POSLLH", "orange"), \
        ("NAV-VELECEF", "deepskyblue"), ("NAV-VELNED", "deepskyblue"), ("NAV-SVINFO", "yellow"),
        ("NAV-TIMEUTC", "cyan"), ("NAV-STATUS", "green2"), ("NAV-PVT", "orange"),
        ("NAV-DOP", "mediumpurple2"), ("NAV-CLOCK", "cyan"), ("NAV-SBAS", "yellow")]


def deg2rad(deg: float) -> float:
    '''
    Convert degrees to radians
    '''

    return deg * pi / 180


def cel2cart(elevation: float, azimuth: float) -> (float, float):
    '''
    Convert celestial coordinates (degrees) to Cartesian coordinates
    '''

    elevation = deg2rad(elevation)
    azimuth = deg2rad(azimuth)
    x = cos(azimuth) * cos(elevation)
    y = sin(azimuth) * cos(elevation)
    return (x, y)


def deg2dms(degrees: float, latlon: float) -> (float, float):
    '''
    Convert decimal degrees to degrees minutes seconds string
    '''

    negative = degrees < 0
    degrees = abs(degrees)
    minutes, seconds = divmod(degrees * 3600, 60)
    degrees, minutes = divmod(minutes, 60)
    if negative:
        sfx = 'S' if latlon == "lat" else 'W'
    else:
        sfx = 'N' if latlon == "lat" else 'E'
    return str(int(degrees)) + '\u00b0' + str(int(minutes)) + '\u2032' \
            +str(round(seconds, 3)) + '\u2033' + sfx


def deg2dmm(degrees: float, latlon: float) -> (float, float):
    '''
    Convert decimal degrees to degrees decimal minutes string
    '''

    negative = degrees < 0
    degrees = abs(degrees)
    degrees, minutes = divmod(degrees * 60, 60)
    if negative:
        sfx = 'S' if latlon == "lat" else 'W'
    else:
        sfx = 'N' if latlon == "lat" else 'E'
    return str(int(degrees)) + '\u00b0' + str(round(minutes, 5)) + '\u2032' + sfx


def m2ft(meters: float) -> float:
    '''
    Convert meters to feet
    '''

    return meters * 3.28084


def ft2m(feet: float) -> float:
    '''
    Convert feet to meters
    '''

    return feet / 3.28084


def kmph2mph(kmph: float) -> float:
    '''
    Convert kilometers per hour to miles per hour
    '''

    return kmph * 0.6213712419


def mph2kmph(mph: float) -> float:
    '''
    Convert miles per hour to kilometers per hour
    '''

    return mph / 0.6213712419


def kmph2ms(kmph: float) -> float:
    '''
    Convert kilometers per hour to meters per second
    '''

    return kmph * 0.2777778


def kmph2knots(kmph: float) -> float:
    '''
    Convert kilometers per hour to knots
    '''

    return kmph / 1.852001


def ms2kmph(ms: float) -> float:
    '''
    Convert meters per second to kilometers per hour
    '''

    return ms / 0.2777778


def pos2iso6709(lat :float, lon: float, alt: float, crs: str="WGS_84") -> str:
    '''
    convert decimal degrees and alt to iso6709 format
    '''

    lati = '-' if lat < 0 else '+'
    loni = '-' if lon < 0 else '+'
    alti = '-' if alt < 0 else '+'
    iso6709 = lati + str(abs(lat)) + loni + str(abs(lon)) + alti + str(alt) + "CRS" + crs + "/"
    return iso6709


def hsv2rgb(h: float, s: float, v: float) -> str:
    '''
    Convert HSV values (in range 0-1) to RGB color string.
    '''

    if s == 0.0:
        v = int(v * 255)
        return v, v, v
    i = int(h * 6.)
    f = (h * 6.) - i
    p = v * (1. - s)
    q = v * (1. - s * f)
    t = v * (1. - s * (1. - f))
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
