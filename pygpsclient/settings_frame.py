"""
Settings frame class for PyGPSClient application.

This handles the settings/configuration panel.

Created on 12 Sep 2020

@author: semuadmin
"""

from tkinter import (
    ttk,
    Frame,
    Button,
    Label,
    Spinbox,
    Scrollbar,
    Listbox,
    Scale,
    Checkbutton,
    Radiobutton,
    StringVar,
    IntVar,
    DoubleVar,
    N,
    S,
    E,
    W,
    LEFT,
    NORMAL,
    DISABLED,
    VERTICAL,
    HORIZONTAL,
)

from PIL import ImageTk, Image
from serial.tools.list_ports import comports

from .globals import (
    ENTCOL,
    DDD,
    DMM,
    DMS,
    UMM,
    UMK,
    UI,
    UIK,
    ADVON,
    ADVOFF,
    READONLY,
    CONNECTED,
    CONNECTED_FILE,
    DISCONNECTED,
    NOPORTS,
    KNOWNGPS,
    ICON_CONN,
    ICON_DISCONN,
    ICON_UBXCONFIG,
    ICON_LOGREAD,
    BAUDRATES,
    NMEA_PROTOCOL,
    UBX_PROTOCOL,
    MIXED_PROTOCOL,
)
from .strings import (
    LBLUBXCONFIG,
    LBLPROTDISP,
    LBLDATADISP,
    LBLDATALOG,
    LBLTRACKRECORD,
    LBLSHOWNULL,
    LBLLEGEND,
)


class SettingsFrame(Frame):
    """
    Frame inheritance class for application settings and controls.
    """

    def __init__(self, app, *args, **kwargs):
        """
        Constructor.

        :param object app: reference to main tkinter application
        """

        self.__app = app  # Reference to main application class
        self.__master = self.__app.get_master()  # Reference to root class (Tk)
        Frame.__init__(self, self.__master, *args, **kwargs)

        self._show_advanced = False
        self._settings = {}
        self._ports = ()
        self._port = StringVar()
        self._port_desc = StringVar()
        self._baudrate = IntVar()
        self._databits = IntVar()
        self._stopbits = DoubleVar()
        self._parity = StringVar()
        self._rtscts = IntVar()
        self._xonxoff = IntVar()
        self._protocol = IntVar()
        self._raw = IntVar()
        self._autoscroll = IntVar()
        self._maxlines = IntVar()
        self._webmap = IntVar()
        self._mapzoom = IntVar()
        self._units = StringVar()
        self._format = StringVar()
        self._datalog = IntVar()
        self._record_track = IntVar()
        self._show_zerosig = IntVar()
        self._show_legend = IntVar()
        self._noports = True
        self._validsettings = True
        self._logpath = None
        self._trackpath = None
        self._img_conn = ImageTk.PhotoImage(Image.open(ICON_CONN))
        self._img_disconn = ImageTk.PhotoImage(Image.open(ICON_DISCONN))
        self._img_ubxconfig = ImageTk.PhotoImage(Image.open(ICON_UBXCONFIG))
        self._img_dataread = ImageTk.PhotoImage(Image.open(ICON_LOGREAD))

        self._body()
        self._do_layout()
        self._get_ports()
        self._reset()

    def _body(self):
        """
        Set up frame and widgets.
        """

        for i in range(4):
            self.grid_columnconfigure(i, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.option_add("*Font", self.__app.font_sm)

        # Serial port settings
        self._frm_basic = Frame(self)
        self._lbl_port = Label(self._frm_basic, text="Port")
        self._lbx_port = Listbox(
            self._frm_basic,
            border=2,
            relief="sunken",
            bg=ENTCOL,
            width=28,
            height=5,
            justify=LEFT,
            exportselection=False,
        )
        self._scr_portv = Scrollbar(self._frm_basic, orient=VERTICAL)
        self._scr_porth = Scrollbar(self._frm_basic, orient=HORIZONTAL)
        self._lbx_port.config(yscrollcommand=self._scr_portv.set)
        self._lbx_port.config(xscrollcommand=self._scr_porth.set)
        self._scr_portv.config(command=self._lbx_port.yview)
        self._scr_porth.config(command=self._lbx_port.xview)
        self._lbx_port.bind("<<ListboxSelect>>", self._on_select_port)
        self._lbl_baudrate = Label(self._frm_basic, text="Baud rate")
        self._spn_baudrate = Spinbox(
            self._frm_basic,
            values=(BAUDRATES),
            width=8,
            state=READONLY,
            readonlybackground=ENTCOL,
            wrap=True,
            textvariable=self._baudrate,
        )
        self._btn_toggle = Button(
            self._frm_basic, text=ADVOFF, width=3, command=self._toggle_advanced
        )

        self._frm_advanced = Frame(self)
        self._lbl_databits = Label(self._frm_advanced, text="Data Bits")
        self._spn_databits = Spinbox(
            self._frm_advanced,
            values=(8, 7, 6, 5),
            width=3,
            state=READONLY,
            readonlybackground=ENTCOL,
            wrap=True,
            textvariable=self._databits,
        )
        self._lbl_stopbits = Label(self._frm_advanced, text="Stop Bits")
        self._spn_stopbits = Spinbox(
            self._frm_advanced,
            values=(2, 1.5, 1),
            width=3,
            state=READONLY,
            readonlybackground=ENTCOL,
            wrap=True,
            textvariable=self._stopbits,
        )
        self._lbl_parity = Label(self._frm_advanced, text="Parity")
        self._spn_parity = Spinbox(
            self._frm_advanced,
            values=("None", "Even", "Odd", "Mark", "Space"),
            width=6,
            state=READONLY,
            readonlybackground=ENTCOL,
            wrap=True,
            textvariable=self._parity,
        )
        self._chk_rts = Checkbutton(
            self._frm_advanced, text="RTS/CTS", variable=self._rtscts
        )
        self._chk_xon = Checkbutton(
            self._frm_advanced, text="Xon/Xoff", variable=self._xonxoff
        )

        self._frm_buttons = Frame(self)
        self._btn_connect = Button(
            self._frm_buttons,
            width=45,
            height=35,
            image=self._img_conn,
            command=lambda: self.__app.serial_handler.connect(),
        )
        self._btn_disconnect = Button(
            self._frm_buttons,
            width=45,
            height=35,
            image=self._img_disconn,
            command=lambda: self.__app.serial_handler.disconnect(),
            state=DISABLED,
        )
        self._btn_connect_file = Button(
            self._frm_buttons,
            width=45,
            height=35,
            image=self._img_dataread,
            command=lambda: self._on_data_stream(),
        )
        self._lbl_status_preset = Label(
            self._frm_buttons, font=self.__app.font_md2, text=""
        )

        # Other configuration options
        self._frm_options = Frame(self)
        self._lbl_protocol = Label(self._frm_options, text=LBLPROTDISP)
        self._rad_nmea = Radiobutton(
            self._frm_options, text="NMEA", variable=self._protocol, value=NMEA_PROTOCOL
        )
        self._rad_ubx = Radiobutton(
            self._frm_options, text="UBX", variable=self._protocol, value=UBX_PROTOCOL
        )
        self._rad_all = Radiobutton(
            self._frm_options, text="ALL", variable=self._protocol, value=MIXED_PROTOCOL
        )
        self._lbl_consoledisplay = Label(self._frm_options, text=LBLDATADISP)
        self._rad_parsed = Radiobutton(
            self._frm_options, text="Parsed", variable=self._raw, value=0
        )
        self._rad_raw = Radiobutton(
            self._frm_options, text="Raw", variable=self._raw, value=1
        )
        self._lbl_format = Label(self._frm_options, text="Degrees Format")
        self._spn_format = Spinbox(
            self._frm_options,
            values=(DDD, DMS, DMM),
            width=6,
            state=READONLY,
            readonlybackground=ENTCOL,
            wrap=True,
            textvariable=self._format,
        )
        self._lbl_units = Label(self._frm_options, text="Units")
        self._spn_units = Spinbox(
            self._frm_options,
            values=(UMM, UIK, UI, UMK),
            width=13,
            state=READONLY,
            readonlybackground=ENTCOL,
            wrap=True,
            textvariable=self._units,
        )
        self._chk_scroll = Checkbutton(
            self._frm_options, text="Autoscroll", variable=self._autoscroll
        )
        self._spn_maxlines = Spinbox(
            self._frm_options,
            values=("100", "200", "500", "1000", "2000"),
            width=6,
            readonlybackground=ENTCOL,
            wrap=True,
            textvariable=self._maxlines,
            state=READONLY,
        )
        self._chk_webmap = Checkbutton(
            self._frm_options,
            text="Web Map  Zoom",
            variable=self._webmap,
            command=lambda: self._on_webmap(),
        )
        self._scl_mapzoom = Scale(
            self._frm_options,
            from_=1,
            to=20,
            orient=HORIZONTAL,
            relief="sunken",
            bg=ENTCOL,
            variable=self._mapzoom,
        )
        self._chk_zerosig = Checkbutton(
            self._frm_options, text=LBLSHOWNULL, variable=self._show_zerosig
        )
        self._chk_legend = Checkbutton(
            self._frm_options, text=LBLLEGEND, variable=self._show_legend
        )
        self._chk_datalog = Checkbutton(
            self._frm_options,
            text=LBLDATALOG,
            variable=self._datalog,
            command=lambda: self._on_data_log(),
        )
        self._chk_recordtrack = Checkbutton(
            self._frm_options,
            text=LBLTRACKRECORD,
            variable=self._record_track,
            command=lambda: self._on_record_track(),
        )
        self._lbl_ubxconfig = Label(self._frm_options, text=LBLUBXCONFIG)
        self._btn_ubxconfig = Button(
            self._frm_options,
            width=45,
            height=35,
            text="UBX",
            image=self._img_ubxconfig,
            command=lambda: self._on_ubx_config(),
            state=DISABLED,
        )

    def _do_layout(self):
        """
        Position widgets in frame.
        """

        self._frm_basic.grid(column=0, row=0, columnspan=4, sticky=(W, E))
        self._lbl_port.grid(column=0, row=0, sticky=(W))
        self._lbx_port.grid(column=1, row=0, sticky=(W, E), padx=3, pady=3)
        self._scr_portv.grid(column=2, row=0, sticky=(N, S))
        self._scr_porth.grid(column=1, row=1, sticky=(E, W))
        self._lbl_baudrate.grid(column=0, row=2, sticky=(W))
        self._spn_baudrate.grid(column=1, row=2, sticky=(W), padx=3, pady=3)
        self._btn_toggle.grid(column=2, row=2, sticky=(E))

        self._frm_advanced.grid_forget()
        self._lbl_databits.grid(column=0, row=0, sticky=(W))
        self._spn_databits.grid(column=1, row=0, sticky=(W), padx=3, pady=3)
        self._lbl_stopbits.grid(column=2, row=0, sticky=(W))
        self._spn_stopbits.grid(column=3, row=0, sticky=(W), padx=3, pady=3)
        self._lbl_parity.grid(column=0, row=1, sticky=(W))
        self._spn_parity.grid(column=1, row=1, sticky=(W), padx=3, pady=3)
        self._chk_rts.grid(column=2, row=1, sticky=(W))
        self._chk_xon.grid(column=3, row=1, sticky=(W), padx=3, pady=3)

        ttk.Separator(self).grid(
            column=0, row=2, columnspan=4, padx=3, pady=3, sticky=(W, E)
        )

        self._frm_buttons.grid(column=0, row=3, columnspan=4, sticky=(W, E))
        self._btn_connect.grid(column=0, row=0, padx=3, pady=3)
        self._btn_connect_file.grid(column=1, row=0, padx=3, pady=3)
        self._btn_disconnect.grid(column=3, row=0, padx=3, pady=3)

        ttk.Separator(self).grid(
            column=0, row=7, columnspan=4, padx=3, pady=3, sticky=(W, E)
        )

        self._frm_options.grid(column=0, row=8, columnspan=4, sticky=(W, E))
        self._lbl_protocol.grid(column=0, row=0, padx=3, pady=3, sticky=(W))
        self._rad_nmea.grid(column=1, row=0, padx=0, pady=0, sticky=(W))
        self._rad_ubx.grid(column=2, row=0, padx=0, pady=0, sticky=(W))
        self._rad_all.grid(column=3, row=0, padx=0, pady=0, sticky=(W))
        self._lbl_consoledisplay.grid(column=0, row=1, padx=2, pady=3, sticky=(W))
        self._rad_parsed.grid(column=1, row=1, padx=1, pady=3, sticky=(W))
        self._rad_raw.grid(column=2, row=1, padx=2, pady=3, sticky=(W))
        self._lbl_format.grid(column=0, row=2, padx=3, pady=3, sticky=(W))
        self._spn_format.grid(column=1, row=2, padx=2, pady=3, sticky=(W))
        self._lbl_units.grid(column=0, row=3, padx=3, pady=3, sticky=(W))
        self._spn_units.grid(column=1, row=3, columnspan=3, padx=2, pady=3, sticky=(W))
        self._chk_scroll.grid(column=0, row=4, padx=3, pady=3, sticky=(W))
        self._spn_maxlines.grid(
            column=1, row=4, columnspan=3, padx=3, pady=3, sticky=(W)
        )
        self._chk_webmap.grid(column=0, row=5, padx=3, pady=3, sticky=(W))
        self._scl_mapzoom.grid(column=1, row=5, columnspan=3, sticky=(W))
        self._chk_legend.grid(column=0, row=6, padx=3, pady=3, sticky=(W))
        self._chk_zerosig.grid(
            column=1, row=6, columnspan=2, padx=3, pady=3, sticky=(W)
        )
        self._chk_datalog.grid(column=0, row=7, padx=3, pady=3, sticky=(W))
        self._chk_recordtrack.grid(
            column=1, row=7, columnspan=2, padx=3, pady=3, sticky=(W)
        )

        ttk.Separator(self._frm_options).grid(
            column=0, row=8, columnspan=4, padx=3, pady=3, sticky=(W, E)
        )
        self._lbl_ubxconfig.grid(column=0, row=9, padx=3, pady=3, sticky=(W))
        self._btn_ubxconfig.grid(column=1, row=9, padx=3, pady=3, sticky=(W))

    def _on_select_port(self, *args, **kwargs):
        """
        Get selected port from listbox and set global variable.
        """

        idx = self._lbx_port.curselection()
        if idx == "":
            idx = 0
        port_orig = self._lbx_port.get(idx)
        port = port_orig[0 : port_orig.find(":")]
        desc = port_orig[port_orig.find(":") + 1 :]
        if desc == "":
            desc = "device"
        self._port.set(port)
        self._port_desc.set(desc)

    def _on_ubx_config(self, *args, **kwargs):
        """
        Open UBX configuration dialog panel.
        """

        self.__app.ubxconfig()

    def _on_webmap(self):
        """
        Reset webmap refresh timer
        """

        self.__app.frm_mapview.reset_map_refresh()

    def _on_data_log(self):
        """
        Start or stop data logger
        """

        if self._datalog.get() == 1:
            self._logpath = self.__app.file_handler.set_logfile_path()
            if self._logpath is not None:
                self.__app.set_status("Data logging enabled: " + self._logpath, "green")
            else:
                self._datalog.set(False)
        else:
            self._logpath = None
            self._datalog.set(False)
            #             self.__app.file_handler.close_logfile()
            self.__app.set_status("Data logging disabled", "blue")

    def _on_record_track(self):
        """
        Start or stop track recorder
        """

        if self._record_track.get() == 1:
            self._trackpath = self.__app.file_handler.set_trackfile_path()
            if self._trackpath is not None:
                self.__app.set_status(
                    "Track recording enabled: " + self._trackpath, "green"
                )
            else:
                self._record_track.set(False)
        else:
            self._trackpath = None
            self._record_track.set(False)
            #             self.__app.file_handler.close_trackfile()
            self.__app.set_status("Track recording disabled", "blue")

    def _on_data_stream(self):
        """
        Start data file streamer
        """

        self._logpath = self.__app.file_handler.open_logfile_input()
        if self._logpath is not None:
            self.__app.set_status("")
            self.__app.serial_handler.connect_file()

    def _toggle_advanced(self):
        """
        Toggle advanced serial port settings panel on or off
        """

        self._show_advanced = not self._show_advanced
        if self._show_advanced:
            self._frm_advanced.grid(column=0, row=1, columnspan=3, sticky=(W, E))
            self._btn_toggle.config(text=ADVON)
        else:
            self._frm_advanced.grid_forget()
            self._btn_toggle.config(text=ADVOFF)

    def _get_ports(self):
        """
        Populate list of available serial ports using pyserial comports tool.
        If no ports found, disable all connection-dependent widgets.

        Attempt to preselect the first port that has a recognisable
        GPS designation in its description (usually only works on
        Posix platforms - Windows doesn't parse UART device desc or HWID)
        """

        self._ports = sorted(comports())
        init_idx = 0
        port = ""
        desc = ""
        if len(self._ports) > 0:
            for idx, (port, desc, _) in enumerate(self._ports, 1):
                self._lbx_port.insert(idx, port + ": " + desc)
                for kgp in KNOWNGPS:
                    if kgp in desc:
                        init_idx = idx
                        break
            self._noports = False
        else:
            self._noports = True
            self.set_controls(NOPORTS)
        self._lbx_port.activate(init_idx)
        self._port.set(port)
        self._port_desc.set(desc)

    def _reset(self):
        """
        Reset settings to defaults.
        """

        self._baudrate.set(BAUDRATES[4])  # 9600
        self._databits.set(8)
        self._stopbits.set(1)
        self._parity.set("None")
        self._rtscts.set(False)
        self._xonxoff.set(False)
        self._protocol.set(MIXED_PROTOCOL)
        self._format.set(DDD)
        self._units.set(UMM)
        self._autoscroll.set(1)
        self._maxlines.set(300)
        self._raw.set(False)
        self._webmap.set(False)
        self._mapzoom.set(10)
        self._show_legend.set(True)
        self._show_zerosig.set(False)
        self._datalog.set(False)
        self._record_track.set(False)

    def set_controls(self, status: int):
        """
        ...for the heart of the sun.
        Public method to enable and disable serial port controls
        depending on connection status.

        :param int status: connection status as integer (0,1,2)
        """

        self._lbl_port.configure(state=(NORMAL if status == DISCONNECTED else DISABLED))
        self._lbx_port.configure(state=(NORMAL if status == DISCONNECTED else DISABLED))
        self._lbl_baudrate.configure(
            state=(NORMAL if status == DISCONNECTED else DISABLED)
        )
        self._spn_baudrate.configure(
            state=(READONLY if status == DISCONNECTED else DISABLED)
        )
        self._lbl_databits.configure(
            state=(NORMAL if status == DISCONNECTED else DISABLED)
        )
        self._spn_databits.configure(
            state=(READONLY if status == DISCONNECTED else DISABLED)
        )
        self._lbl_stopbits.configure(
            state=(NORMAL if status == DISCONNECTED else DISABLED)
        )
        self._spn_stopbits.configure(
            state=(READONLY if status == DISCONNECTED else DISABLED)
        )
        self._lbl_parity.configure(
            state=(NORMAL if status == DISCONNECTED else DISABLED)
        )
        self._spn_parity.configure(
            state=(READONLY if status == DISCONNECTED else DISABLED)
        )
        self._chk_rts.configure(state=(NORMAL if status == DISCONNECTED else DISABLED))
        self._chk_xon.configure(state=(NORMAL if status == DISCONNECTED else DISABLED))
        self._btn_connect.config(
            state=(
                DISABLED if status in (CONNECTED, CONNECTED_FILE, NOPORTS) else NORMAL
            )
        )
        self._btn_disconnect.config(
            state=(DISABLED if status in (DISCONNECTED, NOPORTS) else NORMAL)
        )
        self._chk_datalog.config(
            state=(
                DISABLED if status in (CONNECTED, CONNECTED_FILE, NOPORTS) else NORMAL
            )
        )
        self._chk_recordtrack.config(
            state=(DISABLED if status in (CONNECTED, CONNECTED_FILE) else NORMAL)
        )
        self._btn_connect_file.config(
            state=(DISABLED if status in (CONNECTED, CONNECTED_FILE) else NORMAL)
        )
        self._btn_ubxconfig.config(
            state=(
                DISABLED
                if status in (DISCONNECTED, CONNECTED_FILE, NOPORTS)
                else NORMAL
            )
        )
        self.__app.menu.options_menu.entryconfig(
            0,
            state=(
                DISABLED
                if status in (CONNECTED_FILE, DISCONNECTED, NOPORTS)
                else NORMAL
            ),
        )

    def get_settings(self) -> dict:
        """
        Public method returns all settings as a dict.

        :return current settings
        :rtype dict
        """

        self._settings["port"] = self._port.get()
        self._settings["noports"] = self._noports
        self._settings["port_desc"] = self._port_desc.get()
        self._settings["baudrate"] = self._baudrate.get()
        self._settings["databits"] = self._databits.get()
        self._settings["stopbits"] = self._stopbits.get()
        self._settings["parity"] = self._parity.get()
        self._settings["rtscts"] = self._rtscts.get()
        self._settings["xonxoff"] = self._xonxoff.get()
        self._settings["protocol"] = self._protocol.get()
        self._settings["raw"] = self._raw.get()
        self._settings["autoscroll"] = self._autoscroll.get()
        self._settings["maxlines"] = self._maxlines.get()
        self._settings["webmap"] = self._webmap.get()
        self._settings["mapzoom"] = self._mapzoom.get()
        self._settings["units"] = self._units.get()
        self._settings["format"] = self._format.get()
        self._settings["logpath"] = self._logpath
        self._settings["datalogging"] = self._datalog.get()
        self._settings["recordtrack"] = self._record_track.get()
        self._settings["zerosignal"] = self._show_zerosig.get()
        self._settings["graphlegend"] = self._show_legend.get()

        return self._settings

    def get_size(self) -> (int, int):
        """
        Get current frame size.

        :return (width, height)
        :rtype tuple
        """

        self.update_idletasks()  # Make sure we know about any resizing
        return (self.winfo_width(), self.winfo_height())
