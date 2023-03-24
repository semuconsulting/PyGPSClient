"""
PyGPSClient Globals

Collection of global constants

Created on 14 Sep 2020

:author: semuadmin
:copyright: SEMU Consulting © 2020
:license: BSD 3-Clause

"""
# pylint: disable=invalid-name, line-too-long

import os
from datetime import datetime
from pyubx2 import GET, SET, POLL

DIRNAME = os.path.dirname(__file__)
ICON_BLANK = os.path.join(DIRNAME, "resources/blank-1-24.png")
ICON_APP = os.path.join(DIRNAME, "resources/iconmonstr-location-27-32.png")
ICON_CONN = os.path.join(DIRNAME, "resources/iconmonstr-media-control-48-24.png")
ICON_SERIAL = os.path.join(DIRNAME, "resources/usbport-1-24.png")
ICON_SOCKET = os.path.join(DIRNAME, "resources/ethernet-1-24.png")
ICON_DISCONN = os.path.join(DIRNAME, "resources/iconmonstr-media-control-50-24.png")
ICON_POS = os.path.join(DIRNAME, "resources/iconmonstr-location-1-24.png")
ICON_SEND = os.path.join(DIRNAME, "resources/iconmonstr-arrow-12-24.png")
ICON_EXIT = os.path.join(DIRNAME, "resources/iconmonstr-door-6-24.png")
ICON_PENDING = os.path.join(DIRNAME, "resources/iconmonstr-time-6-24.png")
ICON_CONFIRMED = os.path.join(DIRNAME, "resources/iconmonstr-check-mark-8-24.png")
ICON_WARNING = os.path.join(DIRNAME, "resources/iconmonstr-warning-1-24.png")
ICON_UNKNOWN = os.path.join(DIRNAME, "resources/clear-1-24.png")
ICON_UBXCONFIG = os.path.join(DIRNAME, "resources/iconmonstr-gear-2-24.png")
ICON_NTRIPCONFIG = os.path.join(DIRNAME, "resources/iconmonstr-antenna-4-24.png")
ICON_SPARTNCONFIG = os.path.join(DIRNAME, "resources/iconmonstr-antenna-3-24.png")
ICON_LOGREAD = os.path.join(DIRNAME, "resources/binary-1-24.png")
ICON_REFRESH = os.path.join(DIRNAME, "resources/iconmonstr-refresh-6-16.png")
ICON_CONTRACT = os.path.join(DIRNAME, "resources/iconmonstr-triangle-1-16.png")
ICON_EXPAND = os.path.join(DIRNAME, "resources/iconmonstr-arrow-80-16.png")
ICON_TRANSMIT = os.path.join(DIRNAME, "resources/iconmonstr-transmit-10-24.png")
ICON_NOTRANSMIT = os.path.join(DIRNAME, "resources/iconmonstr-notransmit-10-24.png")
ICON_NOCLIENT = os.path.join(DIRNAME, "resources/iconmonstr-noclient-10-24.png")
ICON_LOAD = os.path.join(DIRNAME, "resources/iconmonstr-folder-18-24.png")
ICON_SAVE = os.path.join(DIRNAME, "resources/iconmonstr-save-14-24.png")
ICON_PLAY = os.path.join(DIRNAME, "resources/iconmonstr-media-control-48-24.png")
ICON_RECORD = os.path.join(DIRNAME, "resources/iconmonstr-record-24.png")
ICON_STOP = os.path.join(DIRNAME, "resources/iconmonstr-stop-1-24.png")
ICON_UNDO = os.path.join(DIRNAME, "resources/iconmonstr-undo-24.png")
ICON_DELETE = os.path.join(DIRNAME, "resources/iconmonstr-trash-can-filled-24.png")
ICON_REDRAW = os.path.join(DIRNAME, "resources/iconmonstr-refresh-lined-24.png")
IMG_WORLD = os.path.join(DIRNAME, "resources/world.png")
PYPI_URL = "https://pypi.org/pypi/PyGPSClient"
GITHUB_URL = "https://github.com/semuconsulting/PyGPSClient"
MAPQURL = "https://www.mapquestapi.com/staticmap/v5/map?key={}"
MAPQTIMEOUT = 5
MAPURL = (
    MAPQURL
    + "&locations={},{}&zoom={}&size={},{}&defaultMarker=marker-sm-616161-ff4444"
    + "&shape=radius:{}|weight:1|fill:ccffff50|border:88888850|{},{}&scalebar={}"
)
GPXMAPURL = (
    MAPQURL
    + "&locations={},{}||{},{}&zoom={}&size={},{}&defaultMarker=marker-num"
    + "&shape=weight:2|border:{}|{}&scalebar={}|bottom"
)
MAP_UPDATE_INTERVAL = (
    60  # how frequently the mapquest api is called to update the web map (seconds)
)
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
EPILOG = "© 2022 SEMU Consulting BSD 3-Clause license - https://github.com/semuconsulting/pygpsclient/"
GPSEPOCH0 = datetime(1980, 1, 6)  # for Wno and Tow calculations
GPXLIMIT = 500  # max number of track points supported by MapQuest API
CHECK_FOR_UPDATES = (
    False  # check for newer PyPi version on startup (requires internet connection)
)
GUI_UPDATE_INTERVAL = 0.5  # minimum GUI widget update interval (seconds)
GPX_TRACK_INTERVAL = 1  # minimum GPS track update interval (seconds)
FILEREAD_INTERVAL = 0.02  # delay between successive datalog file reads (seconds)
SAT_EXPIRY = 10  # how long passed satellites are kept in the sky and graph views
MAX_SNR = 60  # upper limit of graphview snr axis
MAXLOGLINES = 10000  # maximum number of 'lines' per datalog file
# default error handling behaviour for UBXReader.read() calls
# 0 (ERR_IGNORE) = ignore errors, 1 (ERR_LOG) - log errors, 2 (ERR_RAISE) = raise errors
QUITONERRORDEFAULT = 1
POPUP_TRANSIENT = True  # whether pop-up config dialogs are always on top
PORTIDS = ("0 I2C", "1 UART1", "2 UART2", "3 USB", "4 SPI")
TIMEOUTS = (
    "0.1",
    "0.2",
    "1",
    "2",
    "5",
    "10",
    "20",
    "None",
    "0",
)
ANTSTATUS = ("INIT", "DONTKNOW", "OK", "SHORT", "OPEN")
ANTPOWER = ("OFF", "ON", "DONTKNOW")
GGA_INTERVALS = ("None", "2", "5", "10", "60", "120")
ENABLE_CFG_OTHER = True  # enable CFG=* Other Configuration command panel
# names of user preset files:
MQAPIKEY = "mqapikey"
UBXPRESETS = "ubxpresets"
COLORTAGS = "colortags"
# list of recognised serial device descriptors:
KNOWNGPS = (
    "USER-DEFINED",
    "GPS",
    "gps",
    "GNSS",
    "gnss",
    "Garmin",
    "garmin",
    "U-Blox",
    "u-blox",
    "ublox",
    "SiRF",
    "Sirf",
    "sirf",
    "Magellan",
    "magellan",
    "CP210",
    "FT232",
    "USB UART",
    "USB to UART",
    "USB_to_UART",
)
# list of available bps rates (first entry in list is the default):
BPSRATES = (9600, 19200, 38400, 57600, 115200, 230400, 460800, 921600, 1000000, 4800)
# terminator for NMEA protocol
CRLF = b"\x0d\x0a"
# socket client defaults
DEFAULT_SERVER = "localhost"
DEFAULT_PORT = 50010
DEFAULT_BUFSIZE = 4096
# socket server defaults
SOCKSERVER_HOST = "0.0.0.0"  # i.e. bind to all host IP addresses
SOCKSERVER_PORT = 50010
SOCKSERVER_NTRIP_PORT = 2101
SOCKSERVER_MAX_CLIENTS = 5
# display formats
FORMAT_PARSED = 1
FORMAT_BIN = 2
FORMAT_HEX = 4
FORMAT_HEXTABLE = 8
FORMATS = ("Parsed", "Binary", "Hex String", "Hex Tabular", "Parsed + Hex Tabular")
# socket server modes
SOCKMODES = ("SOCKET SERVER", "NTRIP CASTER")
# connection mode flags:
DISCONNECTED = 0
CONNECTED = 1
CONNECTED_SOCKET = 2
CONNECTED_FILE = 4
NOPORTS = 3
CONNMODES = {
    0: "not connected",
    1: "serial",
    2: "file",
    3: "no serial devices",
    4: "socket",
}
MSGMODES = {
    "GET": GET,
    "SET": SET,
    "POLL": POLL,
}
# read event types
GNSS_EVENT = "<<gnss_read>>"
GNSS_EOF_EVENT = "<<gnss_eof>>"
NTRIP_EVENT = "<<ntrip_read>>"
SPARTN_EVENT = "<<spartn_read>>"
SPARTN_EOF_EVENT = "<<spartn_eof>>"
# default widget frame sizes:
WIDGETU1 = (250, 250)  # small widget size
WIDGETU2 = (350, 250)  # medium widget size
WIDGETU3 = (950, 350)  # Console size
WIDGETU4 = (600, 600)  # GPX Track viewer size
MAXCOLSPAN = 4  # max colspan of widgets
MAXROWSPAN = 3  # max no of widget rows

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
KPH2MPH = 0.621371
KPH2KNT = 0.5399568
KPH2MPS = 0.2777776918389111005
M2FT = 3.28084
KM2M = 1000
KM2MIL = 0.621371
KM2NMIL = 0.5399568

# UBX config widget signifiers - used to
# identify which widget should receive the
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

# SPARTN globals
SPARTN_SOURCE_LB = 1
SPARTN_SOURCE_IP = 0
SPARTN_PPSERVER = "pp.services.u-blox.com"
OUTPORT_SPARTN = 8883
SPARTN_PPREGIONS = ("eu", "us", "kr", "au")
SPARTN_KEYLEN = 16
RXMMSG = "RXM-SPARTN-KEY"
CONNECTED_NTRIP = 8
CONNECTED_SPARTNIP = 16
CONNECTED_SPARTNLB = CONNECTED
TOPIC_RXM = "/pp/ubx/0236/ip"
TOPIC_MGA = "/pp/ubx/mga"
TOPIC_IP = "/pp/ip/{}"

GLONASS_NMEA = True  # use GLONASS NMEA SVID (65-96) rather than slot (1-24)
# GNSS color codings:
GNSS_LIST = {
    0: ("GPS", "royalblue"),
    1: ("SBA", "orange"),
    2: ("GAL", "green4"),
    3: ("BEI", "purple"),
    4: ("IME", "violet"),
    5: ("QZS", "yellow"),
    6: ("GLO", "indianred"),
}

# map of fix values to descriptions
# (for NMEA 4 and above)
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
    "NAV-PVT1": "DR",  # fixType or carrSoln
    "NAV-PVT2": "2D",
    "NAV-PVT3": "3D",
    "NAV-PVT4": "GNSS+DR",
    "NAV-PVT5": "TIME ONLY",
    "NAV-PVT6": "RTK FLOAT",
    "NAV-PVT7": "RTK FIXED",
    "NAV-STATUS1": "DR",  # gpsFix or carrSoln
    "NAV-STATUS2": "3D",
    "NAV-STATUS3": "3D",
    "NAV-STATUS4": "GNSS+DR",
    "NAV-STATUS5": "TIME ONLY",
    "NAV-STATUS6": "RTK FLOAT",
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
    "NAV2-PVT1": "DR",  # fixType or carrSoln
    "NAV2-PVT2": "2D",
    "NAV2-PVT3": "3D",
    "NAV2-PVT4": "GNSS+DR",
    "NAV2-PVT5": "TIME ONLY",
    "NAV2-PVT6": "RTK FLOAT",
    "NAV2-PVT7": "RTK FIXED",
    "NAV2-STATUS1": "DR",  # gpsFix or carrSoln
    "NAV2-STATUS2": "3D",
    "NAV2-STATUS3": "3D",
    "NAV2-STATUS4": "GNSS+DR",
    "NAV2-STATUS5": "TIME ONLY",
    "NAV2-STATUS6": "RTK FLOAT",
    "NAV2-STATUS7": "RTK FIXED",
}

FONT_MENU = "TkMenuFont"
FONT_TEXT = "TkTextFont"
FONT_FIXED = "TkFixedFont"
TAG_COLORS = False  # default colortag setting

# TAGS are now in 'colortags' file in user's home directory
