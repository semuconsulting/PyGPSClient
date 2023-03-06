"""
Entry point for PyGPSClient Application.

Created on 12 Sep 2020

:author: semuadmin
:copyright: SEMU Consulting © 2020
:license: BSD 3-Clause
"""

import sys
from argparse import ArgumentParser, SUPPRESS
from tkinter import Tk

from pygpsclient.globals import EPILOG
from pygpsclient.app import App
from pygpsclient._version import __version__ as VERSION


def main():
    """The main tkinter loop."""

    arp = ArgumentParser(epilog=EPILOG, argument_default=SUPPRESS)
    arp.add_argument("-V", "--version", action="version", version="%(prog)s " + VERSION)
    arp.add_argument(
        "-U", "--userport", required=False, help="User-defined GNSS receiver port"
    )
    arp.add_argument(
        "-S", "--spartnport", required=False, help="User-defined SPARTN receiver port"
    )
    arp.add_argument("--mqapikey", required=False, help="MapQuest API Key")
    arp.add_argument("--mqttclientid", required=False, help="MQTT Client ID")

    kwargs = vars(arp.parse_args())

    root = Tk()
    App(root, **kwargs)
    root.mainloop()
    sys.exit()


if __name__ == "__main__":
    main()
