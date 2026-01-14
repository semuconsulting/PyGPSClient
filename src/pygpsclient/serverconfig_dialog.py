"""
serverconfig_dialog.py

Socket Server / NTRIP caster configuration panel Dialog class.
Supports two modes of operation - Socket Server and NTRIP Caster.

If running in NTRIP Caster mode, two base station modes are available -
Survey-In and Fixed. The panel provides methods to configure RTK-compatible
receiver (e.g. ZED-F9P or LG290P) to operate in either of these base station modes.

Application icons from https://iconmonstr.com/license/.

Created on 23 Jul 2023

:author: semuadmin (Steve Smith)
:copyright: 2020 semuadmin
:license: BSD 3-Clause
"""

# pylint: disable=unused-argument, too-many-lines

import logging
from pathlib import Path
from time import sleep
from tkinter import (
    DISABLED,
    EW,
    NORMAL,
    NSEW,
    BooleanVar,
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
from pynmeagps import NMEAMessage, ecef2llh, llh2ecef
from pyubx2 import SET_LAYER_RAM, TXN_NONE, UBXMessage

from pygpsclient.globals import (
    ASCII,
    BSR,
    DISCONNECTED,
    ERRCOL,
    ICON_CONTRACT,
    ICON_EXPAND,
    ICON_SEND,
    INFOCOL,
    LC29H,
    LG290P,
    MOSAIC_X5,
    READONLY,
    SERVERCONFIG,
    TRACEMODE_WRITE,
    VALFLOAT,
    VALINT,
    VALNONBLANK,
    ZED_F9,
    ZED_X20,
)
from pygpsclient.helpers import (
    MAXPORT,
    lanip,
    publicip,
)
from pygpsclient.receiver_config_handler import (
    config_disable_lc29h,
    config_disable_lg290p,
    config_disable_septentrio,
    config_disable_ublox,
    config_fixed_lc29h,
    config_fixed_lg290p,
    config_fixed_septentrio,
    config_fixed_ublox,
    config_nmea,
    config_svin_lc29h,
    config_svin_lg290p,
    config_svin_quectel,
    config_svin_septentrio,
    config_svin_ublox,
)
from pygpsclient.strings import (
    DLGNOTLS,
    DLGTSERVER,
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
from pygpsclient.toplevel_dialog import ToplevelDialog

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
MAXSVIN = 15
POS_ECEF = "ECEF"
POS_LLH = "LLH"
PQTMVER = "PQTMVER"
POSMODES = (POS_LLH, POS_ECEF)
SOCK_NTRIP = "NTRIP CASTER"
SOCK_SERVER = "SOCKET SERVER"
SOCKMODES = (SOCK_SERVER, SOCK_NTRIP)


class ServerConfigDialog(ToplevelDialog):
    """
    Server configuration dialog class.
    """

    def __init__(self, app, *args, **kwargs):
        """
        Constructor.

        :param Frame app: reference to main tkinter application
        :param args: optional args to pass to Frame parent class
        :param kwargs: optional kwargs for value ranges, or to pass to Frame parent class
        """

        self.__app = app
        self.logger = logging.getLogger(__name__)
        super().__init__(app, DLGTSERVER)

        self._show_advanced = False
        self._socket_serve = BooleanVar()
        self.sock_port = StringVar()
        self.sock_host = StringVar()
        self.sock_mode = StringVar()
        self.receiver_type = StringVar()
        self.base_mode = StringVar()
        self.https = IntVar()
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
        self._fixed_lat_temp = 0
        self._fixed_lon_temp = 0
        self._fixed_hae_temp = 0
        self._pending_confs = {}
        self._quectel_restart = 0  # keep track of Quectel receiver restarts

        self._body()
        self._do_layout()
        self._reset()
        # self._attach_events() # done in reset
        self._attach_events1()
        self._finalise()

    def _body(self):
        """
        Set up widgets.
        """

        self._frm_body = Frame(self.container)
        self._frm_basic = Frame(self._frm_body)
        self._chk_socketserve = Checkbutton(
            self._frm_basic,
            text=LBLSOCKSERVE,
            variable=self._socket_serve,
            state=NORMAL,
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
        self._chk_https = Checkbutton(
            self._frm_basic,
            text="TLS",
            variable=self.https,
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
        self._btn_toggle = Button(
            self._frm_basic,
            command=self._on_toggle_advanced,
            image=self._img_expand,
            width=28,
            height=22,
            # state=DISABLED,
        )
        self._frm_advanced = Frame(self._frm_body)
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
            values=(ZED_F9, ZED_X20, LG290P, LC29H, MOSAIC_X5),
            width=18,
            state=READONLY,
            wrap=True,
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

        self._frm_body.grid(column=0, row=0, sticky=NSEW)
        self._frm_basic.grid(column=0, row=0, columnspan=5, sticky=EW)
        self._chk_socketserve.grid(
            column=0, row=0, columnspan=2, rowspan=2, padx=2, pady=1, sticky=W
        )
        self._lbl_sockmode.grid(column=2, row=0, padx=2, pady=1, sticky=W)
        self._spn_sockmode.grid(column=3, row=0, padx=2, pady=1, sticky=W)
        self._lbl_sockhost.grid(column=0, row=2, padx=2, pady=1, sticky=W)
        self._ent_sockhost.grid(column=1, row=2, padx=2, pady=1, sticky=W)
        self._lbl_sockport.grid(column=0, row=3, padx=2, pady=1, sticky=W)
        self._ent_sockport.grid(column=1, row=3, padx=2, pady=1, sticky=W)
        self._chk_https.grid(column=2, row=3, columnspan=2, padx=2, pady=1, sticky=W)
        self._lbl_publicipl.grid(column=0, row=4, padx=2, pady=1, sticky=W)
        self._lbl_publicip.grid(column=1, row=4, padx=2, pady=1, sticky=W)
        self._lbl_lanipl.grid(column=2, row=4, padx=2, pady=1, sticky=W)
        self._lbl_lanip.grid(column=3, row=4, padx=2, pady=1, sticky=W)
        self._btn_toggle.grid(column=4, row=0, sticky=E)
        self._frm_advanced.grid_forget()
        self._lbl_configure_base.grid(column=0, row=0, padx=2, pady=2, sticky=W)
        self._spn_rcvrtype.grid(column=1, row=0, columnspan=2, padx=2, pady=1, sticky=W)
        self._btn_configure_base.grid(column=3, row=0, padx=2, pady=2, sticky=W)
        self._lbl_basemode.grid(column=0, row=1, padx=2, pady=1, sticky=E)
        self._spn_basemode.grid(column=1, row=1, padx=2, pady=1, sticky=W)

    def _reset(self):
        """
        Reset settings to defaults.
        """

        self._attach_events(False)
        cfg = self.__app.configuration
        self._socket_serve.set(self.__app.server_status >= 0)
        self._set_controls()
        self.sock_mode.set(SOCKMODES[cfg.get("sockmode_b")])
        self._on_toggle_advanced()
        self.base_mode.set(cfg.get("ntripcasterbasemode_s"))
        self._on_update_basemode(None, None, TRACEMODE_WRITE)
        self.receiver_type.set(cfg.get("ntripcasterrcvrtype_s"))
        self.acclimit.set(cfg.get("ntripcasteracclimit_f"))
        self.duration.set(cfg.get("ntripcasterduration_n"))
        self.pos_mode.set(cfg.get("ntripcasterposmode_s"))
        self._on_update_posmode(None, None, TRACEMODE_WRITE)
        self.fixedlat.set(cfg.get("ntripcasterfixedlat_f"))
        self.fixedlon.set(cfg.get("ntripcasterfixedlon_f"))
        self.fixedhae.set(cfg.get("ntripcasterfixedalt_f"))
        self.disable_nmea.set(cfg.get("ntripcasterdisablenmea_b"))
        self.sock_host.set(cfg.get("sockhost_s"))
        https = cfg.get("sockhttps_b")
        pem = cfg.get("tlspempath_s")
        if https and not Path(pem).exists():
            err = DLGNOTLS.format(hostpem=pem)
            self.status_label = (err, ERRCOL)
            self.logger.error(err)
            cfg.set("sockhttps_b", 0)
            self._chk_https.config(state=DISABLED)
            https = 0
        self.https.set(https)
        self.after(5, lambda: self._lbl_publicip.config(text=publicip()))
        self.after(5, lambda: self._lbl_lanip.config(text=lanip()))
        if cfg.get("sockmode_b"):  # NTRIP CASTER
            self.sock_port.set(cfg.get("sockportntrip_n"))
        else:  # SOCKET SERVER
            self.sock_port.set(cfg.get("sockport_n"))
        self.user.set(cfg.get("ntripcasteruser_s"))
        self.password.set(cfg.get("ntripcasterpassword_s"))
        self._fixed_lat_temp = self.fixedlat.get()
        self._fixed_lon_temp = self.fixedlon.get()
        self._fixed_hae_temp = self.fixedhae.get()
        self._attach_events(True)

    def _attach_events1(self):
        """
        Bind resize events to variables.
        """

        self.bind("<Configure>", self._on_resize)

    def _attach_events(self, add: bool = True):
        """
        Add or remove event bindings to/from widgets.

        (trace_update() is a class extension method defined in globals.py)

        :param bool add: add or remove trace
        """

        tracemode = TRACEMODE_WRITE
        self._socket_serve.trace_update(tracemode, self._on_socketserve, add)
        self.sock_mode.trace_update(tracemode, self._on_update_sockmode, add)
        self.base_mode.trace_update(tracemode, self._on_update_basemode, add)
        self.pos_mode.trace_update(tracemode, self._on_update_posmode, add)
        self.sock_port.trace_update(tracemode, self._on_update_sockport, add)
        self.https.trace_update(tracemode, self._on_update_https, add)
        self.sock_host.trace_update(tracemode, self._on_update_sockhost, add)
        self.receiver_type.trace_update(tracemode, self._on_update_rcvrtype, add)
        self.acclimit.trace_update(tracemode, self._on_update_acclimit, add)
        self.duration.trace_update(tracemode, self._on_update_svinduration, add)
        self.fixedlat.trace_update(tracemode, self._on_update_fixedlat, add)
        self.fixedlon.trace_update(tracemode, self._on_update_fixedlon, add)
        self.fixedhae.trace_update(tracemode, self._on_update_fixedhae, add)
        self.disable_nmea.trace_update(tracemode, self._on_update_disablenmea, add)
        self.user.trace_update(tracemode, self._on_update_user, add)
        self.password.trace_update(tracemode, self._on_update_password, add)

    def valid_settings(self) -> bool:
        """
        Validate settings.

        :return: valid True/False
        :rtype: bool
        """

        valid = True
        valid = valid & self._ent_sockhost.validate(VALNONBLANK)
        valid = valid & self._ent_sockport.validate(VALINT, 1, MAXPORT)
        valid = valid & self._ent_fixedlat.validate(VALFLOAT)
        valid = valid & self._ent_fixedlon.validate(VALFLOAT)
        valid = valid & self._ent_fixedhae.validate(VALFLOAT)
        valid = valid & self._ent_user.validate(VALNONBLANK)
        valid = valid & self._ent_password.validate(VALNONBLANK)
        return valid

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
            self._frm_advanced.grid(column=0, row=1, columnspan=5, sticky=EW)
            self._btn_toggle.config(image=self._img_contract)
        else:
            self._frm_advanced.grid_forget()
            self._btn_toggle.config(image=self._img_expand)

    def set_status(self, status: int):
        """
        Set connection status, which determines whether controls
        are enabled or not: 0=DISCONNECTED, 1=CONNECTED

        :param int status: status (0,1)
        """

        if status == DISCONNECTED:
            self._chk_socketserve.configure(state=DISABLED)
            self._socket_serve.set(0)
        else:
            self._chk_socketserve.configure(state=NORMAL)

    def _on_socketserve(self, var, index, mode):
        """
        Action when socket server is started or stopped.
        """

        if self.valid_settings():
            self.status_label = ("", INFOCOL)
        else:
            self.status_label = ("ERROR - invalid entry", ERRCOL)
            return

        self._quectel_restart = 0
        if self._socket_serve.get():
            # start server
            self.__app.sockserver_start()
            # self.__app.stream_handler.sock_serve = True
            self._fixed_lat_temp = self.fixedlat.get()
            self._fixed_lon_temp = self.fixedlon.get()
            self._fixed_hae_temp = self.fixedhae.get()
        else:  # stop server
            self.__app.sockserver_stop()
            # self.__app.stream_handler.sock_serve = False

        self._set_controls()

    def _set_controls(self):
        """
        Set visibility of various fields depending on server status.
        """

        for wid in (
            self._ent_sockhost,
            self._ent_sockport,
            self._chk_https,
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

    def _on_configure_base(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Send commands to configure base station.
        """

        if self.sock_mode.get() == SOCK_NTRIP:
            self._config_receiver()

    def _config_receiver(self):
        """
        Configure receiver as Base Station if in NTRIP caster mode.
        """

        # pylint: disable=no-member

        # validate settings
        if self.valid_settings():
            self.status_label = ("", INFOCOL)
        else:
            self.status_label = ("ERROR - invalid entry", ERRCOL)
            return

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
                self.__app.send_to_device(cmd.serialize())
            elif isinstance(cmd, str):  # TTY ASCII string
                self.__app.send_to_device(cmd.encode(ASCII, errors=BSR))
                sleep(delay)  # add delay between each TTY command
            else:  # raw bytes
                self.__app.send_to_device(cmd)

        if self.receiver_type.get() in (ZED_F9, ZED_X20):
            # set RTCM and UBX NAV-SVIN message output rate
            rate = 0 if self.base_mode.get() == BASE_DISABLED else 1
            for port in ("USB", "UART1"):
                self._config_msg_rates(rate, port)
                # self.__app.send_to_device(msg.serialize())
                msg = config_nmea(self.disable_nmea.get(), port)
                self.__app.send_to_device(msg.serialize())
        elif self.receiver_type.get() == LG290P:
            # poll for confirmation that rcvr has restarted,
            # then resend configuration commands a 2nd time
            self._pending_confs[PQTMVER] = SERVERCONFIG
        elif self.receiver_type.get() == LC29H:
            # poll for confirmation warm start has finished
            pass

    def _on_update_sockhost(self, var, index, mode):
        """
        Action on update sockhost.
        """

        if self._ent_sockhost.validate(VALNONBLANK):
            self._chk_socketserve.config(state=NORMAL)
        else:
            self._chk_socketserve.config(state=DISABLED)
            return
        self.__app.configuration.set("sockhost_s", self.sock_host.get())

    def _on_update_sockport(self, var, index, mode):
        """
        Action when socket port is updated.
        """

        if self._ent_sockport.validate(VALINT, 1, MAXPORT):
            self._chk_socketserve.config(state=NORMAL)
        else:
            self._chk_socketserve.config(state=DISABLED)
            return

        try:
            if self.__app.configuration.get("sockmode_b"):  # NTRIP CASTER
                self.__app.configuration.set(
                    "sockportntrip_n", int(self.sock_port.get())
                )
            else:  # SOCKER SERVER
                self.__app.configuration.set("sockport_n", int(self.sock_port.get()))
            # if port ends 443, assume HTTPS; user can override
            self.https.set(str(self.sock_port.get())[-3:] == "443")
        except ValueError:
            pass

    def _on_update_rcvrtype(self, var, index, mode):
        """
        Action on update rcvrtype.
        """

        self.__app.configuration.set("ntripcasterrcvrtype_s", self.receiver_type.get())

    def _on_update_acclimit(self, var, index, mode):
        """
        Action on update acc limit.
        """

        self.__app.configuration.set(
            "ntripcasteracclimit_f", float(self.acclimit.get())
        )

    def _on_update_svinduration(self, var, index, mode):
        """
        Action on update ntrip caster survey-in duration.
        """

        self.__app.configuration.set("ntripcasterduration_n", int(self.duration.get()))

    def _on_update_fixedlat(self, var, index, mode):
        """
        Action on update fixed lat.
        """

        try:
            if self._ent_fixedlat.validate(VALFLOAT):
                self._btn_configure_base.config(state=NORMAL)
            else:
                self._btn_configure_base.config(state=DISABLED)
                return
            self.__app.configuration.set(
                "ntripcasterfixedlat_f", float(self.fixedlat.get())
            )
        except TclError:
            pass

    def _on_update_fixedlon(self, var, index, mode):
        """
        Action on update fixed lon.
        """

        try:
            if self._ent_fixedlon.validate(VALFLOAT):
                self._btn_configure_base.config(state=NORMAL)
            else:
                self._btn_configure_base.config(state=DISABLED)
                return
            self.__app.configuration.set(
                "ntripcasterfixedlon_f", float(self.fixedlon.get())
            )
        except TclError:
            pass

    def _on_update_fixedhae(self, var, index, mode):
        """
        Action on update fixed hae.
        """

        try:
            if self._ent_fixedhae.validate(VALFLOAT):
                self._btn_configure_base.config(state=NORMAL)
            else:
                self._btn_configure_base.config(state=DISABLED)
                return
            self.__app.configuration.set(
                "ntripcasterfixedalt_f", float(self.fixedhae.get())
            )
        except TclError:
            pass

    def _on_update_disablenmea(self, var, index, mode):
        """
        Action on update disable nmea.
        """

        try:
            self.__app.configuration.set(
                "ntripcasterdisablenmea_b", self.disable_nmea.get()
            )
        except TclError:
            pass

    def _on_update_user(self, var, index, mode):
        """
        Action on update ntripcaster user.
        """

        if not self._ent_user.validate(VALNONBLANK):
            return
        self.__app.configuration.set("ntripcasteruser_s", self.user.get())

    def _on_update_password(self, var, index, mode):
        """
        Action on update ntripcaster password.
        """

        if not self._ent_password.validate(VALNONBLANK):
            return
        self.__app.configuration.set("ntripcasterpassword_s", self.password.get())

    def _on_update_sockmode(self, var, index, mode):
        """
        Action when sock_mode variable is updated (SOCKET SERVER/NTRIP CASTER).
        Set default port and expand button depending on socket server mode.
        """

        if self.sock_mode.get() == SOCK_NTRIP:
            self._btn_toggle.config(state=NORMAL)
            self._show_advanced = True
            self.__app.configuration.set("sockmode_b", 1)
            self.sock_port.set(self.__app.configuration.get("sockportntrip_n"))
        else:
            self._btn_toggle.config(state=DISABLED)
            self._show_advanced = False
            self.__app.configuration.set("sockmode_b", 0)
            self.sock_port.set(self.__app.configuration.get("sockport_n"))
        self._set_advanced()

    def _on_update_https(self, var, index, mode):
        """
        Action when https flag is updated.
        """

        pem = self.__app.configuration.get("tlspempath_s")
        if self.https.get() and not Path(pem).exists():
            err = DLGNOTLS.format(hostpem=pem)
            self.status_label = (err, ERRCOL)
            self.logger.error(err)
            self._attach_events(False)
            self.https.set(0)
            self._chk_https.config(state=DISABLED)
            self._attach_events(True)
        self.__app.configuration.set("sockhttps_b", self.https.get())

    def _on_update_basemode(self, var, index, mode):
        """
        Action when base_mode is updated (SVIN/FIXED).
        Set field visibility depending on base mode.
        """

        if self.base_mode.get() == BASE_SVIN:
            self._on_update_basemode_svin()
        elif self.base_mode.get() == BASE_FIXED:
            self._on_update_basemode_fixed()
        else:  # Disabled
            self._on_update_basemode_disabled()
        self.__app.configuration.set("ntripcasterbasemode_s", self.base_mode.get())

    def _on_update_basemode_svin(self):
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

    def _on_update_basemode_fixed(self):
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

    def _on_update_basemode_disabled(self):
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

    def _on_update_posmode(self, var, index, mode):
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

    def _config_msg_rates(self, rate: int, port_type: str):
        """
        Configure RTCM3 and UBX NAV-SVIN message rates.

        :param int rate: message rate (0 = off)
        :param str port_type: port that rcvr is connected on
        """

        layers = SET_LAYER_RAM
        transaction = TXN_NONE
        for rtcm_type, mrate in RTCMTYPES.items():
            cfg = f"CFG_MSGOUT_RTCM_3X_TYPE{rtcm_type}_{port_type}"
            cfg_data = [(cfg, mrate if rate else 0)]
            msg = UBXMessage.config_set(layers, transaction, cfg_data)
            self.__app.send_to_device(msg.serialize())

        # NAV-SVIN only output in SURVEY-IN mode
        rate = rate if self.base_mode.get() == BASE_SVIN else 0
        cfg = f"CFG_MSGOUT_UBX_NAV_SVIN_{port_type}"
        cfg_data = [(cfg, rate)]
        msg = UBXMessage.config_set(layers, transaction, cfg_data)
        self.__app.send_to_device(msg.serialize())

    def _config_disable(self) -> object:
        """
        Disable base station mode.

        :return: one or more UBXMessage, NMEAMessage or bytes
        :rtype: UBXMessage or list
        """

        if self.receiver_type.get() == LG290P:
            return config_disable_lg290p()
        if self.receiver_type.get() == LC29H:
            return config_disable_lc29h()
        if self.receiver_type.get() == MOSAIC_X5:
            return config_disable_septentrio()
        return config_disable_ublox()

    def _config_svin(self, acc_limit: int, svin_min_dur: int) -> object:
        """
        Configure Survey-In mode with specied accuracy limit.

        :param int acc_limit: accuracy limit in cm
        :param int svin_min_dur: survey minimimum duration
        :return: one or more UBXMessage, NMEAMessage or bytes
        :rtype: UBXMessage or list
        """

        if self.receiver_type.get() == LG290P:
            return config_svin_lg290p(acc_limit, svin_min_dur)
        if self.receiver_type.get() == LC29H:
            return config_svin_lc29h(acc_limit, svin_min_dur)
        if self.receiver_type.get() == MOSAIC_X5:
            return config_svin_septentrio(acc_limit, svin_min_dur)
        return config_svin_ublox(acc_limit, svin_min_dur)

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

        posmode = self._spn_posmode.get()
        if self.receiver_type.get() == LG290P:
            return config_fixed_lg290p(acc_limit, lat, lon, height, posmode)
        if self.receiver_type.get() == LC29H:
            return config_fixed_lc29h(acc_limit, lat, lon, height, posmode)
        if self.receiver_type.get() == MOSAIC_X5:
            return config_fixed_septentrio(acc_limit, lat, lon, height, posmode)
        return config_fixed_ublox(acc_limit, lat, lon, height, posmode)

    def _on_quectel_restart(self):
        """
        Action(s) when Quectel receiver has restarted.
        """

        self._quectel_restart += 1
        if self.base_mode.get() in (BASE_SVIN, BASE_FIXED):
            # if first restart, send config commands a 2nd time
            if self._quectel_restart == 1:
                self._config_receiver()
            # if second restart and survey-in mode, enable SVIN status message
            if self.base_mode.get() == BASE_SVIN and self._quectel_restart == 2:
                cmd = config_svin_quectel()
                self.__app.send_to_device(cmd.serialize())

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

        self._socket_serve.set(state)
        self.__app.configuration.set("sockserver_b", state)

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
