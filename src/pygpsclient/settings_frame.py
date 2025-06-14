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
:copyright: 2020 SEMU Consulting
:license: BSD 3-Clause
"""

# pylint: disable=unnecessary-lambda

from platform import system
from tkinter import (
    ALL,
    BOTH,
    BOTTOM,
    DISABLED,
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
from pyubx2 import NMEA_PROTOCOL, RTCM3_PROTOCOL, UBX_PROTOCOL

from pygpsclient.globals import (
    BPSRATES,
    CONNECTED,
    CONNECTED_FILE,
    CONNECTED_SOCKET,
    CUSTOM,
    DDD,
    DISCONNECTED,
    DMM,
    DMS,
    ECEF,
    ERRCOL,
    FORMATS,
    GNSS,
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
    ICON_SPARTNCONFIG,
    ICON_UBXCONFIG,
    KNOWNGPS,
    MAP,
    MSGMODES,
    NOPORTS,
    OKCOL,
    READONLY,
    RPTDELAY,
    SAT,
    SBF_PROTOCOL,
    SPARTN_PROTOCOL,
    TIMEOUTS,
    TTY_PROTOCOL,
    UI,
    UIK,
    UMK,
    UMM,
    WORLD,
)
from pygpsclient.helpers import fontheight, fontwidth
from pygpsclient.serialconfig_frame import SerialConfigFrame
from pygpsclient.serverconfig_frame import ServerConfigFrame
from pygpsclient.socketconfig_frame import SocketConfigFrame
from pygpsclient.strings import (
    DLGTNMEA,
    DLGTNTRIP,
    DLGTSPARTN,
    DLGTUBX,
    LBLDATADISP,
    LBLDATALOG,
    LBLDEGFORMAT,
    LBLNMEACONFIG,
    LBLNTRIPCONFIG,
    LBLPROTDISP,
    LBLSHOWTRACK,
    LBLSHOWUNUSED,
    LBLSPARTNCONFIG,
    LBLTRACKRECORD,
    LBLUBXCONFIG,
)

MAXLINES = ("200", "500", "1000", "2000", "100")
MAPTYPES = (WORLD, MAP, SAT, CUSTOM)
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
        self._prot_nmea = IntVar()
        self._prot_ubx = IntVar()
        self._prot_sbf = IntVar()
        self._prot_rtcm3 = IntVar()
        self._prot_spartn = IntVar()
        self._prot_tty = IntVar()
        self._autoscroll = IntVar()
        self._maxlines = IntVar()
        self.maptype = StringVar()
        self.showtrack = IntVar()
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
        self.defaultports = self.__app.configuration.get("defaultport_s")
        self._validsettings = True
        self._img_conn = ImageTk.PhotoImage(Image.open(ICON_CONN))
        self._img_serial = ImageTk.PhotoImage(Image.open(ICON_SERIAL))
        self._img_socket = ImageTk.PhotoImage(Image.open(ICON_SOCKET))
        self._img_disconn = ImageTk.PhotoImage(Image.open(ICON_DISCONN))
        self._img_exit = ImageTk.PhotoImage(Image.open(ICON_EXIT))
        self._img_ubxconfig = ImageTk.PhotoImage(Image.open(ICON_UBXCONFIG))
        self._img_nmeaconfig = ImageTk.PhotoImage(Image.open(ICON_NMEACONFIG))
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

        dimw = fontwidth(self.__app.font_md) * MINWIDTH
        dimh = fontheight(self.__app.font_md) * MINHEIGHT
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
            GNSS,
            preselect=KNOWNGPS,
            timeouts=TIMEOUTS,
            bpsrates=BPSRATES,
            msgmodes=list(MSGMODES.keys()),
        )

        # socket client configuration panel
        self.frm_socketclient = SocketConfigFrame(
            self.__app,
            self._frm_container,
            GNSS,
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
            repeatdelay=RPTDELAY,
            repeatinterval=RPTDELAY,
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
            repeatdelay=RPTDELAY,
            repeatinterval=RPTDELAY,
            textvariable=self._degrees_format,
        )
        self._spn_units = Spinbox(
            self._frm_options,
            values=(UMM, UIK, UI, UMK),
            width=13,
            state=READONLY,
            wrap=True,
            repeatdelay=RPTDELAY,
            repeatinterval=RPTDELAY,
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
            repeatdelay=RPTDELAY,
            repeatinterval=RPTDELAY,
            textvariable=self._maxlines,
            state=READONLY,
        )
        self._lbl_maptype = Label(self._frm_options, text="Map Type")
        self.spn_maptype = Spinbox(
            self._frm_options,
            values=MAPTYPES,
            width=6,
            wrap=True,
            repeatdelay=RPTDELAY,
            repeatinterval=RPTDELAY,
            textvariable=self.maptype,
            state=READONLY,
        )
        self._chk_showtrack = Checkbutton(
            self._frm_options, text=LBLSHOWTRACK, variable=self.showtrack
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
            repeatdelay=RPTDELAY,
            repeatinterval=RPTDELAY,
            textvariable=self._logformat,
            state=READONLY,
        )
        self._chk_recordtrack = Checkbutton(
            self._frm_options,
            text=LBLTRACKRECORD,
            variable=self._record_track,
            command=lambda: self._on_record_track(),
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
        self._lbl_nmeaconfig = Label(
            self._frm_options,
            text=LBLNMEACONFIG,
        )
        self._btn_nmeaconfig = Button(
            self._frm_options,
            width=45,
            image=self._img_nmeaconfig,
            command=lambda: self._on_nmea_config(),
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
        # socket server configuration
        self.frm_socketserver = ServerConfigFrame(
            self.__app,
            self._frm_container,
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

        self._frm_options.grid(column=0, row=8, columnspan=4, sticky=(W, E))
        self._lbl_protocol.grid(column=0, row=0, padx=2, pady=2, sticky=W)
        self._chk_nmea.grid(column=1, row=0, padx=0, pady=0, sticky=W)
        self._chk_ubx.grid(column=2, row=0, padx=0, pady=0, sticky=W)
        self._chk_rtcm.grid(column=1, row=1, padx=0, pady=0, sticky=W)
        self._chk_spartn.grid(column=2, row=1, padx=0, pady=0, sticky=W)
        self._chk_sbf.grid(column=3, row=0, padx=0, pady=0, sticky=W)
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
        self._spn_maxlines.grid(column=1, row=5, columnspan=3, padx=2, pady=2, sticky=W)
        self._lbl_maptype.grid(column=0, row=6, padx=2, pady=2, sticky=W)
        self._chk_showtrack.grid(column=2, row=6, padx=2, pady=2, sticky=W)
        self.spn_maptype.grid(column=1, row=6, padx=2, pady=2, sticky=W)
        self._chk_unusedsat.grid(
            column=0, row=7, columnspan=2, padx=2, pady=2, sticky=W
        )
        self._chk_datalog.grid(column=0, row=8, padx=2, pady=2, sticky=W)
        self._spn_datalog.grid(column=1, row=8, columnspan=3, padx=2, pady=2, sticky=W)
        self._chk_recordtrack.grid(
            column=0, row=9, columnspan=2, padx=2, pady=2, sticky=W
        )
        self._btn_ubxconfig.grid(column=0, row=10)
        self._lbl_ubxconfig.grid(column=0, row=11)
        self._btn_nmeaconfig.grid(column=1, row=10)
        self._lbl_nmeaconfig.grid(column=1, row=11)
        self._btn_ntripconfig.grid(column=2, row=10)
        self._lbl_ntripconfig.grid(column=2, row=11)
        self._btn_spartnconfig.grid(column=3, row=10)
        self._lbl_spartnconfig.grid(column=3, row=11)
        ttk.Separator(self._frm_container).grid(
            column=0, row=9, columnspan=4, padx=2, pady=2, sticky=(W, E)
        )
        self.frm_socketserver.grid(
            column=0, row=10, columnspan=4, padx=2, pady=2, sticky=(W, E)
        )

    def reset(self):
        """
        Reset settings to saved configuration.
        """

        self._bind_events(False)
        cfg = self.__app.configuration
        self._prot_nmea.set(cfg.get("nmeaprot_b"))
        self._prot_ubx.set(cfg.get("ubxprot_b"))
        self._prot_sbf.set(cfg.get("sbfprot_b"))
        self._prot_rtcm3.set(cfg.get("rtcmprot_b"))
        self._prot_spartn.set(cfg.get("spartnprot_b"))
        self._prot_tty.set(cfg.get("ttyprot_b"))
        self._degrees_format.set(cfg.get("degreesformat_s"))
        self._colortag.set(cfg.get("colortag_b"))
        self._units.set(cfg.get("units_s"))
        self._autoscroll.set(cfg.get("autoscroll_b"))
        self._maxlines.set(cfg.get("maxlines_n"))
        self._console_format.set(cfg.get("consoleformat_s"))
        self.maptype.set(cfg.get("maptype_s"))
        self.showtrack.set(cfg.get("showtrack_b"))
        self.mapzoom.set(cfg.get("mapzoom_n"))
        self.show_legend.set(cfg.get("legend_b"))
        self._show_unusedsat.set(cfg.get("unusedsat_b"))
        self._logformat.set(cfg.get("logformat_s"))
        self._datalog.set(cfg.get("datalog_b"))
        self.logpath = cfg.get("logpath_s")
        self._record_track.set(cfg.get("recordtrack_b"))
        self.trackpath = cfg.get("trackpath_s")
        self.clients = 0
        self._bind_events(True)

    def _bind_events(self, add: bool = True):
        """
        Add or remove event bindings to/from widgets.

        :param bool add: add or remove binding
        """

        tracemode = "write"
        if add:
            self._prot_tty.trace_add(tracemode, self._on_update_tty)
        else:
            if len(self._prot_tty.trace_info()) > 0:
                self._prot_tty.trace_remove(
                    tracemode, self._prot_tty.trace_info()[0][1]
                )
        if add:
            self._prot_ubx.trace_add(tracemode, self._on_update_ubx)
        else:
            if len(self._prot_ubx.trace_info()) > 0:
                self._prot_ubx.trace_remove(
                    tracemode, self._prot_ubx.trace_info()[0][1]
                )
        if add:
            self._prot_sbf.trace_add(tracemode, self._on_update_sbf)
        else:
            if len(self._prot_sbf.trace_info()) > 0:
                self._prot_sbf.trace_remove(
                    tracemode, self._prot_sbf.trace_info()[0][1]
                )
        for setting in (
            self._prot_nmea,
            self._prot_rtcm3,
            self._prot_spartn,
            self._autoscroll,
            self._maxlines,
            self.maptype,
            self.showtrack,
            self.mapzoom,
            self._units,
            self._degrees_format,
            self._console_format,
            self._datalog,
            self._logformat,
            self._record_track,
            self._show_unusedsat,
            self.show_legend,
            self._colortag,
        ):
            if add:
                setting.trace_add(tracemode, self._on_update_config)
            else:
                if len(setting.trace_info()) > 0:
                    setting.trace_remove(tracemode, setting.trace_info()[0][1])

    def _reset_frames(self):
        """
        Reset frames.
        """

        self.__app.frm_mapview.reset_map_refresh()
        self.__app.frm_spectrumview.reset()
        self.__app.reset_gnssstatus()

    def _on_update_ubx(self, var, index, mode):  # pylint: disable=unused-argument
        """
        UBX or SBF protocol mode has been updated.
        """

        try:
            self.update()
            if self._prot_ubx.get():
                self._prot_sbf.set(0)
                self.__app.configuration.set("sbfprot_b", int(self._prot_sbf.get()))
            self.__app.configuration.set("ubxprot_b", int(self._prot_ubx.get()))
            self._on_update_protocol()
        except (ValueError, TclError):
            pass

    def _on_update_sbf(self, var, index, mode):  # pylint: disable=unused-argument
        """
        UBX or SBF protocol mode has been updated.
        """

        try:
            self.update()
            if self._prot_sbf.get():
                self._prot_ubx.set(0)
                self.__app.configuration.set("ubxprot_b", int(self._prot_ubx.get()))
            self.__app.configuration.set("sbfprot_b", int(self._prot_sbf.get()))
            self._on_update_protocol()
        except (ValueError, TclError):
            pass

    def _on_update_tty(self, var, index, mode):  # pylint: disable=unused-argument
        """
        TTY mode has been updated.
        """

        try:
            tty = self._prot_tty.get()
            self.update()
            if tty:
                for wdg in (
                    self._prot_nmea,
                    self._prot_ubx,
                    self._prot_sbf,
                    self._prot_rtcm3,
                    self._prot_spartn,
                ):
                    wdg.set(0)
            else:
                self._prot_nmea.set(1)
                self._prot_ubx.set(1)
                self._prot_sbf.set(0)
                self._prot_rtcm3.set(1)
                self._prot_spartn.set(1)
            self.__app.configuration.set("ttyprot_b", tty)
        except (ValueError, TclError):
            pass

    def _on_update_config(self, var, index, mode):  # pylint: disable=unused-argument
        """
        Update in-memory configuration if setting is changed.
        """

        try:
            self.update()
            cfg = self.__app.configuration
            cfg.set("nmeaprot_b", int(self._prot_nmea.get()))
            cfg.set("rtcmprot_b", int(self._prot_rtcm3.get()))
            cfg.set("spartnprot_b", int(self._prot_spartn.get()))
            self._on_update_protocol()
            cfg.set("degreesformat_s", self._degrees_format.get())
            cfg.set("colortag_b", int(self._colortag.get()))
            cfg.set("units_s", self._units.get())
            cfg.set("autoscroll_b", int(self._autoscroll.get()))
            cfg.set("maxlines_n", int(self._maxlines.get()))
            cfg.set("consoleformat_s", self._console_format.get())
            cfg.set("maptype_s", self.maptype.get())
            cfg.set("showtrack_b", int(self.showtrack.get()))
            cfg.set("mapzoom_n", int(self.mapzoom.get()))
            cfg.set("legend_b", int(self.show_legend.get()))
            cfg.set("unusedsat_b", int(self._show_unusedsat.get()))
            cfg.set("datalog_b", int(self._datalog.get()))
            cfg.set("logformat_s", self._logformat.get())
            cfg.set("logpath_s", self.logpath)
            cfg.set("recordtrack_b", int(self._record_track.get()))
            cfg.set("trackpath_s", int(self.trackpath))
        except (ValueError, TclError):
            pass

    def _on_update_protocol(self):
        """
        Protocol(s) have been updated.
        """

        self.__app.configuration.set(
            "protocol_n",
            NMEA_PROTOCOL * int(self._prot_nmea.get())
            + UBX_PROTOCOL * int(self._prot_ubx.get())
            + SBF_PROTOCOL * int(self._prot_sbf.get())
            + RTCM3_PROTOCOL * int(self._prot_rtcm3.get())
            + SPARTN_PROTOCOL * int(self._prot_spartn.get())
            + TTY_PROTOCOL * int(self._prot_tty.get()),
        )

    def _on_connect(self, conntype: int):
        """
        Start or stop connection (serial, socket or file).

        :param int conntype: connection type
        """

        connstr = ""
        conndict = {
            "protocol": self.__app.configuration.get("protocol_n"),
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

        self.frm_socketserver.set_status(conntype)
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
                self.__app.set_status("ERROR - invalid settings", ERRCOL)
                return
            connstr = f"{frm.server.get()}:{frm.port.get()}"
            conndict = dict(conndict, **{"socket_settings": frm})
        elif conntype == CONNECTED_FILE:
            self.infilepath = self.__app.file_handler.open_file(
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
                self.__app.stream_handler.stop_read_thread()
                return
        else:
            return

        self.__app.set_connection(connstr, OKCOL)
        self.__app.set_status("")
        self.__app.conn_status = conntype
        self._reset_frames()
        self.__app.stream_handler.start_read_thread(self.__app, conndict)

    def _on_ubx_config(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Open UBX configuration dialog panel.
        """

        self.__app.start_dialog(DLGTUBX)

    def _on_nmea_config(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Open NMEA configuration dialog panel.
        """

        self.__app.start_dialog(DLGTNMEA)

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
            self.logpath = self.__app.file_handler.set_logfile_path(self.logpath)
            if self.logpath is not None:
                self.__app.configuration.set("datalog_b", 1)
                self.__app.configuration.set("logpath_s", self.logpath)
                self.__app.set_status("Data logging enabled: " + self.logpath)
                self.__app.file_handler.open_logfile()
            else:
                self.logpath = ""
                self._datalog.set(False)
        else:
            self.__app.configuration.set("datalog_b", 0)
            self._datalog.set(False)
            self.__app.file_handler.close_logfile()
            self.__app.set_status("Data logging disabled")

    def _on_record_track(self):
        """
        Start or stop track recorder.
        """

        if self._record_track.get() == 1:
            self.trackpath = self.__app.file_handler.set_trackfile_path(self.trackpath)
            if self.trackpath is not None:
                self.__app.set_status("Track recording enabled: " + self.trackpath)
                self.__app.file_handler.open_trackfile()
            else:
                self.trackpath = ""
                self._record_track.set(False)
        else:
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
