"""
TCP socket server for PyGPSClient application.

(could also be used independently of a tkinter app framework)

Reads raw data from GNSS receiver message queue and
outputs this to multiple TCP socket clients.

Operates in two modes according to ntripmode setting:

0 - open socket mode - will stream GNSS data to any connected client
    without authentication.
1 - NTRIP server mode - implements NTRIP server protocol and will
    respond to NTRIP client authentication, sourcetable and RTCM3 data
    stream requests.
    NB: THIS ASSUMES THE CONNECTED GNSS RECEIVER IS OPERATING IN BASE
    STATION (SURVEY-IN OR FIXED) MODE AND OUTPUTTING THE RELEVANT RTCM3 MESSAGES.

For NTRIP mode, set authorization credentials via env variables:
export PYGPSCLIENT_USER="user"
export PYGPSCLIENT_PASSWORD="password"

Created on 16 May 2022

:author: semuadmin
:copyright: SEMU Consulting © 2022
:license: BSD 3-Clause
"""

from os import getenv
from socketserver import ThreadingTCPServer, StreamRequestHandler
from threading import Thread, Event
from queue import Queue
from base64 import b64encode
from datetime import datetime, timezone
from pygpsclient import version as PYGPSVERSION

RTCM = b"rtcm"
BUFSIZE = 1024
PYGPSMP = "pygpsclient"


class SocketServer(ThreadingTCPServer):
    """
    Socket server class.

    This instantiates a daemon ClientHandler thread for each
    connected client.
    """

    def __init__(
        self, app, ntripmode: int, maxclients: int, msgqueue: Queue, *args, **kwargs
    ):
        """
        Overridden constructor.

        :param Frame app: reference to main application class (if any)
        :param int ntripmode: 0 = open socket server, 1 = NTRIP server
        :param int maxclients: max no of clients allowed
        :param Queue msgqueue: queue containing raw GNSS messages
        """

        self.__app = app  # Reference to main application class

        self._ntripmode = ntripmode
        self._maxclients = maxclients
        self._msgqueue = msgqueue
        self._connections = 0
        self._stream_thread = None
        self._stopmqread = Event()
        # set up pool of client queues
        self.clientqueues = []
        for _ in range(self._maxclients):
            self.clientqueues.append({"client": None, "queue": Queue()})
        self._start_read_thread()
        self.daemon_threads = True  # stops deadlock on abrupt termination

        super().__init__(*args, **kwargs)

    def server_close(self):
        """
        Overridden server close routine.
        """

        self.stop_read_thread()
        super().server_close()

    def _start_read_thread(self):
        """
        Start GNSS message reader thread.
        """

        while not self._msgqueue.empty():  # flush queue
            self._msgqueue.get()

        self._stopmqread.clear()
        self._stream_thread = Thread(
            target=self._read_thread,
            args=(self._stopmqread, self._msgqueue, self.clientqueues),
            daemon=True,
        )
        self._stream_thread.start()

    def stop_read_thread(self):
        """
        Stop GNSS message reader thread.
        """

        self._stopmqread.set()

    def _read_thread(self, stopmqread: Event, msgqueue: Queue, clientqueues: dict):
        """
        THREADED
        Read from main GNSS message queue and place
        raw data on an output queue for each connected client.

        :param Event stopmqread: stop event for mq read thread
        :param Queue msgqueue: input message queue
        :param Dict clientqueues: pool of output queues for use by clients
        """

        while not stopmqread.is_set():
            raw = msgqueue.get()
            for i in range(self._maxclients):
                # if client connected to this queue
                if clientqueues[i]["client"] is not None:
                    clientqueues[i]["queue"].put(raw)

    @property
    def credentials(self) -> bytes:
        """
        Getter for basic authorization credentials.

        Assumes credentials have been defined in
        environment variables PYGPSCLIENT_USER and
        PYGPSCLIENT_PASSWORD
        """

        user = getenv("PYGPSCLIENT_USER")
        password = getenv("PYGPSCLIENT_PASSWORD")
        if user is None or password is None:
            return None
        user = user + ":" + password
        return b64encode(user.encode(encoding="utf-8"))

    @property
    def connections(self):
        """
        Getter for client connections.
        """

        return self._connections

    @connections.setter
    def connections(self, clients: int):
        """
        Setter for client connections.
        Also updates no. of clients on settings panel.

        :param int clients: no of client connections
        """

        self._connections = clients
        if hasattr(self.__app, "update_clients"):
            self.__app.update_clients(self._connections)

    @property
    def ntripmode(self) -> int:
        """
        Getter for ntrip mode.

        :return: 0 = open socket server, 1 = ntrip mode
        :rtype: int
        """

        return self._ntripmode

    @property
    def latlon(self) -> tuple:
        """
        Get current lat / lon from receiver.

        :return=: tuple of (lat, lon)
        :rtype: tuple
        """

        if hasattr(self.__app, "gnss_status"):
            return (self.__app.gnss_status.lat, self.__app.gnss_status.lon)
        else:
            return ("", "")


class ClientHandler(StreamRequestHandler):
    """
    Threaded TCP client connection handler class.
    """

    def __init__(self, *args, **kwargs):
        """
        Overridden constructor.
        """

        self._qidx = None
        self._msgqueue = None
        self._allowed = False

        super().__init__(*args, **kwargs)

    def setup(self, *args, **kwargs):
        """
        Overridden client handler setup routine.
        Allocates available message queue to client.
        """

        # find next unused client queue in pool...
        for i, clq in enumerate(self.server.clientqueues):
            if clq["client"] is None:
                self.server.clientqueues[i]["client"] = self.client_address[1]
                self._msgqueue = clq["queue"]
                while not self._msgqueue.empty():  # flush queue
                    self._msgqueue.get()
                self._qidx = i
                self._allowed = True
                break
        if self._qidx is None:  # no available client queues in pool
            return

        if self._allowed:
            self.server.connections = self.server.connections + 1
            super().setup(*args, **kwargs)

    def finish(self, *args, **kwargs):
        """
        Overridden client handler finish routine.
        De-allocates message queue from client.
        """

        if self._qidx is not None:
            self.server.clientqueues[self._qidx]["client"] = None

        if self._allowed:
            self.server.connections = self.server.connections - 1
            super().finish(*args, **kwargs)

    def handle(self):
        """
        Overridden main client handler.

        If in NTRIP server mode, will respond to NTRIP client authentication
        and sourcetable requests and, if valid, stream relevant RTCM3 data
        from the input message queue to the socket.

        If in open socket server mode, will simply stream content of
        input message queue to the socket.
        """

        while self._allowed:  # if connection allowed, loop until terminated

            try:

                if self.server.ntripmode:  # NTRIP server mode

                    self.data = self.request.recv(BUFSIZE)
                    resp = self._process_ntrip_request(self.data)
                    if resp is None:
                        break
                    if resp == RTCM:  # start RTCM3 stream
                        while True:
                            self._write_from_mq()
                    else:  # sourcetable or error response
                        self.wfile.write(resp)
                        self.wfile.flush()

                else:  # open socket server mode

                    self._write_from_mq()

            except (
                ConnectionRefusedError,
                ConnectionAbortedError,
                ConnectionResetError,
                BrokenPipeError,
                TimeoutError,
            ):
                break

    def _process_ntrip_request(self, data: bytes) -> bytes:
        """
        Process NTRIP client request.

        :param bytes data: client request
        :return: client response
        :rtype: bytes or None if request rejected
        """

        strreq = False
        authorized = False
        validmp = False
        mountpoint = ""

        request = data.strip().split(b"\r\n")
        for part in request:
            if part[0:21] == b"Authorization: Basic ":
                authorized = part[21:] == self.server.credentials
            if part[0:3] == b"GET":
                get = part.split(b" ")
                mountpoint = get[1].decode("utf-8")
                if mountpoint == "":  # no mountpoint, hence sourcetable request
                    strreq = True
                elif mountpoint == f"/{PYGPSMP}":  # valid mountpoint
                    validmp = True

        if not authorized:  # respond with 401
            http = (
                self._format_http_header(401)
                + f'WWW-Authenticate: Basic realm="{mountpoint}"\r\n'
                + "Connection: close\r\n"
            )
            return bytes(http, "UTF-8")
        if strreq or (not strreq and not validmp):  # respond with nominal sourcetable
            http = self._format_sourcetable()
            return bytes(http, "UTF-8")
        if validmp:  # respond by opening RTCM3 stream
            return RTCM
        return None

    def _format_sourcetable(self) -> str:
        """
        Format nominal HTTP sourcetable response.

        :return: HTTP response string
        :rtype: str
        """

        lat, lon = self.server.latlon
        ipaddr, port = self.server.server_address
        # sourcetable based on ZED-F9P capabilities
        sourcetable = (
            f"STR;{PYGPSMP};PyGPSClient;RTCM 3.3;"
            + "1005(5),1077(1),1087(1),1097(1),1127(1),1230(1);"
            + f"0;GPS+GLO+GAL+BEI;SNIP;SRB;{lat};{lon};1;0;sNTRIP;none;N;N;0;\r\n"
        )
        sourcefooter = (
            f"NET;SNIP;PyGPSClient;N;N;PyGPSClient;{ipaddr}:{port};info@semuconsulting.com;;\r\n"
            + "ENDSOURCETABLE\r\n"
        )
        http = (
            self._format_http_header(200)
            + "Connection: close\r\n"
            + "Content-Type: gnss/sourcetable\r\n"
            + f"Content-Length: {len(sourcetable) + len(sourcefooter)}\r\n"
            + sourcetable
            + sourcefooter
        )
        return http

    def _format_http_header(self, code: int = 200) -> str:
        """
        Format HTTP NTRIP header.

        :param int code: HTTP response code (200)
        :return: HTTP NTRIP header
        :rtype: str
        """
        # pylint: disable=no-self-use

        codes = {200: "OK", 401: "Unauthorized", 403: "Forbidden", 404: "Not Found"}

        dat = datetime.now(timezone.utc)
        server_date = dat.strftime("%d %b %Y")
        http_date = dat.strftime("%a, %d %b %Y %H:%M:%S %Z")
        header = (
            f"HTTP/1.1 {code} {codes[code]}\r\n"
            + "Ntrip-Version: Ntrip/2.0\r\n"
            + "Ntrip-Flags: \r\n"
            + f"Server: PyGPSClient_NTRIP_Caster_{PYGPSVERSION}/of:{server_date}\r\n"
            + f"Date: {http_date}\r\n"
        )
        return header

    def _write_from_mq(self):
        """
        Get data from message queue and write to socket.
        """

        raw = self._msgqueue.get()
        if raw is not None:
            self.wfile.write(raw)
            self.wfile.flush()
