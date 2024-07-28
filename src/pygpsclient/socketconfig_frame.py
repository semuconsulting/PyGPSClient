"""
socketconfig_frame.py

Generic socket configuration Frame subclass
for use in tkinter applications which require a
socket configuration facility.

Supply initial settings via `saved-config` keyword argument.

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
    DEFAULT_PORT,
    DEFAULT_SERVER,
    DEFAULT_TLS_PORTS,
    ICON_CONTRACT,
    ICON_EXPAND,
    SAVED_CONFIG,
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

    def __init__(self, app, container, *args, **kwargs):
        """
        Constructor.

        :param tkinter.Frame container: reference to container frame
        :param args: optional args to pass to Frame parent class
        :param kwargs: optional kwargs for value ranges, or to pass to Frame parent class
        """

        self._saved_config = kwargs.pop(SAVED_CONFIG, {})
        self._server_callback = kwargs.pop("server_callback", None)
        Frame.__init__(self, container, *args, **kwargs)

        self.__app = app
        self._container = container
        self._show_advanced = False
        self.status = DISCONNECTED
        self.server = StringVar()
        self.port = IntVar()
        self.https = IntVar()
        self.protocol = StringVar()
        self._protocol_range = self._saved_config.get("protocols_l", PROTOCOLS)
        self._img_expand = ImageTk.PhotoImage(Image.open(ICON_EXPAND))
        self._img_contract = ImageTk.PhotoImage(Image.open(ICON_CONTRACT))

        self._body()
        self._do_layout()
        self.reset()
        self._attach_events()

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
        Bind events to variables.
        """

        self.bind("<Configure>", self._on_resize)
        self.port.trace_add("write", callback=self._on_port)
        if self._server_callback is not None:
            self.server.trace_add("write", callback=self._server_callback)

    def reset(self):
        """
        Reset settings to defaults (first value in range).
        """

        self.server.set(self._saved_config.get("sockclienthost_s", DEFAULT_SERVER))
        self.port.set(self._saved_config.get("sockclientport_n", DEFAULT_PORT))
        self.protocol.set(
            self._saved_config.get("sockclientprotocol_s", self._protocol_range[0])
        )
        self.https.set(
            self._saved_config.get(
                "sockclienthttps_b", 1 if self.port.get() in DEFAULT_TLS_PORTS else 0
            )
        )

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

    def _on_port(self, var, index, mode):  # pylint: disable=unused-argument
        """
        Callback when port changed.

        :param event event: write event
        """

        try:
            if self.port.get() in DEFAULT_TLS_PORTS:
                self.https.set(1)
            else:
                self.https.set(0)
        except TclError:
            pass
