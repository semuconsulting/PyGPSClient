"""
Entry point for PyGPSClient Application.

Created on 12 Sep 2020

:author: semuadmin
:copyright: 2020 SEMU Consulting
:license: BSD 3-Clause
"""

import sys
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
from logging import getLogger
from os import getenv
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
    DEFAULT_PASSWORD,
    DEFAULT_REGION,
    DEFAULT_USER,
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
        required=False,
        help="Fully-qualified path to configuration file",
        default=CONFIGFILE,
    )
    ap.add_argument(
        "-U",
        "--userport",
        required=False,
        help="User-defined GNSS receiver port",
        default=getenv("PYGPSCLIENT_USERPORT", ""),
    )
    ap.add_argument(
        "-S",
        "--spartnport",
        required=False,
        help="User-defined SPARTN receiver port",
        default=getenv("PYGPSCLIENT_SPARTNPORT", ""),
    )
    ap.add_argument(
        "--mqapikey",
        required=False,
        help="MapQuest API Key",
        default=getenv("MQAPIKEY", ""),
    )
    ap.add_argument(
        "--mqttclientid",
        required=False,
        help="MQTT Client ID",
        default=getenv("MQTTCLIENTID", ""),
    )
    ap.add_argument(
        "--mqttclientregion",
        required=False,
        help="MQTT Client Region",
        default=getenv("MQTTCLIENTREGION", DEFAULT_REGION),
    )
    ap.add_argument(
        "--mqttclientmode",
        required=False,
        help="MQTT Client Mode (0 - IP, 1 - L-Band)",
        default=getenv("MQTTCLIENTMODE", "0"),
    )
    ap.add_argument(
        "--ntripcasteruser",
        required=False,
        help="NTRIP Caster authentication user",
        default=getenv("NTRIPCASTER_USER", DEFAULT_USER),
    )
    ap.add_argument(
        "--ntripcasterpassword",
        required=False,
        help="NTRIP Caster authentication password",
        default=getenv("NTRIPCASTER_PASSWORD", DEFAULT_PASSWORD),
    )
    ap.add_argument(
        "--spartnkey",
        required=False,
        help="SPARTN message decryption key",
        default=getenv("MQTTKEY", ""),
    )
    ap.add_argument(
        "--verbosity",
        required=False,
        help=(
            f"Log message verbosity "
            f"{VERBOSITY_CRITICAL} = critical, "
            f"{VERBOSITY_LOW} = low (error), "
            f"{VERBOSITY_MEDIUM} = medium (warning), "
            f"{VERBOSITY_HIGH} = high (info), {VERBOSITY_DEBUG} = debug"
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
        required=False,
        help="fully qualified log file name, or '' for no log file",
        type=str,
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
