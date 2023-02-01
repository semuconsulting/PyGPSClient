"""
Entry point for PyGPSClient Application.

Created on 12 Sep 2020

:author: semuadmin
:copyright: SEMU Consulting © 2020
:license: BSD 3-Clause
"""

import sys
from argparse import ArgumentParser
from tkinter import Tk

# from pygpsclient.helpstrings import PYGPSCLIENT_HELP
from pygpsclient.globals import EPILOG
from pygpsclient.app import App


def main():
    """The main tkinter loop."""

    ap = ArgumentParser(epilog=EPILOG)
    ap.add_argument(
        "-U", "--userport", required=False, help="User-defined GNSS receiver port"
    )
    ap.add_argument(
        "-S", "--spartnport", required=False, help="User-defined SPARTN receiver port"
    )

    kwargs = vars(ap.parse_args())

    root = Tk()
    App(root, **kwargs)
    root.mainloop()
    sys.exit()


if __name__ == "__main__":
    main()
