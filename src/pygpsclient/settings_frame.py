"""
settings_frame.py

Settings frame class for PyGPSClient application.

- Reads and updates configuration held in self.__app.configuration.
- Starts or stops data logging.
- Sets initial (saved) configuration of the following frames:
- frm_settings (SettingsFrame class) for general application settings.
- frm_serial (SerialConfigFrame class) for serial port settings.
- frm_socketclient (SocketConfigFrame class) for socket client settings.
- frm_socketserver (ServerConfigFrame class) for socket server settings.

Created on 12 Sep 2020

:author: semuadmin (Steve Smith)
:copyright: 2020 semuadmin
:license: BSD 3-Clause
"""

# pylint: disable=unnecessary-lambda, unused-argument

from platform import system
from tkinter import (
    ALL,
    BOTH,
    BOTTOM,
    DISABLED,
    EW,
    HORIZONTAL,
    LEFT,
    NORMAL,
    NW,
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

from pygpsclient.globals import (
    BPSRATES,
    CONNECTED,
    CONNECTED_FILE,
    CONNECTED_SOCKET,
    DDD,
    DISCONNECTED,
    DMM,
    DMS,
    ECEF,
    ERRCOL,
    FORMATS,
    GNSS_EOF_EVENT,
    GNSS_ERR_EVENT,
    GNSS_EVENT,
    GNSS_TIMEOUT_EVENT,
    HOME,
    ICON_CONN,
    ICON_DISCONN,
    ICON_EXIT,
    ICON_LOGREAD,
    ICON_NMEACONFIG,
    ICON_NTRIPCONFIG,
    ICON_SERIAL,
    ICON_SOCKET,
    ICON_TTYCONFIG,
    ICON_UBXCONFIG,
    INFOCOL,
    KNOWNGPS,
    MSGMODES,
    NOPORTS,
    OKCOL,
    READONLY,
    TIMEOUTS,
    TRACEMODE_WRITE,
    UI,
    UIK,
    UMK,
    UMM,
)
from pygpsclient.serialconfig_frame import SerialConfigFrame
from pygpsclient.serverconfig_frame import ServerConfigFrame
from pygpsclient.socketconfig_frame import SocketConfigFrame
from pygpsclient.sqlite_handler import SQLOK
from pygpsclient.strings import (
    DLGTNMEA,
    DLGTNTRIP,
    DLGTTTY,
    DLGTUBX,
    LBLDATABASERECORD,
    LBLDATADISP,
    LBLDATALOG,
    LBLDEGFORMAT,
    LBLNMEACONFIG,
    LBLNTRIPCONFIG,
    LBLPROTDISP,
    LBLSHOWUNUSED,
    LBLTRACKRECORD,
    LBLTTYCONFIG,
    LBLUBXCONFIG,
)

MAXLINES = ("200", "500", "1000", "2000", "100")
FILEDELAYS = (2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000)
# initial dimensions adjusted for different widget
# rendering on different platforms
if system() == "Linux":  # Wayland
    MINHEIGHT = 28
    MINWIDTH = 28
elif system() == "Darwin":  # MacOS

    MINHEIGHT = 38
    MINWIDTH = 30
else:  # Windows and others
    MINHEIGHT = 35
    MINWIDTH = 26


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
        self.logpath = HOME
        self.trackpath = HOME
        self.databasepath = HOME
        self._prot_nmea = IntVar()
        self._prot_ubx = IntVar()
        self._prot_sbf = IntVar()
        self._prot_qgc = IntVar()
        self._prot_rtcm = IntVar()
        self._prot_spartn = IntVar()
        self._prot_tty = IntVar()
        self._autoscroll = IntVar()
        self._maxlines = IntVar()
        self._filedelay = IntVar()
        self._units = StringVar()
        self._degrees_format = StringVar()
        self._console_format = StringVar()
        self._datalog = IntVar()
        self._logformat = StringVar()
        self._record_track = IntVar()
        self._record_database = IntVar()
        self._show_unusedsat = IntVar()
        self._colortag = IntVar()
        self.defaultports = self.__app.configuration.get("defaultport_s")
        self._validsettings = True
        self._img_conn = ImageTk.PhotoImage(Image.open(ICON_CONN))
        self._img_serial = ImageTk.PhotoImage(Image.open(ICON_SERIAL))
        self._img_socket = ImageTk.PhotoImage(Image.open(ICON_SOCKET))
        self._img_disconn = ImageTk.PhotoImage(Image.open(ICON_DISCONN))
        self._img_exit = ImageTk.PhotoImage(Image.open(ICON_EXIT))
        self._img_ubxconfig = ImageTk.PhotoImage(Image.open(ICON_UBXCONFIG))
        self._img_nmeaconfig = ImageTk.PhotoImage(Image.open(ICON_NMEACONFIG))
        self._img_ttyconfig = ImageTk.PhotoImage(Image.open(ICON_TTYCONFIG))
        self._img_ntripconfig = ImageTk.PhotoImage(Image.open(ICON_NTRIPCONFIG))
        self._img_dataread = ImageTk.PhotoImage(Image.open(ICON_LOGREAD))

        self._container()  # create scrollable container
        self._body()
        self._do_layout()
        self.reset()
        # self._attach_events() # done in reset
        self.focus_force()

    def _container(self):
        """
        Create scrollable container frame.

        NB: any expandable sub-frames must implement an on_resize()
        function which invokes the on_expand() method here.
        """

        fntw = self.__app.font_md.measure("W")
        fnth = self.__app.font_md.metrics("linespace")
        dimw = fntw * MINWIDTH
        dimh = fnth * MINHEIGHT
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
        self._can_container.create_window((0, 0), window=self._frm_container, anchor=NW)
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
            recognised=KNOWNGPS,
            timeouts=TIMEOUTS,
            bpsrates=BPSRATES,
            msgmodes=list(MSGMODES.keys()),
        )

        # socket client configuration panel
        self.frm_socketclient = SocketConfigFrame(self.__app, self._frm_container)

        # connection buttons
        self._frm_buttons = Frame(self._frm_container)
        self._btn_connect = Button(
            self._frm_buttons,
            width=45,
            height=35,
            image=self._img_serial,
            command=lambda: self._on_connect(CONNECTED),
            state=NORMAL,
        )
        self._lbl_connect = Label(self._frm_buttons, text="USB/UART")
        self._btn_connect_socket = Button(
            self._frm_buttons,
            width=45,
            height=35,
            image=self._img_socket,
            command=lambda: self._on_connect(CONNECTED_SOCKET),
            state=NORMAL,
        )
        self._lbl_connect_socket = Label(self._frm_buttons, text="TCP/UDP")
        self._btn_connect_file = Button(
            self._frm_buttons,
            width=45,
            height=35,
            image=self._img_dataread,
            command=lambda: self._on_connect(CONNECTED_FILE),
            state=NORMAL,
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
            command=lambda: self.__app.on_exit(),
            state=NORMAL,
        )

        self._lbl_status_preset = Label(
            self._frm_buttons, font=self.__app.font_md2, text=""
        )

        # Other configuration options
        self._frm_options = Frame(self._frm_container)
        self._frm_options_btns = Frame(self._frm_options)
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
            variable=self._prot_rtcm,
        )
        self._chk_spartn = Checkbutton(
            self._frm_options,
            text="SPARTN",
            variable=self._prot_spartn,
        )
        self._chk_sbf = Checkbutton(
            self._frm_options,
            text="SBF",
            variable=self._prot_sbf,
        )
        self._chk_qgc = Checkbutton(
            self._frm_options,
            text="QGC",
            variable=self._prot_qgc,
        )
        self._chk_tty = Checkbutton(
            self._frm_options,
            text="TTY",
            variable=self._prot_tty,
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
        self._lbl_filedelay = Label(
            self._frm_options,
            text="File Delay",
        )
        self._spn_filedelay = Spinbox(
            self._frm_options,
            value=FILEDELAYS,
            width=4,
            wrap=True,
            textvariable=self._filedelay,
            state=READONLY,
            repeatdelay=1000,
            repeatinterval=1000,
        )
        self._chk_unusedsat = Checkbutton(
            self._frm_options, text=LBLSHOWUNUSED, variable=self._show_unusedsat
        )
        self._chk_datalog = Checkbutton(
            self._frm_options,
            text=LBLDATALOG,
            variable=self._datalog,
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
        )
        self._chk_recorddatabase = Checkbutton(
            self._frm_options,
            text=LBLDATABASERECORD,
            variable=self._record_database,
        )
        # configuration panel buttons
        self._lbl_ubxconfig = Label(
            self._frm_options_btns,
            text=LBLUBXCONFIG,
        )
        self._btn_ubxconfig = Button(
            self._frm_options_btns,
            width=45,
            image=self._img_ubxconfig,
            command=lambda: self.__app.start_dialog(DLGTUBX),
        )
        self._lbl_nmeaconfig = Label(
            self._frm_options_btns,
            text=LBLNMEACONFIG,
        )
        self._btn_nmeaconfig = Button(
            self._frm_options_btns,
            width=45,
            image=self._img_nmeaconfig,
            command=lambda: self.__app.start_dialog(DLGTNMEA),
            state=NORMAL,
        )
        self._lbl_ttyconfig = Label(
            self._frm_options_btns,
            text=LBLTTYCONFIG,
        )
        self._btn_ttyconfig = Button(
            self._frm_options_btns,
            width=45,
            image=self._img_ttyconfig,
            command=lambda: self.__app.start_dialog(DLGTTTY),
            state=NORMAL,
        )
        self._lbl_ntripconfig = Label(
            self._frm_options_btns,
            text=LBLNTRIPCONFIG,
        )
        self._btn_ntripconfig = Button(
            self._frm_options_btns,
            width=45,
            image=self._img_ntripconfig,
            command=lambda: self.__app.start_dialog(DLGTNTRIP),
            state=NORMAL,
        )
        # socket server configuration
        self.frm_socketserver = ServerConfigFrame(
            self.__app,
            self._frm_container,
        )

    def _do_layout(self):
        """
        Position widgets in frame.
        """

        self.frm_serial.grid(column=0, row=1, columnspan=4, padx=2, pady=2, sticky=EW)
        ttk.Separator(self._frm_container).grid(
            column=0, row=2, columnspan=4, padx=2, pady=2, sticky=EW
        )

        self.frm_socketclient.grid(
            column=0, row=3, columnspan=4, padx=2, pady=2, sticky=EW
        )
        ttk.Separator(self._frm_container).grid(
            column=0, row=4, columnspan=4, padx=2, pady=2, sticky=EW
        )

        self._frm_buttons.grid(column=0, row=5, columnspan=4, sticky=EW)
        self._btn_connect.grid(column=0, row=0, padx=2, pady=1)
        self._btn_connect_socket.grid(column=1, row=0, padx=2, pady=1)
        self._btn_connect_file.grid(column=2, row=0, padx=2, pady=1)
        self._btn_disconnect.grid(column=3, row=0, padx=2, pady=1)
        self._btn_exit.grid(column=4, row=0, padx=2, pady=1)
        self._lbl_connect.grid(column=0, row=1, padx=1, pady=1, sticky=EW)
        self._lbl_connect_socket.grid(column=1, row=1, padx=1, pady=1, sticky=EW)
        self._lbl_connect_file.grid(column=2, row=1, padx=1, pady=1, sticky=EW)
        self._lbl_disconnect.grid(column=3, row=1, padx=1, pady=1, sticky=EW)

        ttk.Separator(self._frm_container).grid(
            column=0, row=7, columnspan=4, padx=2, pady=2, sticky=EW
        )

        self._frm_options.grid(column=0, row=8, columnspan=4, sticky=EW)
        self._lbl_protocol.grid(column=0, row=0, padx=2, pady=2, sticky=W)
        self._chk_nmea.grid(column=1, row=0, padx=0, pady=0, sticky=W)
        self._chk_ubx.grid(column=2, row=0, padx=0, pady=0, sticky=W)
        self._chk_sbf.grid(column=3, row=0, padx=0, pady=0, sticky=W)
        self._chk_qgc.grid(column=4, row=0, padx=0, pady=0, sticky=W)
        self._chk_rtcm.grid(column=1, row=1, padx=0, pady=0, sticky=W)
        self._chk_spartn.grid(column=2, row=1, padx=0, pady=0, sticky=W)
        self._chk_tty.grid(column=3, row=1, padx=0, pady=0, sticky=W)
        self._lbl_consoledisplay.grid(column=0, row=2, padx=2, pady=2, sticky=W)
        self._spn_conformat.grid(
            column=1, row=2, columnspan=2, padx=1, pady=2, sticky=W
        )
        self._chk_tags.grid(column=3, row=2, padx=1, pady=2, sticky=W)
        self._lbl_format.grid(column=0, row=3, padx=2, pady=2, sticky=W)
        self._spn_format.grid(column=1, row=3, padx=2, pady=2, sticky=W)
        self._spn_units.grid(column=2, row=3, columnspan=2, padx=2, pady=2, sticky=W)
        self._chk_scroll.grid(column=0, row=5, padx=2, pady=2, sticky=W)
        self._spn_maxlines.grid(column=1, row=5, padx=2, pady=2, sticky=W)
        self._lbl_filedelay.grid(column=2, row=5, padx=2, pady=2, sticky=E)
        self._spn_filedelay.grid(column=3, row=5, padx=2, pady=2, sticky=W)
        self._chk_unusedsat.grid(
            column=0, row=6, columnspan=2, padx=2, pady=2, sticky=W
        )
        self._chk_datalog.grid(column=0, row=7, padx=2, pady=2, sticky=W)
        self._spn_datalog.grid(column=1, row=7, columnspan=3, padx=2, pady=2, sticky=W)
        self._chk_recordtrack.grid(
            column=0, row=8, columnspan=2, padx=2, pady=2, sticky=W
        )
        self._chk_recorddatabase.grid(
            column=2, row=8, columnspan=2, padx=2, pady=2, sticky=W
        )
        self._frm_options_btns.grid(column=0, row=9, columnspan=4, sticky=EW)
        self._btn_ubxconfig.grid(column=0, row=0, padx=5)
        self._lbl_ubxconfig.grid(column=0, row=1)
        self._btn_nmeaconfig.grid(column=1, row=0, padx=5)
        self._lbl_nmeaconfig.grid(column=1, row=1)
        self._btn_ttyconfig.grid(column=2, row=0, padx=5)
        self._lbl_ttyconfig.grid(column=2, row=1)
        self._btn_ntripconfig.grid(column=3, row=0, padx=5)
        self._lbl_ntripconfig.grid(column=3, row=1)
        ttk.Separator(self._frm_container).grid(
            column=0, row=10, columnspan=4, padx=2, pady=2, sticky=EW
        )
        self.frm_socketserver.grid(
            column=0, row=11, columnspan=4, padx=2, pady=2, sticky=EW
        )

    def _attach_events(self, add: bool = True):
        """
        Bind events to widgets.

        (trace_update() is a class extension method defined in globals.py)

        :param bool add: add or remove trace
        """

        # pylint: disable=no-member

        tracemode = TRACEMODE_WRITE
        self._prot_ubx.trace_update(tracemode, self._on_update_ubxprot, add)
        self._prot_sbf.trace_update(tracemode, self._on_update_sbfprot, add)
        self._prot_qgc.trace_update(tracemode, self._on_update_qgcprot, add)
        self._prot_nmea.trace_update(tracemode, self._on_update_nmeaprot, add)
        self._prot_rtcm.trace_update(tracemode, self._on_update_rtcmprot, add)
        self._prot_spartn.trace_update(tracemode, self._on_update_spartnprot, add)
        self._prot_tty.trace_update(tracemode, self._on_update_ttyprot, add)
        self._autoscroll.trace_update(tracemode, self._on_update_autoscroll, add)
        self._maxlines.trace_update(tracemode, self._on_update_maxlines, add)
        self._filedelay.trace_update(tracemode, self._on_update_filedelay, add)
        self._units.trace_update(tracemode, self._on_update_units, add)
        self._degrees_format.trace_update(tracemode, self._on_update_degreesformat, add)
        self._console_format.trace_update(tracemode, self._on_update_consoleformat, add)
        self._show_unusedsat.trace_update(tracemode, self._on_update_unusedsat, add)
        self._colortag.trace_update(tracemode, self._on_update_colortag, add)
        self._logformat.trace_update(tracemode, self._on_update_logformat, add)
        self._datalog.trace_update(tracemode, self._on_data_log, add)
        self._record_track.trace_update(tracemode, self._on_record_track, add)
        self._record_database.trace_update(tracemode, self._on_record_database, add)

    def reset(self):
        """
        Reset settings to saved configuration.
        """

        self._attach_events(False)
        cfg = self.__app.configuration
        self._prot_nmea.set(cfg.get("nmeaprot_b"))
        self._prot_ubx.set(cfg.get("ubxprot_b"))
        self._prot_sbf.set(cfg.get("sbfprot_b"))
        self._prot_qgc.set(cfg.get("qgcprot_b"))
        self._prot_rtcm.set(cfg.get("rtcmprot_b"))
        self._prot_spartn.set(cfg.get("spartnprot_b"))
        self._prot_tty.set(cfg.get("ttyprot_b"))
        self._degrees_format.set(cfg.get("degreesformat_s"))
        self._colortag.set(cfg.get("colortag_b"))
        self._units.set(cfg.get("units_s"))
        self._autoscroll.set(cfg.get("autoscroll_b"))
        self._maxlines.set(cfg.get("maxlines_n"))
        self._filedelay.set(cfg.get("filedelay_n"))
        self._console_format.set(cfg.get("consoleformat_s"))
        self._show_unusedsat.set(cfg.get("unusedsat_b"))
        self._logformat.set(cfg.get("logformat_s"))
        self._datalog.set(cfg.get("datalog_b"))
        self.logpath = cfg.get("logpath_s")
        self._record_track.set(cfg.get("recordtrack_b"))
        self.trackpath = cfg.get("trackpath_s")
        self.databasepath = cfg.get("databasepath_s")
        if self.__app.db_enabled == SQLOK:
            self._record_database.set(cfg.get("database_b"))
        else:
            self._record_database.set(0)
            self._chk_recorddatabase.config(state=DISABLED)

        self.clients = 0
        self._attach_events(True)

    def _reset_frames(self):
        """
        Reset frames.
        """

        self.__app.frm_mapview.reset_map_refresh()
        self.__app.frm_spectrumview.reset()
        self.__app.reset_gnssstatus()

    def _on_update_ubxprot(self, var, index, mode):
        """
        Action on updating ubxprot.
        """

        if not self._prot_tty.get():
            self.__app.configuration.set("ubxprot_b", self._prot_ubx.get())

    def _on_update_sbfprot(self, var, index, mode):
        """
        Action on updating sbfprot.
        """

        if not self._prot_tty.get():
            self.__app.configuration.set("sbfprot_b", self._prot_sbf.get())

    def _on_update_qgcprot(self, var, index, mode):
        """
        Action on updating qgcprot.
        """

        if not self._prot_tty.get():
            self.__app.configuration.set("qgcprot_b", self._prot_qgc.get())

    def _on_update_nmeaprot(self, var, index, mode):
        """
        Action on updating nmeaprot.
        """

        if not self._prot_tty.get():
            self.__app.configuration.set("nmeaprot_b", self._prot_nmea.get())

    def _on_update_rtcmprot(self, var, index, mode):
        """
        Action on updating rtcmprot.
        """

        if not self._prot_tty.get():
            self.__app.configuration.set("rtcmprot_b", self._prot_rtcm.get())

    def _on_update_spartnprot(self, var, index, mode):
        """
        Action on updating spartnprot.
        """

        if not self._prot_tty.get():
            self.__app.configuration.set("spartnprot_b", self._prot_spartn.get())

    def _on_update_ttyprot(self, var, index, mode):
        """
        TTY mode has been updated.
        """

        try:
            cfg = self.__app.configuration
            tty = self._prot_tty.get()
            self.update()
            if tty:

                for wdg in (
                    self._prot_nmea,
                    self._prot_ubx,
                    self._prot_sbf,
                    self._prot_qgc,
                    self._prot_rtcm,
                    self._prot_spartn,
                ):
                    wdg.set(0)
            else:
                self._prot_nmea.set(cfg.get("nmeaprot_b"))
                self._prot_ubx.set(cfg.get("ubxprot_b"))
                self._prot_sbf.set(cfg.get("sbfprot_b"))
                self._prot_qgc.set(cfg.get("qgcprot_b"))
                self._prot_rtcm.set(cfg.get("rtcmprot_b"))
                self._prot_spartn.set(cfg.get("spartnprot_b"))
            cfg.set("ttyprot_b", tty)
        except (ValueError, TclError):
            pass

    def _on_update_consoleformat(self, var, index, mode):
        """
        Action on updating console format.
        """

        self.__app.configuration.set("consoleformat_s", self._console_format.get())

    def _on_update_maxlines(self, var, index, mode):
        """
        Action on updating console maxlines.
        """

        self.__app.configuration.set("maxlines_n", self._maxlines.get())

    def _on_update_filedelay(self, var, index, mode):
        """
        Action on updating filedelay.
        """

        self.__app.configuration.set("filedelay_n", self._filedelay.get())

    def _on_update_degreesformat(self, var, index, mode):
        """
        Action on updating degrees format.
        """

        self.__app.configuration.set("degreesformat_s", self._degrees_format.get())

    def _on_update_units(self, var, index, mode):
        """
        Action on updating units.
        """

        self.__app.configuration.set("units_s", self._units.get())

    def _on_update_colortag(self, var, index, mode):
        """
        Action on updating color tagging.
        """

        self.__app.configuration.set("colortag_b", self._colortag.get())

    def _on_update_autoscroll(self, var, index, mode):
        """
        Action on updating autoscroll.
        """

        self.__app.configuration.set("autoscroll_b", self._autoscroll.get())

    def _on_update_unusedsat(self, var, index, mode):
        """
        Action on updating unused satellites.
        """

        self.__app.configuration.set("unusedsat_b", self._show_unusedsat.get())

    def _on_update_logformat(self, var, index, mode):
        """
        Action on updating log format.
        """

        self.__app.configuration.set("logformat_s", self._logformat.get())

    def _on_data_log(self, var, index, mode):
        """
        Start or stop data logger.
        """

        if self._datalog.get() == 1:
            if self.logpath in ("", None):
                self.logpath = self.__app.file_handler.set_logfile_path()
            if self.logpath is not None:
                self.__app.configuration.set("datalog_b", 1)
                self.__app.configuration.set("logpath_s", self.logpath)
                self.__app.status_label = (
                    f"Data logging enabled: {self.logpath}",
                    INFOCOL,
                )
                if not self.__app.file_handler.open_logfile():
                    self.logpath = ""
                    self._datalog.set(0)
            else:
                self.logpath = ""
                self._datalog.set(0)
            self._spn_datalog.config(state=DISABLED)
        else:
            self.__app.configuration.set("datalog_b", 0)
            self._datalog.set(0)
            self.__app.file_handler.close_logfile()
            self.__app.status_label = ("Data logging disabled", INFOCOL)
            self._spn_datalog.config(state=READONLY)

    def _on_record_track(self, var, index, mode):
        """
        Start or stop track recorder.
        """

        if self._record_track.get() == 1:
            if self.trackpath in ("", None):
                self.trackpath = self.__app.file_handler.set_trackfile_path()
            if self.trackpath is not None:
                self.__app.configuration.set("recordtrack_b", 1)
                self.__app.configuration.set("trackpath_s", self.trackpath)
                self.__app.status_label = f"Track recording enabled: {self.trackpath}"
                if not self.__app.file_handler.open_trackfile():
                    self.trackpath = ""
                    self._record_track.set(0)
            else:
                self.trackpath = ""
                self._record_track.set(0)
        else:
            self._record_track.set(0)
            self.__app.configuration.set("recordtrack_b", 0)
            self.__app.file_handler.close_trackfile()
            self.__app.status_label = "Track recording disabled"

    def _on_record_database(self, var, index, mode):
        """
        Start or stop database recorder.
        """

        if self._record_database.get() == 1:
            if self.databasepath in ("", None):
                self.databasepath = self.__app.file_handler.set_database_path()
            if self.databasepath is not None:
                rc = self.__app.sqlite_handler.open(dbpath=self.databasepath)
                self.__app.configuration.set("database_b", rc == SQLOK)
                self.__app.configuration.set("databasepath_s", self.databasepath)
            else:
                self.databasepath = ""
                self._record_database.set(0)
        else:
            self.__app.configuration.set("database_b", 0)
            self.__app.status_label = "Database recording disabled"

    def _on_connect(self, conntype: int):
        """
        Start or stop connection (serial, socket or file).

        :param int conntype: connection type
        """

        connstr = ""
        conndict = {
            "protocol": self.__app.protocol_mask,
            "read_event": GNSS_EVENT,
            "eof_event": GNSS_EOF_EVENT,
            "timeout_event": GNSS_TIMEOUT_EVENT,
            "error_event": GNSS_ERR_EVENT,
            "inqueue": self.__app.gnss_inqueue,
            "outqueue": self.__app.gnss_outqueue,
            "socket_inqueue": self.__app.socket_inqueue,
            "conntype": conntype,
            "msgmode": self.frm_serial.msgmode,
            "inactivity_timeout": self.frm_serial.inactivity_timeout,
        }

        self.frm_socketserver.status_label = conntype
        if conntype == CONNECTED:
            frm = self.frm_serial
            if frm.status == NOPORTS:
                return
            connstr = f"{frm.port}:{frm.port_desc} @ {frm.bpsrate}"
            conndict = dict(conndict, **{"serial_settings": frm})
            # poll for device software version on connection
            self.__app.poll_version(conndict["protocol"])
        elif conntype == CONNECTED_SOCKET:
            frm = self.frm_socketclient
            if not frm.valid_settings():
                self.__app.status_label = ("ERROR - invalid settings", ERRCOL)
                return
            connstr = f"{frm.server.get()}:{frm.port.get()}"
            conndict = dict(conndict, **{"socket_settings": frm})
            # poll for device software version on connection
            self.__app.poll_version(conndict["protocol"])
        elif conntype == CONNECTED_FILE:
            self.infilepath = self.__app.file_handler.open_file(
                self,
                "datalog",
                (
                    ("datalog files", "*.log"),
                    ("u-center logs", "*.ubx"),
                    ("all files", "*.*"),
                ),
            )
            if self.infilepath is None:
                return
            connstr = f"{self.infilepath}"
            conndict = dict(conndict, **{"in_filepath": self.infilepath})
        elif conntype == DISCONNECTED:
            if self.__app.conn_status != DISCONNECTED:
                self.__app.conn_status = DISCONNECTED
                self.__app.stream_handler.stop()
                return
        else:
            return

        self.__app.conn_status = conntype
        self.__app.conn_label = (connstr, OKCOL)
        self.__app.status_label = ("", INFOCOL)
        self._reset_frames()
        self.__app.stream_handler.start(self.__app, conndict)

    def enable_controls(self, status: int):
        """
        Public method to enable or disable controls depending on
        connection status.

        :param int status: connection status as integer
               (0=Disconnected, 1=Connected to serial,
               2=Connected to file, 3=No serial ports available)

        """

        self.frm_serial.status_label = status
        self.frm_socketclient.status_label = status
        self.frm_socketserver.status_label = status

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
            self._chk_tty,
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

    def get_size(self) -> tuple:
        """
        Get current frame size.

        :return: (width, height)
        :rtype: tuple

        """

        self.update_idletasks()  # Make sure we know about any resizing
        return (self.winfo_width(), self.winfo_height())
