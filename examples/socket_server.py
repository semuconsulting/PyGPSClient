"""
FOR TESTING ONLY

Threaded GNSS TCP socket server.

Reads serial stream from GNSS receiver and outputs
raw binary data to multiple TCP socket clients.

Created on 26 Apr 2022

:author: semuadmin
:copyright: SEMU Consulting © 2022
:license: BSD 3-Clause
"""

from io import BufferedReader
from queue import Queue
from socketserver import StreamRequestHandler, ThreadingTCPServer
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

from pygpsclient.globals import DEFAULT_BUFSIZE


class SockServer(ThreadingTCPServer):
    """
    Socket server class.
    """

    def __init__(self, maxclients: int, msgqueue: Queue, *args, **kwargs):
        """
        Constructor.

        :param int maxclients: max no of clients allowed
        :param Queue msgqueue: queue containing raw GNSS messages
        """

        self.maxclients = maxclients
        self._gnss_inqueue = msgqueue
        self.connections = 0
        self._stopevent = Event()
        self.clientqueues = []
        # set up pool of client queues
        for _ in range(self.maxclients):
            self.clientqueues.append({"client": None, "queue": Queue()})
        super().__init__(*args, **kwargs)

        # start GNSS message reader
        while not self._gnss_inqueue.empty():  # flush queue
            self._gnss_inqueue.get()
        self._stopevent.clear()
        self._stream_thread = Thread(
            target=self._read_thread,
            args=(self._stopevent, self._gnss_inqueue, self.clientqueues),
            daemon=True,
        )
        self._stream_thread.start()

    def _read_thread(self, stopevent: Event, msgqueue: Queue, clientqueues: dict):
        """
        Read from main GNSS message queue and place
        raw data on array of socket client queues.

        :param Event stopevent: stop event
        :param Queue msgqueue: message queue
        :param Dict clientqueues: pool of queues for used by clients
        """

        while not stopevent.is_set():
            raw, _ = msgqueue.get()
            for i in range(self.maxclients):
                clientqueues[i]["queue"].put(raw)


class ClientHandler(StreamRequestHandler):
    """
    Threaded TCP client connection handler class.
    """

    def __init__(self, *args, **kwargs):
        """
        Constructor.
        """

        self._qidx = None
        self._gnss_inqueue = None
        self._allowed = False
        super().__init__(*args, **kwargs)

    def setup(self, *args, **kwargs):
        """
        Overidden client handler setup routine.
        """

        # find next unused client queue in pool...
        for i, clq in enumerate(self.server.clientqueues):
            if clq["client"] is None:
                self.server.clientqueues[i]["client"] = self.client_address[1]
                self._gnss_inqueue = clq["queue"]
                while not self._gnss_inqueue.empty():  # flush queue
                    self._gnss_inqueue.get()
                self._qidx = i
                self._allowed = True
                break
        if self._qidx is None:  # no available client queues in pool
            print(
                f"Connection rejected - maximum {self.server.maxclients} clients allowed"
            )
            return

        if self._allowed:
            self.server.connections += 1
            print(
                f"Client connected {self.client_address[0]}:{self.client_address[1]}",
                f"; number of clients: {self.server.connections}",
            )
            super().setup(*args, **kwargs)

    def finish(self, *args, **kwargs):
        """
        Overidden client handler finish routine.
        """

        if self._qidx is not None:
            self.server.clientqueues[self._qidx]["client"] = None

        if self._allowed:
            self.server.connections -= 1
            print(
                f"Client disconnected {self.client_address[0]}:{self.client_address[1]}",
                f"; number of clients: {self.server.connections}",
            )
            super().finish(*args, **kwargs)

    def handle(self):
        """
        Overridden main client handler.
        """

        while self._allowed:
            try:
                raw = self._gnss_inqueue.get()
                if raw is not None:
                    self.wfile.write(raw)
                    self.wfile.flush()
            except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError):
                break


class StreamHandler:
    """
    Stream handler class.
    """

    def __init__(self, serport, baud, timeout):
        """
        Constructor.
        """

        self._serport = serport
        self._baud = baud
        self._timeout = timeout
        self._serial_object = None
        self._serial_buffer = None
        self._stream_thread = None
        self._socket = None
        self._gnss_inqueue = Queue()
        self._stopevent = Event()
        self._maxclients = 10

    @property
    def msgqueue(self) -> Queue:
        """
        Getter for main message queue.

        :return: message queue
        :rtype: Queue
        """

        return self._gnss_inqueue

    def start_read_thread(self):
        """
        Start the stream read thread.
        """

        self._stopevent.clear()
        self._stream_thread = Thread(
            target=self._read_thread,
            args=(self._stopevent, self.msgqueue),
            daemon=True,
        )
        self._stream_thread.start()

    def stop_read_thread(self):
        """
        Stop serial reader thread.
        """

        self._stopevent.set()
        self._stream_thread = None

    def _read_thread(self, stopevent: Event, msgqueue: Queue):
        """
        THREADED PROCESS

        Connects to selected data stream and starts read loop.

        :param Event stopevent: thread stop event
        :param Queue msgqueue: message queue
        """

        try:
            with Serial(
                self._serport, self._baud, timeout=self._timeout
            ) as self._serial_object:
                stream = BufferedReader(self._serial_object)
                self._readloop(stopevent, msgqueue, stream)

        except (SerialException, SerialTimeoutException) as err:
            print(err)

    def _readloop(self, stopevent: Event, msgqueue: Queue, stream: object):
        """
        Read stream continously until stop event or stream error.

        :param Event stopevent: thread stop event
        :param Queue msgqueue: message queue
        :param object stream: data stream
        """
        # pylint: disable=no-self-use

        ubr = UBXReader(
            stream,
            protfilter=NMEA_PROTOCOL | UBX_PROTOCOL | RTCM3_PROTOCOL,
            quitonerror=ERR_IGNORE,
            bufsize=DEFAULT_BUFSIZE,
        )

        raw_data = None
        parsed_data = None
        while not stopevent.is_set():
            try:
                raw_data, parsed_data = ubr.read()
                if raw_data is not None:
                    # print(parsed_data)
                    msgqueue.put((raw_data, parsed_data))
            except (
                UBXMessageError,
                UBXParseError,
                NMEAMessageError,
                NMEAParseError,
                RTCMMessageError,
                RTCMParseError,
            ) as err:
                print(err)
                continue


if __name__ == "__main__":
    SERIAL = "/dev/tty.usbmodem14101"
    BAUD = 9600
    TIMEOUT = 0.1
    HOST = "localhost"
    PORT = 50007
    MAXCLIENTS = 5

    print(f"Creating Serial streamer on {SERIAL}@{BAUD}")
    streamer = StreamHandler(SERIAL, BAUD, TIMEOUT)
    print(f"Creating Socket server on {HOST}:{PORT}")
    server = SockServer(MAXCLIENTS, streamer.msgqueue, (HOST, PORT), ClientHandler)

    try:
        print("starting serial read thread...")
        streamer.start_read_thread()
        print("Starting TCP server, waiting for client connections...")
        server.serve_forever()
    except KeyboardInterrupt:
        streamer.stop_read_thread()
        print("Socket server terminated by user")
