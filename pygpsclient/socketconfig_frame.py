"""
Generic socket configuration Frame subclass
for use in tkinter applications which require a
socket configuration facility.

Exposes the socket settings as properties.

Application icons from https://iconmonstr.com/license/.

Created on 27 Apr 2022

:author: semuadmin
:copyright: SEMU Consulting © 2022
:license: BSD 3-Clause
"""

from tkinter import (
    Frame,
    Entry,
    Spinbox,
    Label,
    StringVar,
    E,
    W,
    NORMAL,
    DISABLED,
)
from pygpsclient.globals import DEFAULT_SERVER, DEFAULT_PORT

ADVOFF = "\u25bc"
ADVON = "\u25b2"
READONLY = "readonly"
ENTCOL = "azure"
BGCOL = "azure"
DISCONNECTED = 0
CONNECTED = 1
PROTOCOLS = ["TCP", "UDP"]


class SocketConfigFrame(Frame):
    """
    Socket configuration frame class.
    """

    def __init__(self, container, *args, **kwargs):
        """
        Constructor.

        :param tkinter.Frame container: reference to container frame
        :param args: optional args to pass to Frame parent class
        :param kwargs: optional kwargs for value ranges, or to pass to Frame parent class
        """

        self._readonlybg = kwargs.pop("readonlybackground", BGCOL)

        Frame.__init__(self, container, *args, **kwargs)

        self._show_advanced = False
        self._status = DISCONNECTED
        self._server = StringVar()
        self._port = StringVar()
        self._protocol = StringVar()

        self._body()
        self._do_layout()
        self.reset()

    def _body(self):
        """
        Set up widgets.
        """

        self._frm_basic = Frame(self)
        self._lbl_server = Label(self._frm_basic, text="Server")
        self.ent_server = Entry(
            self._frm_basic,
            textvariable=self._server,
            bg=ENTCOL,
            relief="sunken",
            width=32,
        )

        self._lbl_port = Label(self._frm_basic, text="Port")
        self.ent_port = Entry(
            self._frm_basic,
            textvariable=self._port,
            bg=ENTCOL,
            relief="sunken",
            width=6,
        )
        self._lbl_protocol = Label(self._frm_basic, text="Protocol")
        self._spn_protocol = Spinbox(
            self._frm_basic,
            textvariable=self._protocol,
            values=PROTOCOLS,
            width=12,
            state=READONLY,
            readonlybackground=self._readonlybg,
            wrap=True,
        )

    def _do_layout(self):
        """
        Layout widgets.
        """

        self._frm_basic.grid(column=0, row=0, columnspan=4, sticky=(W, E))
        self._lbl_server.grid(column=0, row=0, padx=2, pady=2, sticky=(W))
        self.ent_server.grid(
            column=1, row=0, padx=2, pady=2, columnspan=4, sticky=(W, E)
        )
        self._lbl_port.grid(column=0, row=1, padx=2, pady=2, sticky=(W))
        self.ent_port.grid(column=1, row=1, padx=2, pady=2, sticky=(W))
        self._lbl_protocol.grid(column=3, row=1, padx=2, pady=2, sticky=(W))
        self._spn_protocol.grid(column=4, row=1, padx=2, pady=2, sticky=(W))

    def reset(self):
        """
        Reset settings to defaults (first value in range).
        """

        self._server.set(DEFAULT_SERVER)
        self._port.set(DEFAULT_PORT)
        self._protocol.set(PROTOCOLS[0])

    def set_status(self, status: int = DISCONNECTED):
        """
        Set connection status, which determines whether controls
        are enabled or not: 0=DISCONNECTED, 1=CONNECTED

        :param int status: status (0,1)
        """

        self._status = status
        for widget in (
            self._lbl_server,
            self._lbl_port,
            self._lbl_protocol,
            self.ent_server,
            self.ent_port,
        ):
            widget.configure(state=(NORMAL if status == DISCONNECTED else DISABLED))
        for widget in (self._spn_protocol,):
            widget.configure(state=(READONLY if status == DISCONNECTED else DISABLED))

    @property
    def status(self) -> int:
        """
        Getter for status flag: 0=DISCONNECTED, 1=CONNECTED

        :return: status flag (0,1)
        :rtype: int
        """

        return self._status

    @property
    def server(self) -> str:
        """
        Getter for server.

        :return: server address
        :rtype: str
        """

        return self._server.get()

    @property
    def port(self) -> int:
        """
        Getter for port.

        :return: selected port description
        :rtype: int
        """

        try:
            return int(self._port.get())
        except ValueError:
            return 0

    @property
    def protocol(self) -> str:
        """
        Getter for protocol.

        :return: selected protocol
        :rtype: str
        """

        return self._protocol.get()
