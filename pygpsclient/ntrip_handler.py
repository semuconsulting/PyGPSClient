"""
NTRIP Handler class for PyGPSClient application

This handles all the NTRIP Server HTTP I/O and configuration and holds
the current state of the connection.

Originally inspired by these projects:
https://github.com/liukai-tech/NtripClient-Tools
https://github.com/jakepoz/deweeder/blob/main/src/ntrip.py

Created on 03 Apr 2022

:author: semuadmin
:copyright: SEMU Consulting © 2022
:license: BSD 3-Clause
"""
# pylint: disable=invalid-name

import logging
from threading import Thread
import socket
from datetime import datetime, timedelta
from base64 import b64encode
from pygpsclient import version as VERSION
from pyrtcm import RTCMReader, RTCMParseError, RTCMMessageError, RTCMTypeError
from pynmeagps import NMEAMessage, GET
from pyubx2.ubxtypes_core import RTCM3_PROTOCOL, NMEA_PROTOCOL

HDRBUFLEN = 4096
DATBUFLEN = 1024
LOGGING = logging.WARNING
TIMEOUT = 10
USERAGENT = f"PyGPSClient NTRIP Client/{VERSION}"
NTRIP_HEADERS = {
    "Ntrip-Version": "Ntrip/2.0",
    "User-Agent": USERAGENT,
}


class NTRIPHandler:
    """
    NTRIP handler class.
    """

    def __init__(self, app):
        """
        Constructor.

        :param Frame app: reference to main tkinter application

        """

        logging.basicConfig(
            format="%(asctime)-15s [%(levelname)s] %(funcName)s: %(message)s",
            level=LOGGING,
        )

        self.__app = app  # Reference to main application class
        self.__master = self.__app.get_master()  # Reference to root class (Tk)

        self._socket = None  # in THREAD
        self._connected = False
        self._reading = False
        self._ntrip_thread = None
        self._gga_interval = 0
        self._last_gga = datetime.now()
        self._buffer = bytearray()
        self._settings = {
            "server": "NTRIPcasterURL",
            "port": "2101",
            "mountpoint": "",
            "version": "2.0",
            "user": "anon",
            "password": "password",
            "ggainterval": "None",
            "sourcetable": [],
        }

    def __del__(self):
        """
        Destructor.
        """

    def connect(self) -> bool:
        """
        Open NTRIP server connection.
        """

        self._connected = True
        if self._connected:
            self.start_read_thread()

    def disconnect(self) -> bool:
        """
        Close NTRIP server connection.
        """

        self.stop_read_thread()
        self._connected = False

    @property
    def connected(self):
        """
        Connection status getter.
        """

        return self._connected

    @property
    def settings(self):
        """
        Getter for NTRIP settings.
        """

        return self._settings

    @settings.setter
    def settings(self, settings):
        """
        Setter for NTRIP settings.
        """

        self._settings = settings
        if settings["ggainterval"] == "None":
            self._gga_interval = 0
        else:
            self._gga_interval = int(settings["ggainterval"])

    def stop_read_thread(self):
        """
        Stop NTRIP reader thread.
        """

        if self._ntrip_thread is not None:
            self._reading = False
            self._ntrip_thread = None
            self.__app.dlg_ntripconfig.set_controls(False)

    def _read_thread(self):
        """
        THREADED
        Opens socket to NTRIP server and reads incoming data.
        """

        server = self._settings["server"]
        port = int(self._settings["port"])
        mountpoint = self._settings["mountpoint"]
        try:
            with socket.socket() as self._socket:
                self._socket.connect((server, port))
                self._socket.settimeout(TIMEOUT)
                self._socket.sendall(self._formatGET())
                self.__app.dlg_ntripconfig.set_controls(True)
                # send GGA sentence with request
                if self._gga_interval and mountpoint != "":
                    self._send_GGA()
                while self._reading:
                    rc = self._do_header(self._socket)
                    if rc == "0":
                        self._do_data(self._socket)
                    elif rc == "1":
                        self._reading = False
                        self._connected = False
                        self.__app.dlg_ntripconfig.set_controls(False)
                    else:  # error message
                        self._reading = False
                        self._connected = False
                        self.__app.dlg_ntripconfig.set_controls(
                            False, (f"Error!: {rc}", "red")
                        )
        except socket.gaierror as err:
            self._reading = False
            self._connected = False
            print(f"Connection error {server}:{port} {err}")
            self.__app.dlg_ntripconfig.set_controls(
                False, (f"Connection error {err}", "red")
            )

    def _formatGET(self) -> str:
        """
        THREADED
        Format HTTP GET Request.

        :return: formatted HTTP GET request
        :rtype: str
        """

        mountpoint = self._settings["mountpoint"]
        ver = self._settings["version"]
        if mountpoint != "":
            mountpoint = "/" + mountpoint  # sourcetable request
        user = self._settings["user"]
        password = self._settings["password"]
        user = user + ":" + password
        user = b64encode(user.encode(encoding="utf-8"))
        req = (
            f"GET {mountpoint} HTTP/1.1\r\n"
            + f"User-Agent: {USERAGENT}\r\n"
            + f"Authorization: Basic {user.decode(encoding='utf-8')}\r\n"
            + f"Ntrip-Version: Ntrip/{ver}\r\n"
        )
        req += "\r\n"  # NECESSARY!!!
        return req.encode(encoding="utf-8")

    def _formatGGA(self) -> tuple:
        """
        THREADED
        Format NMEA GGA sentence using pynmeagps. The raw string
        output is suitable for sending to an NTRIP socket.

        :return: tuple of (raw NMEA message as string, NMEAMessage)
        :rtype: tuple
        """
        # time will default to now
        status = self.__app.GNSS_status
        lat = status["lat"]
        lon = status["lon"]
        fix = status["fix"]
        if fix == 3:
            fix = 1

        parsed_data = NMEAMessage(
            "GP",
            "GGA",
            GET,
            lat=lat,
            NS="N" if lat > 0 else "S",
            lon=lon,
            EW="E" if lon > 0 else "W",
            quality=fix,
            numSV=status["sip"],
            HDOP=status["hdop"],
            alt=status["alt"],
            altUnit="M",
            sep=status["sep"],
            sepUnit="M",
            diffAge=status["diffAge"],
            diffStation=status["diffStation"],
        )

        raw_data = parsed_data.serialize()
        return raw_data, parsed_data

    def _send_GGA(self):
        """
        THREADED
        Send NMEA GGA sentence to NTRIP server at prescribed interval.
        """

        if datetime.now() > self._last_gga + timedelta(seconds=self._gga_interval):
            raw, parsed = self._formatGGA()
            self._socket.sendall(raw)
            self._last_gga = datetime.now()
            # update console
            if NMEA_PROTOCOL & self.__app.frm_settings.protocol:
                self.__app.frm_console.update_console(raw, "NTRIP<<" + str(parsed))

    def _do_header(self, sock) -> str:
        """
        THREADED
        Parse response header lines.

        :param socket sock: socket
        :return: return status or error message
        :rtype: str
        """

        stable = []
        data = "Initial Header"
        while data:
            try:

                data = sock.recv(HDRBUFLEN)
                header_lines = data.decode(encoding="utf-8").split("\r\n")
                for line in header_lines:
                    # if sourcetable request, populate list
                    if line.find("STR;") >= 0:  # sourcetable entry
                        strbits = line.split(";")
                        if strbits[0] == "STR":
                            strbits.pop(0)
                            stable.append(strbits)
                    elif line.find("ENDSOURCETABLE") >= 0:  # end of sourcetable
                        self._settings["sourcetable"] = stable
                        return "1"
                    elif (
                        line.find("401 Unauthorized") >= 0
                        or line.find("403 Forbidden") >= 0
                        or line.find("404 Not Found") >= 0
                    ):
                        return line
                    elif line == "":
                        break

            except UnicodeDecodeError:
                data = False

        return "0"

    def _do_data(self, sock):
        """
        THREADED
        Read NTRIP server socket and generate virtual <<ntrip_read>> event
        whenever data is received.

        :param socket sock: socket
        """

        data = "Initial data"
        while data and self._reading:
            data = sock.recv(DATBUFLEN)
            if len(data) > 0:
                self._buffer += data
                self.__master.event_generate("<<ntrip_read>>")

    def start_read_thread(self):
        """
        Start the NTRIP reader thread.
        """

        if self._connected:
            self._reading = True
            self._ntrip_thread = Thread(target=self._read_thread, daemon=True)
            self._ntrip_thread.start()

    def on_read(self, event):  # pylint: disable=unused-argument
        """
        Action on <<ntrip_read>> event - read any data in the buffer.

        :param event event: read event
        """

        try:

            self._buffer = self._read_buffer(self._buffer)

        except (RTCMParseError, RTCMMessageError, RTCMTypeError) as err:
            print(err)  # TODO refine exception reporting or simply ignore

    def _read_buffer(self, buf: bytearray) -> bytearray:
        """
        THREADED
        Parse the NTRIP buffer and yield any complete RTCM3
        messages. If we're connected to a GNSS device, the
        messages will be sent to this device.

        If the UBX RXM-RTCM message type has been enabled, you
        should see a UBX-RXM-RTCM response for each RTCM3
        message received:

        :param bytearray buf: input buffer
        :return: remaining buffer
        :rtype: bytearray
        """

        protfilter = self.__app.frm_settings.protocol
        while True:
            raw_data, buf = RTCMReader.parse_buffer(buf)

            if raw_data is not None:
                parsed_data = RTCMReader.parse(raw_data)
                # update console
                if RTCM3_PROTOCOL & protfilter:
                    self.__app.frm_console.update_console(
                        raw_data, "NTRIP>>" + str(parsed_data)
                    )
                if self.__app.serial_handler.connected:
                    self.__app.serial_handler.serial_write(raw_data)
                if self._gga_interval:
                    self._send_GGA()
            else:
                break

        return buf
