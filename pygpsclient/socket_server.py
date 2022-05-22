"""
TCP socket server for PyGPSClient application.

Reads raw data from GNSS receiver message queue and
outputs this to multiple TCP socket clients.

Operates in two modes according to ntripmode setting:

0 - open socket mode - will stream GNSS data to any connected client
    without authentication.
1 - NTRIP server mode - implements NTRIP server protocol and will
    respond to NTRIP client authentication, sourcetable and RTCM3 data
    stream requests.
    NB: THIS ASSUMES THE CONNECTED GNSS RECEIVER IS OPERATING IN BASE
    STATION (SURVEY-IN) MODE AND OUTPUTTING THE RELEVANT RTCM3 MESSAGES.

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

STRLIST = [
    "STR;thismp;thismp;RTCM 3.2;1005(5),1077(1),1087(1),1097(1),1127(1),1230(1);0;GPS+GLO+GAL;SNIP;SRB;51.45;-2.10;1;0;sNTRIP;none;N;N;0;",
    "STR;thatmp;thatmp;RTCM 3.2;1005(5),1075(1),1085(1),1095(1),1195(1),1230(1);0;GPS+GLO+GAL;SNIP;SRB;44.12;20.23;1;0;sNTRIP;none;N;N;0;",
]
STRTERM = (
    "NET;SNIP;PyGPSClient;N;N;PyGPSClient;0.0.0.0:2101;semuadmin@semuconsulting.com;;\r\n"
    + "ENDSOURCETABLE\r\n"
)


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

        :param Frame app: reference to main application class
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
        self._stopevent = Event()
        self.clientqueues = []
        # set up pool of client queues
        for _ in range(self._maxclients):
            self.clientqueues.append({"client": None, "queue": Queue()})
        self._start_read_thread()
        self.daemon_threads = True  # stops deadlock on abrupt termination

        super().__init__(*args, **kwargs)

    def _start_read_thread(self):
        """
        Start message reader thread.
        """

        while not self._msgqueue.empty():  # flush queue
            self._msgqueue.get()

        self._stopevent.clear()
        self._stream_thread = Thread(
            target=self._read_thread,
            args=(self._stopevent, self._msgqueue, self.clientqueues),
            daemon=True,
        )
        self._stream_thread.start()

    def stop_read_thread(self):
        """
        Stop message reader thread.
        """

        self._stopevent.set()

    def _read_thread(self, stopevent: Event, msgqueue: Queue, clientqueues: dict):
        """
        THREADED
        Read from main GNSS message queue and place
        raw data on array of socket client queues.

        :param Event stopevent: stop event
        :param Queue msgqueue: message queue
        :param Dict clientqueues: pool of queues for used by clients
        """

        while not stopevent.is_set():
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
        environment variables:
        PYGPSCLIENT_USER="user"
        PYGPSCLIENT_PASSWORD="password"
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
        self.__app.frm_settings.clients = self._connections

    @property
    def ntripmode(self) -> int:
        """
        Getter for ntrip mode.

        :return: 0 = open socket server, 1 = ntrip mode
        :rtype: int
        """

        return self._ntripmode


class ClientHandler(StreamRequestHandler):
    """
    Threaded TCP client connection handler class.
    """

    def __init__(self, *args, **kwargs):
        """
        Constructor.
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
        from the message queue to the socket.

        If in open socket server mode, will simply stream content of
        message queue to the socket.
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

        request = data.strip().split(b"\r\n")
        for part in request:
            if part[0:21] == b"Authorization: Basic ":
                authorized = part[21:] == self.server.credentials
            if part[0:3] == b"GET":
                get = part.split(b" ")
                if get[1] == b"":  # no mountpoint, hence sourcetable request
                    strreq = True
                elif get[1] in (b"/thismp", b"/thatmp"):  # valid mountpoint
                    validmp = True

        if not authorized:  # respond with 403
            http = (
                "HTTP/1.1 403 Forbidden\r\n"
                + f"Date: {self.http_date()}\r\n"
                + "Connection: close\r\n"
            )
            return bytes(http, "UTF-8")
        if strreq or (not strreq and not validmp):  # respond with sourcetable
            server_version = PYGPSVERSION
            server_date = datetime.now(timezone.utc).strftime("%d %b %Y")
            sourcetable = ""
            for line in STRLIST:
                sourcetable += line + "\r\n"
            http = (
                "HTTP/1.1 200 OK\r\n"
                + "Ntrip-Version: Ntrip/2.0\r\n"
                + "Ntrip-Flags: \r\n"
                + f"Server: PyGPSClient_NTRIP_Caster_{server_version}/of:{server_date}\r\n"
                + f"Date: {self.http_date()}\r\n"
                + "Connection: close\r\n"
                + "Content-Type: gnss/sourcetable\r\n"
                + f"Content-Length: {len(sourcetable)}\r\n"
                + sourcetable
                + STRTERM
            )
            return bytes(http, "UTF-8")
        if validmp:  # respond by opening RTCM3 stream
            return RTCM
        return None

    def _write_from_mq(self):
        """
        Get data from message queue and write to socket.
        """

        raw = self._msgqueue.get()
        if raw is not None:
            self.wfile.write(raw)
            self.wfile.flush()

    @staticmethod
    def http_date() -> bytes:
        """
        Get datestamp in HTTP header format.
        """

        return datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S %Z")
