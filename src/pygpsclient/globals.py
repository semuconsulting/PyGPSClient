"""
globals.py

PyGPSClient Globals

Collection of global constants

Created on 14 Sep 2020

:author: semuadmin
:copyright: SEMU Consulting © 2020
:license: BSD 3-Clause

"""
# pylint: disable=line-too-long

from collections import namedtuple
from datetime import datetime
from os import path
from pathlib import Path

from pyubx2 import GET, POLL, SET

Point = namedtuple("Point", ["lat", "lon"])
HOME = Path.home()

BADCOL = "red"
BGCOL = "gray24"  # default widget background color
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
CFG = "cfg"
CHECK_FOR_UPDATES = False
CLASS = "cls"
COLORTAGS = "colortags"
CONFIGNAME = "pygpsclient"
CONFIGFILE = path.join(HOME, f"{CONFIGNAME}.json")
CONNECTED = 1
CONNECTED_FILE = 4
CONNECTED_NTRIP = 8
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
DDD = "DD.D"
DEFAULT_BUFSIZE = 4096
DEFAULT_PORT = 50010
DEFAULT_SERVER = "localhost"
DIRNAME = path.dirname(__file__)
DISCONNECTED = 0
DLG = "dlg"
DLGTABOUT = "About"
DLGTGPX = "GPX Track Viewer"
DLGTNTRIP = "NTRIP Configuration"
DLGTSPARTN = "SPARTN Configuration"
DLGTUBX = "UBX Configuration"
DMM = "DM.M"
DMS = "D.M.S"
ECEF = "ECEF"
ENABLE_CFG_OTHER = True  # enable CFG=* Other Configuration command panel
EPILOG = "© 2022 SEMU Consulting BSD 3-Clause license - https://github.com/semuconsulting/pygpsclient/"
ERRCOL = "pink"  # default invalid data entry field background color
ERROR = "ERR!"
FGCOL = "white"  # default widget foreground color
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
GNSS_EOF_EVENT = "<<gnss_eof>>"
GNSS_ERR_EVENT = "<<gnss_error>>"
GNSS_EVENT = "<<gnss_read>>"
GNSS_LIST = {
    0: ("GPS", "royalblue"),
    1: ("SBA", "orange"),
    2: ("GAL", "green4"),
    3: ("BEI", "mediumpurple2"),
    4: ("IME", "violet"),
    5: ("QZS", "yellow"),
    6: ("GLO", "indianred"),
    7: ("NAV", "grey60"),
}
GPSEPOCH0 = datetime(1980, 1, 6)  # for Wno and Tow calculations
GPX_NS = " ".join(
    (
        'xmlns="http://www.topografix.com/GPX/1/1"',
        'creator="PyGPSClient" version="1.1"',
        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"',
        'xsi:schemaLocation="http://www.topografix.com/GPX/1/1',
        'http://www.topografix.com/GPX/1/1/gpx.xsd"',
    )
)
GPX_TRACK_INTERVAL = 1  # minimum GPS track update interval (seconds)
GUI_UPDATE_INTERVAL = 0.5  # minimum GUI widget update interval (seconds)
ICON_APP = path.join(DIRNAME, "resources/iconmonstr-location-27-32.png")
ICON_BLANK = path.join(DIRNAME, "resources/blank-1-24.png")
ICON_CONFIRMED = path.join(DIRNAME, "resources/iconmonstr-check-mark-8-24.png")
ICON_CONN = path.join(DIRNAME, "resources/iconmonstr-media-control-48-24.png")
ICON_CONTRACT = path.join(DIRNAME, "resources/iconmonstr-triangle-1-16.png")
ICON_DELETE = path.join(DIRNAME, "resources/iconmonstr-trash-can-filled-24.png")
ICON_DISCONN = path.join(DIRNAME, "resources/iconmonstr-media-control-50-24.png")
ICON_EXIT = path.join(DIRNAME, "resources/iconmonstr-door-6-24.png")
ICON_EXPAND = path.join(DIRNAME, "resources/iconmonstr-arrow-80-16.png")
ICON_LOAD = path.join(DIRNAME, "resources/iconmonstr-folder-18-24.png")
ICON_LOGREAD = path.join(DIRNAME, "resources/binary-1-24.png")
ICON_NOCLIENT = path.join(DIRNAME, "resources/iconmonstr-noclient-10-24.png")
ICON_NOTRANSMIT = path.join(DIRNAME, "resources/iconmonstr-notransmit-10-24.png")
ICON_NTRIPCONFIG = path.join(DIRNAME, "resources/iconmonstr-antenna-4-24.png")
ICON_PENDING = path.join(DIRNAME, "resources/iconmonstr-time-6-24.png")
ICON_PLAY = path.join(DIRNAME, "resources/iconmonstr-media-control-48-24.png")
ICON_POS = path.join(DIRNAME, "resources/iconmonstr-location-1-24.png")
ICON_RECORD = path.join(DIRNAME, "resources/iconmonstr-record-24.png")
ICON_REDRAW = path.join(DIRNAME, "resources/iconmonstr-refresh-lined-24.png")
ICON_REFRESH = path.join(DIRNAME, "resources/iconmonstr-refresh-6-16.png")
ICON_SAVE = path.join(DIRNAME, "resources/iconmonstr-save-14-24.png")
ICON_SEND = path.join(DIRNAME, "resources/iconmonstr-arrow-12-24.png")
ICON_SERIAL = path.join(DIRNAME, "resources/usbport-1-24.png")
ICON_SOCKET = path.join(DIRNAME, "resources/ethernet-1-24.png")
ICON_SPARTNCONFIG = path.join(DIRNAME, "resources/iconmonstr-antenna-3-24.png")
ICON_STOP = path.join(DIRNAME, "resources/iconmonstr-stop-1-24.png")
ICON_TRANSMIT = path.join(DIRNAME, "resources/iconmonstr-transmit-10-24.png")
ICON_UBXCONFIG = path.join(DIRNAME, "resources/iconmonstr-gear-2-24.png")
ICON_UNDO = path.join(DIRNAME, "resources/iconmonstr-undo-24.png")
ICON_UNKNOWN = path.join(DIRNAME, "resources/clear-1-24.png")
ICON_WARNING = path.join(DIRNAME, "resources/iconmonstr-warning-1-24.png")
IMG_WORLD = path.join(DIRNAME, "resources/world.png")
KM2M = 1000
KM2MIL = 0.621371
KM2NMIL = 0.5399568
KNOWNGPS = (
    "CP210",
    "FT230",
    "FT232",
    "garmin",
    "Garmin",
    "gnss",
    "GNSS",
    "gps",
    "GPS",
    "magellan",
    "Magellan",
    "sirf",
    "Sirf",
    "SiRF",
    "trimble",
    "Trimble",
    "u-blox",
    "U-Blox",
    "ublox",
    "USB to UART",
    "USB UART",
    "USB_to_UART",
    "USER-DEFINED",
)
KPH2KNT = 0.5399568
KPH2MPH = 0.621371
KPH2MPS = 0.2777776918389111005
M2FT = 3.28084
MAX_SNR = 60  # upper limit of graphview snr axis
MAXLOGLINES = 10000  # maximum number of 'lines' per datalog file
MQAPIKEY = "mqapikey"
MQTT_PROTOCOL = 6
MSGMODES = {
    "GET": GET,
    "SET": SET,
    "POLL": POLL,
}
NOPORTS = 3
NTRIP_EVENT = "<<ntrip_read>>"
OKCOL = "green"
POPUP_TRANSIENT = True  # whether pop-up config dialogs are always on top
PORTIDS = ("0 I2C", "1 UART1", "2 UART2", "3 USB", "4 SPI")
PYPI_URL = "https://pypi.org/pypi/PyGPSClient"
QUITONERRORDEFAULT = 1
RCVR_CONNECTION = "USB"  # default GNSS receiver connection port
READONLY = "readonly"
RXMMSG = "RXM-SPARTN-KEY"
SAT_EXPIRY = 10  # how long passed satellites are kept in the sky and graph view
SAVED_CONFIG = "saved_config"
SOCK_NTRIP = "NTRIP CASTER"
SOCK_SERVER = "SOCKET SERVER"
SOCKCLIENT_HOST = "localhost"
SOCKCLIENT_PORT = 50010
SOCKMODES = (SOCK_SERVER, SOCK_NTRIP)
SOCKSERVER_HOST = "0.0.0.0"  # i.e. bind to all host IP addresses
SOCKSERVER_MAX_CLIENTS = 5
SOCKSERVER_NTRIP_PORT = 2101
SOCKSERVER_PORT = 50012
SPARTN_EOF_EVENT = "<<spartn_eof>>"
SPARTN_ERR_EVENT = "<<spartn_error>>"
SPARTN_EVENT = "<<spartn_read>>"
SPARTN_KEYLEN = 16
SPARTN_OUTPORT = 8883
SPARTN_PPREGIONS = ("eu", "us", "jp", "kr", "au")
SPARTN_PPSERVER = "pp.services.u-blox.com"
SPARTN_PPSERVER = "pp.services.u-blox.com"
SPARTN_SOURCE_IP = 0
SPARTN_SOURCE_LB = 1
THD = "thd"
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
TOPIC_IP = "/pp/ip/{}"
TOPIC_MGA = "/pp/ubx/mga"
TOPIC_RXM = "/pp/ubx/0236/ip"
UBXPRESETS = "ubxpresets"
UI = "Imperial mph"
UIK = "Imperial knots"
UMK = "Metric kmph"
UMM = "Metric m/s"
WIDGETU1 = (250, 250)  # small widget size
WIDGETU2 = (350, 250)  # medium widget size
WIDGETU3 = (950, 350)  # Console size
WIDGETU4 = (600, 600)  # GPX Track viewer size
XML_HDR = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'

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
SYSMONVIEW = 12
ROVERVIEW = 13

# map of fix values to descriptions
# the keys in this map are a concatenation of NMEA/UBX
# message identifier and attribute value e.g.:
# GGA1: GGA + quality = 1
# NAV-STATUS3: NAV-STATUS + gpsFix = 3
# (valid for NMEA >=4)
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
}
