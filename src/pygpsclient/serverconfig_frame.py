"""
Socket Server / NTRIP caster configuration Frame subclass.

Exposes the server settings as properties.

Application icons from https://iconmonstr.com/license/.

Created on 23 Jul 2023

:author: semuadmin
:copyright: SEMU Consulting © 2022
:license: BSD 3-Clause
"""

from tkinter import (
    DISABLED,
    NORMAL,
    Button,
    Checkbutton,
    E,
    Entry,
    Frame,
    IntVar,
    Label,
    N,
    S,
    Spinbox,
    StringVar,
    W,
)

from PIL import Image, ImageTk

from pygpsclient.globals import (
    DISCONNECTED,
    ICON_CONTRACT,
    ICON_EXPAND,
    SOCKMODES,
    SOCKSERVER_NTRIP_PORT,
    SOCKSERVER_PORT,
)
from pygpsclient.helpers import MAXPORT, VALINT, VALNONBLANK, valid_entry
from pygpsclient.strings import (
    LBLSERVERHOST,
    LBLSERVERMODE,
    LBLSERVERPORT,
    LBLSOCKSERVE,
)

ADVOFF = "\u25bc"
ADVON = "\u25b2"
READONLY = "readonly"


class ServerConfigFrame(Frame):
    """
    Server configuration frame class.
    """

    def __init__(self, app, container, *args, **kwargs):
        """
        Constructor.

        :param Frame app: reference to main tkinter application
        :param tkinter.Frame container: reference to container frame
        :param args: optional args to pass to Frame parent class
        :param kwargs: optional kwargs for value ranges, or to pass to Frame parent class
        """

        Frame.__init__(self, container, *args, **kwargs)

        self.__app = app
        self._show_advanced = False
        self._status = DISCONNECTED
        self.socket_serve = IntVar()
        self.sock_port = StringVar()
        self.sock_host = StringVar()
        self.sock_mode = StringVar()
        self._sock_clients = StringVar()
        self._img_expand = ImageTk.PhotoImage(Image.open(ICON_EXPAND))
        self._img_contract = ImageTk.PhotoImage(Image.open(ICON_CONTRACT))
        self.clients = 0
        self._sock_clients.set(f"Clients {self.clients}")

        self._body()
        self._do_layout()
        self.reset()

    def _body(self):
        """
        Set up widgets.
        """

        self._frm_basic = Frame(self)
        # socket server configuration
        self._chk_socketserve = Checkbutton(
            self._frm_basic,
            text=LBLSOCKSERVE,
            variable=self.socket_serve,
            command=lambda: self._on_socket_serve(),
            state=DISABLED,
        )
        self._lbl_sockmode = Label(
            self._frm_basic,
            text=LBLSERVERMODE,
        )
        self._spn_sockmode = Spinbox(
            self._frm_basic,
            values=SOCKMODES,
            width=16,
            state=READONLY,
            wrap=True,
            textvariable=self.sock_mode,
            command=lambda: self._on_sockmode(),
        )
        self._lbl_sockhost = Label(
            self._frm_basic,
            text=LBLSERVERHOST,
        )
        self._ent_sockhost = Entry(
            self._frm_basic,
            textvariable=self.sock_host,
            relief="sunken",
            width=14,
        )
        self._lbl_sockport = Label(
            self._frm_basic,
            text=LBLSERVERPORT,
        )
        self._ent_sockport = Entry(
            self._frm_basic,
            textvariable=self.sock_port,
            relief="sunken",
            width=6,
        )
        self._lbl_sockclients = Label(
            self._frm_basic,
            textvariable=self._sock_clients,
        )
        self._btn_toggle = Button(
            self._frm_basic,
            command=self._on_toggle_advanced,
            image=self._img_expand,
            width=28,
            height=22,
        )
        self._frm_advanced = Frame(self)

    def _do_layout(self):
        """
        Layout widgets.
        """

        self._frm_basic.grid(column=0, row=0, columnspan=4, sticky=(W, E))
        self._chk_socketserve.grid(
            column=0, row=0, rowspan=2, padx=2, pady=1, sticky=(N, S, W)
        )
        self._lbl_sockmode.grid(column=1, row=0, padx=2, pady=1, sticky=E)
        self._spn_sockmode.grid(column=2, row=0, columnspan=2, padx=2, pady=1, sticky=W)
        self._lbl_sockhost.grid(column=1, row=1, padx=2, pady=1, sticky=E)
        self._ent_sockhost.grid(column=2, row=1, padx=2, columnspan=2, pady=1, sticky=W)
        self._lbl_sockport.grid(column=1, row=2, padx=2, pady=1, sticky=E)
        self._ent_sockport.grid(column=2, row=2, padx=2, columnspan=2, pady=1, sticky=W)
        self._lbl_sockclients.grid(column=0, row=2, padx=2, pady=1, sticky=E)
        self._btn_toggle.grid(column=4, row=0, sticky=E)

        self._frm_advanced.grid_forget()

    def reset(self):
        """
        Reset settings to defaults (first value in range).
        """

        self.clients = 0

    def set_status(self, status: int = DISCONNECTED):
        """
        Set connection status, which determines whether controls
        are enabled or not: 0=DISCONNECTED, 1=CONNECTED

        :param int status: status (0,1)
        """

        self._status = status
        for widget in (
            self._lbl_sockhost,
            self._lbl_sockmode,
            self._lbl_sockport,
            self._lbl_sockclients,
            self._ent_sockhost,
            self._ent_sockport,
        ):
            widget.configure(state=(NORMAL if status == DISCONNECTED else DISABLED))
        for widget in (self._chk_socketserve,):
            widget.configure(state=(DISABLED if status == DISCONNECTED else NORMAL))
        for widget in (self._spn_sockmode,):
            widget.configure(state=(READONLY if status == DISCONNECTED else DISABLED))

    # def enable_controls(self, status: int):
    #     """
    #     Public method to enable and disable those controls
    #     which depend on connection status.

    #     :param int status: connection status as integer
    #            (0=Disconnected, 1=Connected to serial,
    #            2=Connected to file, 3=No serial ports available)

    #     """

    #     self._chk_socketserve.config(
    #         state=(
    #             NORMAL
    #             if status in (CONNECTED, CONNECTED_SOCKET, CONNECTED_FILE)
    #             else DISABLED
    #         )
    #     )

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

    def _on_socket_serve(self):
        """
        Start or stop socket server.
        """

        if not valid_entry(self._ent_sockhost, VALNONBLANK) or not valid_entry(
            self._ent_sockport, VALINT, 1, MAXPORT
        ):
            self.__app.set_status("ERROR - invalid address", "red")
            self.socket_serve.set(0)
            return
        else:
            self.__app.set_status("", "blue")

        if self.socket_serve.get() == 1:
            self.__app.start_sockserver_thread()
            self._ent_sockhost.config(state=DISABLED)
            self._ent_sockport.config(state=DISABLED)
            self._spn_sockmode.config(state=DISABLED)
            self.__app.stream_handler.sock_serve = True
        else:
            self.__app.stop_sockserver_thread()
            self._ent_sockhost.config(state=NORMAL)
            self._ent_sockport.config(state=NORMAL)
            self._spn_sockmode.config(state=READONLY)
            self.__app.stream_handler.sock_serve = False
            self.clients = 0

    def _on_sockmode(self):
        """
        Set default port depending on socket server mode.
        """

        if self.sock_mode.get() == SOCKMODES[1]:  # NTRIP Server
            self.sock_port.set(SOCKSERVER_NTRIP_PORT)
        else:
            self.sock_port.set(SOCKSERVER_PORT)
