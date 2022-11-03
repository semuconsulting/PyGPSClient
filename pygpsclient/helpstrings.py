"""
Help text strings for PyGPSClient command line keyword args
Created on 31 Oct 2022
:author: semuadmin
:copyright: SEMU Consulting © 2022
:license: BSD 3-Clause
"""
# pylint: disable=line-too-long

from platform import system
from pygpsclient._version import __version__ as VERSION

# console escape sequences don't work on standard Windows terminal
RED = ""
GREEN = ""
BLUE = ""
YELLOW = ""
MAGENTA = ""
CYAN = ""
BOLD = ""
NORMAL = ""
if system() != "Windows":
    RED = "\033[31m"
    GREEN = "\033[32m"
    BLUE = "\033[34m"
    YELLOW = "\033[33m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    BOLD = "\033[1m"
    NORMAL = "\033[0m"


PYGPSCLIENT_HELP = (
    f"\n\n{RED}{BOLD}PyGPSClient v{VERSION}\n"
    + f"=================={NORMAL}\n\n"
    + f"{BOLD}PyGPSClient{NORMAL} is a multi-platform graphical "
    + "GNSS/GPS testing, diagnostic and UBX © (u-blox ™) device configuration "
    + "application written entirely in Python and tkinter. "
    + "PyGPSClient is capable of parsing NMEA, UBX and RTCM3 protocols.\n\n"
    + f"{GREEN}Usage:{NORMAL}\n\n"
    + "  pygpsclient\n\n"
    + f"{GREEN}Optional command line keyword arguments (default):{NORMAL}\n\n"
    + "  port - user defined serial port (None)\n\n"
    + f"{CYAN}© 2022 SEMU Consulting BSD 3-Clause license\n"
    + "https://github.com/semuconsulting/pygpsclient/\n\n"
)
