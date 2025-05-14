"""
socketconfig_frame.py

Generic socket configuration Frame subclass
for use in tkinter applications which require a
socket configuration facility.

Application icons from https://iconmonstr.com/license/.

Created on 27 Apr 2022

:author: semuadmin
:copyright: 2020 SEMU Consulting
:license: BSD 3-Clause
"""

from tkinter import (
    DISABLED,
    NORMAL,
    Checkbutton,
    E,
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
    NTRIP,
    RPTDELAY,
)
from pygpsclient.helpers import MAXPORT, VALINT, VALURL, valid_entry

ADVOFF = "\u25bc"
ADVON = "\u25b2"
CONNECTED = 1
DISCONNECTED = 0
READONLY = "readonly"
TCPIPV4 = "TCP IPv4"
TCPIPV6 = "TCP IPv6"
UDPIPV4 = "UDP IPv4"
UDPIPV6 = "UDP IPv6"
PROTOCOLS = [TCPIPV4, UDPIPV6, UDPIPV4, TCPIPV6]


class SocketConfigFrame(Frame):
    """
    Socket configuration frame class.
    """

    def __init__(self, app, container, context, *args, **kwargs):
        """
        Constructor.

        :param tkinter.Frame container: reference to container frame
        :param args: optional args to pass to Frame parent class
        :param str context: serial port context (GNSS or LBAND)
        :param kwargs: optional kwargs for value ranges, or to pass to Frame parent class
        """

        self._server_callback = kwargs.pop("server_callback", None)
        self._protocol_range = kwargs.pop("protocols", PROTOCOLS)
        Frame.__init__(self, container, *args, **kwargs)

        self.__app = app
        self._container = container
        self._context = context
        self._show_advanced = False
        self.status = DISCONNECTED
        self.server = StringVar()
        self.port = IntVar()
        self.https = IntVar()
        self.protocol = StringVar()

        self._img_expand = ImageTk.PhotoImage(Image.open(ICON_EXPAND))
        self._img_contract = ImageTk.PhotoImage(Image.open(ICON_CONTRACT))

        self._body()
        self._do_layout()
        self._attach_events()
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
            values=self._protocol_range,
            width=12,
            state=READONLY,
            wrap=True,
            repeatdelay=RPTDELAY,
            repeatinterval=RPTDELAY,
        )
        self._lbl_https = Label(self._frm_basic, text="HTTPS?")
        self._chk_https = Checkbutton(
            self._frm_basic,
            variable=self.https,
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
        self._lbl_https.grid(column=0, row=2, padx=2, pady=2, sticky=W)
        self._chk_https.grid(column=1, row=2, padx=2, pady=2, sticky=W)

    def _attach_events(self):
        """
        Bind events to frame.
        """

        self.bind("<Configure>", self._on_resize)

    def _bind_events(self, add: bool = True):
        """
        Add or remove event bindings to/from widgets.

        :param bool add: add or remove binding
        """

        tracemode = "write"
        if add:
            self.server.trace_add(tracemode, self._on_update_server)
            self.port.trace_add(tracemode, self._on_update_port)
            for setting in (self.https, self.protocol):
                setting.trace_add(tracemode, callback=self._on_update_config)
        else:
            if len(self.server.trace_info()) > 0:
                self.server.trace_remove(tracemode, self.server.trace_info()[0][1])
            if len(self.port.trace_info()) > 0:
                self.port.trace_remove(tracemode, self.port.trace_info()[0][1])
            for setting in (self.https, self.protocol):
                if len(setting.trace_info()) > 0:
                    setting.trace_remove(tracemode, setting.trace_info()[0][1])

    def _on_update_server(self, var, index, mode):  # pylint: disable=unused-argument
        """
        Server updated.
        """

        if self._server_callback is not None:
            self._server_callback(var, index, mode)
        self._on_update_config(None, None, "write")

    def _on_update_port(self, var, index, mode):  # pylint: disable=unused-argument
        """
        Port updated.
        """

        try:
            if self.port.get() in DEFAULT_TLS_PORTS:
                self.https.set(1)
            else:
                self.https.set(0)
            self._on_update_config(None, None, "write")
        except TclError:
            pass

    def _on_update_config(self, var, index, mode):  # pylint: disable=unused-argument
        """
        Update in-memory configuration if setting is changed.
        """

        self.update()
        cfg = self.__app.configuration
        try:
            if self._context == NTRIP:
                cfg.set("ntripclientserver_s", self.server.get())
                cfg.set("ntripclientport_n", int(self.port.get()))
                cfg.set("ntripclienthttps_b", int(self.https.get()))
                cfg.set("ntripclientprotocol_s", self.protocol.get())
            else:  # GNSS
                cfg.set("sockclienthost_s", self.server.get())
                cfg.set("sockclientport_n", int(self.port.get()))
                cfg.set("sockclienthttps_b", int(self.https.get()))
                cfg.set("sockclientprotocol_s", self.protocol.get())
        except (ValueError, TclError):
            pass

    def reset(self):
        """
        Reset settings to saved configuration.
        """

        self._bind_events(False)
        cfg = self.__app.configuration
        if self._context == NTRIP:
            self.server.set(cfg.get("ntripclientserver_s"))
            self.port.set(cfg.get("ntripclientport_n"))
            self.https.set(cfg.get("ntripclienthttps_b"))
            self.protocol.set(cfg.get("ntripclientprotocol_s"))
        else:  # GNSS
            self.server.set(cfg.get("sockclienthost_s"))
            self.port.set(cfg.get("sockclientport_n"))
            self.https.set(cfg.get("sockclienthttps_b"))
            self.protocol.set(cfg.get("sockclientprotocol_s"))
        self._bind_events(True)

    def valid_settings(self) -> bool:
        """
        Validate settings.

        :return: valid True/False
        :rtype: bool
        """

        valid = True
        valid = valid & valid_entry(self.ent_server, VALURL)
        valid = valid & valid_entry(self.ent_port, VALINT, 0, MAXPORT)
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
            self._lbl_https,
            self._chk_https,
        ):
            widget.configure(state=(NORMAL if status == DISCONNECTED else DISABLED))
        for widget in (self._spn_protocol,):
            widget.configure(state=(READONLY if status == DISCONNECTED else DISABLED))

    def _on_resize(self, event):  # pylint: disable=unused-argument
        """
        Resize frame.

        :param event event: resize event
        """

        self.__app.frm_settings.on_expand()
