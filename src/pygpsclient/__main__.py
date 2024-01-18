"""
Entry point for PyGPSClient Application.

Created on 12 Sep 2020

:author: semuadmin
:copyright: SEMU Consulting © 2020
:license: BSD 3-Clause
"""

import sys
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
from os import getenv
from tkinter import Tk

from pygpsclient._version import __version__ as VERSION
from pygpsclient.app import App
from pygpsclient.globals import (
    CONFIGFILE,
    DEFAULT_PASSWORD,
    DEFAULT_REGION,
    DEFAULT_USER,
    EPILOG,
)


def main():
    """The main tkinter loop."""

    arp = ArgumentParser(
        epilog=EPILOG,
        formatter_class=ArgumentDefaultsHelpFormatter,
        description="Command line arguments will override configuration file",
    )
    arp.add_argument("-V", "--version", action="version", version="%(prog)s " + VERSION)
    arp.add_argument(
        "-C",
        "--config",
        required=False,
        help="Fully-qualified path to configuration file",
        default=CONFIGFILE,
    )
    arp.add_argument(
        "-U",
        "--userport",
        required=False,
        help="User-defined GNSS receiver port",
        default=getenv("PYGPSCLIENT_USERPORT", ""),
    )
    arp.add_argument(
        "-S",
        "--spartnport",
        required=False,
        help="User-defined SPARTN receiver port",
        default=getenv("PYGPSCLIENT_SPARTNPORT", ""),
    )
    arp.add_argument(
        "--mqapikey",
        required=False,
        help="MapQuest API Key",
        default=getenv("MQAPIKEY", ""),
    )
    arp.add_argument(
        "--mqttclientid",
        required=False,
        help="MQTT Client ID",
        default=getenv("MQTTCLIENTID", ""),
    )
    arp.add_argument(
        "--mqttclientregion",
        required=False,
        help="MQTT Client Region",
        default=getenv("MQTTCLIENTREGION", DEFAULT_REGION),
    )
    arp.add_argument(
        "--mqttclientmode",
        required=False,
        help="MQTT Client Mode (0 - IP, 1 - L-Band)",
        default=getenv("MQTTCLIENTMODE", "0"),
    )
    arp.add_argument(
        "--ntripcasteruser",
        required=False,
        help="NTRIP Caster authentication user",
        default=getenv("NTRIPCASTER_USER", DEFAULT_USER),
    )
    arp.add_argument(
        "--ntripcasterpassword",
        required=False,
        help="NTRIP Caster authentication password",
        default=getenv("NTRIPCASTER_PASSWORD", DEFAULT_PASSWORD),
    )

    kwargs = vars(arp.parse_args())

    root = Tk()
    App(root, **kwargs)
    root.mainloop()
    sys.exit()


if __name__ == "__main__":
    main()
