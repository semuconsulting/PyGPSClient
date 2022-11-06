"""
Settings frame class for PyGPSClient application.

This handles the settings/configuration panel. It references
the common SerialConfigFrame utility class for serial port settings.

Exposes the various settings as properties.

Created on 12 Sep 2020

:author: semuadmin
:copyright: SEMU Consulting © 2020
:license: BSD 3-Clause
"""
# pylint: disable=invalid-name, unnecessary-lambda, too-many-instance-attributes

from tkinter import (
    ttk,
    Frame,
    Button,
    Label,
    Entry,
    Spinbox,
    Scale,
    Checkbutton,
    StringVar,
    IntVar,
    N,
    S,
    E,
    W,
    NORMAL,
    DISABLED,
    HORIZONTAL,
)

from PIL import ImageTk, Image
import pyubx2.ubxtypes_core as ubt
from pygpsclient.serialconfig_frame import SerialConfigFrame
from pygpsclient.socketconfig_frame import SocketConfigFrame
from pygpsclient.globals import (
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
    CONNECTED_SOCKET,
    CONNECTED_FILE,
    DISCONNECTED,
    NOPORTS,
    ICON_CONN,
    ICON_SERIAL,
    ICON_SOCKET,
    ICON_DISCONN,
    ICON_UBXCONFIG,
    ICON_NTRIPCONFIG,
    ICON_LOGREAD,
    KNOWNGPS,
    BPSRATES,
    FORMATS,
    SOCKMODES,
    TAG_COLORS,
    SOCKSERVER_PORT,
    SOCKSERVER_NTRIP_PORT,
    SOCKSERVER_MAX_CLIENTS,
)
from pygpsclient.helpers import valid_entry, VALINT, VALURL, MAXPORT
from pygpsclient.strings import (
    LBLUBXCONFIG,
    LBLNTRIPCONFIG,
    LBLPROTDISP,
    LBLDATADISP,
    LBLDATALOG,
    LBLTRACKRECORD,
    LBLSHOWUNUSED,
    LBLLEGEND,
    LBLSOCKSERVE,
    LBLSERVERPORT,
    LBLDEGFORMAT,
    LBLSERVERMODE,
)

TIMEOUTS = (
    "0.1",
    "0.2",
    "1",
    "2",
    "5",
    "10",
    "20",
    "None",
    "0",
)


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
        self.__master = self.__app.get_master()  # Reference to root class (Tk)
        Frame.__init__(self, self.__master, *args, **kwargs)

        self._prot_nmea = IntVar()
        self._prot_ubx = IntVar()
        self._prot_rtcm3 = IntVar()
        self._autoscroll = IntVar()
        self._maxlines = IntVar()
        self._webmap = IntVar()
        self._mapzoom = IntVar()
        self._units = StringVar()
        self._format = StringVar()
        self._datalog = IntVar()
        self._logformat = StringVar()
        self._record_track = IntVar()
        self._show_unusedsat = IntVar()
        self._show_legend = IntVar()
        self._colortags = IntVar()
        self._socket_serve = IntVar()
        self._sock_port = StringVar()
        self._sock_mode = StringVar()
        self._sock_clients = StringVar()
        self._validsettings = True
        self._in_filepath = None
        self._logpath = None
        self._trackpath = None
        self._display_format = StringVar()
        self._img_conn = ImageTk.PhotoImage(Image.open(ICON_CONN))
        self._img_serial = ImageTk.PhotoImage(Image.open(ICON_SERIAL))
        self._img_socket = ImageTk.PhotoImage(Image.open(ICON_SOCKET))
        self._img_disconn = ImageTk.PhotoImage(Image.open(ICON_DISCONN))
        self._img_ubxconfig = ImageTk.PhotoImage(Image.open(ICON_UBXCONFIG))
        self._img_ntripconfig = ImageTk.PhotoImage(Image.open(ICON_NTRIPCONFIG))
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
        self._frm_serial = SerialConfigFrame(
            self,
            preselect=KNOWNGPS,
            timeouts=TIMEOUTS,
            bpsrates=BPSRATES,
            userport=self.__app.user_port,  # user-defined serial port
        )

        # socket configuration panel
        self._frm_socket = SocketConfigFrame(self)

        # connection buttons
        self._frm_buttons = Frame(self)
        self._btn_connect = Button(
            self._frm_buttons,
            width=45,
            height=35,
            image=self._img_serial,
            command=lambda: self._on_serial_stream(),
        )
        self._lbl_connect = Label(self._frm_buttons, text="USB/UART")
        self._btn_connect_socket = Button(
            self._frm_buttons,
            width=45,
            height=35,
            image=self._img_socket,
            command=lambda: self._on_socket_stream(),
        )
        self._lbl_connect_socket = Label(self._frm_buttons, text="TCP/UDP")
        self._btn_connect_file = Button(
            self._frm_buttons,
            width=45,
            height=35,
            image=self._img_dataread,
            command=lambda: self._on_file_stream(),
        )
        self._lbl_connect_file = Label(self._frm_buttons, text="FILE")
        self._btn_disconnect = Button(
            self._frm_buttons,
            width=45,
            height=35,
            image=self._img_disconn,
            command=lambda: self._on_disconnect(),
            state=DISABLED,
        )
        self._lbl_disconnect = Label(self._frm_buttons, text="STOP")
        self._lbl_status_preset = Label(
            self._frm_buttons, font=self.__app.font_md2, text=""
        )

        # Other configuration options
        self._frm_options = Frame(self)
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
            readonlybackground=ENTCOL,
            wrap=True,
            textvariable=self._display_format,
        )
        self._chk_tags = Checkbutton(
            self._frm_options,
            text="Tags",
            variable=self._colortags,
        )
        self._lbl_format = Label(self._frm_options, text=LBLDEGFORMAT)
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
            text="Web Map",
            variable=self._webmap,
            command=lambda: self._on_webmap(),
        )
        self._lbl_mapzoom = Label(self._frm_options, text="Zoom")
        self._scl_mapzoom = Scale(
            self._frm_options,
            from_=1,
            to=20,
            orient=HORIZONTAL,
            relief="sunken",
            bg=ENTCOL,
            variable=self._mapzoom,
        )
        self._chk_unusedsat = Checkbutton(
            self._frm_options, text=LBLSHOWUNUSED, variable=self._show_unusedsat
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
        self._spn_datalog = Spinbox(
            self._frm_options,
            values=(FORMATS),
            width=20,
            readonlybackground=ENTCOL,
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
        self._chk_socketserve = Checkbutton(
            self._frm_options,
            text=LBLSOCKSERVE,
            variable=self._socket_serve,
            command=lambda: self._on_socket_serve(),
            state=DISABLED,
        )
        self._lbl_sockmode = Label(
            self._frm_options,
            text=LBLSERVERMODE,
            state=DISABLED,
        )
        self._spn_sockmode = Spinbox(
            self._frm_options,
            values=SOCKMODES,
            width=18,
            state=DISABLED,
            readonlybackground=ENTCOL,
            wrap=True,
            textvariable=self._sock_mode,
            command=lambda: self._on_sockmode(),
        )
        self._lbl_sockport = Label(
            self._frm_options,
            text=LBLSERVERPORT,
            state=DISABLED,
        )
        self._ent_sockport = Entry(
            self._frm_options,
            textvariable=self._sock_port,
            bg=ENTCOL,
            relief="sunken",
            width=6,
            state=DISABLED,
        )
        self._lbl_sockclients = Label(
            self._frm_options,
            textvariable=self._sock_clients,
            state=DISABLED,
        )
        # configuration panel buttons
        self._lbl_ubxconfig = Label(self._frm_options, text=LBLUBXCONFIG)
        self._btn_ubxconfig = Button(
            self._frm_options,
            width=45,
            height=35,
            text="UBX",
            image=self._img_ubxconfig,
            command=lambda: self._on_ubx_config(),
            state=NORMAL,
        )
        self._lbl_ntripconfig = Label(self._frm_options, text=LBLNTRIPCONFIG)
        self._btn_ntripconfig = Button(
            self._frm_options,
            width=45,
            height=35,
            text="NTRIP",
            image=self._img_ntripconfig,
            command=lambda: self._on_ntrip_config(),
            state=NORMAL,
        )

    def _do_layout(self):
        """
        Position widgets in frame.
        """

        self._frm_serial.grid(
            column=0, row=1, columnspan=4, padx=2, pady=2, sticky=(W, E)
        )
        ttk.Separator(self).grid(
            column=0, row=2, columnspan=4, padx=2, pady=2, sticky=(W, E)
        )

        self._frm_socket.grid(
            column=0, row=3, columnspan=4, padx=2, pady=2, sticky=(W, E)
        )
        ttk.Separator(self).grid(
            column=0, row=4, columnspan=4, padx=2, pady=2, sticky=(W, E)
        )

        self._frm_buttons.grid(column=0, row=5, columnspan=4, sticky=(W, E))
        self._btn_connect.grid(column=0, row=0, padx=2, pady=1)
        self._btn_connect_socket.grid(column=1, row=0, padx=2, pady=1)
        self._btn_connect_file.grid(column=2, row=0, padx=2, pady=1)
        self._btn_disconnect.grid(column=3, row=0, padx=2, pady=1)
        self._lbl_connect.grid(column=0, row=1, padx=1, pady=1, sticky=(W, E))
        self._lbl_connect_socket.grid(column=1, row=1, padx=1, pady=1, sticky=(W, E))
        self._lbl_connect_file.grid(column=2, row=1, padx=1, pady=1, sticky=(W, E))
        self._lbl_disconnect.grid(column=3, row=1, padx=1, pady=1, sticky=(W, E))

        ttk.Separator(self).grid(
            column=0, row=7, columnspan=4, padx=2, pady=2, sticky=(W, E)
        )

        self._frm_options.grid(column=0, row=8, columnspan=4, sticky=(W, E))
        self._lbl_protocol.grid(column=0, row=0, padx=2, pady=2, sticky=(W))
        self._chk_nmea.grid(column=1, row=0, padx=0, pady=0, sticky=(W))
        self._chk_ubx.grid(column=2, row=0, padx=0, pady=0, sticky=(W))
        self._chk_rtcm.grid(column=3, row=0, padx=0, pady=0, sticky=(W))
        self._lbl_consoledisplay.grid(column=0, row=1, padx=2, pady=2, sticky=(W))
        self._spn_conformat.grid(
            column=1, row=1, columnspan=2, padx=1, pady=2, sticky=(W)
        )
        self._chk_tags.grid(column=3, row=1, padx=1, pady=2, sticky=(W))
        self._lbl_format.grid(column=0, row=2, padx=2, pady=2, sticky=(W))
        self._spn_format.grid(column=1, row=2, padx=2, pady=2, sticky=(W))
        self._lbl_units.grid(column=0, row=3, padx=2, pady=2, sticky=(W))
        self._spn_units.grid(column=1, row=3, columnspan=3, padx=2, pady=2, sticky=(W))
        self._chk_scroll.grid(column=0, row=4, padx=2, pady=2, sticky=(W))
        self._spn_maxlines.grid(
            column=1, row=4, columnspan=3, padx=2, pady=2, sticky=(W)
        )
        self._chk_webmap.grid(column=0, row=5, padx=2, pady=2, sticky=(W))
        self._lbl_mapzoom.grid(column=1, row=5, sticky=(E))
        self._scl_mapzoom.grid(column=2, row=5, columnspan=2, sticky=(W))
        self._chk_unusedsat.grid(
            column=0, row=6, columnspan=2, padx=2, pady=2, sticky=(W)
        )
        self._chk_legend.grid(column=2, row=6, columnspan=2, padx=2, pady=2, sticky=(W))
        self._chk_datalog.grid(column=0, row=7, padx=2, pady=2, sticky=(W))
        self._spn_datalog.grid(
            column=1, row=7, columnspan=3, padx=2, pady=2, sticky=(W)
        )
        self._chk_recordtrack.grid(
            column=0, row=8, columnspan=2, padx=2, pady=2, sticky=(W)
        )
        self._chk_socketserve.grid(
            column=0, row=9, rowspan=2, padx=2, pady=2, sticky=(N, S, W)
        )
        self._lbl_sockmode.grid(column=1, row=9, padx=2, pady=2, sticky=(E))
        self._spn_sockmode.grid(
            column=2, row=9, columnspan=2, padx=2, pady=2, sticky=(W)
        )
        self._lbl_sockport.grid(column=1, row=10, padx=2, pady=2, sticky=(E))
        self._ent_sockport.grid(column=2, row=10, padx=2, pady=2, sticky=(W))
        self._lbl_sockclients.grid(column=3, row=10, padx=2, pady=2, sticky=(W))
        ttk.Separator(self._frm_options).grid(
            column=0, row=11, columnspan=4, padx=2, pady=2, sticky=(W, E)
        )
        self._lbl_ubxconfig.grid(column=0, row=12, padx=2, pady=2, sticky=(E))
        self._btn_ubxconfig.grid(column=1, row=12, padx=2, pady=2, sticky=(W))
        self._lbl_ntripconfig.grid(column=2, row=12, padx=2, pady=2, sticky=(E))
        self._btn_ntripconfig.grid(column=3, row=12, padx=2, pady=2, sticky=(W))

    def _on_ubx_config(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Open UBX configuration dialog panel.
        """

        self.__app.ubxconfig()

    def _on_ntrip_config(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Open NTRIP Client configuration dialog panel.
        """

        self.__app.ntripconfig()

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
                self.__app.file_handler.open_logfile()
            else:
                self._datalog.set(False)
        else:
            self._logpath = None
            self._datalog.set(False)
            self.__app.file_handler.close_logfile()
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
                self.__app.file_handler.open_trackfile()
            else:
                self._record_track.set(False)
        else:
            self._trackpath = None
            self._record_track.set(False)
            self.__app.file_handler.close_trackfile()
            self.__app.set_status("Track recording disabled", "blue")

    def _on_serial_stream(self):

        if self.serial_settings().status == NOPORTS:
            return

        self.__app.set_connection(
            (
                f"{self.serial_settings().port}:{self.serial_settings().port_desc} "
                + f"@ {self.serial_settings().bpsrate}"
            ),
            "green",
        )
        self.__app.set_status("")
        self.__app.conn_status = CONNECTED
        self.__app.stream_handler.start_read_thread(CONNECTED)

    def _on_socket_stream(self):
        """
        Start socket streamer if settings are valid
        """

        valid = True
        valid = valid & valid_entry(self._frm_socket.ent_server, VALURL)
        valid = valid & valid_entry(self._frm_socket.ent_port, VALINT, 1, MAXPORT)
        if valid:
            self.__app.set_connection(
                f"{self.socket_settings().server}:{self.socket_settings().port}",
                "green",
            )
            self.__app.set_status("")
            self.__app.conn_status = CONNECTED_SOCKET
            self.__app.stream_handler.start_read_thread(CONNECTED_SOCKET)
        else:
            self.__app.set_status("ERROR - invalid settings", "red")

    def _on_file_stream(self):
        """
        Start data file streamer if file selected
        """

        self._in_filepath = self.__app.file_handler.open_infile()
        if self._in_filepath is not None:
            self.__app.set_connection(f"{self._in_filepath}", "blue")
            self.__app.set_status("")
            self.__app.conn_status = CONNECTED_FILE
            self.__app.stream_handler.start_read_thread(CONNECTED_FILE)

    def _on_socket_serve(self):
        """
        Start or stop socket server.
        """

        if not valid_entry(self._ent_sockport, VALINT, 1, MAXPORT):
            self.__app.set_status("ERROR - invalid port", "red")
            self._socket_serve.set(0)
            return

        if self._socket_serve.get() == 1:
            self.__app.start_sockserver_thread()
            self._ent_sockport.config(state=DISABLED)
            self._spn_sockmode.config(state=DISABLED)
            self.__app.stream_handler.sock_serve = True
        else:
            self.__app.stop_sockserver_thread()
            self._ent_sockport.config(state=NORMAL)
            self._spn_sockmode.config(state=READONLY)
            self.__app.stream_handler.sock_serve = False
            self.clients = 0

    def _on_sockmode(self):
        """
        Set default port depending on socket server mode.
        """

        if self._sock_mode.get() == SOCKMODES[1]:  # NTRIP Server
            self._sock_port.set(SOCKSERVER_NTRIP_PORT)
        else:
            self._sock_port.set(SOCKSERVER_PORT)

    def _on_disconnect(self):
        """
        Disconnect from stream.
        """

        if self.__app.conn_status in (CONNECTED, CONNECTED_FILE, CONNECTED_SOCKET):
            self.__app.stream_handler.stop_read_thread()
            self.__app.stop_sockserver_thread()
            self._socket_serve.set(0)
            self.clients = 0

    def _reset(self):
        """
        Reset settings to defaults.
        """

        self._prot_nmea.set(1)
        self._prot_ubx.set(1)
        self._prot_rtcm3.set(1)
        self._format.set(DDD)
        self._units.set(UMM)
        self._autoscroll.set(1)
        self._maxlines.set(300)
        self._display_format.set(FORMATS[0])  # Parsed
        self._webmap.set(False)
        self._mapzoom.set(10)
        self._show_legend.set(True)
        self._show_unusedsat.set(False)
        self._datalog.set(False)
        self._record_track.set(False)
        self._logformat.set(FORMATS[1])  # Binary
        self._colortags.set(TAG_COLORS)
        self._socket_serve.set(0)
        self._sock_port.set(SOCKSERVER_PORT)
        self._sock_mode.set(SOCKMODES[0])  # open
        self.clients = 0

    def enable_controls(self, status: int):
        """
        Public method to enable and disable those controls
        which depend on connection status.

        :param int status: connection status as integer
               (0=Disconnected, 1=Connected to serial,
               2=Connected to file, 3=No serial ports available)

        """

        self._frm_serial.set_status(status)
        self._frm_socket.set_status(status)

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
        for ctl in (
            self._chk_socketserve,
            self._ent_sockport,
            self._lbl_sockport,
            self._lbl_sockmode,
            self._lbl_sockclients,
        ):
            ctl.config(
                state=(
                    NORMAL
                    if status in (CONNECTED, CONNECTED_SOCKET, CONNECTED_FILE)
                    else DISABLED
                )
            )
        self._spn_sockmode.config(
            state=(
                READONLY
                if status in (CONNECTED, CONNECTED_SOCKET, CONNECTED_FILE)
                else DISABLED
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

    def serial_settings(self) -> Frame:
        """
        Return reference to common serial configuration panel

        :return: reference to serial form
        :rtype: Frame
        """

        return self._frm_serial

    def socket_settings(self) -> Frame:
        """
        Return reference to common socket configuration panel

        :return: reference to socket form
        :rtype: Frame
        """

        return self._frm_socket

    @property
    def protocol(self) -> int:
        """
        Getter for displayed protocols

        :return: protocol displayed (1=NMEA, 2=UBX, 4=RTMC3, 7=ALL)
        :rtype: int
        """

        return (
            (ubt.NMEA_PROTOCOL * self._prot_nmea.get())
            + (ubt.UBX_PROTOCOL * self._prot_ubx.get())
            + (ubt.RTCM3_PROTOCOL * self._prot_rtcm3.get())
        )

    @property
    def display_format(self) -> int:
        """
        Getter for console display format

        :return: display format (0 - parsed, 1 = binary, 2 = hex)
        :rtype: int
        """

        return self._display_format.get()

    @property
    def autoscroll(self) -> int:
        """
        Getter for autoscroll flag

        :return: scroll setting (0 = no scroll, 1 = auto)
        :rtype: int
        """

        return self._autoscroll.get()

    @property
    def maxlines(self) -> int:
        """
        Getter for max console display lines

        :return: max lines in console display (default=300)
        :rtype: int
        """

        return self._maxlines.get()

    @property
    def webmap(self) -> int:
        """
        Getter for webmap flag

        :return: map type (0 = static map, 1 = dynamic web map)
        :rtype: int
        """

        return self._webmap.get()

    @property
    def mapzoom(self) -> int:
        """
        Getter for webmap zoom level

        :return: webmap zoom level (1-20)
        :rtype: int
        """

        return self._mapzoom.get()

    @property
    def units(self) -> str:
        """
        Getter for display units

        :return: "UMM" = metric m/s, "UMK" = metric kmph,
                 "UI" = imperial mph, "UIK" = imperial knots
        :rtype: str
        """

        return self._units.get()

    @property
    def format(self) -> str:
        """
        Getter for degrees format

        :return: "DD.D" = decimal degrees, "DM.M" = degrees, decimal minutes,
                 "D.M.S" = degrees, minutes, seconds
        :rtype: str
        """

        return self._format.get()

    @property
    def colortagging(self) -> bool:
        """
        Getter for colortags boolean

        :return: colortag on/off
        :rtype: bool
        """

        return self._colortags.get()

    @property
    def infilepath(self) -> str:
        """
        Getter for input file path

        :return: input file path
        :rtype: str
        """

        return self._in_filepath

    @property
    def outfilepath(self) -> str:
        """
        Getter for output file path

        :return: output file path
        :rtype: str
        """

        return self._logpath

    @property
    def datalogging(self) -> int:
        """
        Getter for datalogging flag

        :return: 0 = no log, 1 = record datalog
        :rtype: int
        """

        return self._datalog.get()

    @property
    def logformat(self) -> str:
        """
        Getter for datalogging format

        :return: "Parsed", "Binary", "Hex", "Hextable"
        :rtype: str
        """

        return self._logformat.get()

    @property
    def record_track(self) -> int:
        """
        Getter for record track flag

        :return: 0 = no track, 1 = record track
        :rtype: int
        """

        return self._record_track.get()

    @property
    def show_unused(self) -> int:
        """
        Getter for zero signal flag

        :return: 0 = exclude, 1 = include
        :rtype: int
        """

        return self._show_unusedsat.get()

    @property
    def show_legend(self) -> int:
        """
        Getter for graph legend flag

        :return: 0 = hide, 1 = show
        :rtype: int
        """

        return self._show_legend.get()

    @property
    def server_state(self) -> int:
        """
        Getter for socket server run status.

        :return: status 0 = off, 1 = on
        :rtype: int
        """

        return self._socket_serve.get()

    @server_state.setter
    def server_state(self, status: int):
        """
        Setter for server run status.

        :param int status: 0 = off, 1 = on
        """

        self._socket_serve.set(status)

    @property
    def server_port(self) -> int:
        """
        Getter for socket server port

        :return: port
        :rtype: int
        """

        return int(self._sock_port.get())

    @property
    def server_mode(self) -> int:
        """
        Getter for socket server mode

        :return: 0 = open socket server, 1 = NTRIP server
        :rtype: int
        """

        if self._sock_mode.get() == SOCKMODES[1]:  # "NTRIP SERVER"
            return 1
        return 0

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

        self._sock_clients.set(f"Clients {clients}")
        if clients >= SOCKSERVER_MAX_CLIENTS:
            self._lbl_sockclients.config(fg="red")
        elif clients == 0:
            self._lbl_sockclients.config(fg="black")
        else:
            self._lbl_sockclients.config(fg="green")
        if self._socket_serve.get() == 1:
            self.__app.frm_banner.update_transmit_status(clients)
