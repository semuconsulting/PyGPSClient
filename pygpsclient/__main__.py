"""
Entry point for PyGPSClient Application.

Created on 12 Sep 2020

:author: semuadmin
:copyright: SEMU Consulting © 2020
:license: BSD 3-Clause
"""

import sys
from tkinter import Tk
from pygpsclient.helpstrings import PYGPSCLIENT_HELP
from pygpsclient.app import App


def main():
    """The main tkinter loop."""

    if len(sys.argv) > 1:
        if sys.argv[1] in {"-h", "--h", "help", "-help", "--help", "-H"}:
            print(PYGPSCLIENT_HELP)
            sys.exit()

    kwargs = dict(arg.split("=") for arg in sys.argv[1:])

    root = Tk()
    App(root, **kwargs)
    root.mainloop()
    sys.exit()


if __name__ == "__main__":
    main()
