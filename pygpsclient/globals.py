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
ICON_REFRESH = os.path.join(DIRNAME, "resources/iconmonstr-refresh-6-16.png")
ICON_CONTRACT = os.path.join(DIRNAME, "resources/iconmonstr-triangle-1-16.png")
ICON_EXPAND = os.path.join(DIRNAME, "resources/iconmonstr-arrow-80-16.png")
IMG_WORLD = os.path.join(DIRNAME, "resources/world.png")

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
MAXLOGLINES = 10000  # maximum number of 'lines' per datalog file
PORTIDS = ("0 I2C", "1 UART1", "2 UART2", "3 USB", "4 SPI")
ANTSTATUS = ("INIT", "DONTKNOW", "OK", "SHORT", "OPEN")
ANTPOWER = ("OFF", "ON", "DONTKNOW")
# names of user preset files:
MQAPIKEY = "mqapikey"
UBXPRESETS = "ubxpresets"
# list of recognised serial device descriptors:
KNOWNGPS = (
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
# displayed protocol flags:
NMEA_PROTOCOL = 0
UBX_PROTOCOL = 1
MIXED_PROTOCOL = 2
# display formats
PARSED = 0
BIN = 1
HEX = 2
# connection type flags:
DISCONNECTED = 0
CONNECTED = 1
CONNECTED_FILE = 2
NOPORTS = 3
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

# List of tags to highlight in console
# (NB there is a slight performance hit in having many tags)
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
    ("HNR-PVT", "orange"),
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
    ("NMEA", "lightblue1"),
    ("RLM", "pink"),
    ("RMC", "orange"),
    ("RXM", "skyblue1"),
    ("TXT", "lightgrey"),
    ("UBX", "lightblue1"),
    ("UBX, msgId=00", "aquamarine2"),
    ("UBX, msgId=03", "yellow"),
    ("UBX, msgId=04", "cyan"),
    ("UBX, msgId=05", "orange"),
    ("UBX, msgId=06", "orange"),
    ("VLW", "deepskyblue"),
    ("VTG", "deepskyblue"),
    ("ZDA", "cyan"),
]
