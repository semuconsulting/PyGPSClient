"""
RTCM3 Protocol handler - handles all incoming RTCM3 messages

THIS IS JUST A STUB FOR NOW AS THERE'S CURRENTLY NO NEED
TO PROCESS RTCM3 DATA TO UPDATE THE GUI

Uses pyrtcm library for parsing

Created on 10 Apr 2022

:author: semuadmin
:copyright: SEMU Consulting © 2022
:license: BSD 3-Clause
"""
# pylint: disable=invalid-name


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
        self.__master = self.__app.get_master()  # Reference to root class (Tk)

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

            # if parsed_data.identity == "1005":
            #     self._process_1005(parsed_data)
            # etc...

        except ValueError:
            # self.__app.set_status(RTCMVALERROR.format(err), "red")
            pass
