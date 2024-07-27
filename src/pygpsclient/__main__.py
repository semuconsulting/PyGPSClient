"""
Entry point for PyGPSClient Application.

Created on 12 Sep 2020

:author: semuadmin
:copyright: SEMU Consulting © 2020
:license: BSD 3-Clause
"""

import logging
import sys
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
from os import getenv
from tkinter import Tk

from pygnssutils import (
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
    EPILOG,
)


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
            f"Log message verbosity {VERBOSITY_LOW} = low (error, critical), "
            f"{VERBOSITY_MEDIUM} = medium (warning), "
            f"{VERBOSITY_HIGH} = high (info), {VERBOSITY_DEBUG} = debug"
        ),
        type=int,
        choices=[VERBOSITY_LOW, VERBOSITY_MEDIUM, VERBOSITY_HIGH, VERBOSITY_DEBUG],
        default=VERBOSITY_MEDIUM,
    )
    ap.add_argument(
        "--logtofile",
        required=False,
        help="fully qualified log file name, or '' for no log file",
        type=str,
        default="",
    )
    kwargs = vars(ap.parse_args())

    logger = logging.getLogger(APPNAME)
    # This sets logger configuration globally.
    # Subsidiary modules can use:
    # `self.logger = logging.getLogger(__name__)`
    # as __name__ expands to "APPNAME.module_name"
    set_logging(
        logger, kwargs.pop("verbosity", VERBOSITY_MEDIUM), kwargs.pop("logtofile", "")
    )
    # To override individual module loglevel, use e.g. `self.logger.setLevel(INFO)`

    root = Tk()
    App(root, **kwargs)
    root.mainloop()
    sys.exit()


if __name__ == "__main__":
    main()
