"""
Socket Server / NTRIP caster configuration panel Frame class.
Supports two modes of operation - Socket Server and NTRIP Caster.

If running in NTRIP Caster mode, two base station modes are available -
Survey-In and Fixed. The panel provides methods to configure RTK-compatible
receiver (e.g. ZED-F9P) to operate in either of these base station modes.

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
from pyubx2 import UBXMessage, llh2ecef

from pygpsclient.globals import (
    DISCONNECTED,
    ICON_CONTRACT,
    ICON_EXPAND,
    READONLY,
    SOCK_NTRIP,
    SOCKMODES,
    SOCKSERVER_NTRIP_PORT,
    SOCKSERVER_PORT,
)
from pygpsclient.helpers import (
    MAXPORT,
    VALFLOAT,
    VALINT,
    VALNONBLANK,
    val2sphp,
    valid_entry,
)
from pygpsclient.strings import (
    LBLACCURACY,
    LBLCONFIGBASE,
    LBLDURATIONS,
    LBLSERVERHOST,
    LBLSERVERMODE,
    LBLSERVERPORT,
    LBLSOCKSERVE,
)

TMODE_DISABLED = 0
TMODE_SVIN = 1
TMODE_FIXED = 2
ECEF = 0
LLH = 1
BASE_SVIN = "SURVEY IN"
BASE_FIXED = "FIXED"
BASE_DISABLED = "DISABLED"
POS_LLH = "LLH"
POS_ECEF = "ECEF"
BASEMODES = (BASE_SVIN, BASE_DISABLED, BASE_FIXED)
POSMODES = (POS_LLH, POS_ECEF)
ACCURACIES = (
    10,
    5,
    3,
    2,
    1,
    10000,
    5000,
    3000,
    2000,
    1000,
    500,
    300,
    200,
    100,
    50,
    30,
    20,
)
DURATIONS = (60, 1200, 600, 300, 240, 180, 120, 90)


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
        self._base_mode = StringVar()
        self._acclimit = IntVar()
        self._duration = IntVar()
        self._pos_mode = StringVar()
        self._fixedlat = DoubleVar()
        self._fixedlon = DoubleVar()
        self._fixedalt = DoubleVar()
        self._disable_nmea = IntVar()
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
            width=14,
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
            text=LBLCONFIGBASE,
            variable=self._set_basemode,
        )
        self._spn_basemode = Spinbox(
            self._frm_advanced,
            values=BASEMODES,
            width=10,
            state=READONLY,
            wrap=True,
            textvariable=self._base_mode,
        )
        self._lbl_acclimit = Label(
            self._frm_advanced,
            text=LBLACCURACY,
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
            text=LBLDURATIONS,
        )
        self._chk_disablenmea = Checkbutton(
            self._frm_advanced,
            text="Disable NMEA",
            variable=self._disable_nmea,
        )
        self._spn_duration = Spinbox(
            self._frm_advanced,
            values=DURATIONS,
            width=5,
            state=READONLY,
            wrap=True,
            textvariable=self._duration,
        )
        self._lbl_elapsed = Label(
            self._frm_advanced,
            text="",
        )
        self._spn_posmode = Spinbox(
            self._frm_advanced,
            values=POSMODES,
            width=6,
            state=READONLY,
            wrap=True,
            textvariable=self._pos_mode,
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
            text="Height (m)",
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
            column=0, row=0, columnspan=2, padx=2, pady=2, sticky=W
        )
        self._spn_basemode.grid(column=2, row=0, columnspan=2, padx=2, pady=2, sticky=W)

    def _attach_events(self):
        """
        Bind events to variables.
        """

        tracemode = ("write", "unset")
        self.socket_serve.trace_add(tracemode, self._on_socket_serve)
        self.sock_mode.trace_add(tracemode, self._on_sockmode)
        self._base_mode.trace_add(tracemode, self._on_basemode)
        self._pos_mode.trace_add(tracemode, self._on_posmode)

    def reset(self):
        """
        Reset settings to defaults.
        """

        self._base_mode.set(BASE_SVIN)
        self._pos_mode.set(POS_LLH)
        self._disable_nmea.set(1)
        self.clients = 0

    def set_status(self, status: int):
        """
        Set connection status, which determines whether controls
        are enabled or not: 0=DISCONNECTED, 1=CONNECTED

        :param int status: status (0,1)
        """

        if status == DISCONNECTED:
            self._chk_socketserve.configure(state=DISABLED)
            self.socket_serve.set(0)
            self.clients = 0
        else:
            self._chk_socketserve.configure(state=NORMAL)

    def _on_socket_serve(self, var, index, mode):
        """
        Action when socket_serve variable is updated.
        Start or stop socket server.
        """

        if self.socket_serve.get():
            # validate entries
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
            # start server
            self.__app.start_sockserver_thread()
            self.__app.stream_handler.sock_serve = True
        else:  # stop server
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
            self._chk_disablenmea,
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

        # configure receiver as base station if in NTRIP Caster mode
        # and 'Configure Base' option is checked.
        if (
            self.socket_serve.get()
            and self.sock_mode.get() == SOCK_NTRIP
            and self._set_basemode.get()
        ):
            self._config_rcvr()

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
        Action when sock_mode variable is updated.
        Set default port and expand button depending on socket server mode.
        """

        if self.sock_mode.get() == SOCK_NTRIP:
            self.sock_port.set(SOCKSERVER_NTRIP_PORT)
            self._btn_toggle.grid(column=4, row=0, sticky=E)
            self._show_advanced = True
        else:
            self.sock_port.set(SOCKSERVER_PORT)
            self._btn_toggle.grid_forget()
            self._show_advanced = False
        self._set_advanced()

    def _on_basemode(self, var, index, mode):
        """
        Action when base_mode is updated.
        Set field visibility depending on base mode.
        """

        if self._base_mode.get() == BASE_SVIN:
            self._lbl_acclimit.grid(column=0, row=1, padx=2, pady=1, sticky=E)
            self._spn_acclimit.grid(column=1, row=1, padx=2, pady=1, sticky=W)
            self._chk_disablenmea.grid(column=2, row=1, padx=2, pady=1, sticky=W)
            self._lbl_duration.grid(column=0, row=2, padx=2, pady=1, sticky=E)
            self._spn_duration.grid(column=1, row=2, padx=2, pady=1, sticky=W)
            self._lbl_elapsed.grid(column=2, row=2, padx=2, pady=1, sticky=W)
            self._spn_posmode.grid_forget()
            self._lbl_fixedlat.grid_forget()
            self._ent_fixedlat.grid_forget()
            self._lbl_fixedlon.grid_forget()
            self._ent_fixedlon.grid_forget()
            self._lbl_fixedalt.grid_forget()
            self._ent_fixedalt.grid_forget()
        elif self._base_mode.get() == BASE_FIXED:
            self._lbl_acclimit.grid(column=0, row=1, padx=2, pady=1, sticky=E)
            self._spn_acclimit.grid(column=1, row=1, padx=2, pady=1, sticky=W)
            self._chk_disablenmea.grid(column=2, row=1, padx=2, pady=1, sticky=W)
            self._spn_posmode.grid(column=0, row=2, rowspan=3, padx=2, pady=1, sticky=E)
            self._lbl_fixedlat.grid(column=1, row=2, padx=2, pady=1, sticky=E)
            self._ent_fixedlat.grid(
                column=2, row=2, columnspan=3, padx=2, pady=1, sticky=W
            )
            self._lbl_fixedlon.grid(column=1, row=3, padx=2, pady=1, sticky=E)
            self._ent_fixedlon.grid(
                column=2, row=3, columnspan=3, padx=2, pady=1, sticky=W
            )
            self._lbl_fixedalt.grid(column=1, row=4, padx=2, pady=1, sticky=E)
            self._ent_fixedalt.grid(
                column=2, row=4, columnspan=3, padx=2, pady=1, sticky=W
            )
            self._lbl_duration.grid_forget()
            self._spn_duration.grid_forget()
            self._lbl_elapsed.grid_forget()
            self._set_coords(self._pos_mode.get())
        else:  # Disabled
            self._chk_disablenmea.grid(column=0, row=1, padx=2, pady=1, sticky=W)
            self._lbl_acclimit.grid_forget()
            self._spn_acclimit.grid_forget()
            self._spn_posmode.grid_forget()
            self._lbl_fixedlat.grid_forget()
            self._ent_fixedlat.grid_forget()
            self._lbl_fixedlon.grid_forget()
            self._ent_fixedlon.grid_forget()
            self._lbl_fixedalt.grid_forget()
            self._ent_fixedalt.grid_forget()
            self._lbl_duration.grid_forget()
            self._spn_duration.grid_forget()
            self._lbl_elapsed.grid_forget()

    def _on_posmode(self, var, index, mode):
        """
        Action when pos_mode variable is updated.
        Set fixed reference labels depending on position mode (ECEF or LLH)
        """

        lbls = (
            ("Lat", "Lon", "Height (m)")
            if self._pos_mode.get() == POS_LLH
            else ("X (m)", "Y (m)", "Z (m)")
        )
        self._lbl_fixedlat.config(text=lbls[0])
        self._lbl_fixedlon.config(text=lbls[1])
        self._lbl_fixedalt.config(text=lbls[2])
        self._set_coords(self._pos_mode.get())

    def _set_coords(self, posmode: str):
        """
        Set current coordinates in LLH or ECEF format.

        :param str posmode: position mode (LLH or ECEF)
        """

        _, lat, lon, alt, _ = self.__app.get_coordinates()
        try:
            if posmode == POS_ECEF:
                lat, lon, alt = llh2ecef(lat, lon, alt)
        except TypeError:  # e.g. no NMEA fix
            lat = lon = alt = 0.0
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

    def _config_rcvr(self):
        """
        Configure receiver as Base Station if in NTRIP caster mode.
        """

        # set base station timing mode
        if self._base_mode.get() == BASE_SVIN:
            msg = self._config_svin(self._acclimit.get(), self._duration.get())
        elif self._base_mode.get() == BASE_FIXED:
            msg = self._config_fixed(
                self._acclimit.get(),
                self._fixedlat.get(),
                self._fixedlon.get(),
                self._fixedalt.get(),
            )
        else:  # DISABLED
            msg = self._config_disable()
        self.__app.gnss_outqueue.put(msg.serialize())

        # set RTCM and UBX NAV-SVIN message output rate
        rate = 0 if self._base_mode.get() == BASE_DISABLED else 1
        for port in ("USB", "UART1"):
            msg = self._config_msg_rates(rate, port)
            self.__app.gnss_outqueue.put(msg.serialize())
            msg = self._config_nmea(self._disable_nmea.get(), port)
            self.__app.gnss_outqueue.put(msg.serialize())

    def _config_msg_rates(self, rate: int, port_type: str) -> UBXMessage:
        """
        Configure RTCM3 and UBX NAV-SVIN message rates.

        :param int rate: message rate (0 = off)
        :param str port_type: port that rcvr is connected on
        """

        layers = 1  # 1 = RAM, 2 = BBR, 4 = Flash (can be OR'd)
        transaction = 0
        cfg_data = []
        for rtcm_type in (
            "1005",
            "1077",
            "1087",
            "1097",
            "1127",
            "1230",
            "4072_0",
            "4072_1",
        ):
            cfg = f"CFG_MSGOUT_RTCM_3X_TYPE{rtcm_type}_{port_type}"
            cfg_data.append([cfg, rate])

        # NAV-SVIN only output in SURVEY-IN mode
        rate = rate if self._base_mode.get() == BASE_SVIN else 0
        cfg = f"CFG_MSGOUT_UBX_NAV_SVIN_{port_type}"
        cfg_data.append([cfg, rate])

        return UBXMessage.config_set(layers, transaction, cfg_data)

    def _config_disable(self):
        """
        Disable base station mode.
        """

        layers = 1
        transaction = 0
        cfg_data = [
            ("CFG_TMODE_MODE", TMODE_DISABLED),
        ]

        return UBXMessage.config_set(layers, transaction, cfg_data)

    def _config_svin(self, acc_limit: int, svin_min_dur: int) -> UBXMessage:
        """
        Configure Survey-In mode with specied accuracy limit.

        :param int acc_limit: accuracy limit in cm
        :param int svin_min_dur: survey minimimum duration
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

    def _config_fixed(
        self, acc_limit: int, lat: float, lon: float, height: float
    ) -> UBXMessage:
        """
        Configure Fixed mode with specified coordinates.

        :param int acc_limit: accuracy limit in cm
        :param float lat: lat or X in m
        :param float lat: lon or Y in m
        :param float lat: height or Z in m
        """

        layers = 1
        transaction = 0
        acc_limit = int(acc_limit * 100)  # convert to 0.1 mm
        if self._pos_mode.get() == POS_LLH:
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

    def _config_nmea(self, state: int, port_type: str) -> UBXMessage:
        """
        Disable NMEA messages at port level and use minimum UBX instead.

        :param int state: 1 = disable NMEA, 0 = enable NMEA
        :param str port_type: port that rcvr is connected on
        """

        nmea_state = 0 if state else 1
        layers = 1
        transaction = 0
        cfg_data = []
        cfg_data.append((f"CFG_{port_type}OUTPROT_NMEA", nmea_state))
        cfg_data.append((f"CFG_{port_type}OUTPROT_UBX", 1))
        cfg_data.append((f"CFG_MSGOUT_UBX_NAV_PVT_{port_type}", state))
        cfg_data.append((f"CFG_MSGOUT_UBX_NAV_SAT_{port_type}", state * 4))

        return UBXMessage.config_set(layers, transaction, cfg_data)

    def svin_countdown(self, dur: int, valid: bool, active: bool):
        """
        Display countdown of remaining survey-in duration.

        :param int dur: elapsed time
        :param bool valid: valid flag
        :param bool active: active flag
        """

        if not self.socket_serve.get():
            return
        MAX = 15
        if not active and valid:
            txt = "SVIN Valid"
        elif not active and not valid:
            txt = "SVIN Invalid"
        elif active:
            rem = int(((self._duration.get() - dur) / self._duration.get()) * MAX)
            txt = "\u2588" * rem
        else:
            txt = ""
        self._lbl_elapsed.config(text=txt, fg="grey65")
