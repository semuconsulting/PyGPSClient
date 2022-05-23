"""
!!! FOR TESTING ONLY !!!

NTRIP server test harness. Simulates the
functions of an NTRIP server:
1) authenticates NTRIP client credentials.
2) returns nominal sourcetable.
3) returns simulated RTCM3 message stream.
4) DOESN'T currently do anything with client GGA messages.

May at some point form the basis of a functional
NTRIP server in PyGPSClient.

Set authorization credentials via env variables:
export PYGPSCLIENT_USER="user"
export PYGPSCLIENT_PASSWORD="password"

Created on 4 Feb 2022

:author: semuadmin
:copyright: SEMU Consulting © 2022
:license: BSD 3-Clause
"""
# pylint: disable=line-too-long

from os import getenv
from socketserver import ThreadingTCPServer, StreamRequestHandler
from datetime import datetime, timedelta, timezone
from queue import Queue

# from threading import Event, Thread
from base64 import b64encode
from pyrtcm import RTCMMessage

MAXCLIENTS = 5
BUFSIZE = 1024
HOST = "0.0.0.0"  # binds to all host IP addresses
PORT = 2101
SEND_INTERVAL = 1
RTCM = b"rtcm"

# actual RTK2GO response for reference...
# HTTP/1.1 200 OK\r\nNtrip-Version: Ntrip/2.0\r\nNtrip-Flags: \r\nServer: SubCarrier Systems Corp SNIP simpleNTRIP_Caster_[wPRO]R3.04.66/of:Feb 4 2022\r\nDate: Fri, 4 Feb 2022 15:42:10 UTC\r\nConnection: close\r\nContent-Type: gnss/sourcetable\r\nContent-Length: 83203\r\n\r\nSTR;A_CMS_01;Exeter;RTCM 3.2;1005(1),1074(1),1084(1),1094(1),1124(1),1230(5);0;GPS+GLO+GAL+BDS;SNIP;GBR;50.72;-3.44;1;0;sNTRIP;none;N;N;0;\r\nSTR;aamakinen;Evijarvi;RTCM 3.2;1005(1),1077(1),1084(1),1097(1),1127(1),1230(1);;GPS+GLO+GAL+BDS;SNIP;FIN;63.36;23.36;1;0;sNTRIP;none;N;N;7400;\r\n

STRLIST = [
    "STR;thismp;thismp;RTCM 3.2;1005(5),1077(1),1087(1),1097(1),1230(1);0;GPS+GLO+GAL;SNIP;SRB;51.45;-2.10;1;0;sNTRIP;none;N;N;0;",
    "STR;thatmp;thatmp;RTCM 3.2;1005(5),1075(1),1085(1),1095(1),1195(1),1230(1);0;GPS+GLO+GAL;SNIP;SRB;44.12;20.23;1;0;sNTRIP;none;N;N;0;",
]
STRTERM = (
    "NET;SNIP;PyGPSClient;N;N;PyGPSClient;0.0.0.0:2101;semuadmin@semuconsulting.com;;\r\n"
    + "ENDSOURCETABLE\r\n"
)


class NTRIPServer(ThreadingTCPServer):
    """
    Socket server class.

    This instantiates a daemon ClientHandler thread for each
    connected client.
    """

    def __init__(self, app, maxclients: int, msgqueue: Queue, *args, **kwargs):
        """
        Overridden constructor.

        :param Frame app: reference to main application class
        :param int maxclients: max no of clients allowed
        :param Queue msgqueue: queue containing raw GNSS messages
        """

        self.__app = app  # Reference to main application class

        self._maxclients = maxclients
        self._msgqueue = msgqueue

        # OTHER SOCKET STREAMER FUNCTIONALITY COMMENTED OUT FOR NOW
        # This would ultimately stream RTCM3 messages from a connected
        # u-blox receiver running in base station mode

        # self._connections = 0
        # self._stream_thread = None
        # self._stopevent = Event()
        # self.clientqueues = []

        # set up pool of client queues
        # for _ in range(self._maxclients):
        #     self.clientqueues.append({"client": None, "queue": Queue()})
        # self._start_read_thread()
        # self.daemon_threads = True  # stops deadlock on abrupt termination

        super().__init__(*args, **kwargs)

    # def _start_read_thread(self):
    #     """
    #     Start message reader thread.
    #     """

    #     while not self._msgqueue.empty():  # flush queue
    #         self._msgqueue.get()

    #     self._stopevent.clear()
    #     self._stream_thread = Thread(
    #         target=self._read_thread,
    #         args=(self._stopevent, self._msgqueue, self.clientqueues),
    #         daemon=True,
    #     )
    #     self._stream_thread.start()

    # def stop_read_thread(self):
    #     """
    #     Stop message reader thread.
    #     """

    #     self._stopevent.set()

    # def _read_thread(self, stopevent: Event, msgqueue: Queue, clientqueues: dict):
    #     """
    #     THREADED
    #     Read from main GNSS message queue and place
    #     raw data on array of socket client queues.

    #     :param Event stopevent: stop event
    #     :param Queue msgqueue: message queue
    #     :param Dict clientqueues: pool of queues for used by clients
    #     """

    #     while not stopevent.is_set():
    #         raw = msgqueue.get()
    #         for i in range(self._maxclients):
    #             # if client connected to this queue
    #             if clientqueues[i]["client"] is not None:
    #                 clientqueues[i]["queue"].put(raw)

    # @property
    # def connections(self) -> int:
    #     """
    #     Getter for client connections.
    #     """

    #     return self._connections

    # @connections.setter
    # def connections(self, clients: int):
    #     """
    #     Setter for client connections.
    #     Also updates no. of clients on settings panel.

    #     :param int clients: no of client connections
    #     """

    #     self._connections = clients
    #     self.__app.frm_settings.clients = self._connections

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

    @staticmethod
    def create_RTCM3_msg() -> RTCMMessage:
        """
        Create arbitrary RTCM3 message to simulate NTRIP stream.
        """
        # pylint: disable=invalid-name

        msg = RTCMMessage(
            payload=b">\xd0\x00\x03\x8aX\xd9I<\x87/4\x10\x9d\x07\xd6\xafH "
        )
        return msg.serialize()


class ClientHandler(StreamRequestHandler):
    """
    Threaded TCP client connection handler class.
    """

    def handle(self):
        """
        Handle client connection.
        """

        last_rtcm_send = datetime.now()
        print(f"Client connected: {self.client_address[0]}:{self.client_address[1]}")
        while True:
            try:
                self.data = self.request.recv(BUFSIZE)
                resp = self._process_request(self.data)
                if resp is None:
                    break
                if resp == RTCM:  # RTCM3 stream
                    # TODO STUB - in practice, get live RTCM from base station receiver
                    while True:
                        if datetime.now() > (
                            last_rtcm_send + timedelta(seconds=SEND_INTERVAL)
                        ):
                            msg = self.server.create_RTCM3_msg()
                            self.wfile.write(msg)
                            self.wfile.flush()
                            last_rtcm_send = datetime.now()
                else:  # sourcetable or error response
                    self.wfile.write(resp)
                    self.wfile.flush()
            except (
                ConnectionAbortedError,
                ConnectionResetError,
                BrokenPipeError,
                TimeoutError,
            ):
                print(
                    f"Client disconnected: {self.client_address[0]}:{self.client_address[1]}"
                )
                break

    def _process_request(self, data: bytes) -> bytes:
        """
        Process client request.
        """

        strreq = False
        authorized = False
        validmp = False

        request = data.strip().split(b"\r\n")
        print(f"Client {self.client_address[0]} sent {request}")
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
            server_version = "1.3.5"
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
        if validmp:  # respond with RTCM3 stream
            return RTCM
        return None

    @staticmethod
    def http_date() -> bytes:
        """
        Get datestamp in HTTP header format.
        """

        return datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S %Z")


if __name__ == "__main__":

    mq = Queue()
    print(f"Creating NTRIP server on {HOST}:{PORT}")
    server = NTRIPServer(None, MAXCLIENTS, mq, (HOST, PORT), ClientHandler)

    print("Starting NTRIP server, waiting for client connections...")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("NTRIP server terminated by user")
