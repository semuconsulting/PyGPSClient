"""
stream_handler.py

StreamHandler class for PyGPSClient application.

This handles all the serial stream i/o. It is invoked in two use cases,
signified by the 'caller' argument:

- i/o with the main GNSS receiver.
- i/o with a SPARTN L-Band receiver, when the SPARTN Client is active.

The caller object should implement a 'set_status()' method.

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
    FILEREAD_INTERVAL,
    GNSS_ERR_EVENT,
)


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

    def start_read_thread(self, caller: object, settings: dict):
        """
        Start the stream read thread.

        :param caller owner: calling object
        :param dict settings: settings dictionary
        """

        self._stopevent.clear()
        self._stream_thread = Thread(
            target=self._read_thread,
            args=(
                caller,
                self._stopevent,
                self._sockserve_event,
                settings,
            ),
            daemon=True,
        )
        self._stream_thread.start()

    def stop_read_thread(self):
        """
        Stop serial reader thread.
        """

        self._stopevent.set()
        self._stream_thread = None

    def _read_thread(
        self,
        caller,
        stopevent: Event,
        sockserve_event: Event,
        settings: dict,
    ):
        """
        THREADED PROCESS

        Connects to selected data stream and starts read loop.

        :param caller owner: calling object
        :param Event stopevent: thread stop event
        :param Event sockserve_event: socket serving event
        :param dict settings: settings dictionary
        """

        conntype = settings["conntype"]
        try:
            if conntype == CONNECTED:
                ser = settings["serial_settings"]
                with Serial(
                    ser.port,
                    ser.bpsrate,
                    bytesize=ser.databits,
                    stopbits=ser.stopbits,
                    parity=ser.parity,
                    xonxoff=ser.xonxoff,
                    rtscts=ser.rtscts,
                    timeout=ser.timeout,
                ) as stream:
                    self._readloop(
                        stopevent,
                        sockserve_event,
                        stream,
                        settings,
                    )

            elif conntype == CONNECTED_FILE:
                in_filepath = settings["in_filepath"]
                with open(in_filepath, "rb") as stream:
                    self._readloop(
                        stopevent,
                        sockserve_event,
                        stream,
                        settings,
                    )

            elif conntype == CONNECTED_SOCKET:
                soc = settings["socket_settings"]
                server = soc.server
                port = soc.port
                flowinfo = soc.flowinfo
                scopeid = soc.scopeid
                if soc.protocol[-4:] == "IPv6":
                    afam = socket.AF_INET6
                    conn = (server, port, flowinfo, scopeid)
                else:  # IPv4
                    afam = socket.AF_INET
                    conn = (server, port)
                if soc.protocol[:3] == "UDP":
                    socktype = socket.SOCK_DGRAM
                else:  # TCP
                    socktype = socket.SOCK_STREAM
                with socket.socket(afam, socktype) as stream:
                    stream.connect(conn)
                    self._readloop(
                        stopevent,
                        sockserve_event,
                        stream,
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
                self.__master.event_generate(settings["error_event"])
                if hasattr(caller, "set_status"):
                    caller.set_status(str(err), "red")

    def _readloop(
        self,
        stopevent: Event,
        sockserve_event: Event,
        stream: object,
        settings: dict,
    ):
        """
        Read stream continously until stop event or stream error.

        File streams use a small delay between reads to
        prevent thrashing.

        :param Event stopevent: thread stop event
        :param Event sockserve_event: socket serving event
        :param object stream: serial data stream
        :param dict settings: settings dictionary
        """

        conntype = settings["conntype"]
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
                if conntype in (CONNECTED, CONNECTED_SOCKET) or (
                    conntype == CONNECTED_FILE
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
                        if conntype == CONNECTED_FILE:
                            raise EOFError
                    if conntype == CONNECTED_FILE:
                        lastread = datetime.now()
                        self.__master.update_idletasks()

                    # write any queued output data to serial stream
                    if conntype in (CONNECTED, CONNECTED_SOCKET):
                        try:
                            while not settings["outqueue"].empty():
                                data = settings["outqueue"].get(False)
                                if data is not None:
                                    ubr.datastream.write(data)
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
