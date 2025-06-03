"""
tty_handler.py

TTY Protocol handler - handles all incoming TTY (ASCII Terminal) messages

Created on 18 May 2025

:author: semuadmin
:copyright: 2020 SEMU Consulting
:license: BSD 3-Clause
"""

import logging

from pygpsclient.globals import TTYERR, TTYOK
from pygpsclient.strings import DLGTTTY


class TTYStreamError(Exception):
    """
    TTY Streaming error.
    """


class TTYHandler:
    """
    TTYHandler class.

    TTY Protocol handler - handles all incoming TTY (ASCII Terminal) messages.
    """

    def __init__(self, app):
        """
        Constructor.

        :param Frame app: reference to main tkinter application
        """

        self.__app = app  # Reference to main application class
        self.__master = self.__app.appmaster  # Reference to root class (Tk)
        self.logger = logging.getLogger(__name__)

    def process_data(self, raw_data: bytes, parsed_data: str):
        """
        Process relevant TTY message types.

        :param bytes raw_data: raw data
        :param str parsed_data: parsed data
        """

        if raw_data is None:
            return

        # if data is a recognised OK/ERROR command acknowedgement,
        # update the TTY console accordingly
        acks = TTYOK + TTYERR
        for ack in acks:
            if parsed_data.upper().find(ack):
                if self.__app.dialog(DLGTTTY) is not None:
                    self.__app.dialog(DLGTTTY).update_status(raw_data)
                break
