"""
Entry point for PyGPSClient Application.

Created on 12 Sep 2020

:author: semuadmin
:copyright: 2020 SEMU Consulting
:license: BSD 3-Clause
"""

import sys
from argparse import SUPPRESS, ArgumentDefaultsHelpFormatter, ArgumentParser
from logging import getLogger
from tkinter import Tk

from pygnssutils import (
    VERBOSITY_CRITICAL,
    VERBOSITY_DEBUG,
    VERBOSITY_HIGH,
    VERBOSITY_LOW,
    VERBOSITY_MEDIUM,
    set_logging,
)

from pygpsclient._version import __version__ as VERSION
from pygpsclient.app import App
from pygpsclient.globals import (
    APPNAME,
    CONFIGFILE,
    SPARTN_BASEDATE_CURRENT,
    SPARTN_BASEDATE_DATASTREAM,
)
from pygpsclient.strings import EPILOG


def main():
    """The main tkinter loop."""

    ap = ArgumentParser(
        epilog=EPILOG,
        formatter_class=ArgumentDefaultsHelpFormatter,
        description="Command line arguments will override configuration file",
    )
    ap.add_argument("-V", "--version", action="version", version="%(prog)s " + VERSION)
    ap.add_argument(
        "-C",
        "--config",
        help="Fully-qualified path to configuration file",
        default=CONFIGFILE,
    )
    ap.add_argument(
        "-U",
        "--userport",
        help="User-defined GNSS receiver port",
        default=SUPPRESS,
    )
    ap.add_argument(
        "-S",
        "--spartnport",
        help="User-defined SPARTN receiver port",
        default=SUPPRESS,
    )
    ap.add_argument(
        "--mqapikey",
        help="MapQuest API Key",
        default=SUPPRESS,
    )
    ap.add_argument(
        "--mqttclientid",
        help="MQTT Client ID",
        default=SUPPRESS,
    )
    ap.add_argument(
        "--mqttclientregion",
        help="MQTT Client Region",
        default=SUPPRESS,
    )
    ap.add_argument(
        "--mqttclientmode",
        help="MQTT Client Mode (0 - IP, 1 - L-Band)",
        default=SUPPRESS,
    )
    ap.add_argument(
        "--ntripcasteruser",
        help="NTRIP Caster authentication user",
        default=SUPPRESS,
    )
    ap.add_argument(
        "--ntripcasterpassword",
        help="NTRIP Caster authentication password",
        default=SUPPRESS,
    )
    ap.add_argument(
        "--spartnkey",
        help="SPARTN message decryption key",
        default=SUPPRESS,
    )
    ap.add_argument(
        "--spartnbasedate",
        help=f"SPARTN message decryption timetag ({SPARTN_BASEDATE_CURRENT} = \
            current datetime, {SPARTN_BASEDATE_DATASTREAM} = use timetags from data stream)",
        type=int,
        default=SUPPRESS,
    )
    ap.add_argument(
        "--verbosity",
        help=(
            f"Log message verbosity "
            f"{VERBOSITY_CRITICAL} = critical, "
            f"{VERBOSITY_LOW} = low (error), "
            f"{VERBOSITY_MEDIUM} = medium (warning), "
            f"{VERBOSITY_HIGH} = high (info), {VERBOSITY_DEBUG} = debug, "
            f"default = {VERBOSITY_CRITICAL}"
        ),
        type=int,
        choices=[
            VERBOSITY_LOW,
            VERBOSITY_MEDIUM,
            VERBOSITY_HIGH,
            VERBOSITY_DEBUG,
            VERBOSITY_CRITICAL,
        ],
        default=VERBOSITY_CRITICAL,
    )
    ap.add_argument(
        "--logtofile",
        help="fully qualified log file name, or '' for no log file",
        default="",
    )
    kwargs = vars(ap.parse_args())

    # set up global logging configuration
    verbosity = int(kwargs.pop("verbosity", VERBOSITY_CRITICAL))
    logtofile = kwargs.pop("logtofile", "")
    logger = getLogger(APPNAME)  # "pygpsclient"
    logger_utils = getLogger("pygnssutils")
    logger_pyubx2 = getLogger("pyubx2")
    for logr in (logger, logger_utils, logger_pyubx2):
        set_logging(logr, verbosity, logtofile)

    root = Tk()
    App(root, **kwargs)
    root.mainloop()
    sys.exit()


if __name__ == "__main__":
    main()
