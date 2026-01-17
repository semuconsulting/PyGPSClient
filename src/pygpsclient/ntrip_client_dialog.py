"""
nmea_client_dialog.py

NTRIP client configuration dialog.

Initial settings are from the saved json configuration.
Once started, the persisted state for the NTRIP client is held in
the client itself (pygnssutils.ntripclient), NOT in this dialog.

The NTRIP client invokes the `set_controls` method in this dialog
to update any established connection parameters.

The dialog may be closed while the NTRIP client is running.

Created on 2 Apr 2022

:author: semuadmin (Steve Smith)
:copyright: 2020 semuadmin
:license: BSD 3-Clause
"""

from logging import getLogger
from socket import AF_INET, AF_INET6
from tkinter import (
    DISABLED,
    END,
    EW,
    HORIZONTAL,
    NORMAL,
    NSEW,
    VERTICAL,
    Button,
    Entry,
    Frame,
    IntVar,
    Label,
    Listbox,
    N,
    Radiobutton,
    S,
    Scrollbar,
    Spinbox,
    StringVar,
    TclError,
    W,
    ttk,
)
from types import NoneType

from pygnssutils import NOGGA
from pygnssutils.helpers import find_mp_distance

from pygpsclient.globals import (
    CONNECTED_NTRIP,
    DISCONNECTED,
    ERRCOL,
    INFOCOL,
    READONLY,
    TRACEMODE_WRITE,
    UBX_CFGMSG,
    UBX_CFGPRT,
    UBX_CFGRATE,
    UBX_CFGVAL,
    UBX_MONHW,
    UBX_MONVER,
    UBX_PRESET,
    UI,
    UIK,
    VALFLOAT,
)
from pygpsclient.helpers import MAXALT, get_mp_info
from pygpsclient.socketconfig_ntrip_frame import SocketConfigNtripFrame
from pygpsclient.strings import (
    DLGTNTRIP,
    LBLDATATYPE,
    LBLGGAFIXED,
    LBLGGALIVE,
    LBLNTRIPGGAINT,
    LBLNTRIPMOUNT,
    LBLNTRIPPWD,
    LBLNTRIPSTR,
    LBLNTRIPUSER,
    LBLNTRIPVERSION,
)
from pygpsclient.toplevel_dialog import ToplevelDialog

GGA_INTERVALS = ("None", "2", "5", "10", "60", "120")
NTRIP_VERSIONS = ("2.0", "1.0")
KM2MILES = 0.6213712
IP4 = "IPv4"
IP6 = "IPv6"
RTCM = "RTCM"
SPARTN = "SPARTN"
NTRIP_SPARTN = "ppntrip.services.u-blox.com"
TCPIPV4 = "IPv4"
TCPIPV6 = "IPv6"


class NTRIPConfigDialog(ToplevelDialog):
    """,
    NTRIPConfigDialog class.
    """

    def __init__(self, app, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Constructor.

        :param Frame app: reference to main tkinter application
        :param args: optional args to pass to parent class (not currently used)
        :param kwargs: optional kwargs to pass to parent class (not currently used)
        """

        self.__app = app  # Reference to main application class
        self.logger = getLogger(__name__)
        self.__master = self.__app.appmaster  # Reference to root class (Tk)

        super().__init__(app, DLGTNTRIP)
        self._cfg_msg_command = None
        self._pending_confs = {
            UBX_MONVER: (),
            UBX_MONHW: (),
            UBX_CFGPRT: (),
            UBX_CFGMSG: (),
            UBX_CFGVAL: (),
            UBX_PRESET: (),
            UBX_CFGRATE: (),
        }
        self._ntrip_datatype = StringVar()
        self._ntrip_https = IntVar()
        self._ntrip_version = StringVar()
        self._ntrip_mountpoint = StringVar()
        self._ntrip_user = StringVar()
        self._ntrip_password = StringVar()
        self._ntrip_gga_interval = StringVar()
        self._ntrip_gga_mode = IntVar()
        self._ntrip_gga_lat = StringVar()
        self._ntrip_gga_lon = StringVar()
        self._ntrip_gga_alt = StringVar()
        self._ntrip_gga_sep = StringVar()
        self._settings = {}
        self._connected = False
        self._sourcetable = None

        self._body()
        self._do_layout()
        self._reset()
        self._attach_events()
        self._finalise()

    def _body(self):
        """
        Set up frame and widgets.
        """
        # pylint: disable=unnecessary-lambda

        self._frm_body = Frame(self)
        self._frm_socket = SocketConfigNtripFrame(
            self.__app,
            self._frm_body,
            protocols=[TCPIPV4, TCPIPV6],
            server_callback=self._on_server,
        )
        self._lbl_mountpoint = Label(self._frm_body, text=LBLNTRIPMOUNT)
        self._ent_mountpoint = Entry(
            self._frm_body,
            textvariable=self._ntrip_mountpoint,
            state=NORMAL,
            relief="sunken",
            width=12,
        )

        self._lbl_mpdist = Label(
            self._frm_body,
            width=30,
            anchor=W,
        )
        self._lbl_sourcetable = Label(self._frm_body, text=LBLNTRIPSTR)
        self._lbx_sourcetable = Listbox(
            self._frm_body,
            height=4,
            relief="sunken",
            width=40,
        )
        self._scr_sourcetablev = Scrollbar(self._frm_body, orient=VERTICAL)
        self._scr_sourcetableh = Scrollbar(self._frm_body, orient=HORIZONTAL)
        self._lbx_sourcetable.config(yscrollcommand=self._scr_sourcetablev.set)
        self._lbx_sourcetable.config(xscrollcommand=self._scr_sourcetableh.set)
        self._scr_sourcetablev.config(command=self._lbx_sourcetable.yview)
        self._scr_sourcetableh.config(command=self._lbx_sourcetable.xview)

        self._lbl_ntripversion = Label(self._frm_body, text=LBLNTRIPVERSION)
        self._spn_ntripversion = Spinbox(
            self._frm_body,
            values=(NTRIP_VERSIONS),
            width=4,
            wrap=True,
            textvariable=self._ntrip_version,
            state=READONLY,
        )
        self._lbl_datatype = Label(self._frm_body, text=LBLDATATYPE)
        self._spn_datatype = Spinbox(
            self._frm_body,
            values=(RTCM, SPARTN),
            width=8,
            wrap=True,
            textvariable=self._ntrip_datatype,
            state=READONLY,
        )
        self._lbl_user = Label(self._frm_body, text=LBLNTRIPUSER)
        self._ent_user = Entry(
            self._frm_body,
            textvariable=self._ntrip_user,
            state=NORMAL,
            relief="sunken",
            width=40,
        )
        self._lbl_password = Label(self._frm_body, text=LBLNTRIPPWD)
        self._ent_password = Entry(
            self._frm_body,
            textvariable=self._ntrip_password,
            state=NORMAL,
            relief="sunken",
            width=40,
            show="*",
        )
        self._lbl_ntripggaint = Label(self._frm_body, text=LBLNTRIPGGAINT)
        self._spn_ntripggaint = Spinbox(
            self._frm_body,
            values=(GGA_INTERVALS),
            width=5,
            wrap=True,
            textvariable=self._ntrip_gga_interval,
            state=READONLY,
        )
        self._rad_ggalive = Radiobutton(
            self._frm_body, text=LBLGGALIVE, variable=self._ntrip_gga_mode, value=0
        )
        self._rad_ggafixed = Radiobutton(
            self._frm_body,
            text=LBLGGAFIXED,
            variable=self._ntrip_gga_mode,
            value=1,
        )
        self._lbl_lat = Label(self._frm_body, text="Ref Latitude")
        self._ent_lat = Entry(
            self._frm_body,
            textvariable=self._ntrip_gga_lat,
            state=NORMAL,
            relief="sunken",
            width=15,
        )
        self._lbl_lon = Label(self._frm_body, text="Ref Longitude")
        self._ent_lon = Entry(
            self._frm_body,
            textvariable=self._ntrip_gga_lon,
            state=NORMAL,
            relief="sunken",
            width=15,
        )
        self._lbl_alt = Label(self._frm_body, text="Ref Elevation m")
        self._ent_alt = Entry(
            self._frm_body,
            textvariable=self._ntrip_gga_alt,
            state=NORMAL,
            relief="sunken",
            width=15,
        )
        self._lbl_sep = Label(self._frm_body, text="Ref Separation m")
        self._ent_sep = Entry(
            self._frm_body,
            textvariable=self._ntrip_gga_sep,
            state=NORMAL,
            relief="sunken",
            width=15,
        )

        self._btn_connect = Button(
            self._frm_body,
            width=45,
            height=35,
            image=self.img_conn,
            command=lambda: self._connect(),
        )
        self._btn_disconnect = Button(
            self._frm_body,
            width=45,
            height=35,
            image=self.img_disconn,
            command=lambda: self._disconnect(),
            state=DISABLED,
        )

    def _do_layout(self):
        """
        Position widgets in frame.
        """

        # top of grid
        self._frm_body.grid(column=0, row=0, sticky=NSEW)

        # body of grid
        self._frm_socket.grid(
            column=0, row=0, columnspan=5, rowspan=3, padx=3, pady=3, sticky=W
        )
        ttk.Separator(self._frm_body).grid(
            column=0, row=3, columnspan=5, padx=3, pady=3, sticky=EW
        )
        self._lbl_mountpoint.grid(column=0, row=4, padx=3, pady=3, sticky=W)
        self._ent_mountpoint.grid(column=1, row=4, padx=3, pady=3, sticky=W)
        self._lbl_mpdist.grid(column=2, columnspan=2, row=4, padx=3, pady=3, sticky=W)
        self._lbl_sourcetable.grid(column=0, row=5, padx=3, pady=3, sticky=W)
        self._lbx_sourcetable.grid(
            column=1, row=5, columnspan=3, rowspan=4, padx=3, pady=3, sticky=EW
        )
        self._scr_sourcetablev.grid(column=4, row=5, rowspan=4, sticky=(N, S, W))
        self._scr_sourcetableh.grid(column=1, columnspan=3, row=9, sticky=EW)
        self._lbl_ntripversion.grid(column=0, row=10, padx=3, pady=3, sticky=W)
        self._spn_ntripversion.grid(column=1, row=10, padx=3, pady=3, sticky=W)
        self._lbl_datatype.grid(column=2, row=10, padx=3, pady=3, sticky=W)
        self._spn_datatype.grid(column=3, row=10, padx=3, pady=3, sticky=W)
        self._lbl_user.grid(column=0, row=11, padx=3, pady=3, sticky=W)
        self._ent_user.grid(column=1, row=11, columnspan=3, padx=3, pady=3, sticky=W)
        self._lbl_password.grid(column=0, row=12, padx=3, pady=3, sticky=W)
        self._ent_password.grid(
            column=1, row=12, columnspan=3, padx=3, pady=3, sticky=W
        )
        ttk.Separator(self._frm_body).grid(
            column=0, row=13, columnspan=5, padx=3, pady=3, sticky=EW
        )
        self._rad_ggalive.grid(column=0, row=14, padx=3, pady=2, sticky=W)
        self._rad_ggafixed.grid(column=1, row=14, padx=3, pady=2, sticky=W)
        self._lbl_ntripggaint.grid(column=2, row=14, padx=2, pady=3, sticky=W)
        self._spn_ntripggaint.grid(column=3, row=14, padx=3, pady=2, sticky=W)
        self._lbl_lat.grid(column=0, row=15, padx=3, pady=2, sticky=W)
        self._ent_lat.grid(column=1, row=15, padx=3, pady=2, sticky=W)
        self._lbl_lon.grid(column=2, row=15, padx=3, pady=2, sticky=W)
        self._ent_lon.grid(column=3, row=15, padx=3, pady=2, sticky=W)
        self._lbl_alt.grid(column=0, row=16, padx=3, pady=2, sticky=W)
        self._ent_alt.grid(column=1, row=16, padx=3, pady=2, sticky=W)
        self._lbl_sep.grid(column=2, row=16, padx=3, pady=2, sticky=W)
        self._ent_sep.grid(column=3, row=16, padx=3, pady=2, sticky=W)
        ttk.Separator(self._frm_body).grid(
            column=0, row=17, columnspan=5, padx=3, pady=3, sticky=EW
        )
        self._btn_connect.grid(column=0, row=18, padx=3, pady=3, sticky=W)
        self._btn_disconnect.grid(column=1, row=18, padx=3, pady=3, sticky=W)

    def _attach_events(self):
        """
        Set up event listeners.
        """

        self._lbx_sourcetable.bind("<<ListboxSelect>>", self._on_select_mp)

        for setting in (
            self._ntrip_datatype,
            self._ntrip_https,
            self._ntrip_version,
            self._ntrip_mountpoint,
            self._ntrip_user,
            self._ntrip_password,
            self._ntrip_gga_interval,
            self._ntrip_gga_mode,
            self._ntrip_gga_lat,
            self._ntrip_gga_lon,
            self._ntrip_gga_alt,
            self._ntrip_gga_sep,
        ):
            setting.trace_add(TRACEMODE_WRITE, self._on_update_config)

    def _reset(self):
        """
        Reset configuration widgets.
        """

        self._get_settings()
        self.set_controls(self._connected)

    def _on_update_config(self, var, index, mode):  # pylint: disable=unused-argument
        """
        Update in-memory configuration if setting is changed.
        """

        try:
            self.update()
            cfg = self.__app.configuration
            cfg.set("ntripclientdatatype_s", self._ntrip_datatype.get())
            cfg.set("ntripclienthttps_b", int(self._ntrip_https.get()))
            cfg.set("ntripclientversion_s", self._ntrip_version.get())
            cfg.set("ntripclientmountpoint_s", self._ntrip_mountpoint.get())
            cfg.set("ntripclientuser_s", self._ntrip_user.get())
            cfg.set("ntripclientpassword_s", self._ntrip_password.get())
            ggaint = self._ntrip_gga_interval.get()
            ggaint = NOGGA if ggaint in ("None", "Not Required") else int(ggaint)
            cfg.set("ntripclientggainterval_n", ggaint)
            cfg.set("ntripclientggamode_b", self._ntrip_gga_mode.get())
            cfg.set("ntripclientreflat_f", float(self._ntrip_gga_lat.get()))
            cfg.set("ntripclientreflon_f", float(self._ntrip_gga_lon.get()))
            cfg.set("ntripclientrefalt_f", float(self._ntrip_gga_alt.get()))
            cfg.set("ntripclientrefsep_f", float(self._ntrip_gga_sep.get()))
        except (ValueError, TclError):
            pass

    def set_controls(self, connected: bool, msgt: NoneType | tuple = None):
        """
        Set App RTK connection status and enable or disable controls
        depending on connection status.

        NB: Called by pygnssutils.ntripclient when NTRIP connection established.

        :param bool status: connection status (True/False)
        :param NoneType | tuple msgt: tuple of (message, color)
        """

        self.__app.rtk_conn_status = CONNECTED_NTRIP if connected else DISCONNECTED

        try:
            self._settings = self.__app.ntrip_handler.settings
            self._connected = connected
            if msgt is None:
                server = self._settings["server"]
                port = self._settings["port"]
                mp = self._settings["mountpoint"]
                if mp is None:
                    mp = ""
                mountpoint = "/" + mp
                if mountpoint == "/":
                    mountpoint = " - retrieving sourcetable..."
                msg = (
                    f"Connected to {server}:{port}{mountpoint}"
                    if self._connected
                    else "Disconnected"
                )
            if msgt is None:
                self.status_label = (msg, INFOCOL)
            else:
                msg, col = msgt
                self.status_label = (msg, col)

            self._frm_socket.status_label = connected

            self._btn_disconnect.config(state=(NORMAL if connected else DISABLED))

            for ctl in (
                self._spn_ntripversion,
                self._spn_ntripggaint,
                self._spn_datatype,
            ):
                ctl.config(state=(DISABLED if connected else READONLY))

            for ctl in (
                self._btn_connect,
                self._ent_mountpoint,
                self._ent_user,
                self._ent_password,
                self._ent_lat,
                self._ent_lon,
                self._ent_alt,
                self._ent_sep,
                self._rad_ggalive,
                self._rad_ggafixed,
                self._lbx_sourcetable,
            ):
                ctl.config(state=(DISABLED if connected else NORMAL))
            # refresh sourcetable listbox ! NB PLACEMENT OF THIS CALL IS IMPORTANT !
            self.update_sourcetable(self._settings["sourcetable"])
            # update closest mountpoint name and distance (if available)
            lat, lon = self._get_coordinates()
            if isinstance(lat, float) and isinstance(lon, float):
                mpname, mindist = find_mp_distance(
                    lat,
                    lon,
                    self._settings["sourcetable"],
                    self._settings["mountpoint"],
                )
                self.set_mp_dist(mindist, mpname)
        except TclError:  # fudge during thread termination
            pass

    def _on_select_mp(self, event):
        """
        Mountpoint has been selected from listbox; set
        mountpoint and distance from live or reference
        coordinates (if available).
        """

        try:
            w = event.widget
            index = int(w.curselection()[0])
            srt = w.get(index)  # sourcetable entry
            info = get_mp_info(srt)
            name = info["name"]
            if info["gga"] in ("0", 0):  # gga not required
                self._ntrip_gga_interval.set(GGA_INTERVALS[0])
            else:  # gga required
                self._ntrip_gga_interval.set(GGA_INTERVALS[3])
            self._ntrip_mountpoint.set(name)
            lat, lon = self._get_coordinates()
            if isinstance(lat, float) and isinstance(lon, float):
                mpname, mindist = find_mp_distance(
                    lat, lon, self._settings["sourcetable"], name
                )
                if mpname is None:
                    self.set_mp_dist(None, name)
                else:
                    self.set_mp_dist(mindist, mpname)
        except (IndexError, KeyError):  # not yet populated
            pass

    def _on_server(self, var, index, mode):  # pylint: disable=unused-argument
        """
        Callback when server URL changed.

        :param event event: write event
        """

        try:
            if self._frm_socket.server.get() == NTRIP_SPARTN:
                self._ntrip_datatype.set(SPARTN)
            else:
                self._ntrip_datatype.set(RTCM)
        except TclError:
            pass

    def _get_settings(self):
        """
        Get settings from saved configuration or from the running instance of
        the NTRIP handler (pygnssutils.GNSSNTRIPClient).
        """

        self._connected = self.__app.ntrip_handler.connected
        if self._connected:
            # get settings from running instance
            self._settings = self.__app.ntrip_handler.settings
        else:
            # get settings from saved configuration
            cfg = self.__app.configuration
            self._settings = {}
            self._settings["server"] = cfg.get("ntripclientserver_s")
            self._settings["port"] = cfg.get("ntripclientport_n")
            self._settings["https"] = cfg.get("ntripclienthttps_b")
            self._settings["selfsign"] = cfg.get("ntripclientselfsign_b")
            self._settings["ipprot"] = (
                AF_INET6 if cfg.get("ntripclientprotocol_s") == IP6 else AF_INET
            )
            self._settings["flowinfo"] = cfg.get("ntripclientflowinfo_n")
            self._settings["scopeid"] = cfg.get("ntripclientscopeid_n")
            self._settings["mountpoint"] = cfg.get("ntripclientmountpoint_s")
            self._settings["sourcetable"] = []  # this is generated by the NTRIP caster
            self._settings["version"] = cfg.get("ntripclientversion_s")
            self._settings["datatype"] = cfg.get("ntripclientdatatype_s")
            self._settings["ntripuser"] = cfg.get("ntripclientuser_s")
            self._settings["ntrippassword"] = cfg.get("ntripclientpassword_s")
            self._settings["ggainterval"] = cfg.get("ntripclientggainterval_n")
            self._settings["ggamode"] = cfg.get("ntripclientggamode_b")
            self._settings["reflat"] = cfg.get("ntripclientreflat_f")
            self._settings["reflon"] = cfg.get("ntripclientreflon_f")
            self._settings["refalt"] = cfg.get("ntripclientrefalt_f")
            self._settings["refsep"] = cfg.get("ntripclientrefsep_f")
            self._settings["spartndecode"] = cfg.get("spartndecode_b")
            self._settings["spartnkey"] = cfg.get("spartnkey_s")
            if self._settings["spartnkey"] == "":
                self._settings["spartndecode"] = 0
            # if basedate is provided in config file, it must be an integer gnssTimetag
            self._settings["spartnbasedate"] = cfg.get("spartnbasedate_n")

        ipprot = self._settings.get("ipprot")
        self._frm_socket.protocol.set(IP6 if ipprot == AF_INET6 else IP4)
        self._frm_socket.server.set(self._settings["server"])
        self._frm_socket.port.set(self._settings["port"])
        self._frm_socket.https.set(self._settings["https"])
        self._frm_socket.selfsign.set(self._settings["selfsign"])
        self._ntrip_mountpoint.set(self._settings["mountpoint"])
        self._ntrip_version.set(self._settings["version"])
        self._ntrip_datatype.set(self._settings["datatype"])
        self._ntrip_user.set(self._settings["ntripuser"])
        self._ntrip_password.set(self._settings["ntrippassword"])
        ggaint = self._settings["ggainterval"]
        self._ntrip_gga_interval.set("None" if ggaint in (NOGGA, "None") else ggaint)
        self._ntrip_gga_mode.set(self._settings["ggamode"])
        self._ntrip_gga_lat.set(self._settings["reflat"])
        self._ntrip_gga_lon.set(self._settings["reflon"])
        self._ntrip_gga_alt.set(self._settings["refalt"])
        self._ntrip_gga_sep.set(self._settings["refsep"])

        lat, lon = self._get_coordinates()
        mpname, mindist = find_mp_distance(
            lat, lon, self._settings["sourcetable"], self._settings["mountpoint"]
        )
        self.set_mp_dist(mindist, mpname)

    def _set_settings(self):
        """
        Set settings for NTRIP handler.
        """

        self._settings["server"] = self._frm_socket.server.get()
        self._settings["port"] = self._frm_socket.port.get()
        self._settings["https"] = self._frm_socket.https.get()
        self._settings["selfsign"] = self._frm_socket.selfsign.get()
        self._settings["ipprot"] = (
            AF_INET6 if self._frm_socket.protocol.get() == IP6 else AF_INET
        )
        self._settings["mountpoint"] = self._ntrip_mountpoint.get()
        self._settings["version"] = self._ntrip_version.get()
        self._settings["datatype"] = self._ntrip_datatype.get()
        self._settings["ntripuser"] = self._ntrip_user.get()
        self._settings["ntrippassword"] = self._ntrip_password.get()
        ggaint = self._ntrip_gga_interval.get()
        self._settings["ggainterval"] = NOGGA if ggaint in (NOGGA, "None") else ggaint
        self._settings["ggamode"] = self._ntrip_gga_mode.get()
        self._settings["reflat"] = float(self._ntrip_gga_lat.get())
        self._settings["reflon"] = float(self._ntrip_gga_lon.get())
        self._settings["refalt"] = float(self._ntrip_gga_alt.get())
        self._settings["refsep"] = float(self._ntrip_gga_sep.get())

    def update_sourcetable(self, stable: list):
        """
        Update sourcetable listbox for this NTRIP server.

        :param list stable: sourcetable
        """

        self._lbx_sourcetable.unbind("<<ListboxSelect>>")
        self._lbx_sourcetable.delete(0, END)
        for item in stable:
            self._lbx_sourcetable.insert(END, item)
        self._lbx_sourcetable.bind("<<ListboxSelect>>", self._on_select_mp)

    def _connect(self):
        """
        Connect to NTRIP Server. NTRIP handler will invoke set_controls()
        with connection status in due course.
        """

        if self._valid_settings():
            self._set_settings()
            # verbosity and logtofile set in App.__init__()
            self.__app.ntrip_handler.run(
                ipprot=IP6 if self._settings["ipprot"] == AF_INET6 else IP4,
                server=self._settings["server"],
                port=self._settings["port"],
                https=self._settings["https"],
                selfsign=self._settings["selfsign"],
                flowinfo=self._settings["flowinfo"],
                scopeid=self._settings["scopeid"],
                mountpoint=self._settings["mountpoint"],
                version=self._settings["version"],
                datatype=self._settings["datatype"],
                ntripuser=self._settings["ntripuser"],
                ntrippassword=self._settings["ntrippassword"],
                ggainterval=self._settings["ggainterval"],
                ggamode=self._settings["ggamode"],
                reflat=self._settings["reflat"],
                reflon=self._settings["reflon"],
                refalt=self._settings["refalt"],
                refsep=self._settings["refsep"],
                spartndecode=self._settings["spartndecode"],
                spartnkey=self._settings["spartnkey"],
                spartnbasedate=self._settings["spartnbasedate"],
                output=self.__app.ntrip_inqueue,
            )
            self.set_controls(True)

    def _disconnect(self):
        """
        Disconnect from NTRIP Server. NTRIP handler will invoke set_controls()
        with connection status in due course.
        """

        self.__app.ntrip_handler.stop()
        self.set_controls(False)

    def _valid_settings(self) -> bool:
        """
        Validate settings.

        :return: valid True/False
        :rtype: bool
        """

        valid = self._frm_socket.valid_settings()
        if self._settings["ggamode"] == 1:  # fixed reference
            valid = valid & self._ent_lat.validate(VALFLOAT, -90.0, 90.0)
            valid = valid & self._ent_lon.validate(VALFLOAT, -180.0, 180.0)
            valid = valid & self._ent_alt.validate(VALFLOAT, -MAXALT, MAXALT)
            valid = valid & self._ent_sep.validate(VALFLOAT, -MAXALT, MAXALT)

        if not valid:
            self.status_label = ("ERROR - invalid settings", ERRCOL)

        return valid

    def set_mp_dist(self, dist: float, name: str = ""):
        """
        Set mountpoint distance label.

        :param float dist: distance to mountpoint km
        """

        if name in (None, ""):
            return
        dist_l = "Baseline n/a"
        dist_u = "km"
        if isinstance(dist, float):
            units = self.__app.configuration.get("units_s")
            if units in (UI, UIK):
                dist *= KM2MILES
                dist_u = "miles"
            dist_l = f"Baseline: {dist:,.1f} {dist_u}"
        self._ntrip_mountpoint.set(name)
        self._lbl_mpdist.config(text=dist_l)

    def _get_coordinates(self) -> tuple[float, float]:
        """
        Get coordinates from receiver or fixed reference settings.

        :returns: tuple (lat,lon)
        :rtype: tuple[float,float]
        """

        try:
            if self._ntrip_gga_mode.get() == 0:  # live position
                status = self.__app.get_coordinates()
                lat, lon = status["lat"], status["lon"]
            else:  # fixed reference
                lat = float(self._settings["reflat"])
                lon = float(self._settings["reflon"])
            return lat, lon
        except (ValueError, TypeError):
            return 0, 0
