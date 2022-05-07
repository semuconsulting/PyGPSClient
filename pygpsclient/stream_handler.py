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

# import pyubx2.ubxtypes_core as ubt
from pygpsclient.globals import (
    CONNECTED,
    CONNECTED_FILE,
    CONNECTED_SOCKET,
    DISCONNECTED,
    FILEREAD_INTERVAL,
    DEFAULT_BUFSIZE,
    NOPORTS,
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
        self._lastfileread = datetime.now()

    def __del__(self):
        """
        Destructor.
        """

        if self._stream_thread is not None:
            self._reading = False
            self._stream_thread = None
            self.disconnect()

    def connect(self):
        """
        Open serial connection.
        """
        # pylint: disable=consider-using-with

        serial_settings = self.__app.frm_settings.serial_settings()
        if serial_settings.status == NOPORTS:
            return

        self.__app.conn_status = CONNECTED
        self.__app.set_connection(
            (
                f"{serial_settings.port}:{serial_settings.port_desc} "
                + f"@ {str(serial_settings.bpsrate)}"
            ),
            "green",
        )
        self.start_read_thread()

    def connect_file(self):
        """
        Open binary data file connection.
        """
        # pylint: disable=consider-using-with

        in_filepath = self.__app.frm_settings.infilepath
        if in_filepath is None:
            return

        self.__app.conn_status = CONNECTED_FILE
        self.__app.set_connection(f"{in_filepath}", "blue")
        self.start_read_thread()

    def connect_socket(self):
        """
        Open socket connection.
        """

        socket_settings = self.__app.frm_settings.socket_settings()

        self.__app.conn_status = CONNECTED_SOCKET
        self.__app.set_connection(
            f"{socket_settings.server}:{socket_settings.port}", "green"
        )
        self.start_read_thread()

    def disconnect(self):
        """
        Terminate stream connection.
        """

        self._reading = False
        self.__app.conn_status = DISCONNECTED
        self.__app.frm_settings.enable_controls(DISCONNECTED)

    @property
    def port(self):
        """
        Getter for port
        """

        return self.__app.frm_settings.serial_settings().port

    @property
    def serial(self):
        """
        Getter for serial object
        """

        return self._serial_object

    @property
    def buffer(self):
        """
        Getter for serial buffer
        """

        return self._serial_buffer

    @property
    def thread(self):
        """
        Getter for serial thread
        """

        return self._stream_thread

    def serial_write(self, data: bytes):
        """
        Write binary data to serial port.

        :param bytes data: data to write to stream
        """

        if self.__app.conn_status == CONNECTED and self._serial_object is not None:
            try:
                self._serial_object.write(data)
            except (SerialException, SerialTimeoutException) as err:
                print(f"Error writing to serial port {err}")

    def start_read_thread(self):
        """
        Start the appropriate serial reader thread.
        """

        self._reading = True
        self.__app.frm_mapview.reset_map_refresh()
        if self.__app.conn_status == CONNECTED:
            target = self._readserial_thread
        if self.__app.conn_status == CONNECTED_FILE:
            target = self._readfile_thread
        if self.__app.conn_status == CONNECTED_SOCKET:
            target = self._readsocket_thread
        self._stream_thread = Thread(target=target, daemon=True)
        self._stream_thread.start()
        self.__app.set_status("Connected", "blue")

    def stop_read_thread(self):
        """
        Stop serial reader thread.
        """

        if self._stream_thread is not None:
            self._reading = False
            self._stream_thread = None
            # self.__app.set_status(STOPDATA, "red")

    def _readserial_thread(self):
        """
        THREADED PROCESS
        Reads binary data from serial port and places output on message queue.
        """

        raw_data = None
        parsed_data = None
        serial_settings = self.__app.frm_settings.serial_settings()

        try:

            with Serial(
                serial_settings.port,
                serial_settings.bpsrate,
                bytesize=serial_settings.databits,
                stopbits=serial_settings.stopbits,
                parity=serial_settings.parity,
                xonxoff=serial_settings.xonxoff,
                rtscts=serial_settings.rtscts,
                timeout=serial_settings.timeout,
            ) as serial_object:
                serial_buffer = BufferedReader(serial_object)
                ubr = UBXReader(
                    serial_buffer,
                    protfilter=NMEA_PROTOCOL | UBX_PROTOCOL | RTCM3_PROTOCOL,
                    quitonerror=ERR_IGNORE,
                )

                while self._reading:
                    try:

                        raw_data, parsed_data = ubr.read()
                        if raw_data is not None:
                            self.__app.enqueue(raw_data, parsed_data)

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

        except EOFError:
            self.__master.event_generate("<<gnss_eof>>")
        except (IOError, SerialException, SerialTimeoutException) as err:
            self.__app.conn_status = DISCONNECTED
            self.__app.set_connection(
                (
                    f"{serial_settings.port}:{serial_settings.port_desc} "
                    + f"@ {str(serial_settings.bpsrate)}"
                ),
                "red",
            )
            self.__app.set_status(f"Error in serial read {err}", "red")
        # spurious errors as thread shuts down after serial disconnection
        # except (TypeError, OSError):
        #     pass

    def _readfile_thread(self):
        """
        THREADED PROCESS
        Reads binary data from file and places output on message queue.
        """

        raw_data = None
        parsed_data = None
        in_filepath = self.__app.frm_settings.infilepath

        try:

            with open(in_filepath, "rb") as serial_object:
                serial_buffer = BufferedReader(serial_object)
                ubr = UBXReader(
                    serial_buffer,
                    protfilter=NMEA_PROTOCOL | UBX_PROTOCOL | RTCM3_PROTOCOL,
                    quitonerror=ERR_IGNORE,
                )

                while self._reading:
                    try:

                        # introduce time delay to prevent GUI locking
                        # during file reads
                        if datetime.now() > self._lastfileread + timedelta(
                            seconds=FILEREAD_INTERVAL
                        ):
                            raw_data, parsed_data = ubr.read()
                            if raw_data is None:
                                raise EOFError
                            self.__app.enqueue(raw_data, parsed_data)
                            self._lastfileread = datetime.now()

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

        except EOFError:
            self.__master.event_generate("<<gnss_eof>>")
        except (IOError, SerialException, SerialTimeoutException) as err:
            self.__app.conn_status = DISCONNECTED
            self.__app.set_connection(f"{in_filepath}", "red")
            self.__app.set_status(f"Error in file read {err}", "red")
        # spurious errors as thread shuts down after serial disconnection
        # except (TypeError, OSError):
        #     pass

    def _readsocket_thread(self):
        """
        THREADED PROCESS
        Reads binary data from socket and places output on message queue.
        """

        raw_data = None
        parsed_data = None
        socket_settings = self.__app.frm_settings.socket_settings()
        server = socket_settings.server
        port = socket_settings.port

        if socket_settings.protocol == "UDP":
            socktype = socket.SOCK_DGRAM
        else:  # TCP
            socktype = socket.SOCK_STREAM

        try:
            with socket.socket(socket.AF_INET, socktype) as sock:
                sock.connect((server, port))
                ubr = UBXReader(
                    sock,
                    protfilter=NMEA_PROTOCOL | UBX_PROTOCOL | RTCM3_PROTOCOL,
                    quitonerror=ERR_IGNORE,
                    bufsize=DEFAULT_BUFSIZE,
                )

                while self._reading:
                    try:

                        raw_data, parsed_data = ubr.read()
                        if raw_data is not None:
                            self.__app.enqueue(raw_data, parsed_data)

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

        except (EOFError, TimeoutError):
            self.__master.event_generate("<<gnss_eof>>")
        except (OSError, AttributeError, socket.gaierror) as err:
            if self._reading:
                self._reading = False
                self.__app.conn_status = DISCONNECTED
                self.__app.set_status(f"Error in socket read {err}", "red")

    def on_eof(self, event):  # pylint: disable=unused-argument
        """
        EVENT TRIGGERED
        Action on end of file

        :param event event: eof event
        """

        self.disconnect()
        self.__app.set_status(ENDOFFILE, "blue")
