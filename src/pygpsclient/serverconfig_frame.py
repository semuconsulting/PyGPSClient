"""
serverconfig_frame.py

Socket Server / NTRIP caster configuration panel Frame class.
Supports two modes of operation - Socket Server and NTRIP Caster.

If running in NTRIP Caster mode, two base station modes are available -
Survey-In and Fixed. The panel provides methods to configure RTK-compatible
receiver (e.g. ZED-F9P or LG290P) to operate in either of these base station modes.

Application icons from https://iconmonstr.com/license/.

Created on 23 Jul 2023

:author: semuadmin
:copyright: 2020 SEMU Consulting
:license: BSD 3-Clause
"""

# pylint: disable=unused-argument

import logging
from time import sleep
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
    TclError,
    W,
)
from tkinter.ttk import Progressbar

from PIL import Image, ImageTk
from pygnssutils import RTCMTYPES
from pynmeagps import SET, NMEAMessage, ecef2llh, llh2ecef
from pyubx2 import UBXMessage

from pygpsclient.globals import (
    ASCII,
    BSR,
    DISCONNECTED,
    ERRCOL,
    ICON_CONTRACT,
    ICON_EXPAND,
    ICON_SEND,
    INFOCOL,
    LG290P,
    MOSAIC_X5,
    READONLY,
    RPTDELAY,
    SERVERCONFIG,
    SOCK_NTRIP,
    SOCKMODES,
    SOCKSERVER_NTRIP_PORT,
    SOCKSERVER_PORT,
    ZED_F9,
)
from pygpsclient.helpers import (
    MAXPORT,
    VALFLOAT,
    VALINT,
    VALNONBLANK,
    config_nmea,
    lanip,
    publicip,
    val2sphp,
    valid_entry,
)
from pygpsclient.strings import (
    LBLACCURACY,
    LBLCONFIGBASE,
    LBLDISNMEA,
    LBLDURATIONS,
    LBLLANIP,
    LBLPUBLICIP,
    LBLSERVERHOST,
    LBLSERVERMODE,
    LBLSERVERPORT,
    LBLSOCKSERVE,
)

ACCURACIES = (
    10.0,
    5.0,
    3.0,
    2.0,
    1.0,
    10000.0,
    5000.0,
    3000.0,
    2000.0,
    1000.0,
    500.0,
    300.0,
    200.0,
    100.0,
    50.0,
    30.0,
    20.0,
)

BASE_DISABLED = "DISABLED"
BASE_FIXED = "FIXED"
BASE_SVIN = "SURVEY IN"
BASEMODES = (BASE_SVIN, BASE_DISABLED, BASE_FIXED)
DURATIONS = (60, 1200, 600, 300, 240, 180, 120, 90)
ECEF = 0
LLH = 1
MAXSVIN = 15
POS_ECEF = "ECEF"
POS_LLH = "LLH"
PQTMVER = "PQTMVER"
POSMODES = (POS_LLH, POS_ECEF)
TMODE_DISABLED = 0
TMODE_FIXED = 2
TMODE_SVIN = 1


class ServerConfigFrame(Frame):
    """
    Server configuration frame class.
    """

    def __init__(self, app, container, *args, **kwargs):
        """
        Constructor.

        :param Frame app: reference to main tkinter application
        :param Frame container: reference to container frame
        :param args: optional args to pass to Frame parent class
        :param kwargs: optional kwargs for value ranges, or to pass to Frame parent class
        """

        Frame.__init__(self, container, *args, **kwargs)
        self.logger = logging.getLogger(__name__)

        self.__app = app
        self._container = container
        self._show_advanced = False
        self._socket_serve = IntVar()
        self.sock_port = IntVar()
        self.sock_host = StringVar()
        self.sock_mode = StringVar()
        self._sock_clients = StringVar()
        # self._set_basemode = IntVar()
        self.receiver_type = StringVar()
        self.base_mode = StringVar()
        self.acclimit = IntVar()
        self.duration = IntVar()
        self.pos_mode = StringVar()
        self.fixedlat = DoubleVar()
        self.fixedlon = DoubleVar()
        self.fixedhae = DoubleVar()
        self.disable_nmea = IntVar()
        self.user = StringVar()
        self.password = StringVar()
        self._img_expand = ImageTk.PhotoImage(Image.open(ICON_EXPAND))
        self._img_contract = ImageTk.PhotoImage(Image.open(ICON_CONTRACT))
        self._img_send = ImageTk.PhotoImage(Image.open(ICON_SEND))
        self._sock_port_temp = SOCKSERVER_PORT
        self._fixed_lat_temp = 0
        self._fixed_lon_temp = 0
        self._fixed_hae_temp = 0
        self._pending_confs = {}
        self._quectel_restart = 0  # keep track of Quectel receiver restarts

        self._body()
        self._do_layout()
        self._attach_events()
        self.reset()

    def _body(self):
        """
        Set up widgets.
        """

        self._frm_basic = Frame(self)
        self._chk_socketserve = Checkbutton(
            self._frm_basic,
            text=LBLSOCKSERVE,
            variable=self._socket_serve,
            state=DISABLED,
        )
        self._lbl_sockmode = Label(
            self._frm_basic,
            text=LBLSERVERMODE,
        )
        self._spn_sockmode = Spinbox(
            self._frm_basic,
            values=SOCKMODES,
            width=14,
            state=READONLY,
            wrap=True,
            repeatdelay=RPTDELAY,
            repeatinterval=RPTDELAY,
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
        self._lbl_publicipl = Label(
            self._frm_basic,
            text=LBLPUBLICIP,
        )
        self._lbl_publicip = Label(
            self._frm_basic,
            text="N/A",
        )
        self._lbl_lanipl = Label(
            self._frm_basic,
            text=LBLLANIP,
        )
        self._lbl_lanip = Label(
            self._frm_basic,
            text="N/A",
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
            # state=DISABLED,
        )
        self._frm_advanced = Frame(self)
        self._lbl_user = Label(
            self._frm_advanced,
            text="User",
        )
        self._ent_user = Entry(
            self._frm_advanced,
            textvariable=self.user,
            relief="sunken",
            width=15,
        )
        self._lbl_password = Label(
            self._frm_advanced,
            text="Password",
        )
        self._ent_password = Entry(
            self._frm_advanced,
            textvariable=self.password,
            relief="sunken",
            width=15,
        )
        self._lbl_configure_base = Label(
            self._frm_advanced,
            text=LBLCONFIGBASE,
        )
        self._btn_configure_base = Button(
            self._frm_advanced,
            command=self._on_configure_base,
            image=self._img_send,
            width=40,
            height=22,
        )
        self._spn_rcvrtype = Spinbox(
            self._frm_advanced,
            values=(ZED_F9, LG290P, MOSAIC_X5),
            width=18,
            state=READONLY,
            wrap=True,
            repeatdelay=RPTDELAY,
            repeatinterval=RPTDELAY,
            textvariable=self.receiver_type,
        )
        self._lbl_basemode = Label(
            self._frm_advanced,
            text="Mode",
        )
        self._spn_basemode = Spinbox(
            self._frm_advanced,
            values=BASEMODES,
            width=10,
            state=READONLY,
            wrap=True,
            repeatdelay=RPTDELAY,
            repeatinterval=RPTDELAY,
            textvariable=self.base_mode,
        )
        self._lbl_acclimit = Label(
            self._frm_advanced,
            text=LBLACCURACY,
        )
        self._spn_acclimit = Spinbox(
            self._frm_advanced,
            values=ACCURACIES,
            width=7,
            state=READONLY,
            wrap=True,
            repeatdelay=RPTDELAY,
            repeatinterval=RPTDELAY,
            textvariable=self.acclimit,
        )
        self._lbl_duration = Label(
            self._frm_advanced,
            text=LBLDURATIONS,
        )
        self._chk_disablenmea = Checkbutton(
            self._frm_advanced,
            text=LBLDISNMEA,
            variable=self.disable_nmea,
        )
        self._spn_duration = Spinbox(
            self._frm_advanced,
            values=DURATIONS,
            width=5,
            state=READONLY,
            wrap=True,
            repeatdelay=RPTDELAY,
            repeatinterval=RPTDELAY,
            textvariable=self.duration,
        )
        self._lbl_elapsed = Label(
            self._frm_advanced,
            text="",
        )
        self._pgb_elapsed = Progressbar(
            self._frm_advanced,
            orient="horizontal",
            mode="determinate",
            length=150,
        )
        self._spn_posmode = Spinbox(
            self._frm_advanced,
            values=POSMODES,
            width=6,
            state=READONLY,
            wrap=True,
            repeatdelay=RPTDELAY,
            repeatinterval=RPTDELAY,
            textvariable=self.pos_mode,
        )
        self._lbl_fixedlat = Label(
            self._frm_advanced,
            text="Lat",
        )
        self._ent_fixedlat = Entry(
            self._frm_advanced,
            textvariable=self.fixedlat,
            relief="sunken",
            width=18,
        )
        self._lbl_fixedlon = Label(
            self._frm_advanced,
            text="Lon",
        )
        self._ent_fixedlon = Entry(
            self._frm_advanced,
            textvariable=self.fixedlon,
            relief="sunken",
            width=18,
        )
        self._lbl_fixedhae = Label(
            self._frm_advanced,
            text="Height (m)",
        )
        self._ent_fixedhae = Entry(
            self._frm_advanced,
            textvariable=self.fixedhae,
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
        self._lbl_sockmode.grid(column=2, row=0, padx=2, pady=1, sticky=W)
        self._spn_sockmode.grid(column=3, row=0, padx=2, pady=1, sticky=W)
        self._lbl_sockhost.grid(column=0, row=2, padx=2, pady=1, sticky=W)
        self._ent_sockhost.grid(column=1, row=2, padx=2, pady=1, sticky=W)
        self._lbl_sockport.grid(column=2, row=2, padx=2, pady=1, sticky=W)
        self._ent_sockport.grid(column=3, row=2, padx=2, pady=1, sticky=W)
        self._lbl_publicipl.grid(column=0, row=3, padx=2, pady=1, sticky=W)
        self._lbl_publicip.grid(column=1, row=3, padx=2, pady=1, sticky=W)
        self._lbl_lanipl.grid(column=0, row=4, padx=2, pady=1, sticky=W)
        self._lbl_lanip.grid(column=1, row=4, padx=2, pady=1, sticky=W)
        self._lbl_clients.grid(column=2, row=3, rowspan=2, padx=2, pady=1, sticky=W)
        self._lbl_sockclients.grid(column=3, row=3, rowspan=2, padx=2, pady=1, sticky=W)
        self._btn_toggle.grid(column=4, row=0, sticky=E)
        self._frm_advanced.grid_forget()
        self._lbl_configure_base.grid(column=0, row=0, padx=2, pady=2, sticky=W)
        self._spn_rcvrtype.grid(column=1, row=0, columnspan=2, padx=2, pady=1, sticky=W)
        self._btn_configure_base.grid(column=3, row=0, padx=2, pady=2, sticky=W)
        self._lbl_basemode.grid(column=0, row=1, padx=2, pady=1, sticky=E)
        self._spn_basemode.grid(column=1, row=1, padx=2, pady=1, sticky=W)

    def reset(self):
        """
        Reset settings to defaults.
        """

        self._bind_events(False)
        cfg = self.__app.configuration
        self._socket_serve.set(cfg.get("sockserver_b"))
        self.sock_mode.set(SOCKMODES[cfg.get("sockmode_b")])
        self._on_toggle_advanced()
        self.base_mode.set(cfg.get("ntripcasterbasemode_s"))
        self._on_basemode(None, None, "write")
        self.receiver_type.set(cfg.get("ntripcasterrcvrtype_s"))
        self.acclimit.set(cfg.get("ntripcasteracclimit_f"))
        self.duration.set(cfg.get("ntripcasterduration_n"))
        self.pos_mode.set(cfg.get("ntripcasterposmode_s"))
        self._on_posmode(None, None, "write")
        self.fixedlat.set(cfg.get("ntripcasterfixedlat_f"))
        self.fixedlon.set(cfg.get("ntripcasterfixedlon_f"))
        self.fixedhae.set(cfg.get("ntripcasterfixedalt_f"))
        self.disable_nmea.set(cfg.get("ntripcasterdisablenmea_b"))
        self.sock_host.set(cfg.get("sockhost_s"))
        self._lbl_publicip.config(text=publicip())
        self._lbl_lanip.config(text=lanip())
        self.sock_port.set(cfg.get("sockport_n"))
        self.user.set(cfg.get("ntripcasteruser_s"))
        self.password.set(cfg.get("ntripcasterpassword_s"))
        self.clients = 0
        self._sock_port_temp = self.sock_port.get()
        self._fixed_lat_temp = self.fixedlat.get()
        self._fixed_lon_temp = self.fixedlon.get()
        self._fixed_hae_temp = self.fixedhae.get()
        self._bind_events(True)

    def _attach_events(self):
        """
        Bind events to variables.
        """

        self.bind("<Configure>", self._on_resize)

    def _bind_events(self, add: bool = True):
        """
        Add or remove event bindings to/from widgets.

        :param bool add: add or remove binding
        """

        tracemode = ("write", "unset")
        if add:
            self._socket_serve.trace_add(tracemode, self._on_socket_serve)
            self.sock_mode.trace_add(tracemode, self._on_sockmode)
            self.base_mode.trace_add(tracemode, self._on_basemode)
            self.pos_mode.trace_add(tracemode, self._on_posmode)
        else:
            for setting in (
                self._socket_serve,
                self.sock_mode,
                self.base_mode,
                self.pos_mode,
            ):
                if len(setting.trace_info()) > 0:
                    setting.trace_remove(tracemode, setting.trace_info()[0][1])

        tracemode = "write"
        for setting in (
            self.sock_port,
            self.sock_host,
            self.receiver_type,
            self.acclimit,
            self.duration,
            self.fixedlat,
            self.fixedlon,
            self.fixedhae,
            self.disable_nmea,
            self.user,
            self.password,
        ):
            if add:
                setting.trace_add(tracemode, self._on_update_config)
            else:
                if len(setting.trace_info()) > 0:
                    setting.trace_remove(tracemode, setting.trace_info()[0][1])

    def _on_update_config(self, var, index, mode):  # pylint: disable=unused-argument
        """
        Update in-memory configuration if setting is changed.
        """

        try:
            self.update()
            cfg = self.__app.configuration
            cfg.set("ntripcasterrcvrtype_s", self.receiver_type.get())
            cfg.set("ntripcasteracclimit_f", float(self.acclimit.get()))
            cfg.set("ntripcasterduration_n", int(self.duration.get()))
            cfg.set("ntripcasterfixedlat_f", float(self.fixedlat.get()))
            cfg.set("ntripcasterfixedlon_f", float(self.fixedlon.get()))
            cfg.set("ntripcasterfixedalt_f", float(self.fixedhae.get()))
            cfg.set("ntripcasterdisablenmea_b", self.disable_nmea.get())
            cfg.set("sockhost_s", self.sock_host.get())
            cfg.set("sockport_n", int(self.sock_port.get()))
            cfg.set("ntripcasteruser_s", self.user.get())
            cfg.set("ntripcasterpassword_s", self.password.get())
            # self.sockserve, self.sock_mode, self.base_mode & self.pos_mode
            # are updated in their respective routines below
        except (ValueError, TclError):
            pass

    def _on_configure_base(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Send commands to configure base station.
        """

        if self.sock_mode.get() == SOCK_NTRIP:
            self._config_rcvr()

    def set_status(self, status: int):
        """
        Set connection status, which determines whether controls
        are enabled or not: 0=DISCONNECTED, 1=CONNECTED

        :param int status: status (0,1)
        """

        if status == DISCONNECTED:
            self._chk_socketserve.configure(state=DISABLED)
            self._socket_serve.set(0)
            self.clients = 0
        else:
            self._chk_socketserve.configure(state=NORMAL)

    def _on_socket_serve(self, var, index, mode):
        """
        Action when socket_serve variable is updated.
        Start or stop socket server.
        """

        self._quectel_restart = 0
        if self._socket_serve.get():
            # validate entries
            valid = True
            valid = valid & valid_entry(self._ent_sockhost, VALNONBLANK)
            valid = valid & valid_entry(self._ent_sockport, VALINT, 1, MAXPORT)
            valid = valid & valid_entry(self._ent_fixedlat, VALFLOAT)
            valid = valid & valid_entry(self._ent_fixedlon, VALFLOAT)
            valid = valid & valid_entry(self._ent_fixedhae, VALFLOAT)
            if valid:
                self.__app.set_status("", INFOCOL)
            else:
                self.__app.set_status("ERROR - invalid entry", ERRCOL)
                self._socket_serve.set(0)
                return
            # start server
            self.__app.start_sockserver_thread()
            self.__app.stream_handler.sock_serve = True
            self._sock_port_temp = self.sock_port.get()
            self._fixed_lat_temp = self.fixedlat.get()
            self._fixed_lon_temp = self.fixedlon.get()
            self._fixed_hae_temp = self.fixedhae.get()
        else:  # stop server
            self.__app.stop_sockserver_thread()
            self.__app.stream_handler.sock_serve = False
            self.clients = 0

        # set visibility of various fields depending on server status
        for wid in (
            self._ent_sockhost,
            self._ent_sockport,
            self._spn_sockmode,
            self._spn_rcvrtype,
            self._lbl_basemode,
            self._spn_basemode,
            self._lbl_acclimit,
            self._spn_acclimit,
            self._lbl_duration,
            self._spn_duration,
            self._chk_disablenmea,
            self._spn_posmode,
            self._lbl_fixedlat,
            self._lbl_fixedlon,
            self._lbl_fixedhae,
            self._lbl_user,
            self._ent_user,
            self._lbl_password,
            self._ent_password,
        ):
            if self._socket_serve.get():
                state = DISABLED
            else:
                state = READONLY if isinstance(wid, Spinbox) else NORMAL
            wid.config(state=state)
        for wid in (
            self._ent_fixedlat,
            self._ent_fixedlon,
            self._ent_fixedhae,
        ):
            if self._socket_serve.get():
                state = DISABLED
            else:
                state = READONLY if self.base_mode.get() == BASE_SVIN else NORMAL
            wid.config(state=state)
        for wid in (self._btn_configure_base,):
            if self._socket_serve.get():
                state = DISABLED
            else:
                state = NORMAL
            wid.config(state=state)
        self._lbl_elapsed.config(text="")
        self.__app.configuration.set("sockserver_b", int(self._socket_serve.get()))

    def _on_toggle_advanced(self):
        """
        Toggle advanced socket settings panel on or off
        if server mode is "NTRIP Caster".
        """

        if self.sock_mode.get() != SOCK_NTRIP:
            return
        self._show_advanced = not self._show_advanced
        self._set_advanced()

    def _set_advanced(self):
        """
        Set visibility of advanced socket server settings panel.
        """

        if self._show_advanced:
            self._frm_advanced.grid(column=0, row=1, columnspan=5, sticky=(W, E))
            self._btn_toggle.config(image=self._img_contract)
        else:
            self._frm_advanced.grid_forget()
            self._btn_toggle.config(image=self._img_expand)

    def _on_sockmode(self, var, index, mode):
        """
        Action when sock_mode variable is updated (SOCKET SERVER/NTRIP CASTER).
        Set default port and expand button depending on socket server mode.
        """

        if self.sock_mode.get() == SOCK_NTRIP:
            self.sock_port.set(SOCKSERVER_NTRIP_PORT)
            self._btn_toggle.config(state=NORMAL)
            self._show_advanced = True
            sockmode = 1
        else:
            self.sock_port.set(self._sock_port_temp)
            self._btn_toggle.config(state=DISABLED)
            self._show_advanced = False
            sockmode = 0
        self._set_advanced()
        self.__app.configuration.set("sockmode_b", sockmode)

    def _on_basemode(self, var, index, mode):
        """
        Action when base_mode is updated (SVIN/FIXED).
        Set field visibility depending on base mode.
        """

        if self.base_mode.get() == BASE_SVIN:
            self._on_basemode_svin()
        elif self.base_mode.get() == BASE_FIXED:
            self._on_basemode_fixed()
        else:  # Disabled
            self._on_basemode_disabled()
        self.__app.configuration.set("ntripcasterbasemode_s", self.base_mode.get())

    def _on_basemode_svin(self):
        """
        Set SURVEY-IN base mode.
        """

        self._lbl_acclimit.grid(column=0, row=2, padx=2, pady=1, sticky=E)
        self._spn_acclimit.grid(column=1, row=2, padx=2, pady=1, sticky=W)
        self._chk_disablenmea.grid(column=2, row=1, padx=2, pady=1, sticky=W)
        self._spn_posmode.grid(column=0, row=3, rowspan=3, padx=2, pady=1, sticky=E)
        self._lbl_fixedlat.grid(column=1, row=3, padx=2, pady=1, sticky=E)
        self._ent_fixedlat.grid(column=2, row=3, columnspan=3, padx=2, pady=1, sticky=W)
        self._lbl_fixedlon.grid(column=1, row=4, padx=2, pady=1, sticky=E)
        self._ent_fixedlon.grid(column=2, row=4, columnspan=3, padx=2, pady=1, sticky=W)
        self._lbl_fixedhae.grid(column=1, row=5, padx=2, pady=1, sticky=E)
        self._ent_fixedhae.grid(column=2, row=5, columnspan=3, padx=2, pady=1, sticky=W)
        self._lbl_user.grid(column=0, row=6, padx=2, pady=1, sticky=E)
        self._ent_user.grid(column=1, row=6, columnspan=2, padx=2, pady=1, sticky=W)
        self._lbl_password.grid(column=0, row=7, padx=2, pady=1, sticky=E)
        self._ent_password.grid(column=1, row=7, columnspan=2, padx=2, pady=1, sticky=W)
        for wid in self._ent_fixedlat, self._ent_fixedlon, self._ent_fixedhae:
            wid.config(state=DISABLED)

    def _on_basemode_fixed(self):
        """
        Set FIXED base mode.
        """

        self._lbl_acclimit.grid(column=0, row=2, padx=2, pady=1, sticky=E)
        self._spn_acclimit.grid(column=1, row=2, padx=2, pady=1, sticky=W)
        self._chk_disablenmea.grid(column=2, row=1, padx=2, pady=1, sticky=W)
        self._spn_posmode.grid(column=0, row=3, rowspan=3, padx=2, pady=1, sticky=E)
        self._lbl_fixedlat.grid(column=1, row=3, padx=2, pady=1, sticky=E)
        self._ent_fixedlat.grid(column=2, row=3, columnspan=3, padx=2, pady=1, sticky=W)
        self._lbl_fixedlon.grid(column=1, row=4, padx=2, pady=1, sticky=E)
        self._ent_fixedlon.grid(column=2, row=4, columnspan=3, padx=2, pady=1, sticky=W)
        self._lbl_fixedhae.grid(column=1, row=5, padx=2, pady=1, sticky=E)
        self._ent_fixedhae.grid(column=2, row=5, columnspan=3, padx=2, pady=1, sticky=W)
        self._lbl_user.grid(column=0, row=6, padx=2, pady=1, sticky=E)
        self._ent_user.grid(column=1, row=6, columnspan=2, padx=2, pady=1, sticky=W)
        self._lbl_password.grid(column=0, row=7, padx=2, pady=1, sticky=E)
        self._ent_password.grid(column=1, row=7, columnspan=2, padx=2, pady=1, sticky=W)
        self._lbl_duration.grid_forget()
        self._spn_duration.grid_forget()
        self._pgb_elapsed.grid_forget()
        self._lbl_elapsed.grid_forget()
        for wid in self._ent_fixedlat, self._ent_fixedlon, self._ent_fixedhae:
            wid.config(state=NORMAL)
        self._set_coords(self.pos_mode.get())

    def _on_basemode_disabled(self):
        """
        Set DISABLED base mode.
        """

        self._chk_disablenmea.grid(column=2, row=1, padx=2, pady=1, sticky=W)
        self._lbl_acclimit.grid_forget()
        self._spn_acclimit.grid_forget()
        self._spn_posmode.grid_forget()
        self._lbl_fixedlat.grid_forget()
        self._ent_fixedlat.grid_forget()
        self._lbl_fixedlon.grid_forget()
        self._ent_fixedlon.grid_forget()
        self._lbl_fixedhae.grid_forget()
        self._ent_fixedhae.grid_forget()
        self._lbl_duration.grid_forget()
        self._spn_duration.grid_forget()
        self._pgb_elapsed.grid_forget()
        self._lbl_elapsed.grid_forget()
        self._lbl_user.grid_forget()
        self._ent_user.grid_forget()
        self._lbl_password.grid_forget()
        self._ent_password.grid_forget()

    def _on_posmode(self, var, index, mode):
        """
        Action when pos_mode variable is updated (LLH/ECEF).
        Set fixed reference labels depending on position mode (ECEF or LLH)
        """

        lbls = (
            ("Lat", "Lon", "Height (m)")
            if self.pos_mode.get() == POS_LLH
            else ("X (m)", "Y (m)", "Z (m)")
        )
        self._lbl_fixedlat.config(text=lbls[0])
        self._lbl_fixedlon.config(text=lbls[1])
        self._lbl_fixedhae.config(text=lbls[2])
        self._set_coords(self.pos_mode.get())
        self.__app.configuration.set("ntripcasterposmode_s", self.pos_mode.get())

    def _set_coords(self, posmode: str):
        """
        Set current coordinates in LLH or ECEF format from either:
        - values provided in configuration file or, if blank/zero,
        - current receiver position

        :param str posmode: position mode (LLH or ECEF)
        """

        lat = self._fixed_lat_temp
        lon = self._fixed_lon_temp
        hae = self._fixed_hae_temp
        if lat in ("", "0", 0) and lon in ("", "0", 0) and hae in ("", "0", 0):
            # live position
            status = self.__app.get_coordinates()
            lat, lon, hae = status["lat"], status["lon"], status["hae"]
        try:
            if posmode == POS_ECEF:
                lat, lon, hae = llh2ecef(lat, lon, hae)
        except TypeError:  # e.g. no fix
            lat = lon = hae = 0.0
        self.fixedlat.set(lat)
        self.fixedlon.set(lon)
        self.fixedhae.set(hae)

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
        if self._socket_serve.get() in ("1", 1):
            self.__app.frm_banner.update_transmit_status(clients)

    def _config_rcvr(self):
        """
        Configure receiver as Base Station if in NTRIP caster mode.
        """

        delay = self.__app.configuration.get("guiupdateinterval_f") / 2
        # set base station timing mode
        if self.base_mode.get() == BASE_SVIN:
            cmds = self._config_svin(self.acclimit.get(), self.duration.get())
        elif self.base_mode.get() == BASE_FIXED:
            cmds = self._config_fixed(
                self.acclimit.get(),
                self.fixedlat.get(),
                self.fixedlon.get(),
                self.fixedhae.get(),
            )
        else:  # DISABLED
            cmds = self._config_disable()
        if not isinstance(cmds, list):
            cmds = [
                cmds,
            ]
        for cmd in cmds:
            # self.logger.debug(f"Base Config Message: {cmd}")
            if isinstance(cmd, (UBXMessage, NMEAMessage)):
                self.__app.gnss_outqueue.put(cmd.serialize())
            elif isinstance(cmd, str):  # TTY ASCII string
                self.__app.gnss_outqueue.put(cmd.encode(ASCII, errors=BSR))
                sleep(delay)  # add delay between each TTY command
            else:  # raw bytes
                self.__app.gnss_outqueue.put(cmd)

        if self.receiver_type.get() == ZED_F9:
            # set RTCM and UBX NAV-SVIN message output rate
            rate = 0 if self.base_mode.get() == BASE_DISABLED else 1
            for port in ("USB", "UART1"):
                msg = self._config_msg_rates(rate, port)
                self.__app.gnss_outqueue.put(msg.serialize())
                msg = config_nmea(self.disable_nmea.get(), port)
                self.__app.gnss_outqueue.put(msg.serialize())
        elif self.receiver_type.get() == LG290P:
            # poll for confirmation that rcvr has restarted,
            # then resend configuration commands a 2nd time
            self._pending_confs[PQTMVER] = SERVERCONFIG

    def _config_msg_rates(self, rate: int, port_type: str) -> UBXMessage:
        """
        Configure RTCM3 and UBX NAV-SVIN message rates.

        :param int rate: message rate (0 = off)
        :param str port_type: port that rcvr is connected on
        """

        layers = 1  # 1 = RAM, 2 = BBR, 4 = Flash (can be OR'd)
        transaction = 0
        cfg_data = []
        for rtcm_type, mrate in RTCMTYPES.items():

            cfg = f"CFG_MSGOUT_RTCM_3X_TYPE{rtcm_type}_{port_type}"
            cfg_data.append([cfg, mrate if rate else 0])

        # NAV-SVIN only output in SURVEY-IN mode
        rate = rate if self.base_mode.get() == BASE_SVIN else 0
        cfg = f"CFG_MSGOUT_UBX_NAV_SVIN_{port_type}"
        cfg_data.append([cfg, rate])

        return UBXMessage.config_set(layers, transaction, cfg_data)

    def _config_disable(self) -> object:
        """
        Disable base station mode.

        :return: one or more UBXMessage, NMEAMessage or bytes
        :rtype: UBXMessage or list
        """

        if self.receiver_type.get() == LG290P:
            return self._config_disable_quectel()
        if self.receiver_type.get() == MOSAIC_X5:
            return self._config_disable_septentrio()
        return self._config_disable_ublox()

    def _config_disable_ublox(self) -> UBXMessage:
        """
        Disable base station mode for u-blox receivers.

        :return: UBXMessage
        :rtype: UBXMessage
        """

        layers = 1
        transaction = 0
        cfg_data = [
            ("CFG_TMODE_MODE", TMODE_DISABLED),
        ]

        return UBXMessage.config_set(layers, transaction, cfg_data)

    def _config_disable_quectel(self) -> list:
        """
        Disable base station mode for Quectel receivers.

        NB: A 'feature' of Quectel firmware is that some command sequences
        require multiple restarts before taking effect.

        :return: list of NMEAMessage(s)
        :rtype: list
        """

        msgs = []
        msgs.append(NMEAMessage("P", "QTMCFGRCVRMODE", SET, rcvrmode=1))
        msgs.append(NMEAMessage("P", "QTMSAVEPAR", SET))
        msgs.append(NMEAMessage("P", "QTMSRR", SET))
        return msgs

    def _config_disable_septentrio(self) -> list:
        """
        Disable base station mode for Septentrio receivers.

        :return: ASCII TTY commands
        :rtype: list
        """

        msgs = []
        # msgs.append("SSSSSSSSSS\r\n")
        msgs.append("SSSSSSSSSS\r\n")
        msgs.append("erst,soft,config\r\n")
        return msgs

    def _config_svin(self, acc_limit: int, svin_min_dur: int) -> object:
        """
        Configure Survey-In mode with specied accuracy limit.

        :param int acc_limit: accuracy limit in cm
        :param int svin_min_dur: survey minimimum duration
        :return: one or more UBXMessage, NMEAMessage or bytes
        :rtype: UBXMessage or list
        """

        if self.receiver_type.get() == LG290P:
            return self._config_svin_quectel(acc_limit, svin_min_dur)
        if self.receiver_type.get() == MOSAIC_X5:
            return self._config_svin_septentrio(acc_limit, svin_min_dur)
        return self._config_svin_ublox(acc_limit, svin_min_dur)

    def _config_svin_ublox(self, acc_limit: int, svin_min_dur: int) -> UBXMessage:
        """
        Configure Survey-In mode with specified accuracy limit for u-blox receivers.

        :param int acc_limit: accuracy limit in cm
        :param int svin_min_dur: survey minimimum duration
        :return: UBXMessage
        :rtype: UBXMessage
        """

        layers = 1
        transaction = 0
        acc_limit = int(acc_limit * 100)  # convert to 0.1 mm
        cfg_data = [
            ("CFG_TMODE_MODE", TMODE_SVIN),
            ("CFG_TMODE_SVIN_ACC_LIMIT", acc_limit),
            ("CFG_TMODE_SVIN_MIN_DUR", svin_min_dur),
        ]

        return UBXMessage.config_set(layers, transaction, cfg_data)

    def _config_svin_quectel(self, acc_limit: int, svin_min_dur: int) -> list:
        """
        Configure Survey-In mode with specified accuracy limit for Quectel receivers.

        NB: A 'feature' of Quectel firmware is that some command sequences
        require multiple restarts before taking effect.

        :param int acc_limit: accuracy limit in cm
        :param int svin_min_dur: survey minimimum duration
        :return: list of NMEAMessage(s)
        :rtype: list
        """

        msgs = []
        msgs.append(NMEAMessage("P", "QTMCFGRCVRMODE", SET, rcvrmode=2))
        msgs.append(
            NMEAMessage(
                "P",
                "QTMCFGRTCM",
                SET,
                msmtype=7,  # MSM 7 types e.g. 1077
                msmmode=0,
                msmelevthd=-90,
                reserved1="07",
                reserved2="06",
                ephmode=1,
                ephinterval=0,
            )
        )
        msgs.append(
            NMEAMessage(
                "P",
                "QTMCFGSVIN",
                SET,
                svinmode=1,
                cfgcnt=svin_min_dur,
                acclimit=acc_limit / 100,  # m
            )
        )
        msgs.append(NMEAMessage("P", "QTMSAVEPAR", SET))
        msgs.append(NMEAMessage("P", "QTMSRR", SET))
        return msgs

    def _config_svin_septentrio(self, acc_limit: int, svin_min_dur: int) -> list:
        """
        Configure Survey-In mode with specified accuracy limit for Septentrio receivers.

        :param int acc_limit: accuracy limit in cm
        :param int svin_min_dur: survey minimimum duration
        :return: ASCII TTY commands
        :rtype: list
        """

        msgs = []
        msgs.append("SSSSSSSSSS\r\n")
        msgs.append("setDataInOut, COM1, ,RTCMv3\r\n")
        msgs.append("setRTCMv3Formatting,1234\r\n")
        msgs.append(
            "setRTCMv3Output,COM1,RTCM1006+RTCM1033+RTCM1077+RTCM1087+"
            "RTCM1097+RTCM1107+RTCM1117+RTCM1127+RTCM1137+RTCM1230\r\n"
        )
        msgs.append("setPVTMode,Static, ,auto\r\n")
        return msgs

    def _config_fixed(
        self, acc_limit: int, lat: float, lon: float, height: float
    ) -> object:
        """
        Configure Fixed mode with specified coordinates.

        :param int acc_limit: accuracy limit in cm
        :param float lat: lat or X in m
        :param float lon: lon or Y in m
        :param float height: height or Z in m
        :return: one or more UBXMessage, NMEAMessage or bytes
        :rtype: UBXMessage or list
        """

        if self.receiver_type.get() == LG290P:
            return self._config_fixed_quectel(acc_limit, lat, lon, height)
        if self.receiver_type.get() == MOSAIC_X5:
            return self._config_fixed_septentrio(acc_limit, lat, lon, height)
        return self._config_fixed_ublox(acc_limit, lat, lon, height)

    def _config_fixed_ublox(
        self, acc_limit: int, lat: float, lon: float, height: float
    ) -> UBXMessage:
        """
        Configure Fixed mode with specified coordinates for u-blox receivers.

        :param int acc_limit: accuracy limit in cm
        :param float lat: lat or X in m
        :param float lon: lon or Y in m
        :param float height: height or Z in m
        :return: UBXMessage
        :rtype: UBXMessage
        """

        layers = 1
        transaction = 0
        acc_limit = int(acc_limit * 100)  # convert to 0.1 mm
        if self.pos_mode.get() == POS_LLH:
            lat_sp, lat_hp = val2sphp(lat, 1e-7)
            lon_sp, lon_hp = val2sphp(lon, 1e-7)
            height_sp, height_hp = val2sphp(height, 0.01)
            cfg_data = [
                ("CFG_TMODE_MODE", TMODE_FIXED),
                ("CFG_TMODE_POS_TYPE", LLH),
                ("CFG_TMODE_FIXED_POS_ACC", acc_limit),
                ("CFG_TMODE_LAT", lat_sp),
                ("CFG_TMODE_LAT_HP", lat_hp),
                ("CFG_TMODE_LON", lon_sp),
                ("CFG_TMODE_LON_HP", lon_hp),
                ("CFG_TMODE_HEIGHT", height_sp),
                ("CFG_TMODE_HEIGHT_HP", height_hp),
            ]
        else:  # ECEF
            x_sp, x_hp = val2sphp(lat, 0.01)
            y_sp, y_hp = val2sphp(lon, 0.01)
            z_sp, z_hp = val2sphp(height, 0.01)
            cfg_data = [
                ("CFG_TMODE_MODE", TMODE_FIXED),
                ("CFG_TMODE_POS_TYPE", ECEF),
                ("CFG_TMODE_FIXED_POS_ACC", acc_limit),
                ("CFG_TMODE_ECEF_X", x_sp),
                ("CFG_TMODE_ECEF_X_HP", x_hp),
                ("CFG_TMODE_ECEF_Y", y_sp),
                ("CFG_TMODE_ECEF_Y_HP", y_hp),
                ("CFG_TMODE_ECEF_Z", z_sp),
                ("CFG_TMODE_ECEF_Z_HP", z_hp),
            ]

        return UBXMessage.config_set(layers, transaction, cfg_data)

    def _config_fixed_quectel(
        self, acc_limit: int, lat: float, lon: float, height: float
    ) -> list:
        """
        Configure Fixed mode with specified coordinates for Quectel receivers.

        NB: A 'feature' of Quectel firmware is that some command sequences
        require multiple restarts before taking effect.

        :param int acc_limit: accuracy limit in cm
        :param float lat: lat or X in m
        :param float lon: lon or Y in m
        :param float height: height or Z in m
        :return: list of NMEAMessage(s)
        :rtype: list
        """

        if self._spn_posmode.get() == POS_LLH:
            ecef_x, ecef_y, ecef_z = llh2ecef(lat, lon, height)
        else:  # POS_ECEF
            ecef_x, ecef_y, ecef_z = lat, lon, height

        msgs = []
        msgs.append(NMEAMessage("P", "QTMCFGRCVRMODE", SET, rcvrmode=2))
        msgs.append(
            NMEAMessage(
                "P",
                "QTMCFGRTCM",
                SET,
                msmtype=7,  # MSM 7 types e.g. 1077
                msmmode=0,
                msmelevthd=-90,
                reserved1="07",
                reserved2="06",
                ephmode=1,
                ephinterval=0,
            )
        )
        msgs.append(
            NMEAMessage(
                "P",
                "QTMCFGSVIN",
                SET,
                svinmode=2,
                cfgcnt=0,
                acclimit=acc_limit / 100,  # m
                ecefx=ecef_x,
                ecefy=ecef_y,
                ecefz=ecef_z,
            )
        )
        msgs.append(NMEAMessage("P", "QTMSAVEPAR", SET))
        msgs.append(NMEAMessage("P", "QTMSRR", SET))
        return msgs

    def _config_fixed_septentrio(
        self, acc_limit: int, lat: float, lon: float, height: float
    ) -> list:
        """
        Configure Fixed mode with specified coordinates for Septentrio receivers.

        :param int acc_limit: accuracy limit in cm
        :param float lat: lat or X in m
        :param float lon: lon or Y in m
        :param float height: height or Z in m
        :return: ASCII TTY commands
        :rtype: list
        """

        msgs = []
        msgs.append("SSSSSSSSSS\r\n")
        msgs.append("setDataInOut,COM1, ,RTCMv3\r\n")
        msgs.append("setRTCMv3Formatting,1234\r\n")
        msgs.append(
            "setRTCMv3Output,COM1,RTCM1006+RTCM1033+RTCM1077+RTCM1087+"
            "RTCM1097+RTCM1107+RTCM1117+RTCM1127+RTCM1137+RTCM1230\r\n"
        )
        msgs.append(
            f"setStaticPosGeodetic,Geodetic1,{lat:.8f},{lon:.8f},{height:.4f}\r\n"
        )
        msgs.append("setPVTMode,Static, ,Geodetic1\r\n")
        return msgs

    def _on_quectel_restart(self):
        """
        Action(s) when Quectel receiver has restarted.
        """

        self._quectel_restart += 1
        if self.base_mode.get() in (BASE_SVIN, BASE_FIXED):
            # if first restart, send config commands a 2nd time
            if self._quectel_restart == 1:
                self._config_rcvr()
            # if second restart and survey-in mode, enable SVIN status message
            if self.base_mode.get() == BASE_SVIN and self._quectel_restart == 2:
                cmd = NMEAMessage(
                    "P",
                    "QTMCFGMSGRATE",
                    SET,
                    msgname="PQTMSVINSTATUS",
                    rate=1,
                    msgver=1,
                )
                self.__app.gnss_outqueue.put(cmd.serialize())

    def svin_countdown(self, ela: int, valid: bool, active: bool):
        """
        Display countdown of remaining survey-in duration.
        Invoked from ubx_handler or nmea_handler on receipt of SVIN status
        message from receiver.

        :param int ela: elapsed time
        :param bool valid: SVIN validity status
        :param bool active: SVIN active status
        """

        if self.base_mode.get() == BASE_SVIN and active and not valid:
            self._lbl_elapsed.grid_forget()
            self._pgb_elapsed.grid(
                column=2, row=2, columnspan=2, padx=2, pady=1, sticky=W
            )
            dur = self.duration.get()
            self._pgb_elapsed["value"] = 100 * (dur - ela) / dur
        elif self.base_mode.get() == BASE_SVIN and valid:
            self._pgb_elapsed.grid_forget()
            self._lbl_elapsed.grid(
                column=2, row=2, columnspan=2, padx=2, pady=1, sticky=W
            )
            self._lbl_elapsed.config(text="SVIN Valid")
        else:
            self._lbl_elapsed.grid_forget()
            self._pgb_elapsed.grid_forget()

    @property
    def socketserving(self) -> bool:
        """
        Getter for socket serve flag.

        :return: server running True/False
        :rtype: bool
        """

        return self._socket_serve.get()

    @socketserving.setter
    def socketserving(self, state: bool):
        """
        Setter for socket serve flag.

        :param bool state: server running True/False
        """

        return self._socket_serve.set(state)

    def _on_resize(self, event):  # pylint: disable=unused-argument
        """
        Resize frame.

        :param event event: resize event
        """

        self.__app.frm_settings.on_expand()

    def update_pending(self, msg: object):
        """
        Receives polled confirmation (PQTMVER) message from the nmea
        handler and updates status.

        :param NMEAMessage msg: NMEA PQTMVER message
        """

        frm = self._pending_confs.get(msg.identity, None)
        if frm == SERVERCONFIG:
            # reset all confirmation flags for this frame
            self._pending_confs.pop(PQTMVER)
            self._on_quectel_restart()

    def update_base_location(self):
        """
        Update base station location from RTCM 1005/6 message after Survey-in.
        """

        if self.base_mode.get() in (BASE_FIXED, BASE_SVIN):
            if self.pos_mode.get() == POS_ECEF:
                self.fixedlat.set(self.__app.gnss_status.base_ecefx)
                self.fixedlon.set(self.__app.gnss_status.base_ecefy)
                self.fixedhae.set(self.__app.gnss_status.base_ecefz)
            else:
                lat, lon, hae = ecef2llh(
                    self.__app.gnss_status.base_ecefx,
                    self.__app.gnss_status.base_ecefy,
                    self.__app.gnss_status.base_ecefz,
                )
                self.fixedlat.set(round(lat, 8))
                self.fixedlon.set(round(lon, 8))
                self.fixedhae.set(round(hae, 4))
