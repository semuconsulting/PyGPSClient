"""
stream_handler.py

StreamHandler class for PyGPSClient application.

This handles all the serial stream i/o. It uses the pyubx2.UBXReader
class to read and parse incoming data from the receiver. It places
this data on an input message queue and generates a <<read-event>>
which triggers the main App class to process the data.

It also reads any command and poll messages placed on an output
message queue and sends these to the receiver.

The StreamHandler class is used by two PyGPSClient 'caller' objects:

- SettingsFrame - i/o with the main GNSS receiver.
- SpartnLbandDialog - i/o with a SPARTN L-Band receiver when SPARTN Client active.

The caller object can implement a 'status_label = ()' method to
display any status messages output by StreamHandler.

Created on 16 Sep 2020

:author: semuadmin (Steve Smith)
:copyright: 2020 semuadmin
:license: BSD 3-Clause
"""

import logging
import ssl
from datetime import datetime, timedelta
from io import BufferedReader
from queue import Empty
from socket import (
    AF_INET,
    AF_INET6,
    SOCK_DGRAM,
    SOCK_STREAM,
    gaierror,
    getaddrinfo,
    socket,
)
from threading import Event, Thread
from time import sleep
from tkinter import Frame, Label, Tk

from certifi import where as findcacerts
from pygnssutils import (
    NMEA_PROTOCOL,
    QGC_PROTOCOL,
    RTCM3_PROTOCOL,
    SBF_PROTOCOL,
    UBX_PROTOCOL,
    GNSSError,
    GNSSReader,
)
from pynmeagps import NMEAMessageError, NMEAParseError, NMEAStreamError
from pyqgc import QGCMessageError, QGCParseError, QGCStreamError
from pyrtcm import RTCMMessageError, RTCMParseError, RTCMStreamError
from pysbf2 import SBFMessageError, SBFParseError, SBFStreamError
from pyubx2 import ERR_LOG, UBXMessageError, UBXParseError, UBXStreamError
from pyubxutils import UBXSimulator
from serial import Serial, SerialException, SerialTimeoutException

from pygpsclient.globals import (
    ASCII,
    BSR,
    CONNECTED,
    CONNECTED_FILE,
    CONNECTED_SIMULATOR,
    CONNECTED_SOCKET,
    DEFAULT_BUFSIZE,
    ERRCOL,
    TTY_PROTOCOL,
    UBXSIMULATOR,
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
        self.logger = logging.getLogger(__name__)

        self._stream_thread = None
        self._stopevent = Event()
        self._ttyevent = Event()

    def start(self, caller: Frame, settings: dict):
        """
        Start the stream read thread.

        :param Frame caller: calling Frame
        :param dict settings: settings dictionary
        """

        self._stopevent.clear()
        self._stream_thread = Thread(
            target=self._read_thread,
            args=(
                self.__master,
                self._stopevent,
                settings,
                caller.status_label,  # for status update messages
            ),
            daemon=True,
        )
        self._stream_thread.start()

    def stop(self):
        """
        Stop serial reader thread.
        """

        self._stopevent.set()
        self._stream_thread = None

    def _read_thread(
        self,
        master: Tk,
        stopevent: Event,
        settings: dict,
        status: Label,
    ):
        """
        THREADED PROCESS
        Connects to selected data stream and starts read loop.

        :param caller owner: calling object
        :param Event stopevent: thread stop event
        :param dict settings: settings dictionary
        """

        conntype = settings["conntype"]
        inactivity_timeout = settings.get("inactivity_timeout", 0)
        if conntype == CONNECTED:
            if settings["serial_settings"].port == UBXSIMULATOR:
                conntype = CONNECTED_SIMULATOR
        ttydelay = (
            self.__app.configuration.get("ttydelay_b")
            * self.__app.configuration.get("guiupdateinterval_f")
            / 2
        )

        try:
            if conntype == CONNECTED:
                ser = settings["serial_settings"]
                if settings["protocol"] & TTY_PROTOCOL:
                    timeout = 3
                else:
                    timeout = ser.timeout
                with Serial(
                    ser.port,
                    ser.bpsrate,
                    bytesize=ser.databits,
                    stopbits=ser.stopbits,
                    parity=ser.parity,
                    xonxoff=ser.xonxoff,
                    rtscts=ser.rtscts,
                    timeout=timeout,
                ) as stream:
                    if settings["protocol"] & TTY_PROTOCOL:
                        self._readlooptty(
                            master,
                            stopevent,
                            stream,
                            settings,
                            ttydelay,
                        )
                    else:
                        self._readloop(
                            master,
                            stopevent,
                            stream,
                            settings,
                            inactivity_timeout,
                        )

            elif conntype == CONNECTED_FILE:
                in_filepath = settings["in_filepath"]
                with open(in_filepath, "rb") as stream:
                    self._readloop(
                        master,
                        stopevent,
                        stream,
                        settings,
                        inactivity_timeout,
                    )

            elif conntype == CONNECTED_SOCKET:
                soc = settings["socket_settings"]
                server = soc.server.get()
                port = int(soc.port.get())
                https = int(soc.https.get())
                selfsign = int(soc.selfsign.get())
                if soc.protocol.get()[-4:] == "IPv6":
                    afam = AF_INET6
                    conn = getaddrinfo(server, port)[1][4]
                else:  # IPv4
                    afam = AF_INET
                    conn = (server, port)
                if soc.protocol.get()[:3] == "UDP":
                    socktype = SOCK_DGRAM
                else:  # TCP
                    socktype = SOCK_STREAM
                with socket(afam, socktype) as stream:
                    if https:
                        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
                        context.load_verify_locations(findcacerts())
                        if selfsign:
                            crt = settings.get("tlscrtpath")
                            # context.verify_mode = ssl.CERT_NONE
                            context.load_verify_locations(crt)
                            context.check_hostname = False
                        stream = context.wrap_socket(stream, server_hostname=server)
                    stream.connect(conn)
                    if socktype == SOCK_DGRAM:
                        stream.send(b"")  # send empty datagram to establish connection
                    self._readloop(
                        master,
                        stopevent,
                        stream,
                        settings,
                        inactivity_timeout,
                    )

            elif conntype == CONNECTED_SIMULATOR:
                with UBXSimulator() as stream:
                    if settings["protocol"] & TTY_PROTOCOL:
                        self._readlooptty(
                            master,
                            stopevent,
                            stream,
                            settings,
                            ttydelay,
                        )
                    else:
                        self._readloop(
                            master,
                            stopevent,
                            stream,
                            settings,
                            inactivity_timeout,
                        )

        except EOFError:
            stopevent.set()
            master.event_generate(settings["eof_event"])
        except TimeoutError:
            stopevent.set()
            master.event_generate(settings["timeout_event"])
        except (
            IOError,
            FileNotFoundError,
            SerialException,
            SerialTimeoutException,
            OSError,
            AttributeError,
            gaierror,
        ) as err:
            if not stopevent.is_set():
                fnam = (
                    settings.get("tlscrtpath")
                    if isinstance(err, FileNotFoundError)
                    else ""
                )
                stopevent.set()
                master.event_generate(settings["error_event"])
                # use after(0) to avoid tkinter main thread contention
                status.after(0, status.config, {"text": f"{err} {fnam}", "fg": ERRCOL})

    def _readloop(
        self,
        master: Tk,
        stopevent: Event,
        stream: Serial | BufferedReader | socket,
        settings: dict,
        inactivity: int,
    ):
        """
        THREADED PROCESS
        Read stream continously until stop event or stream error.

        File streams use a small delay between reads to
        prevent thrashing.

        :param Event stopevent: thread stop event
        :param Serial | BufferedReader stream: serial data stream
        :param dict settings: settings dictionary
        :param int inactivity: inactivity timeout (s)
        """

        def _errorhandler(err: Exception):
            """
            Stream error handler.

            :param Exception err: error
            """

            parsed_data = f"Error parsing data stream {err}"
            settings["inqueue"].put((raw_data, parsed_data))
            master.event_generate(settings["read_event"])

        conntype = settings["conntype"]

        ubr = GNSSReader(
            stream,
            protfilter=NMEA_PROTOCOL
            | UBX_PROTOCOL
            | SBF_PROTOCOL
            | QGC_PROTOCOL
            | RTCM3_PROTOCOL,
            quitonerror=ERR_LOG,
            bufsize=DEFAULT_BUFSIZE,
            msgmode=settings["msgmode"],
            errorhandler=_errorhandler,
        )

        raw_data = None
        parsed_data = None
        lastread = datetime.now()
        lastevent = datetime.now()
        while not stopevent.is_set():
            try:
                if conntype in (CONNECTED, CONNECTED_SOCKET) or (
                    conntype == CONNECTED_FILE
                    and datetime.now()
                    > lastread
                    + timedelta(
                        milliseconds=self.__app.configuration.get("filedelay_n")
                    )
                ):
                    raw_data, parsed_data = ubr.read()
                    if raw_data is not None:
                        settings["inqueue"].put((raw_data, parsed_data))
                        master.event_generate(settings["read_event"])
                        lastevent = datetime.now()
                    else:  # timeout or eof
                        if conntype == CONNECTED_FILE:
                            raise EOFError
                        if inactivity and datetime.now() > lastevent + timedelta(
                            seconds=inactivity
                        ):
                            raise TimeoutError
                    if conntype == CONNECTED_FILE:
                        lastread = datetime.now()

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
                UBXStreamError,
                NMEAMessageError,
                NMEAParseError,
                NMEAStreamError,
                RTCMMessageError,
                RTCMParseError,
                RTCMStreamError,
                SBFMessageError,
                SBFParseError,
                SBFStreamError,
                QGCMessageError,
                QGCParseError,
                QGCStreamError,
                GNSSError,
            ) as err:
                _errorhandler(err)
                continue

            # allow for any tkinter events e.g. dialogs
            self.__app.update_idletasks()

    def _readlooptty(
        self,
        master: Tk,
        stopevent: Event,
        stream: Serial,
        settings: dict,
        delay: float = 0.0,
    ):
        """
        THREADED PROCESS
        TTY (ASCII) Read stream continously until stop event or stream error.

        :param Event stopevent: thread stop event
        :param Serial stream: serial data stream
        :param dict settings: settings dictionary
        :param float delay: delay between commands (secs)
        """

        def _errorhandler(err: Exception):
            """
            Stream error handler.

            :param Exception err: error
            """

            parsed_data = f"Error parsing data stream {err}"
            settings["inqueue"].put((raw_data, parsed_data))
            master.event_generate(settings["read_event"])

        raw_data = None
        while not stopevent.is_set():

            try:

                # write any queued output command to serial stream
                try:
                    # while not settings["outqueue"].empty():
                    cmd = settings["outqueue"].get(False)
                    if cmd is not None:
                        stream.write(cmd)
                    settings["outqueue"].task_done()
                except Empty:
                    pass

                if delay:
                    sleep(delay)

                # read ascii input from serial stream
                raw_data = b""
                while stream.in_waiting > 0:
                    raw_data += stream.read(1)

                # place ascii data on input queue
                if raw_data != b"":
                    settings["inqueue"].put(
                        (raw_data, raw_data.decode(ASCII, errors=BSR))
                    )
                    master.event_generate(settings["read_event"])

            except (ValueError, SerialException) as err:
                _errorhandler(err)
                continue
