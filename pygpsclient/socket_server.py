"""
TCP socket server for PyGPSClient application.

Reads raw data from GNSS receiver message queue and
outputs this to multiple TCP socket clients.

Created on 16 May 2022

:author: semuadmin
:copyright: SEMU Consulting © 2022
:license: BSD 3-Clause
"""

from socketserver import ThreadingTCPServer, StreamRequestHandler
from threading import Thread, Event
from queue import Queue


class SocketServer(ThreadingTCPServer):
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
        """

        if self._allowed:
            while True:
                try:
                    raw = self._msgqueue.get()
                    if raw is not None:
                        self.wfile.write(raw)
                        self.wfile.flush()
                except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError):
                    break
