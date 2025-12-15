"""
globals.py

PyGPSClient Globals

Collection of global constants

Created on 14 Sep 2020

:author: semuadmin (Steve Smith)
:copyright: 2020 semuadmin
:license: BSD 3-Clause
"""

# pylint: disable=line-too-long

from collections import namedtuple
from datetime import datetime
from os import path
from pathlib import Path
from tkinter import Canvas

from pyubx2 import GET, POLL, SET, SETPOLL

# Type Declarations
Point = namedtuple("Point", ["lat", "lon"])
# Area convention is minlat, minlon, maxlat, maxlon
Area = namedtuple("Area", ["lat1", "lon1", "lat2", "lon2"])
TrackPoint = namedtuple("TrackPoint", ["lat", "lon", "tim", "ele", "spd"])
PointXY = namedtuple("PointXY", ["x", "y"])
AreaXY = namedtuple("AreaXY", ["x1", "y1", "x2", "y2"])


def create_circle(self: Canvas, x: int, y: int, r: int, **kwargs):
    """
    Extends tkinter.Canvas class to simplify drawing compass grids on canvas.

    :param int x: x coordinate
    :param int y: y coordinate
    :param int r: radius
    """

    return self.create_oval(x - r, y - r, x + r, y + r, **kwargs)


Canvas.create_circle = create_circle

# Default colors
AXISCOL = "#E5E5E5"  # default plot axis color
BGCOL = "#3D3D3D"  # default widget background color
ERRCOL = "#FA8072"  # default error message color
FGCOL = "#FFFFFF"  # default widget foreground color
GNSS_LIST = {
    0: ("GPS", "#6495ED"),
    1: ("SBA", "#FF8000"),
    2: ("GAL", "#008B00"),
    3: ("BEI", "#9F79EE"),
    4: ("IME", "#EE82EE"),
    5: ("QZS", "#CDCD00"),
    6: ("GLO", "#CD5C5C"),
    7: ("NAV", "#D2B48C"),
}
GRIDLEGEND = "#B0B0B0"  # default grid legend color
GRIDMAJCOL = "#666666"  # default grid major tick color
GRIDMINCOL = "#4D4D4D"  # default grid minor tick color
INFOCOL = "#5CACEE"  # default info message color
OKCOL = "#008000"  # default OK message color
PLOTCOLS = ("#FFFF00", "#00FFFF", "#FF00FF", "#00BFFF")
PNTCOL = "#FF8000"  # default plot point color

# Protocols to be used in protocol mask (others defined in gnss_reader.py)
SPARTN_PROTOCOL = 32
MQTT_PROTOCOL = 64
TTY_PROTOCOL = 128

# Various global constants - please keep in ascending alphabetical order
HOME = Path.home()
APPNAME = __name__.split(".", 1)[0]  # i.e. "pygpsclient"
ASCII = "ascii"
BPSRATES = (
    9600,
    19200,
    38400,
    57600,
    115200,
    230400,
    460800,
    921600,
    1000000,
    4800,
)
BSR = "backslashreplace"
CLASS = "cls"
COLORTAGS = "colortags"
CONFIGFILE = path.join(HOME, f"{APPNAME}.json")
CONNECTED = 1
CONNECTED_FILE = 4
CONNECTED_NTRIP = 8
CONNECTED_SIMULATOR = 32
CONNECTED_SOCKET = 2
CONNECTED_SPARTNIP = 16
CONNECTED_SPARTNLB = CONNECTED
CONNMODES = {
    0: "not connected",
    1: "serial",
    2: "file",
    3: "no serial devices",
    4: "socket",
}
CRLF = b"\x0d\x0a"
CUSTOM = "custom"
DDD = "DD.D"
DEFAULT_BUFSIZE = 4096
DEFAULT_PASSWORD = "password"  # nosec
DEFAULT_PORT = 50010
DEFAULT_REGION = "eu"
DEFAULT_SERVER = "localhost"
DEFAULT_TLS_PORTS = (443, 2102, 8443, 50443, 58443)
DEFAULT_USER = "anon"
DIRNAME = path.dirname(__file__)
DISCONNECTED = 0
DMM = "DM.M"
DMS = "D.M.S"
ECEF = "ECEF"
ENABLE_CFG_LEGACY = True  # enable CFG=* Other Configuration command panel
ERROR = "ERR!"
FILEREAD_INTERVAL = 0.02  # delay between successive datalog file reads (seconds)
FONT_FIXED = "TkFixedFont"
FONT_MENU = "TkMenuFont"
FONT_TEXT = "TkTextFont"
FORMAT_BINARY = "Binary"
FORMAT_BOTH = "Parsed + Hex Tabular"
FORMAT_HEXSTR = "Hex String"
FORMAT_HEXTAB = "Hex Tabular"
FORMAT_PARSED = "Parsed"
FORMATS = (
    FORMAT_PARSED,
    FORMAT_BINARY,
    FORMAT_HEXSTR,
    FORMAT_HEXTAB,
    FORMAT_BOTH,
)
FRAME = "frm"
GGA_INTERVALS = ("None", "2", "5", "10", "60", "120")
GITHUB_URL = "https://github.com/semuconsulting/PyGPSClient"
GLONASS_NMEA = True  # use GLONASS NMEA SVID (65-96) rather than slot (1-24)
GNSS = "GNSS"
GNSS_EOF_EVENT = "<<gnss_eof>>"
GNSS_ERR_EVENT = "<<gnss_error>>"
GNSS_EVENT = "<<gnss_read>>"
GNSS_TIMEOUT_EVENT = "<<gnss_timeout>>"
GPSEPOCH0 = datetime(1980, 1, 6)  # for Wno and Tow calculations
GPX_NS = (
    'xmlns="http://www.topografix.com/GPX/1/1" '
    'creator="PyGPSClient" version="1.1" '
    'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
    'xsi:schemaLocation="http://www.topografix.com/GPX/1/1 '
    'http://www.topografix.com/GPX/1/1/gpx.xsd"'
)
GPX_TRACK_INTERVAL = 1  # minimum GPS track update interval (seconds)
GUI_UPDATE_INTERVAL = 0.5  # GUI widget update interval (seconds)
ICON_APP128 = path.join(DIRNAME, "resources/app-128.png")
ICON_BLANK = path.join(DIRNAME, "resources/blank-1-24.png")
ICON_CONFIRMED = path.join(DIRNAME, "resources/iconmonstr-check-mark-8-24.png")
ICON_CONN = path.join(DIRNAME, "resources/iconmonstr-media-control-48-24.png")
ICON_CONTRACT = path.join(DIRNAME, "resources/iconmonstr-triangle-1-16.png")
ICON_DELETE = path.join(DIRNAME, "resources/iconmonstr-trash-can-filled-24.png")
ICON_DISCONN = path.join(DIRNAME, "resources/iconmonstr-media-control-50-24.png")
ICON_END = path.join(DIRNAME, "resources/marker_end.png")
ICON_EXIT = path.join(DIRNAME, "resources/iconmonstr-door-6-24.png")
ICON_EXPAND = path.join(DIRNAME, "resources/iconmonstr-arrow-80-16.png")
ICON_GITHUB = path.join(DIRNAME, "resources/github-256.png")
ICON_LOAD = path.join(DIRNAME, "resources/iconmonstr-folder-18-24.png")
ICON_LOGREAD = path.join(DIRNAME, "resources/binary-1-24.png")
ICON_NMEACONFIG = path.join(DIRNAME, "resources/iconmonstr-gear-2-24-nmea.png")
ICON_NOCLIENT = path.join(DIRNAME, "resources/iconmonstr-noclient-10-24.png")
ICON_NOTRANSMIT = path.join(DIRNAME, "resources/iconmonstr-notransmit-10-24.png")
ICON_NTRIPCONFIG = path.join(DIRNAME, "resources/iconmonstr-antenna-4-24.png")
ICON_PENDING = path.join(DIRNAME, "resources/iconmonstr-time-6-24.png")
ICON_PLAY = path.join(DIRNAME, "resources/iconmonstr-media-control-48-24.png")
ICON_POS = path.join(DIRNAME, "resources/iconmonstr-plus-lined-24.png")
ICON_RECORD = path.join(DIRNAME, "resources/iconmonstr-record-24.png")
ICON_REDRAW = path.join(DIRNAME, "resources/iconmonstr-refresh-lined-24.png")
ICON_REFRESH = path.join(DIRNAME, "resources/iconmonstr-refresh-6-16.png")
ICON_SAVE = path.join(DIRNAME, "resources/iconmonstr-save-14-24.png")
ICON_SEND = path.join(DIRNAME, "resources/iconmonstr-arrow-12-24.png")
ICON_SERIAL = path.join(DIRNAME, "resources/usbport-1-24.png")
ICON_SOCKET = path.join(DIRNAME, "resources/ethernet-1-24.png")
ICON_SPARTNCONFIG = path.join(DIRNAME, "resources/iconmonstr-antenna-3-24.png")
ICON_SPONSOR = path.join(DIRNAME, "resources/bmac-logo-60.png")
ICON_START = path.join(DIRNAME, "resources/marker_start.png")
ICON_STOP = path.join(DIRNAME, "resources/iconmonstr-stop-1-24.png")
ICON_TRANSMIT = path.join(DIRNAME, "resources/iconmonstr-transmit-10-24.png")
ICON_TTYCONFIG = path.join(DIRNAME, "resources/iconmonstr-gear-2-24-tty.png")
ICON_UBXCONFIG = path.join(DIRNAME, "resources/iconmonstr-gear-2-24-ubx.png")
ICON_UNDO = path.join(DIRNAME, "resources/iconmonstr-undo-24.png")
ICON_UNKNOWN = path.join(DIRNAME, "resources/clear-1-24.png")
ICON_WARNING = path.join(DIRNAME, "resources/iconmonstr-warning-1-24.png")
IMG_WORLD = path.join(DIRNAME, "resources/world.png")
IMG_WORLD_BOUNDS = Area(-90, -180, 90, 180)
IMPORT = "import"
LBAND = "LBAND"
LC29H = "Quectel LC29H"
LG290P = "Quectel LG29P/LG580P"
LICENSE_URL = "https://github.com/semuconsulting/PyGPSClient/blob/master/LICENSE"
MAPAPI_URL = "https://developer.mapquest.com/user/login/sign-up"
MAX_SNR = 60  # upper limit of levelsview CNo axis
MAXFLOAT = 2e20
MAXLOGSIZE = 10485760  # maximum size of individual log file in bytes
MIN_GUI_UPDATE_INTERVAL = 0.1  # minimum GUI widget update interval (seconds)
MINFLOAT = -MAXFLOAT
MINHEIGHT = 600
MINWIDTH = 800
MOSAIC_X5 = "Septentrio Mosaic X3/X5"
MQAPIKEY = "mqapikey"
MQTTIPMODE = 0
MQTTLBANDMODE = 1
MSGMODES = {"GET": GET, "SET": SET, "POLL": POLL, "SETPOLL": SETPOLL}
NOPORTS = 3
NTRIP = "NTRIP"
NTRIP_EVENT = "<<ntrip_read>>"
PASSTHRU = "Passthrough"
PORTIDS = ("0 I2C", "1 UART1", "2 UART2", "3 USB", "4 SPI")
PUBLICIP_URL = "https://ipinfo.io/json"
PYPI_URL = "https://pypi.org/pypi/PyGPSClient"
QUITONERRORDEFAULT = 1
RCVR_CONNECTION = "USB,UART1"  # default GNSS receiver connection port(s)
READONLY = "readonly"
RESIZE = "resize"
ROMVER_NEW = "23.01"  # min device ROM version using configuration database
ROUTE = "route"
RXMMSG = "RXM-SPARTN-KEY"
SAT_EXPIRY = 10  # how long passed satellites are kept in the sky and graph view
SCREENSCALE = 0.8  # screen resolution scaling factor
SOCK_NTRIP = "NTRIP CASTER"
SOCK_SERVER = "SOCKET SERVER"
SOCKCLIENT_HOST = "localhost"
SOCKCLIENT_PORT = 50010
SOCKMODES = (SOCK_SERVER, SOCK_NTRIP)
SOCKSERVER_HOST = "0.0.0.0"  # i.e. bind to all host IP addresses
SOCKSERVER_MAX_CLIENTS = 5
SOCKSERVER_NTRIP_PORT = 2101
SOCKSERVER_PORT = 50012
SPARTN_BASEDATE_CURRENT = -1
SPARTN_BASEDATE_DATASTREAM = 0
SPARTN_DEFAULT_KEY = "abcd1234abcd1234abcd1234abcd1234"
SPARTN_EOF_EVENT = "<<spartn_eof>>"
SPARTN_ERR_EVENT = "<<spartn_error>>"
SPARTN_EVENT = "<<spartn_read>>"
SPARTN_KEYLEN = 16
SPARTN_OUTPORT = 8883
SPARTN_PPREGIONS = ("eu", "us", "jp", "kr", "au")
SPARTN_PPSERVER_URL = "pp.services.u-blox.com"
SPARTN_SOURCE_IP = 0
SPARTN_SOURCE_LB = 1
SPONSOR_URL = "https://buymeacoffee.com/semuconsulting"
SQRT2 = 0.7071067811865476  # square root of 2
STATUSPRIORITY = {INFOCOL: 0, "blue": 0, OKCOL: 2, "green": 1, ERRCOL: 3, "red": 3}
TIME0 = datetime(1970, 1, 1)  # basedate for time()
TIMEOUTS = ("0.1", "0.2", "1", "2", "5", "10", "20", "None", "0")
# map nmea talker to gnss_id
TKGN = {"GN": 0, "GP": 0, "GA": 2, "GB": 3, "BD": 3, "GQ": 5, "GL": 6, "GI": 7}
TOPIC_IP = "/pp/ip/{}"
TOPIC_MGA = "/pp/ubx/mga"
TOPIC_RXM = "/pp/ubx/0236/ip"
TRACK = "track"
TRACEMODE_WRITE = "write"
TTYOK = ("OK", "$R:")
TTYERR = ("ERROR", "$R?")
TTYMARKER = "TTY<<"
UBXPRESETS = "ubxpresets"
UBXSIMULATOR = "ubxsimulator"
UNDO = "UNDO"
UTF8 = "utf-8"
VALBLANK = 1
VALNONBLANK = 2
VALNONSPACE = 3
VALINT = 4
VALFLOAT = 5
VALURL = 6
VALHEX = 7
VALDMY = 8
VALLEN = 9
VALBOOL = 10
WAYPOINT = "waypoint"
WIDGETU1 = (200, 200)  # small widget size
WIDGETU2 = (300, 200)  # medium widget size
WIDGETU3 = (800, 200)  # Console size
WIDGETU4 = (500, 500)  # GPX Track viewer size
WIDGETU6 = (400, 200)  # Chart size
WORLD = "world"
XML_HDR = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
ZED_F9 = "u-blox ZED-F9"
ZED_X20 = "u-blox ZED-X20"

# Conversion factors
UI = "Imperial mph"
UIK = "Imperial knots"
UMK = "Metric kmph"
UMM = "Metric m/s"
KM2M = 1000
KM2MIL = 0.621371
KM2NMIL = 0.5399568
KPH2KNT = 0.5399568
KPH2MPH = 0.6213712
KPH2MPS = 0.2777778
M2FT = 3.28084
M2MIL = 0.0006213712
M2NMIL = 0.0005399568
M2KM = 0.001
MPS2MPH = 2.236936
MPS2KPH = 3.6
MPS2KNT = 1.943844

# UBX & NMEA config widget signifiers - used
# to identify which widget should receive the
# data from a given POLL or ACK message:
UBX_MONVER = 0
UBX_MONHW = 1
UBX_CFGPRT = 2
UBX_CFGMSG = 3
UBX_CFGVAL = 4
UBX_PRESET = 5
UBX_CFGRATE = 6
UBX_CFGOTHER = 7
SPARTN_GNSS = 8
SPARTN_LBAND = 9
SPARTN_MQTT = 10
SPECTRUMVIEW = 11
SYSMONVIEW = 12
ROVERVIEW = 13
UBX_MONRF = 14
NMEA_MONHW = 15
NMEA_PRESET = 16
NMEA_CFGOTHER = 17
SERVERCONFIG = 18
SBF_MONHW = 19

KNOWNGPS = (
    "cp210",
    "ft230",
    "ft232",
    "garmin",
    "gnss",
    "gps",
    "iousbhostdevice",
    "magellan",
    "navstar",
    "septentrio",
    "sirf",
    "trimble",
    "u-blox",
    "ublox",
    "usb serial",
    "usb to uart",
    "usb uart",
    "usb dual_serial",
    "usb_to_uart",
    "user-defined",
)
"""
Recognised GNSS device serial port designators.
Used to 'auto-select' GNSS device in serial port list.
(keep in lower-case)
"""

FIXLOOKUP = {
    "GGA1": "3D",  # quality
    "GGA2": "3D",
    "GGA4": "RTK FIXED",
    "GGA5": "RTK FLOAT",
    "GGA6": "DR",
    "GLLA": "3D",  # posMode
    "GLLD": "RTK",
    "GLLE": "DR",
    "GNSA": "3D",  # posMode
    "GNSD": "3D",
    "GNSF": "RTK FLOAT",
    "GNSR": "RTK FIXED",
    "GNSE": "DR",
    "RMCA": "3D",  # posMode
    "RMCD": "3D",
    "RMCF": "RTK FLOAT",
    "RMCR": "RTK FIXED",
    "RMCE": "DR",
    "VTGA": "3D",  # posMode
    "VTGD": "RTK",
    "VTGE": "DR",
    "NAV-PVT1": "DR",  # fixType
    "NAV-PVT2": "2D",
    "NAV-PVT3": "3D",
    "NAV-PVT4": "GNSS+DR",
    "NAV-PVT5": "TIME ONLY",
    "NAV-PVT6": "RTK FLOAT",  # carrSoln
    "NAV-PVT7": "RTK FIXED",
    "NAV-STATUS1": "DR",  # gpsFix
    "NAV-STATUS2": "3D",
    "NAV-STATUS3": "3D",
    "NAV-STATUS4": "GNSS+DR",
    "NAV-STATUS5": "TIME ONLY",
    "NAV-STATUS6": "RTK FLOAT",  # carrSoln
    "NAV-STATUS7": "RTK FIXED",
    "NAV-SOL1": "DR",  # gpsFix
    "NAV-SOL2": "3D",
    "NAV-SOL3": "3D",
    "NAV-SOL4": "GNSS+DR",
    "NAV-SOL5": "TIME ONLY",
    "HNR-PVT1": "DR",  # gpsFix
    "HNR-PVT2": "2D",
    "HNR-PVT3": "3D",
    "HNR-PVT4": "GNSS+DR",
    "HNR-PVT5": "TIME ONLY",
    "HNR-PVT6": "RTK",
    "NAV2-PVT1": "DR",  # fixType
    "NAV2-PVT2": "2D",
    "NAV2-PVT3": "3D",
    "NAV2-PVT4": "GNSS+DR",
    "NAV2-PVT5": "TIME ONLY",
    "NAV2-PVT6": "RTK FLOAT",  # carrSoln
    "NAV2-PVT7": "RTK FIXED",
    "NAV2-STATUS1": "DR",  # gpsFix
    "NAV2-STATUS2": "3D",
    "NAV2-STATUS3": "3D",
    "NAV2-STATUS4": "GNSS+DR",
    "NAV2-STATUS5": "TIME ONLY",
    "NAV2-STATUS6": "RTK FLOAT",  # carrSoln
    "NAV2-STATUS7": "RTK FIXED",
    "PVTGeodetic0": "NO FIX",
    "PVTGeodetic1": "3D",
    "PVTGeodetic2": "RTK",
    "PVTGeodetic3": "3D",
    "PVTGeodetic4": "RTK FIXED",
    "PVTGeodetic5": "RTK FLOAT",
    "PVTGeodetic6": "SBAS",
    "PVTGeodetic7": "RTK FIXED",
    "PVTGeodetic8": "RTK FLOAT",
    "PVTGeodetic10": "PPP",
}
"""
Map of fix values to descriptions.
The keys in this map are a concatenation of NMEA/UBX
message identifier and attribute value e.g.
GGA1: GGA + quality = 1
NAV-STATUS3: NAV-STATUS + gpsFix = 3
(valid for NMEA >=4)
"""
