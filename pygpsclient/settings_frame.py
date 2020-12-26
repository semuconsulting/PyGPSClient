"""
Settings frame class for PyGPSClient application.

This handles the settings/configuration panel.

Created on 12 Sep 2020

@author: semuadmin
"""
# pylint: disable=invalid-name, too-many-instance-attributes, too-many-ancestors, unnecessary-lambda

from tkinter import (
    ttk,
    Frame,
    Button,
    Label,
    Spinbox,
    Scale,
    Checkbutton,
    Radiobutton,
    StringVar,
    IntVar,
    E,
    W,
    NORMAL,
    DISABLED,
    HORIZONTAL,
)

from PIL import ImageTk, Image
from common.serialconfig_frame import SerialConfigFrame
from .globals import (
    ENTCOL,
    DDD,
    DMM,
    DMS,
    UMM,
    UMK,
    UI,
    UIK,
    READONLY,
    CONNECTED,
    CONNECTED_FILE,
    DISCONNECTED,
    NOPORTS,
    ICON_CONN,
    ICON_DISCONN,
    ICON_UBXCONFIG,
    ICON_LOGREAD,
    NMEA_PROTOCOL,
    UBX_PROTOCOL,
    MIXED_PROTOCOL,
    KNOWNGPS,
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

        self._settings = {}
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
        self._validsettings = True
        self._logpath = None
        self._trackpath = None
        self._img_conn = ImageTk.PhotoImage(Image.open(ICON_CONN))
        self._img_disconn = ImageTk.PhotoImage(Image.open(ICON_DISCONN))
        self._img_ubxconfig = ImageTk.PhotoImage(Image.open(ICON_UBXCONFIG))
        self._img_dataread = ImageTk.PhotoImage(Image.open(ICON_LOGREAD))

        self._body()
        self._do_layout()
        self._reset()

    def _body(self):
        """
        Set up frame and widgets.
        """

        for i in range(4):
            self.grid_columnconfigure(i, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.option_add("*Font", self.__app.font_sm)

        # serial port configuration panel
        self._frm_serial = SerialConfigFrame(self, preselect=KNOWNGPS)

        # connection buttons
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

        self._frm_serial.grid(
            column=0, row=1, columnspan=4, padx=3, pady=3, sticky=(W, E)
        )
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

    def _on_ubx_config(self, *args, **kwargs):  # pylint: disable=unused-argument
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

    def _reset(self):
        """
        Reset settings to defaults.
        """

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

        self._frm_serial.set_controls(status)

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

        self._settings["noports"] = self._frm_serial.noports
        self._settings["port"] = self._frm_serial.port
        self._settings["port_desc"] = self._frm_serial.port_desc
        self._settings["baudrate"] = self._frm_serial.baudrate
        self._settings["databits"] = self._frm_serial.databits
        self._settings["stopbits"] = self._frm_serial.stopbits
        self._settings["parity"] = self._frm_serial.parity
        self._settings["rtscts"] = self._frm_serial.rtscts
        self._settings["xonxoff"] = self._frm_serial.xonxoff

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
