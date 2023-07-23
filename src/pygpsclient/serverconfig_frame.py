"""
Socket Server / NTRIP caster configuration Frame subclass.

Exposes the server settings as properties.

Application icons from https://iconmonstr.com/license/.

Created on 23 Jul 2023

:author: semuadmin
:copyright: SEMU Consulting © 2022
:license: BSD 3-Clause
"""
# pylint: disable=unused-argument

from tkinter import (
    DISABLED,
    NORMAL,
    Button,
    Checkbutton,
    DoubleVar,
    E,
    Entry,
    Frame,
    IntVar,
    Label,
    Spinbox,
    StringVar,
    W,
)

from PIL import Image, ImageTk
from pynmeagps import llh2ecef

from pygpsclient.globals import (
    ACCURACIES,
    BASEMODES,
    DISCONNECTED,
    DURATIONS,
    ICON_CONTRACT,
    ICON_EXPAND,
    POSMODES,
    SOCKMODES,
    SOCKSERVER_NTRIP_PORT,
    SOCKSERVER_PORT,
    TRACEMODE,
)
from pygpsclient.helpers import MAXPORT, VALFLOAT, VALINT, VALNONBLANK, valid_entry
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
        self.socket_serve = IntVar()
        self.sock_port = StringVar()
        self.sock_host = StringVar()
        self.sock_mode = StringVar()
        self._sock_clients = StringVar()
        self._set_basemode = IntVar()
        self._basemode = StringVar()
        self._acclimit = IntVar()
        self._duration = IntVar()
        self._posmode = StringVar()
        self._fixedlat = DoubleVar()
        self._fixedlon = DoubleVar()
        self._fixedalt = DoubleVar()
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
        # socket server configuration
        self._chk_socketserve = Checkbutton(
            self._frm_basic,
            text=LBLSOCKSERVE,
            variable=self.socket_serve,
            state=DISABLED,
        )
        self._lbl_sockmode = Label(
            self._frm_basic,
            text=LBLSERVERMODE,
        )
        self._spn_sockmode = Spinbox(
            self._frm_basic,
            values=SOCKMODES,
            width=12,
            state=READONLY,
            wrap=True,
            textvariable=self.sock_mode,
        )
        self._lbl_sockhost = Label(
            self._frm_basic,
            text=LBLSERVERHOST,
        )
        self._ent_sockhost = Entry(
            self._frm_basic,
            textvariable=self.sock_host,
            relief="sunken",
            width=12,
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
        self._lbl_clients = Label(self._frm_basic, text="Clients")
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
        self._chk_set_basemode = Checkbutton(
            self._frm_advanced,
            text="Enable Base Station",
            variable=self._set_basemode,
        )
        self._spn_basemode = Spinbox(
            self._frm_advanced,
            values=BASEMODES,
            width=10,
            state=READONLY,
            wrap=True,
            textvariable=self._basemode,
        )
        self._lbl_acclimit = Label(
            self._frm_advanced,
            text="Accuracy (cm)",
        )
        self._spn_acclimit = Spinbox(
            self._frm_advanced,
            values=ACCURACIES,
            width=5,
            state=READONLY,
            wrap=True,
            textvariable=self._acclimit,
        )
        self._lbl_duration = Label(
            self._frm_advanced,
            text="Duration (s)",
        )
        self._spn_duration = Spinbox(
            self._frm_advanced,
            values=DURATIONS,
            width=5,
            state=READONLY,
            wrap=True,
            textvariable=self._duration,
        )
        self._spn_posmode = Spinbox(
            self._frm_advanced,
            values=POSMODES,
            width=6,
            state=READONLY,
            wrap=True,
            textvariable=self._posmode,
        )
        self._lbl_fixedlat = Label(
            self._frm_advanced,
            text="Lat",
        )
        self._ent_fixedlat = Entry(
            self._frm_advanced,
            textvariable=self._fixedlat,
            relief="sunken",
            width=18,
        )
        self._lbl_fixedlon = Label(
            self._frm_advanced,
            text="Lon",
        )
        self._ent_fixedlon = Entry(
            self._frm_advanced,
            textvariable=self._fixedlon,
            relief="sunken",
            width=18,
        )
        self._lbl_fixedalt = Label(
            self._frm_advanced,
            text="Height (mm)",
        )
        self._ent_fixedalt = Entry(
            self._frm_advanced,
            textvariable=self._fixedalt,
            relief="sunken",
            width=18,
        )

    def _do_layout(self):
        """
        Layout widgets.
        """

        self._frm_basic.grid(column=0, row=0, columnspan=5, sticky=(W, E))
        self._chk_socketserve.grid(
            column=0, row=0, columnspan=2, rowspan=2, padx=2, pady=1, sticky=W
        )
        self._lbl_sockmode.grid(column=2, row=0, padx=2, pady=1, sticky=E)
        self._spn_sockmode.grid(column=3, row=0, padx=2, pady=1, sticky=W)
        self._lbl_sockhost.grid(column=2, row=1, padx=2, pady=1, sticky=E)
        self._ent_sockhost.grid(column=3, row=1, padx=2, pady=1, sticky=W)
        self._lbl_sockport.grid(column=2, row=2, padx=2, pady=1, sticky=E)
        self._ent_sockport.grid(column=3, row=2, padx=2, pady=1, sticky=W)
        self._lbl_clients.grid(column=0, row=2, padx=2, pady=1, sticky=E)
        self._lbl_sockclients.grid(column=1, row=2, padx=2, pady=1, sticky=W)
        self._btn_toggle.grid_forget()
        self._frm_advanced.grid_forget()
        self._chk_set_basemode.grid(
            column=0, row=0, columnspan=2, padx=2, pady=1, sticky=W
        )
        self._spn_basemode.grid(column=2, row=0, columnspan=2, padx=2, pady=1, sticky=W)

    def _attach_events(self):
        """
        Bind events to variables.
        """

        self.socket_serve.trace_add(TRACEMODE, self._on_socket_serve)
        self.sock_mode.trace_add(TRACEMODE, self._on_sockmode)
        self._set_basemode.trace_add(TRACEMODE, self._on_set_basemode)
        self._basemode.trace_add(TRACEMODE, self._on_basemode)
        self._posmode.trace_add(TRACEMODE, self._on_posmode)

    def reset(self):
        """
        Reset settings to defaults (first value in range).
        """

        self._basemode.set(BASEMODES[0])
        self._posmode.set(POSMODES[0])
        self.clients = 0

    def set_status(self, status: int = DISCONNECTED):
        """
        Set connection status, which determines whether controls
        are enabled or not: 0=DISCONNECTED, 1=CONNECTED

        :param int status: status (0,1)
        """

        self._chk_socketserve.configure(
            state=(DISABLED if status == DISCONNECTED else NORMAL)
        )

        if status == DISCONNECTED:
            self.clients = 0

    def _on_toggle_advanced(self):
        """
        Toggle advanced socket settings panel on or off
        if server mode is "NTRIP Caster".
        """

        if self.sock_mode.get() != SOCKMODES[1]:
            return
        self._show_advanced = not self._show_advanced
        if self._show_advanced:
            self._frm_advanced.grid(column=0, row=1, columnspan=5, sticky=(W, E))
            self._btn_toggle.config(image=self._img_contract)
        else:
            self._frm_advanced.grid_forget()
            self._btn_toggle.config(image=self._img_expand)

    def _on_socket_serve(self, var, index, mode):
        """
        Start or stop socket server.
        """

        valid = True
        valid = valid & valid_entry(self._ent_sockhost, VALNONBLANK)
        valid = valid & valid_entry(self._ent_sockport, VALINT, 1, MAXPORT)
        valid = valid & valid_entry(self._ent_fixedlat, VALFLOAT)
        valid = valid & valid_entry(self._ent_fixedlon, VALFLOAT)
        valid = valid & valid_entry(self._ent_fixedalt, VALFLOAT)
        if valid:
            self.__app.set_status("", "blue")
        else:
            self.__app.set_status("ERROR - invalid entry", "red")
            self.socket_serve.set(0)
            return

        if self.socket_serve.get() == 1:
            self.__app.start_sockserver_thread()
            self.__app.stream_handler.sock_serve = True
        else:
            self.__app.stop_sockserver_thread()
            self.__app.stream_handler.sock_serve = False
            self.clients = 0

        # set visibility of various fields depending on server status
        for wid in (
            self._ent_sockhost,
            self._ent_sockport,
            self._spn_sockmode,
            self._chk_set_basemode,
            self._spn_basemode,
            self._lbl_acclimit,
            self._spn_acclimit,
            self._lbl_duration,
            self._spn_duration,
            self._spn_posmode,
            self._lbl_fixedlat,
            self._ent_fixedlat,
            self._lbl_fixedlon,
            self._ent_fixedlon,
            self._lbl_fixedalt,
            self._ent_fixedalt,
        ):
            if self.socket_serve.get():
                state = DISABLED
            else:
                state = READONLY if isinstance(wid, Spinbox) else NORMAL
            wid.config(state=state)

    def _on_sockmode(self, var, index, mode):
        """
        Set default port depending on socket server mode.
        """

        if self.sock_mode.get() == SOCKMODES[1]:  # NTRIP Server
            self.sock_port.set(SOCKSERVER_NTRIP_PORT)
            self._btn_toggle.grid(column=4, row=0, sticky=E)
        else:
            self.sock_port.set(SOCKSERVER_PORT)
            self._btn_toggle.grid_forget()

    def _on_set_basemode(self, var, index, mode):
        """
        Configure receiver for base mode.
        """

        # TODO do something along the lines of F9P_basestation example

    def _on_basemode(self, var, index, mode):
        """
        Set available fields depending on base mode.
        """

        if self._basemode.get() == BASEMODES[0]:  # Survey In Base Mode
            self._lbl_acclimit.grid(column=0, row=1, padx=2, pady=1, sticky=E)
            self._spn_acclimit.grid(column=1, row=1, padx=2, pady=1, sticky=W)
            self._lbl_duration.grid(column=2, row=1, padx=2, pady=1, sticky=E)
            self._spn_duration.grid(column=3, row=1, padx=2, pady=1, sticky=W)
            self._spn_posmode.grid_forget()
            self._lbl_fixedlat.grid_forget()
            self._ent_fixedlat.grid_forget()
            self._lbl_fixedlon.grid_forget()
            self._ent_fixedlon.grid_forget()
            self._lbl_fixedalt.grid_forget()
            self._ent_fixedalt.grid_forget()
        else:  # Fixed Base Mode
            self._spn_posmode.grid(column=0, row=1, rowspan=3, padx=2, pady=1, sticky=E)
            self._lbl_fixedlat.grid(column=1, row=1, padx=2, pady=1, sticky=E)
            self._ent_fixedlat.grid(
                column=2, row=1, columnspan=3, padx=2, pady=1, sticky=W
            )
            self._lbl_fixedlon.grid(column=1, row=2, padx=2, pady=1, sticky=E)
            self._ent_fixedlon.grid(
                column=2, row=2, columnspan=3, padx=2, pady=1, sticky=W
            )
            self._lbl_fixedalt.grid(column=1, row=3, padx=2, pady=1, sticky=E)
            self._ent_fixedalt.grid(
                column=2, row=3, columnspan=3, padx=2, pady=1, sticky=W
            )
            self._lbl_acclimit.grid_forget()
            self._spn_acclimit.grid_forget()
            self._lbl_duration.grid_forget()
            self._spn_duration.grid_forget()

        self._set_coords(self._posmode.get())

    def _on_posmode(self, var, index, mode):
        """
        Set fixed reference labels depending on position mode (ECEF or LLH)
        """

        lbls = (
            ("Lat", "Lon", "Height (m)")
            if self._posmode.get() == POSMODES[0]  # LLH
            else ("X (m)", "Y (m)", "Z (m)")
        )
        self._lbl_fixedlat.config(text=lbls[0])
        self._lbl_fixedlon.config(text=lbls[1])
        self._lbl_fixedalt.config(text=lbls[2])
        self._set_coords(self._posmode.get())

    def _set_coords(self, posmode: str):
        """Set current coordinates in LLA or ECEF format.

        :param str posmode: position mode (LLA or ECEF)
        """

        _, lat, lon, alt, _ = self.__app.get_coordinates()
        if posmode == POSMODES[1]:
            lat, lon, alt = llh2ecef(lat, lon, alt)
        self._fixedlat.set(lat)
        self._fixedlon.set(lon)
        self._fixedalt.set(alt)

    @property
    def clients(self) -> int:
        """
        Getter for number of socket clients.
        """

        return self._sock_clients.get()

    @clients.setter
    def clients(self, clients: int):
        """
        Setter for number of socket clients.

        :param int clients: no of clients connected
        """

        self._sock_clients.set(clients)
        if self.socket_serve.get() == 1:
            self.__app.frm_banner.update_transmit_status(clients)
