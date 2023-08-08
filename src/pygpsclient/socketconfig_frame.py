"""
socketconfig_frame.py

Generic socket configuration Frame subclass
for use in tkinter applications which require a
socket configuration facility.

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
TCPIPV4 = "TCP IPv4"
TCPIPV6 = "TCP IPv6"
PROTOCOLS = [TCPIPV4, "UDP IPv6", "UDP IPv4", TCPIPV6]


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

        self._init_config = kwargs.pop("config", {})
        Frame.__init__(self, container, *args, **kwargs)

        self._show_advanced = False
        self.status = DISCONNECTED
        self.server = StringVar()
        self.port = StringVar()
        self.protocol = StringVar()
        self.flowinfo = StringVar()
        self.scopeid = StringVar()
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
            textvariable=self.server,
            relief="sunken",
            width=32,
        )

        self._lbl_port = Label(self._frm_basic, text="Port")
        self.ent_port = Entry(
            self._frm_basic,
            textvariable=self.port,
            relief="sunken",
            width=6,
        )
        self._lbl_protocol = Label(self._frm_basic, text="Protocol")
        self._spn_protocol = Spinbox(
            self._frm_basic,
            textvariable=self.protocol,
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
            textvariable=self.flowinfo,
            relief="sunken",
            width=6,
            state=DISABLED,
        )

        self._lbl_scopeid = Label(self._frm_advanced, text="Scope ID")
        self.ent_scopeid = Entry(
            self._frm_advanced,
            textvariable=self.scopeid,
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

        self.server.set(self._init_config.get("sockclienthost", DEFAULT_SERVER))
        self.port.set(self._init_config.get("sockclientport", DEFAULT_PORT))
        self.protocol.set(self._init_config.get("sockclientprotocol", TCPIPV4))
        self.flowinfo.set(self._init_config.get("sockclientflowinfo", 0))
        self.scopeid.set(self._init_config.get("sockclientscopeid", 0))

    def set_status(self, status: int = DISCONNECTED):
        """
        Set connection status, which determines whether controls
        are enabled or not: 0=DISCONNECTED, 1=CONNECTED

        :param int status: status (0,1)
        """

        self.status = status
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
                    if self.protocol.get() in ("TCP IPv6", "UDP IPv6")
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
