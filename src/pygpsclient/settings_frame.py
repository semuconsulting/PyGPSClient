"""
settings_frame.py

Settings frame class for PyGPSClient application.

This handles the settings/configuration panel. It references
the SerialConfigFrame class for serial port settings
and the SocketConfigFrame class for socket settings.

Exposes the various settings as properties.

Created on 12 Sep 2020

:author: semuadmin
:copyright: SEMU Consulting © 2020
:license: BSD 3-Clause
"""
# pylint: disable=unnecessary-lambda

from os import getenv
from socket import AF_INET, AF_INET6
from tkinter import (
    DISABLED,
    NORMAL,
    Button,
    Checkbutton,
    E,
    Frame,
    IntVar,
    Label,
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
    ECEF,
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
    READONLY,
    SOCK_NTRIP,
    SOCK_SERVER,
    SOCKCLIENT_HOST,
    SOCKCLIENT_PORT,
    SOCKSERVER_HOST,
    SOCKSERVER_PORT,
    TIMEOUTS,
    UI,
    UIK,
    UMK,
    UMM,
)
from pygpsclient.helpers import MAXPORT, VALINT, VALURL, valid_entry
from pygpsclient.serialconfig_frame import SerialConfigFrame
from pygpsclient.serverconfig_frame import ServerConfigFrame
from pygpsclient.socketconfig_frame import SocketConfigFrame
from pygpsclient.strings import (
    CONFIGERR,
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
        self._init_config = kwargs.pop("config", {})

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
        userport = self._init_config.get("userport", "")
        self.frm_serial = SerialConfigFrame(
            self,
            preselect=KNOWNGPS,
            timeouts=TIMEOUTS,
            bpsrates=BPSRATES,
            msgmodes=list(MSGMODES.keys()),
            userport=userport,  # user-defined serial port
        )

        # socket client configuration panel
        self.frm_socketclient = SocketConfigFrame(self, config=self._init_config)

        # connection buttons
        self._frm_buttons = Frame(self)
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
            values=(DDD, DMS, DMM, ECEF),
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
        self._lbl_maptype = Label(self._frm_options, text="Map Type")
        self.spn_maptype = Spinbox(
            self._frm_options,
            values=("world", "map", "sat"),
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
            self.__app, self, config=self._init_config
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
        ttk.Separator(self).grid(
            column=0, row=2, columnspan=4, padx=2, pady=2, sticky=(W, E)
        )

        self.frm_socketclient.grid(
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
        self._lbl_units.grid(column=0, row=3, padx=2, pady=2, sticky=W)
        self._spn_units.grid(column=1, row=3, columnspan=3, padx=2, pady=2, sticky=W)
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

    def _reset(self):
        """
        Reset settings to defaults.
        """

        self.config = self._init_config
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
            valid = True
            valid = valid & valid_entry(frm.ent_server, VALURL)
            valid = valid & valid_entry(frm.ent_port, VALINT, 1, MAXPORT)
            if not valid:
                self.__app.set_status("ERROR - invalid settings", "red")
                return
            connstr = f"{frm.server}:{frm.port}"
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
        Getter for configuration settings to save as file.

        This collates current settings from the various frames
        and protocol handlers into a dictionary which can be
        saved to the pygpsclient.json config file.

        :return: settings as dictionary
        :rtype: dict
        """

        protocol = (
            (ubt.NMEA_PROTOCOL * self._prot_nmea.get())
            + (ubt.UBX_PROTOCOL * self._prot_ubx.get())
            + (ubt.RTCM3_PROTOCOL * self._prot_rtcm3.get())
        )
        sockmode = 1 if self.frm_socketserver.sock_mode.get() == SOCK_NTRIP else 0

        ntripclient_settings = self.__app.ntrip_handler.settings
        ntripprot = "IPv6" if ntripclient_settings["ipprot"] == AF_INET6 else "IPv4"

        config = {
            # main settings from frm_settings
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
            "maptype": self.maptype.get(),
            "mapzoom": self.mapzoom.get(),
            "legend": self.show_legend.get(),
            "unusedsat": self._show_unusedsat.get(),
            "logformat": self._logformat.get(),
            "datalog": self._datalog.get(),
            "recordtrack": self._record_track.get(),
            # socket client settings from frm_socketclient
            "sockclienthost": self.frm_socketclient.server.get(),
            "sockclientport": self.frm_socketclient.port.get(),
            "sockclientprotocol": self.frm_socketclient.protocol.get(),
            "sockclientflowinfo": self.frm_socketclient.flowinfo.get(),
            "sockclientscopeid": self.frm_socketclient.scopeid.get(),
            # socket server settings from frm_sockerserver
            "sockserver": self.frm_socketserver.socketserving,
            "sockhost": self.frm_socketserver.sock_host.get(),
            "sockport": self.frm_socketserver.sock_port.get(),
            "sockmode": sockmode,
            "ntripcasterbasemode": self.frm_socketserver.base_mode.get(),
            "ntripcasteracclimit": self.frm_socketserver.acclimit.get(),
            "ntripcasterduration": self.frm_socketserver.duration.get(),
            "ntripcasterposmode": self.frm_socketserver.pos_mode.get(),
            "ntripcasterfixedlat": self.frm_socketserver.fixedlat.get(),
            "ntripcasterfixedlon": self.frm_socketserver.fixedlon.get(),
            "ntripcasterfixedalt": self.frm_socketserver.fixedalt.get(),
            "ntripcasterdisablenmea": self.frm_socketserver.disable_nmea.get(),
            # NTRIP client settings from pygnssutils.GNSSNTRIPClient
            "ntripclientserver": ntripclient_settings["server"],
            "ntripclientport": ntripclient_settings["port"],
            "ntripclientprotocol": ntripprot,
            "ntripclientflowinfo": ntripclient_settings["flowinfo"],
            "ntripclientscopeid": ntripclient_settings["scopeid"],
            "ntripclientmountpoint": ntripclient_settings["mountpoint"],
            "ntripclientversion": ntripclient_settings["version"],
            "ntripclientuser": ntripclient_settings["ntripuser"],
            "ntripclientpassword": ntripclient_settings["ntrippassword"],
            "ntripclientggainterval": ntripclient_settings["ggainterval"],
            "ntripclientggamode": ntripclient_settings["ggamode"],
            "ntripclientreflat": ntripclient_settings["reflat"],
            "ntripclientreflon": ntripclient_settings["reflon"],
            "ntripclientrefalt": ntripclient_settings["refalt"],
            "ntripclientrefsep": ntripclient_settings["refsep"],
        }
        return config

    @config.setter
    def config(self, config: dict):
        """
        Setter for configuration loaded from file.

        This reads the configuration dictionary from a pygpsclient.json
        file and updates the various frames and protocol handlers.

        :param dict config: configuration
        """

        try:
            # main settings to frm_settings
            self._prot_nmea.set(config.get("nmeaprot", 1))
            self._prot_ubx.set(config.get("ubxprot", 1))
            self._prot_rtcm3.set(config.get("rtcmprot", 1))
            self._degrees_format.set(config.get("degreesformat", DDD))
            self._colortag.set(config.get("colortag", 0))
            self._units.set(config.get("units", UMM))
            self._autoscroll.set(config.get("autoscroll", 1))
            self._maxlines.set(config.get("maxlines", 200))
            self._console_format.set(config.get("consoleformat", FORMATS[0]))
            self.maptype.set(config.get("maptype", "world"))
            self.mapzoom.set(config.get("mapzoom", 10))
            self.show_legend.set(config.get("legend", 1))
            self._show_unusedsat.set(config.get("unusedsat", 1))
            self._logformat.set(config.get("logformat", FORMATS[1]))  # Binary
            # socket client settings to frm_socketclient
            self.frm_socketclient.server.set(
                config.get("sockclienthost", SOCKCLIENT_HOST)
            )
            self.frm_socketclient.port.set(
                config.get("sockclientport", SOCKCLIENT_PORT)
            )
            self.frm_socketclient.protocol.set(
                config.get("sockclientprotocol", "TCP IPv4")
            )
            self.frm_socketclient.flowinfo.set(config.get("sockclientflowinfo", 0))
            self.frm_socketclient.scopeid.set(config.get("sockclientscopeid", 0))
            # socket server settings to frm_sockerserver
            self.frm_socketserver.socketserving = config.get("sockserver", 0)
            self.frm_socketserver.sock_host.set(
                config.get(
                    "sockhost", getenv("PYGPSCLIENT_BINDADDRESS", SOCKSERVER_HOST)
                )
            )
            self.frm_socketserver.sock_port.set(config.get("sockport", SOCKSERVER_PORT))
            self.frm_socketserver.sock_mode.set(
                SOCK_NTRIP if config.get("sockmode", 0) == 1 else SOCK_SERVER
            )
            self.frm_socketserver.base_mode.set(
                config.get("ntripcasterbasemode", "SURVEY IN")
            )
            self.frm_socketserver.acclimit.set(config.get("ntripcasteracclimit", 10))
            self.frm_socketserver.duration.set(config.get("ntripcasterduration", 60))
            self.frm_socketserver.pos_mode.set(config.get("ntripcasterposmode", "LLH"))
            self.frm_socketserver.fixedlat.set(config.get("ntripcasterfixedlat", 0))
            self.frm_socketserver.fixedlon.set(config.get("ntripcasterfixedlon", 0))
            self.frm_socketserver.fixedalt.set(config.get("ntripcasterfixedalt", 0))
            self.frm_socketserver.disable_nmea.set(
                config.get("ntripcasterdisablenmea", 1)
            )
            # NTRIP client settings to pygnssutils.GNSSNTRIPClient
            ntripsettings = {}
            ntripsettings["server"] = config.get("ntripclientserver", "")
            ntripsettings["port"] = config.get("ntripclientport", 2101)
            ntripsettings["ipprot"] = (
                AF_INET6 if config.get("ntripclientprotocol") == "IPv6" else AF_INET
            )
            ntripsettings["flowinfo"] = config.get("ntripclientflowinfo", 0)
            ntripsettings["scopeid"] = config.get("ntripclientscopeid", 0)
            ntripsettings["mountpoint"] = config.get("ntripclientmountpoint", "")
            ntripsettings["sourcetable"] = []
            ntripsettings["version"] = config.get("ntripclientversion", "2.0")
            ntripsettings["ntripuser"] = config.get("ntripclientuser", "anon")
            ntripsettings["ntrippassword"] = config.get(
                "ntripclientpassword", "password"
            )
            ntripsettings["ggainterval"] = config.get("ntripclientggainterval", -1)
            ntripsettings["ggamode"] = config.get("ntripclientggamode", 0)  # GGALIVE
            ntripsettings["reflat"] = config.get("ntripclientreflat", 0.0)
            ntripsettings["reflon"] = config.get("ntripclientreflon", 0.0)
            ntripsettings["refalt"] = config.get("ntripclientrefalt", 0.0)
            ntripsettings["refsep"] = config.get("ntripclientrefsep", 0.0)
            self.__app.ntrip_handler.settings = ntripsettings

        except KeyError as err:
            self.__app.set_status(f"{CONFIGERR} - {err}", BADCOL)
