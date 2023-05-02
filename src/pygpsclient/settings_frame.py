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
# pylint: disable=unnecessary-lambda

from tkinter import (
    DISABLED,
    HORIZONTAL,
    NORMAL,
    Button,
    Checkbutton,
    E,
    Entry,
    Frame,
    IntVar,
    Label,
    N,
    S,
    Scale,
    Spinbox,
    StringVar,
    W,
    ttk,
)

import pyubx2.ubxtypes_core as ubt
from PIL import Image, ImageTk

from pygpsclient.globals import (
    BADCOL,
    BPSRATES,
    CONNECTED,
    CONNECTED_FILE,
    CONNECTED_SOCKET,
    DDD,
    DISCONNECTED,
    DLGTNTRIP,
    DLGTSPARTN,
    DLGTUBX,
    DMM,
    DMS,
    FORMATS,
    GNSS_EOF_EVENT,
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
    READONLY,
    SOCKMODES,
    SOCKSERVER_MAX_CLIENTS,
    SOCKSERVER_NTRIP_PORT,
    SOCKSERVER_PORT,
    TAG_COLORS,
    TIMEOUTS,
    UI,
    UIK,
    UMK,
    UMM,
)
from pygpsclient.helpers import MAXPORT, VALINT, VALURL, valid_entry
from pygpsclient.serialconfig_frame import SerialConfigFrame
from pygpsclient.socketconfig_frame import SocketConfigFrame
from pygpsclient.strings import (
    CONFIGERR,
    LBLDATADISP,
    LBLDATALOG,
    LBLDEGFORMAT,
    LBLLEGEND,
    LBLNTRIPCONFIG,
    LBLPROTDISP,
    LBLSERVERMODE,
    LBLSERVERPORT,
    LBLSHOWUNUSED,
    LBLSOCKSERVE,
    LBLSPARTNCONFIG,
    LBLTRACKRECORD,
    LBLUBXCONFIG,
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
        self.__master = self.__app.appmaster  # Reference to root class (Tk)
        Frame.__init__(self, self.__master, *args, **kwargs)

        self.infilepath = None
        self.outfilepath = None
        self._prot_nmea = IntVar()
        self._prot_ubx = IntVar()
        self._prot_rtcm3 = IntVar()
        self._autoscroll = IntVar()
        self._maxlines = IntVar()
        self._webmap = IntVar()
        self._mapzoom = IntVar()
        self._units = StringVar()
        self._degrees_format = StringVar()
        self._console_format = StringVar()
        self._datalog = IntVar()
        self._logformat = StringVar()
        self._record_track = IntVar()
        self._show_unusedsat = IntVar()
        self.show_legend = IntVar()
        self._colortag = IntVar()
        self._socket_serve = IntVar()
        self._sock_port = StringVar()
        self._sock_mode = StringVar()
        self._sock_clients = StringVar()
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
        userport = self.__app.app_config.get("userport", "")
        self._frm_serial = SerialConfigFrame(
            self,
            preselect=KNOWNGPS,
            timeouts=TIMEOUTS,
            bpsrates=BPSRATES,
            msgmodes=list(MSGMODES.keys()),
            userport=userport,  # user-defined serial port
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
            values=(DDD, DMS, DMM),
            width=6,
            state=READONLY,
            wrap=True,
            textvariable=self._degrees_format,
        )
        self._lbl_units = Label(self._frm_options, text="Units")
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
            values=("100", "200", "500", "1000", "2000"),
            width=6,
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
            variable=self._mapzoom,
        )
        self._chk_unusedsat = Checkbutton(
            self._frm_options, text=LBLSHOWUNUSED, variable=self._show_unusedsat
        )
        self._chk_legend = Checkbutton(
            self._frm_options, text=LBLLEGEND, variable=self.show_legend
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
        self._btn_exit.grid(column=4, row=0, padx=2, pady=1)
        self._lbl_connect.grid(column=0, row=1, padx=1, pady=1, sticky=(W, E))
        self._lbl_connect_socket.grid(column=1, row=1, padx=1, pady=1, sticky=(W, E))
        self._lbl_connect_file.grid(column=2, row=1, padx=1, pady=1, sticky=(W, E))
        self._lbl_disconnect.grid(column=3, row=1, padx=1, pady=1, sticky=(W, E))

        ttk.Separator(self).grid(
            column=0, row=7, columnspan=4, padx=2, pady=2, sticky=(W, E)
        )

        self._frm_options.grid(column=0, row=8, columnspan=4, sticky=(W, E))
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
        self._lbl_units.grid(column=0, row=3, padx=2, pady=2, sticky=W)
        self._spn_units.grid(column=1, row=3, columnspan=3, padx=2, pady=2, sticky=W)
        self._chk_scroll.grid(column=0, row=4, padx=2, pady=2, sticky=W)
        self._spn_maxlines.grid(column=1, row=4, columnspan=3, padx=2, pady=2, sticky=W)
        self._chk_webmap.grid(column=0, row=5, padx=2, pady=2, sticky=W)
        self._lbl_mapzoom.grid(column=1, row=5, sticky=E)
        self._scl_mapzoom.grid(column=2, row=5, columnspan=2, sticky=W)
        self._chk_unusedsat.grid(
            column=0, row=6, columnspan=2, padx=2, pady=2, sticky=W
        )
        self._chk_legend.grid(column=2, row=6, columnspan=2, padx=2, pady=2, sticky=W)
        self._chk_datalog.grid(column=0, row=7, padx=2, pady=2, sticky=W)
        self._spn_datalog.grid(column=1, row=7, columnspan=3, padx=2, pady=2, sticky=W)
        self._chk_recordtrack.grid(
            column=0, row=8, columnspan=2, padx=2, pady=2, sticky=W
        )
        self._chk_socketserve.grid(
            column=0, row=9, rowspan=2, padx=2, pady=2, sticky=(N, S, W)
        )
        self._lbl_sockmode.grid(column=1, row=9, padx=2, pady=2, sticky=E)
        self._spn_sockmode.grid(column=2, row=9, columnspan=2, padx=2, pady=2, sticky=W)
        self._lbl_sockport.grid(column=1, row=10, padx=2, pady=2, sticky=E)
        self._ent_sockport.grid(column=2, row=10, padx=2, pady=2, sticky=W)
        self._lbl_sockclients.grid(column=3, row=10, padx=2, pady=2, sticky=W)
        ttk.Separator(self._frm_options).grid(
            column=0, row=11, columnspan=4, padx=2, pady=2, sticky=(W, E)
        )
        self._btn_ubxconfig.grid(column=0, row=12)
        self._lbl_ubxconfig.grid(column=0, row=13)
        self._btn_ntripconfig.grid(column=1, row=12)
        self._lbl_ntripconfig.grid(column=1, row=13)
        self._btn_spartnconfig.grid(column=2, row=12)
        self._lbl_spartnconfig.grid(column=2, row=13)

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
        Start or stop track recorder
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

    def _on_serial_stream(self):
        if self.serial_settings.status == NOPORTS:
            return

        self.__app.set_connection(
            (
                f"{self.serial_settings.port}:{self.serial_settings.port_desc} "
                + f"@ {self.serial_settings.bpsrate}"
            ),
            "green",
        )
        self.__app.set_status("")
        self.__app.conn_status = CONNECTED
        self._reset_frames()
        self.__app.stream_handler.start_read_thread(self._get_settings())

    def _on_socket_stream(self):
        """
        Start socket streamer if settings are valid
        """

        valid = True
        valid = valid & valid_entry(self._frm_socket.ent_server, VALURL)
        valid = valid & valid_entry(self._frm_socket.ent_port, VALINT, 1, MAXPORT)
        if valid:
            self.__app.set_connection(
                f"{self.socket_settings.server}:{self.socket_settings.port}",
                "green",
            )
            self.__app.set_status("")
            self.__app.conn_status = CONNECTED_SOCKET
            self._reset_frames()
            self.__app.stream_handler.start_read_thread(self._get_settings())
        else:
            self.__app.set_status("ERROR - invalid settings", "red")

    def _on_file_stream(self):
        """
        Start data file streamer if file selected
        """

        self.infilepath = self.__app.file_handler.open_infile()
        if self.infilepath is not None:
            self.__app.set_connection(f"{self.infilepath}")
            self.__app.set_status("")
            self.__app.conn_status = CONNECTED_FILE
            self._reset_frames()
            self.__app.stream_handler.start_read_thread(self._get_settings())

    def _get_settings(self) -> dict:
        """
        Get settings dict.

        :return: dictionary of settings for stream handler
        :rtype: dict
        """

        return {
            "owner": self,
            "read_event": GNSS_EVENT,
            "eof_event": GNSS_EOF_EVENT,
            "inqueue": self.__app.gnss_inqueue,
            "outqueue": self.__app.gnss_outqueue,
            "socket_inqueue": self.__app.socket_inqueue,
            "socket_outqueue": self.__app.socket_outqueue,
            "serial_settings": self._frm_serial,
            "socket_settings": self._frm_socket,
            "in_filepath": self.infilepath,
        }

    def _reset(self):
        """
        Reset settings to defaults.
        """

        self.config = {}
        self.clients = 0

    def _reset_frames(self):
        """
        Reset frames.
        """

        self.__app.frm_mapview.reset_map_refresh()
        self.__app.frm_spectrumview.reset()
        self.__app.reset_gnssstatus()

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

    @property
    def config(self) -> dict:
        """
        Getter for configuration settings to save as file.

        :return: settings as dictionary
        :rtype: dict
        """

        protocol = (
            (ubt.NMEA_PROTOCOL * self._prot_nmea.get())
            + (ubt.UBX_PROTOCOL * self._prot_ubx.get())
            + (ubt.RTCM3_PROTOCOL * self._prot_rtcm3.get())
        )
        sockmode = 0 if self._sock_mode.get() == SOCKMODES[0] else 1

        config = {
            "protocol": protocol,
            "nmeaprot": self._prot_nmea.get(),
            "ubxprot": self._prot_ubx.get(),
            "rtcmprot": self._prot_rtcm3.get(),
            "degreesformat": self._degrees_format.get(),
            "colortag": self._colortag.get(),
            "units": self._units.get(),
            "autoscroll": self._autoscroll.get(),
            "maxlines": self._maxlines.get(),
            "consoleformat": self._console_format.get(),
            "webmap": self._webmap.get(),
            "mapzoom": self._mapzoom.get(),
            "legend": self.show_legend.get(),
            "unusedsat": self._show_unusedsat.get(),
            "logformat": self._logformat.get(),
            "datalog": self._datalog.get(),
            "recordtrack": self._record_track.get(),
            "sockserver": self._socket_serve.get(),
            "sockport": self._sock_port.get(),
            "sockmode": sockmode,
        }
        return config

    @config.setter
    def config(self, config: dict):
        """
        Setter for configuration loaded from file.

        :param dict config: configuration
        """

        try:
            self._prot_nmea.set(config.get("nmeaprot", 1))
            self._prot_ubx.set(config.get("ubxprot", 1))
            self._prot_rtcm3.set(config.get("rtcmprot", 1))
            self._degrees_format.set(config.get("degreesformat", DDD))
            self._colortag.set(config.get("colortag", TAG_COLORS))
            self._units.set(config.get("units", UMM))
            self._autoscroll.set(config.get("autoscroll", 1))
            self._maxlines.set(config.get("maxlines", 200))
            self._console_format.set(config.get("consoleformat", FORMATS[0]))
            self._webmap.set(config.get("webmap", 0))
            self._mapzoom.set(config.get("mapzoom", 10))
            self.show_legend.set(config.get("legend", 1))
            self._show_unusedsat.set(config.get("unusedsat", 1))
            self._logformat.set(config.get("logformat", FORMATS[1]))  # Binary
            # don't persist datalog or gpx track settings...
            # self._datalog.set(config.get("datalog", 0))
            # self._record_track.set(config.get("recordtrack", 0))
            self._socket_serve.set(config.get("sockserver", 0))
            self._sock_port.set(config.get("sockport", SOCKSERVER_PORT))
            self._sock_mode.set(
                SOCKMODES[1] if config.get("sockmode", 0) == 1 else SOCKMODES[0]
            )
        except KeyError as err:
            self.set_status(f"{CONFIGERR} - {err}", BADCOL)

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

    # ============================================
    # FOLLOWING METHODS REQUIRED BY STREAM_HANDLER
    # ============================================

    @property
    def conn_status(self) -> int:
        """
        Getter for connection mode
        (0 = disconnected, 1 = serial, 2 = socket, 4 = file).
        """

        return self.__app.conn_status

    @conn_status.setter
    def conn_status(self, status: int):
        """
        Setter for connection mode.

        :param int status: 0 = disconnected, 1 = serial, 2 = socket, 4 = file.
        """

        self.__app.conn_status = status

    def set_status(self, msg: str, col: str):
        """
        Set status message.

        :param str msg: status message.
        :param str col: colour
        """

        self.__app.set_status(msg, col)

    def set_connection(self, msg: str, col: str):
        """
        Set connection message.

        :param str msg: status message.
        :param str col: colour
        """

        self.__app.set_connection(msg, col)

    @property
    def serial_settings(self) -> Frame:
        """
        Getter for common serial configuration panel

        :return: reference to serial form
        :rtype: Frame
        """

        return self._frm_serial

    @property
    def socket_settings(self) -> Frame:
        """
        Getter for common socket configuration panel

        :return: reference to socket form
        :rtype: Frame
        """

        return self._frm_socket
