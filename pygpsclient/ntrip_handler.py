"""
NTRIP Handler class for PyGPSClient application

This handles all the NTRIP Server HTTP I/O and configuration and holds
the current state of the connection.

Created on 03 Apr 2022

:author: semuadmin
:copyright: SEMU Consulting © 2022
:license: BSD 3-Clause
"""
# pylint: disable=invalid-name

from threading import Thread, Event
from queue import Queue
import socket
from datetime import datetime, timedelta
from base64 import b64encode
from pyubx2 import UBXReader, RTCM3_PROTOCOL, ERR_IGNORE
from pyrtcm import (
    RTCMParseError,
    RTCMMessageError,
    RTCMTypeError,
)
from pynmeagps import NMEAMessage, GET
from pygpsclient import version as VERSION
from pygpsclient.globals import DEFAULT_BUFSIZE

TIMEOUT = 10
USERAGENT = f"PyGPSClient NTRIP Client/{VERSION}"
NTRIP_HEADERS = {
    "Ntrip-Version": "Ntrip/2.0",
    "User-Agent": USERAGENT,
}
FIXES = {
    "3D": 1,
    "2D": 2,
    "RTK FIXED": 4,
    "RTK FLOAT": 5,
    "RTK": 5,
    "DR": 6,
    "NO FIX": 0,
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

        self.__app = app  # Reference to main application class
        self.__master = self.__app.get_master()  # Reference to root class (Tk)

        self._socket = None  # in THREAD
        self._connected = False
        self._stopevent = Event()
        self._ntrip_thread = None
        self._gga_interval = 0
        self._last_gga = datetime.now()
        self._settings = {
            "server": "",
            "port": "2101",
            "mountpoint": "",
            "version": "2.0",
            "user": "anon",
            "password": "password",
            "ggainterval": "None",
            "sourcetable": [],
            "ggalat": "",
            "ggalon": "",
            "ggaalt": "",
            "ggasep": "",
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

    def start_read_thread(self):
        """
        Start the NTRIP reader thread.
        """

        if self._connected:
            self._stopevent.clear()
            self._ntrip_thread = Thread(
                target=self._read_thread,
                args=(
                    self._stopevent,
                    self.__app.ntripqueue,
                ),
                daemon=True,
            )
            self._ntrip_thread.start()

    def stop_read_thread(self):
        """
        Stop NTRIP reader thread.
        """

        if self._ntrip_thread is not None:
            self._set_controls(False)
            self._stopevent.set()
            self._ntrip_thread = None

    def _read_thread(self, stopevent: Event, ntripqueue: Queue):
        """
        THREADED
        Opens socket to NTRIP server and reads incoming data.

        :param Event stopevent: stop event
        :param Queue ntripqueue: NTRIP message queue
        """

        server = self._settings["server"]
        port = int(self._settings["port"])
        mountpoint = self._settings["mountpoint"]
        try:
            with socket.socket() as self._socket:
                self._socket.connect((server, port))
                self._socket.settimeout(TIMEOUT)
                self._socket.sendall(self._formatGET())
                self._set_controls(True)
                # send GGA sentence with request
                if self._gga_interval and mountpoint != "":
                    self._send_GGA()
                while not stopevent.is_set():
                    rc = self._do_header(self._socket, stopevent)
                    if rc == "0":
                        self._do_data(self._socket, stopevent, ntripqueue)
                    elif rc == "1":
                        stopevent.set()
                        self._connected = False
                        self._set_controls(False)
                    else:  # error message
                        stopevent.set()
                        self._connected = False
                        self._set_controls(False, (f"Error!: {rc}", "red"))
        except (socket.gaierror, ConnectionResetError, TimeoutError) as err:
            stopevent.set()
            self._connected = False
            self._set_controls(False, (f"Connection error {err}", "red"))

    def _set_controls(self, status: bool, msg: tuple = None):
        """Set controls on config panel if it is displayed."""

        if self.__app.dlg_ntripconfig is not None:
            self.__app.dlg_ntripconfig.set_controls(status, msg)

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

    def _do_header(self, sock: socket, stopevent: Event) -> str:
        """
        THREADED
        Parse response header lines.

        :param socket sock: socket
        :param Event stopevent: stop event
        :return: return status or error message
        :rtype: str
        """

        stable = []
        data = "Initial Header"
        while data and not stopevent.is_set():
            try:

                data = sock.recv(DEFAULT_BUFSIZE)
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
                        if self.__app.dlg_ntripconfig is not None:
                            self.__app.dlg_ntripconfig.find_mp_distance()
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

    def _do_data(self, sock: socket, stopevent: Event, ntripqueue: Queue):
        """
        THREADED
        Read NTRIP server socket and generate virtual <<ntrip_read>> event
        whenever data is received.

        :param socket sock: socket
        :param Event stopevent: stop event
        :param Queue ntripqueue: NTRIP message queue
        """

        # UBXreader will wrap socket as SocketStream
        rtr = UBXReader(
            sock,
            protfilter=RTCM3_PROTOCOL,
            quitonerror=ERR_IGNORE,
            bufsize=DEFAULT_BUFSIZE,
        )

        raw_data = None
        parsed_data = None
        while not stopevent.is_set():
            try:

                raw_data, parsed_data = rtr.read()
                if raw_data is not None:
                    ntripqueue.put((raw_data, parsed_data))
                    self.__master.event_generate("<<ntrip_read>>")
                if self._gga_interval:
                    self._send_GGA()

            except (
                RTCMMessageError,
                RTCMParseError,
                RTCMTypeError,
            ) as err:
                parsed_data = f"Error parsing data stream {err}"
                ntripqueue.put((raw_data, parsed_data))
                self.__master.event_generate("<<ntrip_read>>")
                continue

    def _formatGGA(self) -> tuple:
        """
        THREADED
        Format NMEA GGA sentence using pynmeagps. The raw string
        output is suitable for sending to an NTRIP socket.

        :return: tuple of (raw NMEA message as string, NMEAMessage)
        :rtype: tuple
        """
        # time will default to now

        # use live GNSS coordinates if available, else use
        # user-provided fixed GGA settings
        if self._settings["ggalat"] == "":  # live
            lat = self.__app.gnss_status.lat
            lon = self.__app.gnss_status.lon
            alt = self.__app.gnss_status.alt
            sep = self.__app.gnss_status.sep
            numSV = self.__app.gnss_status.sip
            hdop = self.__app.gnss_status.hdop
            diffstation = self.__app.gnss_status.diff_station
            diffage = self.__app.gnss_status.diff_age
            quality = FIXES.get(self.__app.gnss_status.fix, 0)
        else:  # user fixed
            lat = float(self._settings["ggalat"])
            lon = float(self._settings["ggalon"])
            alt = float(self._settings["ggaalt"])
            sep = float(self._settings["ggasep"])
            numSV = 15
            hdop = 0
            diffstation = 0
            diffage = ""
            quality = 1

        if type(lat) not in (int, float) or type(lon) not in (int, float):
            return None, None

        parsed_data = NMEAMessage(
            "GP",
            "GGA",
            GET,
            lat=lat,
            NS="N" if lat > 0 else "S",
            lon=lon,
            EW="E" if lon > 0 else "W",
            quality=quality,
            numSV=numSV,
            HDOP=hdop,
            alt=alt,
            altUnit="M",
            sep=sep,
            sepUnit="M",
            diffAge=diffage,
            diffStation=diffstation,
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
            if parsed is not None:
                self._socket.sendall(raw)
                self._last_gga = datetime.now()
                self.__app.process_data(raw, parsed, "NTRIP<<")
