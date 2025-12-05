"""
socketconfig_frame.py

Generic socket configuration Frame subclass
for use in tkinter applications which require a
socket configuration facility.

Application icons from https://iconmonstr.com/license/.

Created on 27 Apr 2022

:author: semuadmin (Steve Smith)
:copyright: 2020 semuadmin
:license: BSD 3-Clause
"""

# pylint: disable=unused-argument

from tkinter import (
    DISABLED,
    EW,
    NORMAL,
    Checkbutton,
    Entry,
    Frame,
    IntVar,
    Label,
    Spinbox,
    StringVar,
    TclError,
    W,
)

from PIL import Image, ImageTk

from pygpsclient.globals import (
    DEFAULT_TLS_PORTS,
    ICON_CONTRACT,
    ICON_EXPAND,
    READONLY,
    TRACEMODE_WRITE,
    VALINT,
    VALNONBLANK,
    VALURL,
)
from pygpsclient.helpers import MAXPORT

ADVOFF = "\u25bc"
ADVON = "\u25b2"
CONNECTED = 1
DISCONNECTED = 0
TCPIPV4 = "TCP IPv4"
TCPIPV6 = "TCP IPv6"
UDPIPV4 = "UDP IPv4"
UDPIPV6 = "UDP IPv6"
PROTOCOLS = [TCPIPV4, UDPIPV6, UDPIPV4, TCPIPV6]


class SocketConfigFrame(Frame):
    """
    Socket configuration frame class.
    """

    def __init__(self, app, container, *args, **kwargs):
        """
        Constructor.

        :param tkinter.Frame container: reference to container frame
        :param args: optional args to pass to Frame parent class
        :param kwargs: optional kwargs for value ranges, or to pass to Frame parent class
        """

        self._server_callback = kwargs.pop("server_callback", None)
        self._protocol_range = kwargs.pop("protocols", PROTOCOLS)
        Frame.__init__(self, container, *args, **kwargs)

        self.__app = app
        self._container = container
        self._show_advanced = False
        self.status = DISCONNECTED
        self.server = StringVar()
        self.port = IntVar()
        self.https = IntVar()
        self.selfsign = IntVar()
        self.protocol = StringVar()

        self._img_expand = ImageTk.PhotoImage(Image.open(ICON_EXPAND))
        self._img_contract = ImageTk.PhotoImage(Image.open(ICON_CONTRACT))

        self._body()
        self._do_layout()
        self.reset()
        # self._attach_events() # done in reset

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
            values=self._protocol_range,
            width=12,
            state=READONLY,
            wrap=True,
        )
        self._chk_https = Checkbutton(self._frm_basic, variable=self.https, text="TLS")
        self._chk_selfsign = Checkbutton(
            self._frm_basic, variable=self.selfsign, text="Self Sign"
        )

    def _do_layout(self):
        """
        Layout widgets.
        """

        self._frm_basic.grid(column=0, row=0, columnspan=4, sticky=EW)
        self._lbl_server.grid(column=0, row=0, padx=2, pady=2, sticky=W)
        self.ent_server.grid(column=1, row=0, padx=2, pady=2, columnspan=4, sticky=EW)
        self._lbl_port.grid(column=0, row=1, padx=2, pady=2, sticky=W)
        self.ent_port.grid(column=1, row=1, padx=2, pady=2, sticky=W)
        self._lbl_protocol.grid(column=2, row=1, padx=2, pady=2, sticky=W)
        self._spn_protocol.grid(column=3, row=1, padx=2, pady=2, sticky=W)
        self._chk_https.grid(column=1, row=2, padx=2, pady=2, sticky=W)
        self._chk_selfsign.grid(column=2, row=2, padx=2, pady=2, sticky=W)

    def _attach_events(self, add: bool = True):
        """
        Add or remove event bindings to/from widgets.

        (trace_update() is a class extension method defined in globals.py)

        :param bool add: add or remove binding
        """

        tracemode = TRACEMODE_WRITE
        self.server.trace_update(tracemode, self._on_update_server, add)
        self.port.trace_update(tracemode, self._on_update_port, add)
        self.https.trace_update(tracemode, self._on_update_https, add)
        self.protocol.trace_update(tracemode, self._on_update_protocol, add)
        self.selfsign.trace_update(tracemode, self._on_update_selfsign, add)

    def _on_update_server(self, var, index, mode):
        """
        Server updated.
        """

        if not self.ent_server.validate(VALNONBLANK):
            return

        self.__app.configuration.set("sockclienthost_s", self.server.get())

    def _on_update_port(self, var, index, mode):
        """
        Port updated.
        """

        if not self.ent_port.validate(VALINT, 0, MAXPORT):
            return

        try:
            if self.port.get() in DEFAULT_TLS_PORTS:
                self.https.set(1)
            else:
                self.https.set(0)
            self.__app.configuration.set("sockclientport_n", int(self.port.get()))
        except TclError:
            pass

    def _on_update_https(self, var, index, mode):
        """
        Action on updating TLS flag.
        """

        self.__app.configuration.set("sockclienthttps_b", int(self.https.get()))

    def _on_update_protocol(self, var, index, mode):
        """
        Action on updating TCP/UDP protocol.
        """

        self.__app.configuration.set("sockclientprotocol_s", self.protocol.get())

    def _on_update_selfsign(self, var, index, mode):
        """
        Action on updating self-sign flag.
        """

        self.__app.configuration.set("sockclientselfsign_b", int(self.selfsign.get()))

    def reset(self):
        """
        Reset settings to saved configuration.
        """

        self._attach_events(False)
        cfg = self.__app.configuration
        self.server.set(cfg.get("sockclienthost_s"))
        self.port.set(cfg.get("sockclientport_n"))
        self.https.set(cfg.get("sockclienthttps_b"))
        self.selfsign.set(cfg.get("sockclientselfsign_b"))
        self.protocol.set(cfg.get("sockclientprotocol_s"))
        self._attach_events(True)

    def valid_settings(self) -> bool:
        """
        Validate settings.

        :return: valid True/False
        :rtype: bool
        """

        valid = True
        valid = valid & self.ent_server.validate(VALURL)
        valid = valid & self.ent_port.validate(VALINT, 0, MAXPORT)
        return valid

    def set_status(self, status: int = DISCONNECTED):
        """
        Set connection status, which determines whether controls
        are enabled or not: 0=DISCONNECTED, 1=CONNECTED

        :param int status: status (0,1)
        """

        self.status = status
        for widget in (
            self._lbl_server,
            self.ent_server,
            self._lbl_port,
            self.ent_port,
            self._lbl_protocol,
            self._chk_https,
            self._chk_selfsign,
        ):
            widget.configure(state=(NORMAL if status == DISCONNECTED else DISABLED))
        for widget in (self._spn_protocol,):
            widget.configure(state=(READONLY if status == DISCONNECTED else DISABLED))

    def _on_resize(self, event):
        """
        Resize frame.

        :param event event: resize event
        """

        self.__app.frm_settings.on_expand()
