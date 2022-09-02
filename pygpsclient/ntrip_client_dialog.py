"""
NTRIP client container dialog

This is the pop-up dialog containing the various
NTRIP client configuration functions.

NB: the NTRIP handler gnssntripclient is part of the separate
pygnssutils  package.

Created on 2 Apr 2022

:author: semuadmin
:copyright: SEMU Consulting © 2022
:license: BSD 3-Clause
"""
# pylint: disable=invalid-name

from tkinter import (
    ttk,
    Toplevel,
    Frame,
    Button,
    Label,
    Entry,
    Spinbox,
    Listbox,
    Scrollbar,
    Radiobutton,
    StringVar,
    IntVar,
    N,
    S,
    E,
    W,
    NORMAL,
    DISABLED,
    END,
    VERTICAL,
    HORIZONTAL,
    TclError,
)
from PIL import ImageTk, Image
from pygnssutils import NOGGA
from pygnssutils.helpers import find_mp_distance
from pygpsclient.globals import (
    ICON_EXIT,
    ICON_CONN,
    ICON_DISCONN,
    UBX_MONVER,
    UBX_MONHW,
    UBX_CFGPRT,
    UBX_CFGRATE,
    UBX_CFGMSG,
    UBX_CFGVAL,
    UBX_PRESET,
    ENTCOL,
    READONLY,
    POPUP_TRANSIENT,
    UI,
    UIK,
    GGA_INTERVALS,
)
from pygpsclient.strings import (
    DLGNTRIPCONFIG,
    LBLNTRIPSERVER,
    LBLNTRIPPORT,
    LBLNTRIPVERSION,
    LBLNTRIPMOUNT,
    LBLNTRIPUSER,
    LBLNTRIPPWD,
    LBLNTRIPGGAINT,
    LBLNTRIPSTR,
    LBLGGALIVE,
    LBLGGAFIXED,
)
from pygpsclient.helpers import (
    valid_entry,
    VALINT,
    VALFLOAT,
    VALURL,
    MAXPORT,
    MAXALT,
)

NTRIP_VERSIONS = ("2.0", "1.0")
KM2MILES = 0.6213712


class NTRIPConfigDialog(Toplevel):
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
        self.__master = self.__app.get_master()  # Reference to root class (Tk)
        Toplevel.__init__(self, app)
        if POPUP_TRANSIENT:
            self.transient(self.__app)
        self.resizable(True, True)  # allow for MacOS resize glitches
        self.title(DLGNTRIPCONFIG)  # pylint: disable=E1102
        self.protocol("WM_DELETE_WINDOW", self.on_exit)
        self._img_exit = ImageTk.PhotoImage(Image.open(ICON_EXIT))
        self._img_conn = ImageTk.PhotoImage(Image.open(ICON_CONN))
        self._img_disconn = ImageTk.PhotoImage(Image.open(ICON_DISCONN))
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
        self._status = StringVar()
        self._status_cfgmsg = StringVar()
        self._ntrip_version = StringVar()
        self._ntrip_server = StringVar()
        self._ntrip_port = StringVar()
        self._ntrip_mountpoint = StringVar()
        self._ntrip_mpdist = StringVar()
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
        self._attach_events()
        self._reset()

    def _body(self):
        """
        Set up frame and widgets.
        """
        # pylint: disable=unnecessary-lambda

        self._frm_container = Frame(self, borderwidth=2, relief="groove")
        self._frm_status = Frame(self._frm_container, borderwidth=2, relief="groove")
        self._lbl_status = Label(
            self._frm_status, textvariable=self._status, anchor="w"
        )
        self._btn_exit = Button(
            self._frm_status,
            image=self._img_exit,
            width=55,
            fg="red",
            command=self.on_exit,
            font=self.__app.font_md,
        )

        # NTRIP client configuration options
        self._lbl_server = Label(self._frm_container, text=LBLNTRIPSERVER)
        self._ent_server = Entry(
            self._frm_container,
            textvariable=self._ntrip_server,
            bg=ENTCOL,
            state=NORMAL,
            relief="sunken",
            width=50,
        )
        self._lbl_port = Label(self._frm_container, text=LBLNTRIPPORT)
        self._ent_port = Entry(
            self._frm_container,
            textvariable=self._ntrip_port,
            bg=ENTCOL,
            state=NORMAL,
            relief="sunken",
            width=6,
        )
        self._lbl_mountpoint = Label(self._frm_container, text=LBLNTRIPMOUNT)
        self._ent_mountpoint = Entry(
            self._frm_container,
            textvariable=self._ntrip_mountpoint,
            bg=ENTCOL,
            state=NORMAL,
            relief="sunken",
            width=20,
        )
        self._lbl_mpdist = Label(
            self._frm_container,
            textvariable=self._ntrip_mpdist,
            width=30,
            anchor="w",
        )
        self._lbl_sourcetable = Label(self._frm_container, text=LBLNTRIPSTR)
        self._lbx_sourcetable = Listbox(
            self._frm_container,
            bg=ENTCOL,
            height=4,
            relief="sunken",
            width=55,
        )
        self._scr_sourcetablev = Scrollbar(self._frm_container, orient=VERTICAL)
        self._scr_sourcetableh = Scrollbar(self._frm_container, orient=HORIZONTAL)
        self._lbx_sourcetable.config(yscrollcommand=self._scr_sourcetablev.set)
        self._lbx_sourcetable.config(xscrollcommand=self._scr_sourcetableh.set)
        self._scr_sourcetablev.config(command=self._lbx_sourcetable.yview)
        self._scr_sourcetableh.config(command=self._lbx_sourcetable.xview)

        self._lbl_ntripversion = Label(self._frm_container, text=LBLNTRIPVERSION)
        self._spn_ntripversion = Spinbox(
            self._frm_container,
            values=(NTRIP_VERSIONS),
            width=4,
            readonlybackground=ENTCOL,
            wrap=True,
            textvariable=self._ntrip_version,
            state=READONLY,
        )
        self._lbl_user = Label(self._frm_container, text=LBLNTRIPUSER)
        self._ent_user = Entry(
            self._frm_container,
            textvariable=self._ntrip_user,
            bg=ENTCOL,
            state=NORMAL,
            relief="sunken",
            width=50,
        )
        self._lbl_password = Label(self._frm_container, text=LBLNTRIPPWD)
        self._ent_password = Entry(
            self._frm_container,
            textvariable=self._ntrip_password,
            bg=ENTCOL,
            state=NORMAL,
            relief="sunken",
            width=20,
            show="*",
        )
        self._lbl_ntripggaint = Label(self._frm_container, text=LBLNTRIPGGAINT)
        self._spn_ntripggaint = Spinbox(
            self._frm_container,
            values=(GGA_INTERVALS),
            width=5,
            readonlybackground=ENTCOL,
            wrap=True,
            textvariable=self._ntrip_gga_interval,
            state=READONLY,
        )
        self._rad_ggalive = Radiobutton(
            self._frm_container, text=LBLGGALIVE, variable=self._ntrip_gga_mode, value=0
        )
        self._rad_ggafixed = Radiobutton(
            self._frm_container,
            text=LBLGGAFIXED,
            variable=self._ntrip_gga_mode,
            value=1,
        )
        self._lbl_lat = Label(self._frm_container, text="Ref Latitude")
        self._ent_lat = Entry(
            self._frm_container,
            textvariable=self._ntrip_gga_lat,
            bg=ENTCOL,
            state=NORMAL,
            relief="sunken",
            width=15,
        )
        self._lbl_lon = Label(self._frm_container, text="Ref Longitude")
        self._ent_lon = Entry(
            self._frm_container,
            textvariable=self._ntrip_gga_lon,
            bg=ENTCOL,
            state=NORMAL,
            relief="sunken",
            width=15,
        )
        self._lbl_alt = Label(self._frm_container, text="Ref Elevation m")
        self._ent_alt = Entry(
            self._frm_container,
            textvariable=self._ntrip_gga_alt,
            bg=ENTCOL,
            state=NORMAL,
            relief="sunken",
            width=15,
        )
        self._lbl_sep = Label(self._frm_container, text="Ref Separation m")
        self._ent_sep = Entry(
            self._frm_container,
            textvariable=self._ntrip_gga_sep,
            bg=ENTCOL,
            state=NORMAL,
            relief="sunken",
            width=15,
        )

        self._btn_connect = Button(
            self._frm_container,
            width=45,
            height=35,
            image=self._img_conn,
            command=lambda: self._connect(),
        )
        self._btn_disconnect = Button(
            self._frm_container,
            width=45,
            height=35,
            image=self._img_disconn,
            command=lambda: self._disconnect(),
            state=DISABLED,
        )

    def _do_layout(self):
        """
        Position widgets in frame.
        """

        # top of grid
        col = 0
        row = 0
        self._frm_container.grid(
            column=col,
            row=row,
            columnspan=12,
            rowspan=22,
            padx=3,
            pady=3,
            ipadx=5,
            ipady=5,
            sticky=(N, S, W, E),
        )

        # body of grid
        self._lbl_server.grid(column=0, row=0, padx=3, pady=3, sticky=W)
        self._ent_server.grid(column=1, row=0, columnspan=2, padx=3, pady=3, sticky=W)
        self._lbl_port.grid(column=0, row=1, padx=3, pady=3, sticky=W)
        self._ent_port.grid(column=1, row=1, padx=3, pady=3, sticky=W)
        self._lbl_mountpoint.grid(column=0, row=2, padx=3, pady=3, sticky=W)
        self._ent_mountpoint.grid(column=1, row=2, padx=3, pady=3, sticky=W)
        self._lbl_mpdist.grid(column=2, row=2, padx=3, pady=3, sticky=W)
        self._lbl_sourcetable.grid(column=0, row=3, padx=3, pady=3, sticky=W)
        self._lbx_sourcetable.grid(
            column=1, row=3, columnspan=2, rowspan=4, padx=3, pady=3, sticky=W
        )
        self._scr_sourcetablev.grid(column=3, row=3, rowspan=4, sticky=(N, S))
        self._scr_sourcetableh.grid(column=1, columnspan=2, row=7, sticky=(E, W))
        self._lbl_ntripversion.grid(column=0, row=8, padx=3, pady=3, sticky=W)
        self._spn_ntripversion.grid(
            column=1, row=8, padx=3, pady=3, rowspan=2, sticky=W
        )
        self._lbl_user.grid(column=0, row=10, padx=3, pady=3, sticky=W)
        self._ent_user.grid(column=1, row=10, columnspan=2, padx=3, pady=3, sticky=W)
        self._lbl_password.grid(column=0, row=11, padx=3, pady=3, sticky=W)
        self._ent_password.grid(column=1, row=11, padx=3, pady=3, sticky=W)
        ttk.Separator(self._frm_container).grid(
            column=0, row=12, columnspan=3, padx=3, pady=3, sticky=(W, E)
        )
        self._lbl_ntripggaint.grid(column=0, row=13, padx=2, pady=3, sticky=W)
        self._spn_ntripggaint.grid(
            column=1, row=13, padx=3, pady=2, rowspan=2, sticky=W
        )
        self._rad_ggalive.grid(column=0, row=15, padx=3, pady=2, sticky=W)
        self._rad_ggafixed.grid(column=1, row=15, padx=3, pady=2, sticky=W)
        self._lbl_lat.grid(column=0, row=16, padx=3, pady=2, sticky=W)
        self._ent_lat.grid(column=1, row=16, padx=3, pady=2, sticky=W)
        self._lbl_lon.grid(column=0, row=17, padx=3, pady=2, sticky=W)
        self._ent_lon.grid(column=1, row=17, padx=3, pady=2, sticky=W)
        self._lbl_alt.grid(column=0, row=18, padx=3, pady=2, sticky=W)
        self._ent_alt.grid(column=1, row=18, padx=3, pady=2, sticky=W)
        self._lbl_sep.grid(column=0, row=19, padx=3, pady=2, sticky=W)
        self._ent_sep.grid(column=1, row=19, padx=3, pady=2, sticky=W)
        ttk.Separator(self._frm_container).grid(
            column=0, row=20, columnspan=3, padx=3, pady=3, sticky=(W, E)
        )
        self._btn_connect.grid(column=0, row=21, padx=3, pady=3, sticky=W)
        self._btn_disconnect.grid(column=1, row=21, padx=3, pady=3, sticky=W)

        # bottom of grid
        row = 22
        col = 0
        (colsp, rowsp) = self._frm_container.grid_size()
        self._frm_status.grid(column=col, row=row, columnspan=colsp, sticky=(W, E))
        self._lbl_status.grid(
            column=0, row=0, columnspan=colsp - 1, ipadx=3, ipady=3, sticky=(W, E)
        )
        self._btn_exit.grid(column=colsp - 1, row=0, ipadx=3, ipady=3, sticky=(E))

        for frm in (self._frm_container, self._frm_status):
            for i in range(colsp):
                frm.grid_columnconfigure(i, weight=1)
            for i in range(rowsp):
                frm.grid_rowconfigure(i, weight=1)

        self._frm_container.option_add("*Font", self.__app.font_sm)
        self._frm_status.option_add("*Font", self.__app.font_sm)

    def _attach_events(self):
        """
        Set up event listeners.
        """

        self._lbx_sourcetable.bind("<<ListboxSelect>>", self._on_select_mp)

    def _reset(self):
        """
        Reset configuration widgets.
        """

        self._get_settings()
        self.set_controls(self._connected)

    def set_controls(self, connected: bool, msg: tuple = None):
        """
        Enable or disable controls depending on connection status.

        :param bool status: connection status (True/False)
        :param tuple msg: optional status message tuple (text, color)
        """

        try:

            self._settings = self.__app.ntrip_handler.settings
            self._connected = connected
            if msg is None:
                server = self._settings["server"]
                port = self._settings["port"]
                mountpoint = "/" + self._settings["mountpoint"]
                if mountpoint == "/":
                    mountpoint = " - retrieving sourcetable..."
                msg = (
                    (f"Connected to {server}:{port}{mountpoint}", "green")
                    if self._connected
                    else ("Disconnected", "blue")
                )
            txt, col = msg
            self.set_status(txt, col)

            self._btn_disconnect.config(state=(NORMAL if connected else DISABLED))

            for ctl in (
                self._spn_ntripversion,
                self._spn_ntripggaint,
            ):
                ctl.config(state=(DISABLED if connected else READONLY))

            for ctl in (
                self._btn_connect,
                self._ent_server,
                self._ent_port,
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

    def set_status(self, message: str, color: str = "blue"):
        """
        Set status message.

        :param str message: message to be displayed
        :param str color: rgb color of text (blue)
        """

        message = (message[:80] + "..") if len(message) > 80 else message
        self._lbl_status.config(fg=color)
        self._status.set(" " + message)

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
            name = srt[0]
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
        except IndexError:  # not yet populated
            pass

    def on_exit(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Handle Exit button press.
        """

        # self.__master.update_idletasks()
        self.__app.stop_ntripconfig_thread()
        self.destroy()

    def get_size(self):
        """
        Get current frame size.

        :return: window size (width, height)
        :rtype: tuple
        """

        self.__master.update_idletasks()  # Make sure we know about any resizing
        return (self.winfo_width(), self.winfo_height())

    def _get_settings(self):
        """
        Get settings from NTRIP handler.
        """

        self._connected = self.__app.ntrip_handler.connected
        self._settings = self.__app.ntrip_handler.settings
        self._ntrip_server.set(self._settings["server"])
        self._ntrip_port.set(self._settings["port"])
        self._ntrip_mountpoint.set(self._settings["mountpoint"])
        self._ntrip_version.set(self._settings["version"])
        self._ntrip_user.set(self._settings["user"])
        self._ntrip_password.set(self._settings["password"])
        ggaint = self._settings["ggainterval"]
        self._ntrip_gga_interval.set("None" if ggaint == NOGGA else ggaint)
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

        self._settings["server"] = self._ntrip_server.get()
        self._settings["port"] = self._ntrip_port.get()
        self._settings["mountpoint"] = self._ntrip_mountpoint.get()
        self._settings["version"] = self._ntrip_version.get()
        self._settings["user"] = self._ntrip_user.get()
        self._settings["password"] = self._ntrip_password.get()
        self._settings["ggainterval"] = (
            NOGGA
            if self._ntrip_gga_interval.get() == "None"
            else self._ntrip_gga_interval.get()
        )
        self._settings["ggamode"] = self._ntrip_gga_mode.get()
        self._settings["reflat"] = self._ntrip_gga_lat.get()
        self._settings["reflon"] = self._ntrip_gga_lon.get()
        self._settings["refalt"] = self._ntrip_gga_alt.get()
        self._settings["refsep"] = self._ntrip_gga_sep.get()

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
            self.__app.ntrip_handler.run(
                server=self._settings["server"],
                port=self._settings["port"],
                mountpoint=self._settings["mountpoint"],
                version=self._settings["version"],
                user=self._settings["user"],
                password=self._settings["password"],
                ggainterval=self._settings["ggainterval"],
                ggamode=self._settings["ggamode"],
                reflat=self._settings["reflat"],
                reflon=self._settings["reflon"],
                refalt=self._settings["refalt"],
                refsep=self._settings["refsep"],
                output=self.__app.ntripqueue,
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

        valid = True
        valid = valid & valid_entry(self._ent_server, VALURL)
        valid = valid & valid_entry(self._ent_port, VALINT, 1, MAXPORT)
        if self._settings["ggamode"] == 1:  # fixed reference
            valid = valid & valid_entry(self._ent_lat, VALFLOAT, -90.0, 90.0)
            valid = valid & valid_entry(self._ent_lon, VALFLOAT, -180.0, 180.0)
            valid = valid & valid_entry(self._ent_alt, VALFLOAT, -MAXALT, MAXALT)
            valid = valid & valid_entry(self._ent_sep, VALFLOAT, -MAXALT, MAXALT)

        if not valid:
            self.set_status("ERROR - invalid settings", "red")

        return valid

    def set_mp_dist(self, dist: float, name: str = ""):
        """
        Set mountpoint distance label.

        :param float dist: distance to mountpoint km
        """

        if name in (None, ""):
            return
        dist_l = "Distance n/a"
        dist_u = "km"
        if isinstance(dist, float):
            units = self.__app.frm_settings.units
            if units in (UI, UIK):
                dist *= KM2MILES
                dist_u = "miles"
            dist_l = f"Distance {dist:,.1f} {dist_u}"

        self._ntrip_mountpoint.set(name)
        self._ntrip_mpdist.set(dist_l)

    def _get_coordinates(self) -> tuple:
        """
        Get coordinates from receiver or fixed reference settings.

        :returns: tuple (lat,lon)
        :rtype: tuple
        """

        try:
            if self._settings.get("ggamode", 0) == 0:  # live position
                _, lat, lon, _, _ = self.__app.get_coordinates()
            else:  # fixed reference
                lat = float(self._settings["reflat"])
                lon = float(self._settings["reflon"])
            return lat, lon
        except (ValueError, TypeError):
            return "", ""
