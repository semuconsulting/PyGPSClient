"""
StreamHandler class for PyGPSClient application

This handles all the stream i/o, threaded read process and direction to
the appropriate protocol handler.

NB: The calling object ('settings["owner"]') must implement the following methods:

- conn_status(self) -> int:
- conn_status(self, status: int):
- set_status(self, msg: str, col: str):
- set_connection(self, msg: str, col: str):
- serial_settings(self) -> Frame:

Created on 16 Sep 2020

:author: semuadmin
:copyright: SEMU Consulting © 2020
:license: BSD 3-Clause
"""

import socket
from datetime import datetime, timedelta
from queue import Empty
from threading import Event, Thread

from pynmeagps import NMEAMessageError, NMEAParseError
from pyrtcm import RTCMMessageError, RTCMParseError
from pyubx2 import (
    ERR_IGNORE,
    NMEA_PROTOCOL,
    RTCM3_PROTOCOL,
    UBX_PROTOCOL,
    UBXMessageError,
    UBXParseError,
    UBXReader,
)
from serial import Serial, SerialException, SerialTimeoutException

from pygpsclient.globals import (
    CONNECTED,
    CONNECTED_FILE,
    CONNECTED_SOCKET,
    DEFAULT_BUFSIZE,
    DISCONNECTED,
    FILEREAD_INTERVAL,
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
        self.__master = self.__app.appmaster  # Reference to root class (Tk)

        self._stream_thread = None
        self._stopevent = Event()
        self._sockserve_event = Event()
        self._owner = None

    def start_read_thread(self, settings: dict):
        """
        Start the stream read thread.

        :param dict settings: settings dictionary
        """

        self._stopevent.clear()
        self._owner = settings["owner"]
        self._stream_thread = Thread(
            target=self._read_thread,
            args=(
                self._stopevent,
                self._sockserve_event,
                settings,
            ),
            daemon=True,
        )
        self._stream_thread.start()
        self._set_status("Connected")

    def stop_read_thread(self):
        """
        Stop serial reader thread.
        """

        self._stopevent.set()
        self._stream_thread = None
        if self._owner is not None:
            self._owner.conn_status = DISCONNECTED

    def _read_thread(
        self,
        stopevent: Event,
        sockserve_event: Event,
        settings: dict,
    ):
        """
        THREADED PROCESS

        Connects to selected data stream and starts read loop.

        :param Event stopevent: thread stop event
        :param Event sockserve_event: socket serving event
        :param dict settings: settings dictionary
        """

        connstr = ""
        owner = settings["owner"]
        conn_status = owner.conn_status
        try:
            if conn_status == CONNECTED:
                ser = settings["serial_settings"]
                connstr = f"{ser.port}:{ser.port_desc} @ {str(ser.bpsrate)}"
                with Serial(
                    ser.port,
                    ser.bpsrate,
                    bytesize=ser.databits,
                    stopbits=ser.stopbits,
                    parity=ser.parity,
                    xonxoff=ser.xonxoff,
                    rtscts=ser.rtscts,
                    timeout=ser.timeout,
                ) as serial_object:
                    self._readloop(
                        stopevent,
                        sockserve_event,
                        serial_object,
                        settings,
                    )

            elif conn_status == CONNECTED_FILE:
                in_filepath = settings["in_filepath"]
                connstr = f"{in_filepath}"
                with open(in_filepath, "rb") as serial_object:
                    self._readloop(
                        stopevent,
                        sockserve_event,
                        serial_object,
                        settings,
                    )

            elif conn_status == CONNECTED_SOCKET:
                soc = settings["socket_settings"]
                server = soc.server
                port = soc.port
                connstr = f"{server}:{port}"
                if soc.protocol == "UDP":
                    socktype = socket.SOCK_DGRAM
                else:  # TCP
                    socktype = socket.SOCK_STREAM
                with socket.socket(socket.AF_INET, socktype) as serial_object:
                    serial_object.connect((server, port))
                    self._readloop(
                        stopevent,
                        sockserve_event,
                        serial_object,
                        settings,
                    )

        except (EOFError, TimeoutError):
            self.__master.event_generate(settings["eof_event"])
        except (
            IOError,
            SerialException,
            SerialTimeoutException,
            OSError,
            AttributeError,
            socket.gaierror,
        ) as err:
            if not stopevent.is_set():
                stopevent.set()
                owner.conn_status = DISCONNECTED
                self._set_connection(connstr, "red")
                self._set_status(f"Error in stream read {err}", "red")

    def _readloop(
        self,
        stopevent: Event,
        sockserve_event: Event,
        serial_object: object,
        settings: dict,
    ):
        """
        Read stream continously until stop event or stream error.

        File streams use a small delay between reads to
        prevent thrashing.

        :param Event stopevent: thread stop event
        :param Event sockserve_event: socket serving event
        :param object serial_object: serial data stream
        :param dict settings: settings dictionary
        """

        owner = settings["owner"]
        # stream = BufferedReader(serial_object)
        stream = serial_object
        ubr = UBXReader(
            stream,
            protfilter=NMEA_PROTOCOL | UBX_PROTOCOL | RTCM3_PROTOCOL,
            quitonerror=ERR_IGNORE,
            bufsize=DEFAULT_BUFSIZE,
            msgmode=settings["serial_settings"].msgmode,
        )

        raw_data = None
        parsed_data = None
        lastread = datetime.now()
        while not stopevent.is_set():
            try:
                if owner.conn_status in (CONNECTED, CONNECTED_SOCKET) or (
                    owner.conn_status == CONNECTED_FILE
                    and datetime.now() > lastread + timedelta(seconds=FILEREAD_INTERVAL)
                ):
                    raw_data, parsed_data = ubr.read()
                    if raw_data is not None:
                        settings["inqueue"].put((raw_data, parsed_data))
                        self.__master.event_generate(settings["read_event"])
                        # if socket server is running
                        if sockserve_event.is_set():
                            settings["socket_outqueue"].put(raw_data)
                    else:
                        if owner.conn_status == CONNECTED_FILE:
                            raise EOFError
                    if owner.conn_status == CONNECTED_FILE:
                        lastread = datetime.now()
                        self.__master.update_idletasks()

                    # write any queued output data to serial stream
                    if owner.conn_status == CONNECTED:
                        try:
                            while not settings["outqueue"].empty():
                                data = settings["outqueue"].get(False)
                                if data is not None:
                                    serial_object.write(data)
                                settings["outqueue"].task_done()
                        except Empty:
                            pass

            except (
                UBXMessageError,
                UBXParseError,
                NMEAMessageError,
                NMEAParseError,
                RTCMMessageError,
                RTCMParseError,
            ) as err:
                parsed_data = f"Error parsing data stream {err}"
                settings["inqueue"].put((raw_data, parsed_data))
                self.__master.event_generate(settings["read_event"])
                continue

    def on_eof(self, event):  # pylint: disable=unused-argument
        """
        EVENT TRIGGERED
        Action on end of file

        :param event event: <<gnss_eof>> event
        """

        self.stop_read_thread()
        self.__app.frm_settings.server_state = 0  # turn off socket server
        self._set_status(
            ENDOFFILE,
        )

    def _set_connection(self, msg: str, col: str = ""):
        """
        Set connection message.

        :param str msg: status message
        :param str col: colour
        """

        if self._owner is not None:
            self._owner.set_connection(msg, col)

    def _set_status(self, msg: str, col: str = ""):
        """
        Set status message.

        :param str msg: status message
        :param str col: colour
        """

        if self._owner is not None:
            self._owner.set_status(msg, col)

    @property
    def sock_serve(self) -> bool:
        """
        Getter for socket serve event status.

        :return: socket server status (True/False)
        :rtype: bool
        """

        return self._sockserve_event.is_set()

    @sock_serve.setter
    def sock_serve(self, status: bool):
        """
        Setter for socket serve event status.

        :param bool status: sock serve status
        """

        if status:
            self._sockserve_event.set()
        else:
            self._sockserve_event.clear()
