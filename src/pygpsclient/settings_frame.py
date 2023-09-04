"""
settings_frame.py

Settings frame class for PyGPSClient application.

- Holds all the latest settings in self.config
- Sets initial (saved) configuration of the following frames:
- frm_settings (SettingsFrame class) for general application settings.
- frm_serial (SerialConfigFrame class) for serial port settings.
- frm_socketclient (SocketConfigFrame class) for socket client settings.
- frm_socketserver (ServerConfigFrame class) for socket server settings.

Created on 12 Sep 2020

:author: semuadmin
:copyright: SEMU Consulting © 2020
:license: BSD 3-Clause
"""
# pylint: disable=unnecessary-lambda

from socket import AF_INET6
from tkinter import (
    ALL,
    BOTH,
    BOTTOM,
    DISABLED,
    HORIZONTAL,
    LEFT,
    NORMAL,
    RIGHT,
    VERTICAL,
    Button,
    Canvas,
    Checkbutton,
    E,
    Frame,
    IntVar,
    Label,
    Scrollbar,
    Spinbox,
    StringVar,
    TclError,
    W,
    X,
    Y,
    ttk,
)

from PIL import Image, ImageTk
from pyubx2 import GET
from pyubx2 import ubxtypes_core as ubt
from serial import PARITY_NONE

from pygpsclient.globals import (
    BADCOL,
    BPSRATES,
    CONNECTED,
    CONNECTED_FILE,
    CONNECTED_SOCKET,
    DDD,
    DISCONNECTED,
    DLG,
    DLGTNTRIP,
    DLGTSPARTN,
    DLGTUBX,
    DMM,
    DMS,
    ECEF,
    FORMAT_BINARY,
    FORMAT_PARSED,
    FORMATS,
    GNSS_EOF_EVENT,
    GNSS_ERR_EVENT,
    GNSS_EVENT,
    ICON_CONN,
    ICON_DISCONN,
    ICON_EXIT,
    ICON_LOGREAD,
    ICON_NTRIPCONFIG,
    ICON_SERIAL,
    ICON_SOCKET,
    ICON_SPARTNCONFIG,
    ICON_UBXCONFIG,
    KNOWNGPS,
    MSGMODES,
    NOPORTS,
    RCVR_CONNECTION,
    READONLY,
    SOCK_NTRIP,
    TIMEOUTS,
    UI,
    UIK,
    UMK,
    UMM,
)
from pygpsclient.helpers import adjust_dimensions
from pygpsclient.mapquest import MAP_UPDATE_INTERVAL
from pygpsclient.serialconfig_frame import SerialConfigFrame
from pygpsclient.serverconfig_frame import ServerConfigFrame
from pygpsclient.socketconfig_frame import SocketConfigFrame
from pygpsclient.strings import (
    LBLDATADISP,
    LBLDATALOG,
    LBLDEGFORMAT,
    LBLNTRIPCONFIG,
    LBLPROTDISP,
    LBLSHOWUNUSED,
    LBLSPARTNCONFIG,
    LBLTRACKRECORD,
    LBLUBXCONFIG,
)

MAXLINES = ("200", "500", "1000", "2000", "100")
MAPTYPES = ("world", "map", "sat")
MINHEIGHT = 690
MINWIDTH = 365


class SettingsFrame(Frame):
    """
    Settings frame class.
    """

    def __init__(self, app, *args, **kwargs):
        """
        Constructor.

        :param Frame app: reference to main tkinter application
        :param args: optional args to pass to Frame parent class
        :param kwargs: optional kwargs to pass to Frame parent class
        """

        self.__app = app  # Reference to main application class
        self.__master = self.__app.appmaster  # Reference to root class (Tk)

        Frame.__init__(self, self.__master, *args, **kwargs)

        self.infilepath = None
        self.outfilepath = None
        self._prot_nmea = IntVar()
        self._prot_ubx = IntVar()
        self._prot_rtcm3 = IntVar()
        self._autoscroll = IntVar()
        self._maxlines = IntVar()
        self.maptype = StringVar()
        self.mapzoom = IntVar()
        self._units = StringVar()
        self._degrees_format = StringVar()
        self._console_format = StringVar()
        self._datalog = IntVar()
        self._logformat = StringVar()
        self._record_track = IntVar()
        self._show_unusedsat = IntVar()
        self.show_legend = IntVar()
        self._colortag = IntVar()
        self._validsettings = True
        self._trackpath = None
        self._img_conn = ImageTk.PhotoImage(Image.open(ICON_CONN))
        self._img_serial = ImageTk.PhotoImage(Image.open(ICON_SERIAL))
        self._img_socket = ImageTk.PhotoImage(Image.open(ICON_SOCKET))
        self._img_disconn = ImageTk.PhotoImage(Image.open(ICON_DISCONN))
        self._img_exit = ImageTk.PhotoImage(Image.open(ICON_EXIT))
        self._img_ubxconfig = ImageTk.PhotoImage(Image.open(ICON_UBXCONFIG))
        self._img_ntripconfig = ImageTk.PhotoImage(Image.open(ICON_NTRIPCONFIG))
        self._img_spartnconfig = ImageTk.PhotoImage(Image.open(ICON_SPARTNCONFIG))
        self._img_dataread = ImageTk.PhotoImage(Image.open(ICON_LOGREAD))

        self._container()  # create scrollable container
        self._body()
        self._do_layout()
        self.reset()

    def _container(self):
        """
        Create scrollable container frame.

        NB: any expandable sub-frames must implement an on_resize()
        function which invokes the on_expand() method here.
        """

        dimw, dimh = [adjust_dimensions(x) for x in (MINWIDTH, MINHEIGHT)]
        self._frm_main = Frame(self)
        self._frm_main.pack(fill=BOTH, expand=1)
        self_frm_scrollx = Frame(self._frm_main)
        self_frm_scrollx.pack(fill=X, side=BOTTOM)
        self._can_container = Canvas(self._frm_main, height=dimh, width=dimw)
        self._frm_container = Frame(self._can_container)
        self._can_container.pack(side=LEFT, fill=BOTH, expand=1)
        x_scrollbar = Scrollbar(
            self_frm_scrollx, orient=HORIZONTAL, command=self._can_container.xview
        )
        x_scrollbar.pack(side=BOTTOM, fill=X)
        y_scrollbar = Scrollbar(
            self._frm_main, orient=VERTICAL, command=self._can_container.yview
        )
        y_scrollbar.pack(side=RIGHT, fill=Y)
        self._can_container.configure(xscrollcommand=x_scrollbar.set)
        self._can_container.configure(yscrollcommand=y_scrollbar.set)
        self._can_container.create_window(
            (0, 0), window=self._frm_container, anchor="nw"
        )
        self._can_container.bind(
            "<Configure>",
            lambda e: self._can_container.config(
                scrollregion=self._can_container.bbox(ALL)
            ),
        )

    def on_expand(self):
        """
        Automatically expand container canvas when sub-frames are resized.
        """

        self._can_container.event_generate("<Configure>")

    def _body(self):
        """
        Set up frame and widgets.
        """

        for i in range(4):
            self._frm_container.grid_columnconfigure(i, weight=1)
        self._frm_container.grid_rowconfigure(0, weight=1)

        self._frm_container.option_add("*Font", self.__app.font_sm)

        # serial port configuration panel
        self.frm_serial = SerialConfigFrame(
            self.__app,
            self._frm_container,
            preselect=KNOWNGPS,
            timeouts=TIMEOUTS,
            bpsrates=BPSRATES,
            msgmodes=list(MSGMODES.keys()),
            saved_config=self.__app.saved_config,
        )

        # socket client configuration panel
        self.frm_socketclient = SocketConfigFrame(
            self.__app, self._frm_container, saved_config=self.__app.saved_config
        )

        # connection buttons
        self._frm_buttons = Frame(self._frm_container)
        self._btn_connect = Button(
            self._frm_buttons,
            width=45,
            height=35,
            image=self._img_serial,
            command=lambda: self._on_connect(CONNECTED),
        )
        self._lbl_connect = Label(self._frm_buttons, text="USB/UART")
        self._btn_connect_socket = Button(
            self._frm_buttons,
            width=45,
            height=35,
            image=self._img_socket,
            command=lambda: self._on_connect(CONNECTED_SOCKET),
        )
        self._lbl_connect_socket = Label(self._frm_buttons, text="TCP/UDP")
        self._btn_connect_file = Button(
            self._frm_buttons,
            width=45,
            height=35,
            image=self._img_dataread,
            command=lambda: self._on_connect(CONNECTED_FILE),
        )
        self._lbl_connect_file = Label(self._frm_buttons, text="FILE")
        self._btn_disconnect = Button(
            self._frm_buttons,
            width=45,
            height=35,
            image=self._img_disconn,
            command=lambda: self._on_connect(DISCONNECTED),
            state=DISABLED,
        )
        self._lbl_disconnect = Label(self._frm_buttons, text="STOP")
        self._btn_exit = Button(
            self._frm_buttons,
            width=45,
            height=35,
            image=self._img_exit,
            command=lambda: self.__app.quit(),
        )

        self._lbl_status_preset = Label(
            self._frm_buttons, font=self.__app.font_md2, text=""
        )

        # Other configuration options
        self._frm_options = Frame(self._frm_container)
        self._lbl_protocol = Label(self._frm_options, text=LBLPROTDISP)
        self._chk_nmea = Checkbutton(
            self._frm_options,
            text="NMEA",
            variable=self._prot_nmea,
        )
        self._chk_ubx = Checkbutton(
            self._frm_options,
            text="UBX",
            variable=self._prot_ubx,
        )
        self._chk_rtcm = Checkbutton(
            self._frm_options,
            text="RTCM",
            variable=self._prot_rtcm3,
        )
        self._lbl_consoledisplay = Label(self._frm_options, text=LBLDATADISP)
        self._spn_conformat = Spinbox(
            self._frm_options,
            values=FORMATS,
            width=10,
            state=READONLY,
            wrap=True,
            textvariable=self._console_format,
        )
        self._chk_tags = Checkbutton(
            self._frm_options,
            text="Tags",
            variable=self._colortag,
        )
        self._lbl_format = Label(self._frm_options, text=LBLDEGFORMAT)
        self._spn_format = Spinbox(
            self._frm_options,
            values=(DDD, DMS, DMM, ECEF),
            width=6,
            state=READONLY,
            wrap=True,
            textvariable=self._degrees_format,
        )
        self._spn_units = Spinbox(
            self._frm_options,
            values=(UMM, UIK, UI, UMK),
            width=13,
            state=READONLY,
            wrap=True,
            textvariable=self._units,
        )
        self._chk_scroll = Checkbutton(
            self._frm_options, text="Autoscroll", variable=self._autoscroll
        )
        self._spn_maxlines = Spinbox(
            self._frm_options,
            values=MAXLINES,
            width=6,
            wrap=True,
            textvariable=self._maxlines,
            state=READONLY,
        )
        self._lbl_maptype = Label(self._frm_options, text="Map Type")
        self.spn_maptype = Spinbox(
            self._frm_options,
            values=MAPTYPES,
            width=6,
            wrap=True,
            textvariable=self.maptype,
            state=READONLY,
        )
        self._chk_unusedsat = Checkbutton(
            self._frm_options, text=LBLSHOWUNUSED, variable=self._show_unusedsat
        )
        self._chk_datalog = Checkbutton(
            self._frm_options,
            text=LBLDATALOG,
            variable=self._datalog,
            command=lambda: self._on_data_log(),
        )
        self._spn_datalog = Spinbox(
            self._frm_options,
            values=(FORMATS),
            width=20,
            wrap=True,
            textvariable=self._logformat,
            state=READONLY,
        )
        self._chk_recordtrack = Checkbutton(
            self._frm_options,
            text=LBLTRACKRECORD,
            variable=self._record_track,
            command=lambda: self._on_record_track(),
        )
        # socket server configuration
        self.frm_socketserver = ServerConfigFrame(
            self.__app, self._frm_container, saved_config=self.__app.saved_config
        )
        # configuration panel buttons
        self._lbl_ubxconfig = Label(
            self._frm_options,
            text=LBLUBXCONFIG,
        )
        self._btn_ubxconfig = Button(
            self._frm_options,
            width=45,
            image=self._img_ubxconfig,
            command=lambda: self._on_ubx_config(),
        )
        self._lbl_ntripconfig = Label(
            self._frm_options,
            text=LBLNTRIPCONFIG,
        )
        self._btn_ntripconfig = Button(
            self._frm_options,
            width=45,
            image=self._img_ntripconfig,
            command=lambda: self._on_ntrip_config(),
        )
        self._lbl_spartnconfig = Label(
            self._frm_options,
            text=LBLSPARTNCONFIG,
        )
        self._btn_spartnconfig = Button(
            self._frm_options,
            width=45,
            image=self._img_spartnconfig,
            command=lambda: self._on_spartn_config(),
        )

    def _do_layout(self):
        """
        Position widgets in frame.
        """

        self.frm_serial.grid(
            column=0, row=1, columnspan=4, padx=2, pady=2, sticky=(W, E)
        )
        ttk.Separator(self._frm_container).grid(
            column=0, row=2, columnspan=4, padx=2, pady=2, sticky=(W, E)
        )

        self.frm_socketclient.grid(
            column=0, row=3, columnspan=4, padx=2, pady=2, sticky=(W, E)
        )
        ttk.Separator(self._frm_container).grid(
            column=0, row=4, columnspan=4, padx=2, pady=2, sticky=(W, E)
        )

        self._frm_buttons.grid(column=0, row=5, columnspan=4, sticky=(W, E))
        self._btn_connect.grid(column=0, row=0, padx=2, pady=1)
        self._btn_connect_socket.grid(column=1, row=0, padx=2, pady=1)
        self._btn_connect_file.grid(column=2, row=0, padx=2, pady=1)
        self._btn_disconnect.grid(column=3, row=0, padx=2, pady=1)
        self._btn_exit.grid(column=4, row=0, padx=2, pady=1)
        self._lbl_connect.grid(column=0, row=1, padx=1, pady=1, sticky=(W, E))
        self._lbl_connect_socket.grid(column=1, row=1, padx=1, pady=1, sticky=(W, E))
        self._lbl_connect_file.grid(column=2, row=1, padx=1, pady=1, sticky=(W, E))
        self._lbl_disconnect.grid(column=3, row=1, padx=1, pady=1, sticky=(W, E))

        ttk.Separator(self._frm_container).grid(
            column=0, row=7, columnspan=4, padx=2, pady=2, sticky=(W, E)
        )

        self._frm_options.grid(column=0, row=8, columnspan=5, sticky=(W, E))
        self._lbl_protocol.grid(column=0, row=0, padx=2, pady=2, sticky=W)
        self._chk_nmea.grid(column=1, row=0, padx=0, pady=0, sticky=W)
        self._chk_ubx.grid(column=2, row=0, padx=0, pady=0, sticky=W)
        self._chk_rtcm.grid(column=3, row=0, padx=0, pady=0, sticky=W)
        self._lbl_consoledisplay.grid(column=0, row=1, padx=2, pady=2, sticky=W)
        self._spn_conformat.grid(
            column=1, row=1, columnspan=2, padx=1, pady=2, sticky=W
        )
        self._chk_tags.grid(column=3, row=1, padx=1, pady=2, sticky=W)
        self._lbl_format.grid(column=0, row=2, padx=2, pady=2, sticky=W)
        self._spn_format.grid(column=1, row=2, padx=2, pady=2, sticky=W)
        self._spn_units.grid(column=2, row=2, columnspan=2, padx=2, pady=2, sticky=W)
        self._chk_scroll.grid(column=0, row=4, padx=2, pady=2, sticky=W)
        self._spn_maxlines.grid(column=1, row=4, columnspan=3, padx=2, pady=2, sticky=W)
        self._lbl_maptype.grid(column=0, row=5, padx=2, pady=2, sticky=W)
        self.spn_maptype.grid(column=1, row=5, padx=2, pady=2, sticky=W)
        self._chk_unusedsat.grid(
            column=0, row=6, columnspan=2, padx=2, pady=2, sticky=W
        )
        self._chk_datalog.grid(column=0, row=7, padx=2, pady=2, sticky=W)
        self._spn_datalog.grid(column=1, row=7, columnspan=3, padx=2, pady=2, sticky=W)
        self._chk_recordtrack.grid(
            column=0, row=8, columnspan=2, padx=2, pady=2, sticky=W
        )
        ttk.Separator(self._frm_options).grid(
            column=0, row=9, columnspan=4, padx=2, pady=2, sticky=(W, E)
        )
        self.frm_socketserver.grid(
            column=0, row=10, columnspan=4, padx=2, pady=2, sticky=(W, E)
        )
        ttk.Separator(self._frm_options).grid(
            column=0, row=11, columnspan=4, padx=2, pady=2, sticky=(W, E)
        )
        self._btn_ubxconfig.grid(column=0, row=13)
        self._lbl_ubxconfig.grid(column=0, row=14)
        self._btn_ntripconfig.grid(column=1, row=13)
        self._lbl_ntripconfig.grid(column=1, row=14)
        self._btn_spartnconfig.grid(column=2, row=13)
        self._lbl_spartnconfig.grid(column=2, row=14)

    def reset(self):
        """
        Reset settings to defaults.
        """

        # self.config = self._saved_config
        self._prot_nmea.set(self.__app.saved_config.get("nmeaprot_b", 1))
        self._prot_ubx.set(self.__app.saved_config.get("ubxprot_b", 1))
        self._prot_rtcm3.set(self.__app.saved_config.get("rtcmprot_b", 1))
        self._degrees_format.set(self.__app.saved_config.get("degreesformat_s", DDD))
        self._colortag.set(self.__app.saved_config.get("colortag_b", 0))
        self._units.set(self.__app.saved_config.get("units_s", UMM))
        self._autoscroll.set(self.__app.saved_config.get("autoscroll_b", 1))
        self._maxlines.set(self.__app.saved_config.get("maxlines_n", MAXLINES[0]))
        self._console_format.set(
            self.__app.saved_config.get("consoleformat_s", FORMAT_PARSED)
        )
        self.maptype.set(self.__app.saved_config.get("maptype_s", MAPTYPES[0]))
        self.mapzoom.set(self.__app.saved_config.get("mapzoom_n", 10))
        self.show_legend.set(self.__app.saved_config.get("legend_b", 1))
        self._show_unusedsat.set(self.__app.saved_config.get("unusedsat_b", 0))
        self._logformat.set(self.__app.saved_config.get("logformat_s", FORMAT_BINARY))
        self._datalog.set(self.__app.saved_config.get("datalog_b", 0))
        self._record_track.set(self.__app.saved_config.get("recordtrack_b", 0))
        self.clients = 0

    def _reset_frames(self):
        """
        Reset frames.
        """

        self.__app.frm_mapview.reset_map_refresh()
        self.__app.frm_spectrumview.reset()
        self.__app.reset_gnssstatus()

    def _on_connect(self, conntype: int):
        """
        Start or stop connection (serial, socket or file).

        :param int conntype: connection type
        """

        conndict = {
            "read_event": GNSS_EVENT,
            "eof_event": GNSS_EOF_EVENT,
            "error_event": GNSS_ERR_EVENT,
            "inqueue": self.__app.gnss_inqueue,
            "outqueue": self.__app.gnss_outqueue,
            "socket_inqueue": self.__app.socket_inqueue,
            "conntype": conntype,
            "msgmode": self.frm_serial.msgmode,
        }

        self.frm_socketserver.set_status(conntype)
        if conntype == CONNECTED:
            frm = self.frm_serial
            if frm.status == NOPORTS:
                return
            connstr = f"{frm.port}:{frm.port_desc} @ {frm.bpsrate}"
            conndict = dict(conndict, **{"serial_settings": frm})
        elif conntype == CONNECTED_SOCKET:
            frm = self.frm_socketclient
            if not frm.valid_settings():
                self.__app.set_status("ERROR - invalid settings", "red")
                return
            connstr = f"{frm.server.get()}:{frm.port.get()}"
            conndict = dict(conndict, **{"socket_settings": frm})
        elif conntype == CONNECTED_FILE:
            self.infilepath = self.__app.file_handler.open_infile()
            if self.infilepath is None:
                return
            connstr = f"{self.infilepath}"
            conndict = dict(conndict, **{"in_filepath": self.infilepath})
        elif conntype == DISCONNECTED:
            if self.__app.conn_status != DISCONNECTED:
                self.__app.conn_status = DISCONNECTED
                self.__app.stream_handler.stop_read_thread()
                return
        else:
            return

        self.__app.set_connection(connstr, "green")
        self.__app.set_status("")
        self.__app.conn_status = conntype
        self._reset_frames()
        self.__app.stream_handler.start_read_thread(self.__app, conndict)

    def _on_ubx_config(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Open UBX configuration dialog panel.
        """

        self.__app.start_dialog(DLGTUBX)

    def _on_ntrip_config(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Open NTRIP Client configuration dialog panel.
        """

        self.__app.start_dialog(DLGTNTRIP)

    def _on_spartn_config(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Open SPARTN Client configuration dialog panel.
        """

        self.__app.start_dialog(DLGTSPARTN)

    def _on_webmap(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Reset webmap refresh timer.
        """

        self.__app.frm_mapview.reset_map_refresh()

    def _on_data_log(self):
        """
        Start or stop data logger.
        """

        if self._datalog.get() == 1:
            self.outfilepath = self.__app.file_handler.set_logfile_path()
            if self.outfilepath is not None:
                self.__app.set_status("Data logging enabled: " + self.outfilepath)
                self.__app.file_handler.open_logfile()
            else:
                self._datalog.set(False)
        else:
            self.outfilepath = None
            self._datalog.set(False)
            self.__app.file_handler.close_logfile()
            self.__app.set_status("Data logging disabled")

    def _on_record_track(self):
        """
        Start or stop track recorder.
        """

        if self._record_track.get() == 1:
            self._trackpath = self.__app.file_handler.set_trackfile_path()
            if self._trackpath is not None:
                self.__app.set_status("Track recording enabled: " + self._trackpath)
                self.__app.file_handler.open_trackfile()
            else:
                self._record_track.set(False)
        else:
            self._trackpath = None
            self._record_track.set(False)
            self.__app.file_handler.close_trackfile()
            self.__app.set_status("Track recording disabled")

    def enable_controls(self, status: int):
        """
        Public method to enable or disable controls depending on
        connection status.

        :param int status: connection status as integer
               (0=Disconnected, 1=Connected to serial,
               2=Connected to file, 3=No serial ports available)

        """

        self.frm_serial.set_status(status)
        self.frm_socketclient.set_status(status)
        self.frm_socketserver.set_status(status)

        self._btn_connect.config(
            state=(
                DISABLED
                if status in (CONNECTED, CONNECTED_SOCKET, CONNECTED_FILE, NOPORTS)
                else NORMAL
            )
        )
        for ctl in (
            self._btn_connect_socket,
            self._btn_connect_file,
            self._chk_datalog,
            self._chk_recordtrack,
        ):
            ctl.config(
                state=(
                    DISABLED
                    if status in (CONNECTED, CONNECTED_SOCKET, CONNECTED_FILE)
                    else NORMAL
                )
            )
        self._btn_disconnect.config(
            state=(DISABLED if status in (DISCONNECTED,) else NORMAL)
        )
        self._spn_datalog.config(
            state=(
                DISABLED
                if status in (CONNECTED, CONNECTED_SOCKET, CONNECTED_FILE)
                else READONLY
            )
        )

    def get_size(self) -> tuple:
        """
        Get current frame size.

        :return: (width, height)
        :rtype: tuple

        """

        self.update_idletasks()  # Make sure we know about any resizing
        return (self.winfo_width(), self.winfo_height())

    @property
    def config(self) -> dict:
        """
        Getter for current configuration settings from all frames and
        protocol handlers. Use the output from this function to save
        configuration settings to a *.json config file.

        :return: settings as dictionary
        :rtype: dict
        """

        try:
            protocol = (
                (ubt.NMEA_PROTOCOL * self._prot_nmea.get())
                + (ubt.UBX_PROTOCOL * self._prot_ubx.get())
                + (ubt.RTCM3_PROTOCOL * self._prot_rtcm3.get())
            )
            sockmode = 1 if self.frm_socketserver.sock_mode.get() == SOCK_NTRIP else 0

            ntripclient_settings = self.__app.ntrip_handler.settings
            spartnclient_settings = self.__app.spartn_handler.settings
            # get SPARTN L-Band settings if (and ONLY if) dialog is open
            lband_dlg = self.__app.dialogs[DLGTSPARTN][DLG]
            lband_settings = (
                {} if lband_dlg is None else lband_dlg.frm_corrlband.settings
            )
            ntripprot = "IPv6" if ntripclient_settings["ipprot"] == AF_INET6 else "IPv4"
            ggaint = ntripclient_settings["ggainterval"]
            if ggaint == "None":
                ggaint = -1

            config = {
                # main settings from frm_settings
                "protocol_n": protocol,
                "nmeaprot_b": self._prot_nmea.get(),
                "ubxprot_b": self._prot_ubx.get(),
                "rtcmprot_b": self._prot_rtcm3.get(),
                "degreesformat_s": self._degrees_format.get(),
                "colortag_b": self._colortag.get(),
                "units_s": self._units.get(),
                "autoscroll_b": self._autoscroll.get(),
                "maxlines_n": self._maxlines.get(),
                "consoleformat_s": self._console_format.get(),
                "maptype_s": self.maptype.get(),
                "mapzoom_n": self.mapzoom.get(),
                "legend_b": self.show_legend.get(),
                "unusedsat_b": self._show_unusedsat.get(),
                "logformat_s": self._logformat.get(),
                "datalog_b": self._datalog.get(),
                "recordtrack_b": self._record_track.get(),
                # serial port settings from frm_serial
                "bpsrate_n": self.frm_serial.bpsrate,
                "databits_n": self.frm_serial.databits,
                "stopbits_f": self.frm_serial.stopbits,
                "parity_s": self.frm_serial.parity,
                "rtscts_b": self.frm_serial.rtscts,
                "xonxoff_b": self.frm_serial.xonxoff,
                "timeout_f": self.frm_serial.timeout,
                "msgmode_n": self.frm_serial.msgmode,
                "userport_s": self.frm_serial.userport,
                # socket client settings from frm_socketclient
                "sockclienthost_s": self.frm_socketclient.server.get(),
                "sockclientport_n": self.frm_socketclient.port.get(),
                "sockclientprotocol_s": self.frm_socketclient.protocol.get(),
                "sockclientflowinfo_n": self.frm_socketclient.flowinfo.get(),
                "sockclientscopeid_n": self.frm_socketclient.scopeid.get(),
                # socket server settings from frm_socketserver
                "sockserver_b": self.frm_socketserver.socketserving,
                "sockhost_s": self.frm_socketserver.sock_host.get(),
                "sockport_n": self.frm_socketserver.sock_port.get(),
                "sockmode_b": sockmode,
                "ntripcasterbasemode_s": self.frm_socketserver.base_mode.get(),
                "ntripcasteracclimit_f": self.frm_socketserver.acclimit.get(),
                "ntripcasterduration_n": self.frm_socketserver.duration.get(),
                "ntripcasterposmode_s": self.frm_socketserver.pos_mode.get(),
                "ntripcasterfixedlat_f": self.frm_socketserver.fixedlat.get(),
                "ntripcasterfixedlon_f": self.frm_socketserver.fixedlon.get(),
                "ntripcasterfixedalt_f": self.frm_socketserver.fixedalt.get(),
                "ntripcasterdisablenmea_b": self.frm_socketserver.disable_nmea.get(),
                "ntripcasteruser_s": self.frm_socketserver.user.get(),
                "ntripcasterpassword_s": self.frm_socketserver.password.get(),
                # NTRIP client settings from pygnssutils.GNSSNTRIPClient
                "ntripclientserver_s": ntripclient_settings["server"],
                "ntripclientport_n": ntripclient_settings["port"],
                "ntripclientprotocol_s": ntripprot,
                "ntripclientflowinfo_n": ntripclient_settings["flowinfo"],
                "ntripclientscopeid_n": ntripclient_settings["scopeid"],
                "ntripclientmountpoint_s": ntripclient_settings["mountpoint"],
                "ntripclientversion_s": ntripclient_settings["version"],
                "ntripclientuser_s": ntripclient_settings["ntripuser"],
                "ntripclientpassword_s": ntripclient_settings["ntrippassword"],
                "ntripclientggainterval_n": ggaint,
                "ntripclientggamode_b": ntripclient_settings["ggamode"],
                "ntripclientreflat_f": ntripclient_settings["reflat"],
                "ntripclientreflon_f": ntripclient_settings["reflon"],
                "ntripclientrefalt_f": ntripclient_settings["refalt"],
                "ntripclientrefsep_f": ntripclient_settings["refsep"],
                # SPARTN MQTT (IP) client settings from pygnssutils.GNSSMQTTClient
                "mqttclientserver_s": spartnclient_settings["server"],
                "mqttclientport_n": spartnclient_settings["port"],
                "mqttclientid_s": spartnclient_settings["clientid"],
                "mgttclientregion_s": spartnclient_settings["region"],
                "mgttclientmode_n": spartnclient_settings["mode"],
                "mgttclienttopicip_b": spartnclient_settings["topic_ip"],
                "mgttclienttopicmga_b": spartnclient_settings["topic_mga"],
                "mgttclienttopickey_b": spartnclient_settings["topic_key"],
                "mgttclienttlscrt_s": spartnclient_settings["tlscrt"],
                "mgttclienttlskey_s": spartnclient_settings["tlskey"],
                # SPARTN L-Band client settings from SpartnLbandDialog if open
                "lbandclientbpsrate_n": lband_settings.get(
                    "bpsrate", self.__app.saved_config.get("lbandclientbpsrate_n", 9600)
                ),
                "lbandclientdatabits_n": lband_settings.get(
                    "databits", self.__app.saved_config.get("lbandclientdatabits_n", 8)
                ),
                "lbandclientstopbits_f": lband_settings.get(
                    "stopbits",
                    self.__app.saved_config.get("lbandclientstopbits_f", 1.0),
                ),
                "lbandclientparity_s": lband_settings.get(
                    "parity",
                    self.__app.saved_config.get("lbandclientparity_s", PARITY_NONE),
                ),
                "lbandclientrtscts_b": lband_settings.get(
                    "rtscts", self.__app.saved_config.get("lbandclientrtscts_b", 0)
                ),
                "lbandclientxonxoff_b": lband_settings.get(
                    "xonxoff", self.__app.saved_config.get("lbandclientxonxoff_b", 0)
                ),
                "lbandclienttimeout_f": lband_settings.get(
                    "timeout", self.__app.saved_config.get("lbandclienttimeout_f", 0.1)
                ),
                "lbandclientmsgmode_n": lband_settings.get(
                    "msgmode", self.__app.saved_config.get("lbandclientmsgmode_n", GET)
                ),
                "spartnport_s": lband_settings.get(
                    "userport", self.__app.saved_config.get("spartnport_s", "")
                ),
                "lbandclientfreq_n": lband_settings.get(
                    "freq", self.__app.saved_config.get("lbandclientfreq_n", 1556290000)
                ),
                "lbandclientschwin_n": lband_settings.get(
                    "schwin", self.__app.saved_config.get("lbandclientschwin_n", 2200)
                ),
                "lbandclientsid_n": lband_settings.get(
                    "sid", self.__app.saved_config.get("lbandclientsid_n", 21845)
                ),
                "lbandclientdrat_n": lband_settings.get(
                    "drat", self.__app.saved_config.get("lbandclientdrat_n", 2400)
                ),
                "lbandclientusesid_b": lband_settings.get(
                    "usesid", self.__app.saved_config.get("lbandclientusesid_b", 0)
                ),
                "lbandclientdescrm_b": lband_settings.get(
                    "descrm", self.__app.saved_config.get("lbandclientdescrm_b", 1)
                ),
                "lbandclientprescrm_b": lband_settings.get(
                    "prescrm", self.__app.saved_config.get("lbandclientprescrm_b", 0)
                ),
                "lbandclientdescrminit_n": lband_settings.get(
                    "descrminit",
                    self.__app.saved_config.get("lbandclientdescrminit_n", 26969),
                ),
                "lbandclientunqword_s": lband_settings.get(
                    "unqword",
                    self.__app.saved_config.get(
                        "lbandclientunqword_s", "16238547128276412563"
                    ),
                ),
                "lbandclientoutport_s": lband_settings.get(
                    "outport",
                    self.__app.saved_config.get("lbandclient_outport_s", "Passthrough"),
                ),
                "lbandclientdebug_b": lband_settings.get(
                    "debug",
                    self.__app.saved_config.get(
                        "lbandclientdebug_b",
                        0,
                    ),
                ),
                # Manually edited config settings
                # (cater for older config file element names without suffices)
                "mapupdateinterval_n": self.__app.saved_config.get(
                    "mapupdateinterval_n",
                    self.__app.saved_config.get(
                        "mapupdateinterval", MAP_UPDATE_INTERVAL
                    ),
                ),
                "defaultport_s": self.__app.saved_config.get(
                    "defaultport_s",
                    self.__app.saved_config.get("defaultport", RCVR_CONNECTION),
                ),
                "mqapikey_s": self.__app.saved_config.get(
                    "mqapikey_s",
                    self.__app.saved_config.get("mqapikey", self.__app.mqapikey),
                ),
                "colortags_l": self.__app.saved_config.get(
                    "colortags_l", self.__app.saved_config.get("colortags", [])
                ),
                "ubxpresets_l": self.__app.saved_config.get(
                    "ubxpresets_l", self.__app.saved_config.get("ubxpresets", [])
                ),
            }
            return config
        except (KeyError, ValueError, TypeError, TclError) as err:
            self.__app.set_status(f"Error processing config data: {err}", BADCOL)
            return {}
