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

DIRNAME = os.path.dirname(__file__)
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
ICON_NTRIPCONFIG = os.path.join(DIRNAME, "resources/iconmonstr-antenna-6-24.png")
ICON_LOGREAD = os.path.join(DIRNAME, "resources/binary-1-24.png")
ICON_REFRESH = os.path.join(DIRNAME, "resources/iconmonstr-refresh-6-16.png")
ICON_CONTRACT = os.path.join(DIRNAME, "resources/iconmonstr-triangle-1-16.png")
ICON_EXPAND = os.path.join(DIRNAME, "resources/iconmonstr-arrow-80-16.png")
ICON_TRANSMIT = os.path.join(DIRNAME, "resources/iconmonstr-transmit-10-24.png")
ICON_NOTRANSMIT = os.path.join(DIRNAME, "resources/iconmonstr-notransmit-10-24.png")
ICON_NOCLIENT = os.path.join(DIRNAME, "resources/iconmonstr-noclient-10-24.png")
IMG_WORLD = os.path.join(DIRNAME, "resources/world.png")

GITHUB_URL = "https://github.com/semuconsulting/PyGPSClient"
PYPI_URL = "https://pypi.org/pypi/PyGPSClient"
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
    60  # how frequently the mapquest api is called to update the web map (seconds)
)
GUI_UPDATE_INTERVAL = 1  # minimum GUI widget update interval (seconds)
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
BPSRATES = (9600, 19200, 38400, 57600, 115200, 230400, 460800, 921600, 4800)
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
# default widget frame sizes:
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
    "NAV-PVT1": "DR",  # fixType
    "NAV-PVT2": "2D",
    "NAV-PVT3": "3D",
    "NAV-PVT4": "GNSS+DR",
    "NAV-PVT5": "TIME ONLY",
    "NAV-STATUS1": "DR",  # gpsFix
    "NAV-STATUS2": "3D",
    "NAV-STATUS3": "3D",
    "NAV-STATUS4": "GNSS+DR",
    "NAV-STATUS5": "TIME ONLY",
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
    "NAV2-PVT1": "DR",  # fixType
    "NAV2-PVT2": "2D",
    "NAV2-PVT3": "3D",
    "NAV2-PVT4": "GNSS+DR",
    "NAV2-PVT5": "TIME ONLY",
    "NAV2-STATUS1": "DR",  # gpsFix
    "NAV2-STATUS2": "3D",
    "NAV2-STATUS3": "3D",
    "NAV2-STATUS4": "GNSS+DR",
    "NAV2-STATUS5": "TIME ONLY",
}

FONT_MENU = "TkMenuFont"
FONT_TEXT = "TkTextFont"
FONT_FIXED = "TkFixedFont"
TAG_COLORS = False  # default colortag setting

# TAGS are now in 'colortags' file in user's home directory
