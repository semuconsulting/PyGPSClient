"""
qgc_handler.py

QGC Protocol handler - handles all incoming QGC messages

Parses individual QGC messages (using pyqgc library)
and adds selected attribute values to the app.gnss_status
data dictionary. This dictionary is then used to periodically
update the various user-selectable widget panels.

Created on 6 Oct 2025

:author: semuadmin (Steve Smith)
:copyright: 2020 semuadmin
:license: BSD 3-Clause
"""

import logging


class QGCHandler:
    """
    QGCHandler class
    """

    def __init__(self, app):
        """
        Constructor.

        :param Frame app: reference to main tkinter application
        """

        self.__app = app  # Reference to main application class
        self.__master = self.__app.appmaster  # Reference to root class (Tk)
        self.logger = logging.getLogger(__name__)

        self._raw_data = None
        self._parsed_data = None

    def process_data(self, raw_data: bytes, parsed_data: object):
        """
        Process relevant QGC message types

        :param bytes raw_data: raw data
        :param QGCMessage parsed_data: parsed data
        """

        if raw_data is None:
            pass
        # self.logger.debug(f"data received {parsed_data.identity}")
