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
from threading import Thread, Event
from queue import Queue
from datetime import datetime, timedelta
from serial import Serial, SerialException, SerialTimeoutException
from pyubx2 import (
    UBXReader,
    UBXMessageError,
    UBXParseError,
    ERR_IGNORE,
    UBX_PROTOCOL,
    NMEA_PROTOCOL,
    RTCM3_PROTOCOL,
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
        self._stopevent = Event()
        self._sockserve_event = Event()

    @property
    def serial(self):
        """
        Getter for serial object
        """

        return self._serial_object

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

    def start_read_thread(self, mode: int):
        """
        Start the stream read thread.

        :param int mode: connection mode
        """

        self._stopevent.clear()
        self.__app.frm_mapview.reset_map_refresh()
        self._stream_thread = Thread(
            target=self._read_thread,
            args=(
                self._stopevent,
                self._sockserve_event,
                self.__app.msgqueue,
                self.__app.socketqueue,
                mode,
            ),
            daemon=True,
        )
        self._stream_thread.start()
        self.__app.set_status("Connected", "blue")

    def stop_read_thread(self):
        """
        Stop serial reader thread.
        """

        self._stopevent.set()
        self._stream_thread = None
        self.__app.conn_status = DISCONNECTED

    def _read_thread(
        self,
        stopevent: Event,
        sockserve_event: Event,
        msgqueue: Queue,
        socketqueue: Queue,
        mode: int,
    ):
        """
        THREADED PROCESS

        Connects to selected data stream and starts read loop.

        :param Event stopevent: thread stop event
        :param Event sockserve_event: socket serving event
        :param Queue msgqueue: message queue
        :param Queue socketqueue: socket server message queue
        :param int mode: connection mode
        """

        connstr = ""
        try:

            if mode == CONNECTED:

                ser = self.__app.frm_settings.serial_settings()
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
                ) as self._serial_object:
                    stream = BufferedReader(self._serial_object)
                    self._readloop(
                        stopevent,
                        sockserve_event,
                        msgqueue,
                        socketqueue,
                        stream,
                        mode,
                    )

            elif mode == CONNECTED_FILE:

                in_filepath = self.__app.frm_settings.infilepath
                connstr = f"{in_filepath}"
                with open(in_filepath, "rb") as self._serial_object:
                    stream = BufferedReader(self._serial_object)
                    self._readloop(
                        stopevent,
                        sockserve_event,
                        msgqueue,
                        socketqueue,
                        stream,
                        mode,
                    )

            elif mode == CONNECTED_SOCKET:

                soc = self.__app.frm_settings.socket_settings()
                server = soc.server
                port = soc.port
                connstr = f"{server}:{port}"
                if soc.protocol == "UDP":
                    socktype = socket.SOCK_DGRAM
                else:  # TCP
                    socktype = socket.SOCK_STREAM
                with socket.socket(socket.AF_INET, socktype) as stream:
                    stream.connect((server, port))
                    self._readloop(
                        stopevent, sockserve_event, msgqueue, socketqueue, stream, mode
                    )

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
            if not stopevent.is_set():
                stopevent.set()
                self.__app.conn_status = DISCONNECTED
                self.__app.set_connection(connstr, "red")
                self.__app.set_status(f"Error in stream read {err}", "red")

    def _readloop(
        self,
        stopevent: Event,
        sockserve_event: Event,
        msgqueue: Queue,
        socketqueue: Queue,
        stream: object,
        mode: int,
    ):
        """
        Read stream continously until stop event or stream error.

        File streams use a small delay between reads to
        prevent thrashing.

        :param Event stopevent: thread stop event
        :param Event sockserve_event: socket serving event
        :param Queue msgqueue: message queue
        :param Queue socketqueue: socket server message queue
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
        while not stopevent.is_set():
            try:

                if mode in (CONNECTED, CONNECTED_SOCKET) or (
                    mode == CONNECTED_FILE
                    and datetime.now() > lastread + timedelta(seconds=FILEREAD_INTERVAL)
                ):
                    raw_data, parsed_data = ubr.read()
                    if raw_data is not None:
                        msgqueue.put((raw_data, parsed_data))
                        self.__master.event_generate("<<stream_read>>")
                        if sockserve_event.is_set():
                            socketqueue.put(raw_data)
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
                msgqueue.put((raw_data, parsed_data))
                self.__master.event_generate("<<stream_read>>")
                continue

    def on_eof(self, event):  # pylint: disable=unused-argument
        """
        EVENT TRIGGERED
        Action on end of file

        :param event event: <<gnss_eof>> event
        """

        self.stop_read_thread()
        self.__app.frm_settings.server_state = 0  # turn off socket server
        self.__app.set_status(ENDOFFILE, "blue")
