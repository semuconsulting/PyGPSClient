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
    DISABLED,
    NORMAL,
    Button,
    E,
    Entry,
    Frame,
    Label,
    Spinbox,
    StringVar,
    W,
)

from PIL import Image, ImageTk

from pygpsclient.globals import DEFAULT_PORT, DEFAULT_SERVER, ICON_CONTRACT, ICON_EXPAND

ADVOFF = "\u25bc"
ADVON = "\u25b2"
READONLY = "readonly"
DISCONNECTED = 0
CONNECTED = 1
PROTOCOLS = ["TCP IPv4", "UDP IPv6", "UDP IPv4", "TCP IPv6"]


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

        Frame.__init__(self, container, *args, **kwargs)

        self._show_advanced = False
        self._status = DISCONNECTED
        self._server = StringVar()
        self._port = StringVar()
        self._protocol = StringVar()
        self._flowinfo = StringVar()
        self._scopeid = StringVar()
        self._img_expand = ImageTk.PhotoImage(Image.open(ICON_EXPAND))
        self._img_contract = ImageTk.PhotoImage(Image.open(ICON_CONTRACT))

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
            relief="sunken",
            width=32,
        )

        self._lbl_port = Label(self._frm_basic, text="Port")
        self.ent_port = Entry(
            self._frm_basic,
            textvariable=self._port,
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
            wrap=True,
            command=self._on_change_protocol,
        )
        self._btn_toggle = Button(
            self._frm_basic,
            command=self._on_toggle_advanced,
            image=self._img_expand,
            width=28,
            height=22,
        )
        self._frm_advanced = Frame(self)
        self._lbl_flowinfo = Label(self._frm_advanced, text="Flow Info")
        self.ent_flowinfo = Entry(
            self._frm_advanced,
            textvariable=self._flowinfo,
            relief="sunken",
            width=6,
            state=DISABLED,
        )

        self._lbl_scopeid = Label(self._frm_advanced, text="Scope ID")
        self.ent_scopeid = Entry(
            self._frm_advanced,
            textvariable=self._scopeid,
            relief="sunken",
            width=6,
            state=DISABLED,
        )

    def _do_layout(self):
        """
        Layout widgets.
        """

        self._frm_basic.grid(column=0, row=0, columnspan=4, sticky=(W, E))
        self._lbl_server.grid(column=0, row=0, padx=2, pady=2, sticky=W)
        self.ent_server.grid(
            column=1, row=0, padx=2, pady=2, columnspan=4, sticky=(W, E)
        )
        self._lbl_port.grid(column=0, row=1, padx=2, pady=2, sticky=W)
        self.ent_port.grid(column=1, row=1, padx=2, pady=2, sticky=W)
        self._lbl_protocol.grid(column=3, row=1, padx=2, pady=2, sticky=W)
        self._spn_protocol.grid(column=4, row=1, padx=2, pady=2, sticky=W)
        self._btn_toggle.grid(column=5, row=1, padx=2, pady=2, sticky=W)
        self._frm_advanced.grid_forget()
        self._lbl_flowinfo.grid(column=0, row=0, padx=2, pady=2, sticky=W)
        self.ent_flowinfo.grid(column=1, row=0, padx=2, pady=2, sticky=W)
        self._lbl_scopeid.grid(column=2, row=0, padx=2, pady=2, sticky=W)
        self.ent_scopeid.grid(column=3, row=0, padx=2, pady=2, sticky=W)

    def reset(self):
        """
        Reset settings to defaults (first value in range).
        """

        self._server.set(DEFAULT_SERVER)
        self._port.set(DEFAULT_PORT)
        self._protocol.set(PROTOCOLS[0])
        self._flowinfo.set(0)
        self._scopeid.set(0)

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
            self._lbl_flowinfo,
            self._lbl_scopeid,
            self.ent_server,
            self.ent_port,
            self.ent_flowinfo,
            self.ent_scopeid,
        ):
            widget.configure(state=(NORMAL if status == DISCONNECTED else DISABLED))
        for widget in (self._spn_protocol,):
            widget.configure(state=(READONLY if status == DISCONNECTED else DISABLED))

    def _on_change_protocol(self):
        """
        Toggle fields only used for IPv6.
        """

        for widget in (
            self._lbl_flowinfo,
            self._lbl_scopeid,
            self.ent_flowinfo,
            self.ent_scopeid,
        ):
            widget.configure(
                state=(
                    NORMAL
                    if self._protocol.get() in ("TCP IPv6", "UDP IPv6")
                    else DISABLED
                )
            )

    def _on_toggle_advanced(self):
        """
        Toggle advanced socket settings panel on or off.
        """

        self._show_advanced = not self._show_advanced
        if self._show_advanced:
            self._frm_advanced.grid(column=0, row=1, columnspan=4, sticky=(W, E))
            self._btn_toggle.config(image=self._img_contract)
        else:
            self._frm_advanced.grid_forget()
            self._btn_toggle.config(image=self._img_expand)

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
    def flowinfo(self) -> int:
        """
        Getter for flowinfo.

        :return: IPv6 flowinfo
        :rtype: int
        """

        try:
            return int(self._flowinfo.get())
        except ValueError:
            return 0

    @property
    def scopeid(self) -> int:
        """
        Getter for scopeid.

        :return: IPv6 scopeid
        :rtype: int
        """

        try:
            return int(self._scopeid.get())
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
