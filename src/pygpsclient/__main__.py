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
from pygpsclient.globals import CONFIGFILE, EPILOG


def main():
    """The main tkinter loop."""

    arp = ArgumentParser(
        epilog=EPILOG,
        formatter_class=ArgumentDefaultsHelpFormatter,
        description="Config file will override other command line arguments",
    )
    arp.add_argument("-V", "--version", action="version", version="%(prog)s " + VERSION)
    arp.add_argument(
        "-C",
        "--config",
        required=False,
        help="Fully-qualified path to config file",
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
        default=getenv("MQTTCLIENTREGION", "eu"),
    )
    arp.add_argument(
        "--mqttclientmode",
        required=False,
        help="MQTT Client Mode (0 - IP, 1 - L-Band)",
        default=getenv("MQTTCLIENTMODE", "0"),
    )
    arp.add_argument(
        "--ntripuser",
        required=False,
        help="NTRIP Caster authentication user",
        default=getenv("PYGPSCLIENT_USER", "anon"),
    )
    arp.add_argument(
        "--ntrippassword",
        required=False,
        help="NTRIP Caster authentication password",
        default=getenv("PYGPSCLIENT_PASSWORD", "password"),
    )

    kwargs = vars(arp.parse_args())

    root = Tk()
    App(root, **kwargs)
    root.mainloop()
    sys.exit()


if __name__ == "__main__":
    main()
