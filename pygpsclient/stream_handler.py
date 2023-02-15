"""
StreamHandler class for PyGPSClient application

This handles all the stream i/o, threaded read process and direction to
the appropriate protocol handler.

NB: requires the calling app to implement the following attributes:

- mode
- infile_path
- socket_settings
- read_event
- inqueue
- outqueue
- serial_settings

Created on 16 Sep 2020

:author: semuadmin
:copyright: SEMU Consulting © 2020
:license: BSD 3-Clause
"""

import socket
from threading import Thread, Event
from queue import Empty
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
    GNSS_EOF_EVENT,
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
        self._mode = DISCONNECTED

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

    def start_read_thread(self, settings: object):
        """
        Start the stream read thread.

        :param object settings: reference to object holding settings attributes
        """

        self._stopevent.clear()
        self._mode = settings.mode
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
        settings: object,
    ):
        """
        THREADED PROCESS

        Connects to selected data stream and starts read loop.

        :param Event stopevent: thread stop event
        :param Event sockserve_event: socket serving event
        :param object settings: reference to object holding settings attributes
        """

        connstr = ""
        try:
            if settings.mode == CONNECTED:
                ser = settings.serial_settings
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

            elif settings.mode == CONNECTED_FILE:
                in_filepath = settings.infilepath
                connstr = f"{in_filepath}"
                with open(in_filepath, "rb") as serial_object:
                    self._readloop(
                        stopevent,
                        sockserve_event,
                        serial_object,
                        settings,
                    )

            elif settings.mode == CONNECTED_SOCKET:
                soc = settings.socket_settings
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
            self.__master.event_generate(GNSS_EOF_EVENT)
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
        serial_object: object,
        settings: object,
    ):
        """
        Read stream continously until stop event or stream error.

        File streams use a small delay between reads to
        prevent thrashing.

        :param Event stopevent: thread stop event
        :param Event sockserve_event: socket serving event
        :param object serial_object: serial data stream
        :param object settings: reference to object holding settings attributes
        """

        # stream = BufferedReader(serial_object)
        stream = serial_object
        ubr = UBXReader(
            stream,
            protfilter=NMEA_PROTOCOL | UBX_PROTOCOL | RTCM3_PROTOCOL,
            quitonerror=ERR_IGNORE,
            bufsize=DEFAULT_BUFSIZE,
            msgmode=settings.serial_settings.msgmode,
        )

        raw_data = None
        parsed_data = None
        lastread = datetime.now()
        readevent = settings.read_event
        while not stopevent.is_set():
            try:
                if settings.mode in (CONNECTED, CONNECTED_SOCKET) or (
                    settings.mode == CONNECTED_FILE
                    and datetime.now() > lastread + timedelta(seconds=FILEREAD_INTERVAL)
                ):
                    raw_data, parsed_data = ubr.read()
                    if raw_data is not None:
                        settings.inqueue.put((raw_data, parsed_data))
                        self.__master.event_generate(readevent)
                        if sockserve_event.is_set():
                            settings.socketqueue.put(raw_data)
                    else:
                        if settings.mode == CONNECTED_FILE:
                            raise EOFError
                    if settings.mode == CONNECTED_FILE:
                        lastread = datetime.now()

                    # write any queued output data to serial stream
                    if settings.mode == CONNECTED:
                        try:
                            while not settings.outqueue.empty():
                                data = settings.outqueue.get(False)
                                if data is not None:
                                    serial_object.write(data)
                                settings.outqueue.task_done()
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
                settings.inqueue.put((raw_data, parsed_data))
                self.__master.event_generate(readevent)
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
