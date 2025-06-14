"""
rtcm3_handler.py

RTCM Protocol handler - handles all incoming RTCM messages.

Parses individual RTCM3 sentences (using pyrtcm library).

Created on 10 Apr 2022

:author: semuadmin
:copyright: 2020 SEMU Consulting
:license: BSD 3-Clause
"""

import logging

from pynmeagps import ecef2llh, haversine
from pyrtcm import RTCMMessage


class RTCM3Handler:
    """
    RTCM3 handler class.
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
        Process relevant RTCM message types

        :param bytes raw_data: raw_data
        :param RTCMMessage parsed_data: parsed data
        """
        # pylint: disable=no-member

        try:
            if raw_data is None:
                return

            if parsed_data.identity in ("1005", "1006"):
                self._process_1005(parsed_data)

        except ValueError:
            # self.__app.set_status(RTCMVALERROR.format(err), ERRCOL)
            pass

    def _process_1005(self, parsed: RTCMMessage):
        """
        Process 1005/1006 ARP information message.

        :param RTCMMessage parsed: 1005/1006 message
        """

        try:
            self.__app.gnss_status.diff_station = parsed.DF003
            self.__app.gnss_status.base_ecefx = parsed.DF025
            self.__app.gnss_status.base_ecefy = parsed.DF026
            self.__app.gnss_status.base_ecefz = parsed.DF027
            lat2, lon2, _ = ecef2llh(parsed.DF025, parsed.DF026, parsed.DF027)
            self.__app.gnss_status.rel_pos_length = (
                haversine(
                    self.__app.gnss_status.lat,
                    self.__app.gnss_status.lon,
                    lat2,
                    lon2,
                )
                * 100000
            )  # km to cm
            # update Survey-In base station location
            if self.__app.frm_settings.frm_socketserver is not None:
                self.__app.frm_settings.frm_socketserver.update_base_location()
        except (AttributeError, ValueError):
            pass
