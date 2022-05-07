"""
StreamHandler class for PyGPSClient application

This handles all the stream i/o, threaded read process and direction to
the appropriate protocol handler

Created on 16 Sep 2020

:author: semuadmin
:copyright: SEMU Consulting © 2020
:license: BSD 3-Clause
"""

import socket
from io import BufferedReader
from threading import Thread
from datetime import datetime, timedelta
from serial import Serial, SerialException, SerialTimeoutException

from pyubx2 import (
    UBXReader,
    ERR_IGNORE,
    UBX_PROTOCOL,
    NMEA_PROTOCOL,
    RTCM3_PROTOCOL,
    UBXMessageError,
    UBXParseError,
)
from pynmeagps import NMEAMessageError, NMEAParseError
from pyrtcm import RTCMMessageError, RTCMParseError
from pygpsclient.globals import (
    CONNECTED,
    CONNECTED_FILE,
    CONNECTED_SOCKET,
    DISCONNECTED,
    FILEREAD_INTERVAL,
    DEFAULT_BUFSIZE,
)
from pygpsclient.strings import ENDOFFILE


class StreamHandler:
    """
    Stream handler class.
    """

    def __init__(self, app):
        """
        Constructor.

        :param Frame app: reference to main tkinter application

        """

        self.__app = app  # Reference to main application class
        self.__master = self.__app.get_master()  # Reference to root class (Tk)

        self._serial_object = None
        self._serial_buffer = None
        self._stream_thread = None
        self._reading = False

    def disconnect(self):
        """
        Terminate stream connection.
        """

        self._reading = False
        self.__app.conn_status = DISCONNECTED
        self.__app.frm_settings.enable_controls(DISCONNECTED)

    @property
    def serial(self):
        """
        Getter for serial object
        """

        return self._serial_object

    def serial_write(self, data: bytes):
        """
        Write binary data to serial port.

        :param bytes data: data to write to stream
        """

        if self.__app.conn_status == CONNECTED and self._serial_object is not None:
            try:
                self._serial_object.write(data)
            except (SerialException, SerialTimeoutException) as err:
                self.__app.set_status(f"Error writing to serial port {err}", "red")

    def start_read_thread(self):
        """
        Start the stream read thread.
        """

        self._reading = True
        self.__app.frm_mapview.reset_map_refresh()
        self._stream_thread = Thread(target=self._read_thread, daemon=True)
        self._stream_thread.start()
        self.__app.set_status("Connected", "blue")

    def stop_read_thread(self):
        """
        Stop serial reader thread.
        """

        if self._stream_thread is not None:
            self._reading = False
            self._stream_thread = None

    def _read_thread(self):
        """
        THREADED PROCESS

        Connects to selected data stream and starts read loop.
        """

        try:

            if self.__app.conn_status == CONNECTED:

                serial_settings = self.__app.frm_settings.serial_settings()
                connstr = (
                    f"{serial_settings.port}:{serial_settings.port_desc} ",
                    f"@ {str(serial_settings.bpsrate)}",
                )
                with Serial(
                    serial_settings.port,
                    serial_settings.bpsrate,
                    bytesize=serial_settings.databits,
                    stopbits=serial_settings.stopbits,
                    parity=serial_settings.parity,
                    xonxoff=serial_settings.xonxoff,
                    rtscts=serial_settings.rtscts,
                    timeout=serial_settings.timeout,
                ) as self._serial_object:
                    stream = BufferedReader(self._serial_object)
                    self._readloop(stream, self.__app.conn_status)

            elif self.__app.conn_status == CONNECTED_FILE:

                in_filepath = self.__app.frm_settings.infilepath
                connstr = f"{in_filepath}"
                with open(in_filepath, "rb") as self._serial_object:
                    stream = BufferedReader(self._serial_object)
                    self._readloop(stream, self.__app.conn_status)

            elif self.__app.conn_status == CONNECTED_SOCKET:

                socket_settings = self.__app.frm_settings.socket_settings()
                server = socket_settings.server
                port = socket_settings.port
                connstr = f"{server}:{port}"
                if socket_settings.protocol == "UDP":
                    socktype = socket.SOCK_DGRAM
                else:  # TCP
                    socktype = socket.SOCK_STREAM
                with socket.socket(socket.AF_INET, socktype) as stream:
                    stream.connect((server, port))
                    self._readloop(stream, self.__app.conn_status)

        except (EOFError, TimeoutError):
            self.__master.event_generate("<<gnss_eof>>")
        except (
            IOError,
            SerialException,
            SerialTimeoutException,
            OSError,
            AttributeError,
            socket.gaierror,
        ) as err:
            if self._reading:
                self._reading = False
                self.__app.conn_status = DISCONNECTED
                self.__app.set_connection(connstr, "red")
                self.__app.set_status(f"Error in stream read {err}", "red")

    def _readloop(self, stream: object, mode: int):
        """
        Read stream in loop until disconnect or stream error.

        File streams use a small delay between reads to
        prevent thrashing.

        :param object stream: data stream
        :param int mode: connection mode
        """

        ubr = UBXReader(
            stream,
            protfilter=NMEA_PROTOCOL | UBX_PROTOCOL | RTCM3_PROTOCOL,
            quitonerror=ERR_IGNORE,
            bufsize=DEFAULT_BUFSIZE,
        )

        raw_data = None
        parsed_data = None
        lastread = datetime.now()
        while self._reading:
            try:

                if mode in (CONNECTED, CONNECTED_SOCKET) or (
                    mode == CONNECTED_FILE
                    and datetime.now() > lastread + timedelta(seconds=FILEREAD_INTERVAL)
                ):
                    raw_data, parsed_data = ubr.read()
                    if raw_data is not None:
                        self.__app.enqueue(raw_data, parsed_data)
                    else:
                        if mode == CONNECTED_FILE:
                            raise EOFError
                    if mode == CONNECTED_FILE:
                        lastread = datetime.now()

            except (
                UBXMessageError,
                UBXParseError,
                NMEAMessageError,
                NMEAParseError,
                RTCMMessageError,
                RTCMParseError,
            ) as err:
                parsed_data = f"Error parsing data stream {err}"
                self.__app.enqueue(raw_data, parsed_data)
                continue

    def on_eof(self, event):  # pylint: disable=unused-argument
        """
        EVENT TRIGGERED
        Action on end of file

        :param event event: <<gnss_eof>> event
        """

        self.disconnect()
        self.__app.set_status(ENDOFFILE, "blue")
