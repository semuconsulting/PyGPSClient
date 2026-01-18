"""
app.py

PyGPSClient - Main tkinter application class.

Essentially the 'Model' in a nominal MVC (Model-View-Controller)
architecture.

- Loads configuration from json file (if available)
- Instantiates all frames, widgets, and protocol handlers.
- Maintains state of all user-selectable widgets.
- Maintains state of all threaded dialog and protocol handler processes.
- Maintains state of serial and RTK connections.
- Handles event-driven data processing of navigation data placed on
  input message queue by stream handler and assigns to appropriate
  protocol handler.
- Maintains central dictionary of current key navigation data as
  `gnss_status`, for use by user-selectable widgets.

Global logging configuration is defined in __main__.py. To enable module
logging, this and other subsidiary modules can use:

```self.logger = logging.getLogger(__name__)```

To override individual module loglevel, use e.g.

```self.logger.setLevel(INFO)```

Created on 12 Sep 2020

:author: semuadmin (Steve Smith)
:copyright: 2020 semuadmin
:license: BSD 3-Clause
"""

# pylint: disable=too-many-ancestors, no-member

import logging
from datetime import datetime, timedelta
from inspect import currentframe, getfile
from os import path
from queue import Empty, Queue
from subprocess import CalledProcessError, run
from sys import executable
from threading import Thread
from time import process_time_ns, time
from tkinter import EW, NSEW, NW, Frame, Label, PhotoImage, Tk, Toplevel, font
from types import NoneType

from pygnssutils import GNSSMQTTClient, GNSSNTRIPClient, MQTTMessage
from pygnssutils.gnssreader import (
    NMEA_PROTOCOL,
    POLL,
    QGC_PROTOCOL,
    RTCM3_PROTOCOL,
    SBF_PROTOCOL,
    UBX_PROTOCOL,
)
from pygnssutils.socket_server import ClientHandler, ClientHandlerTLS, SocketServer
from pynmeagps import NMEAMessage
from pyqgc import QGCMessage
from pyrtcm import RTCMMessage
from pysbf2 import SBFMessage
from pyspartn import SPARTNMessage
from pyubx2 import UBXMessage
from serial import SerialException, SerialTimeoutException

from pygpsclient._version import __version__ as VERSION
from pygpsclient.banner_frame import BannerFrame
from pygpsclient.configuration import Configuration
from pygpsclient.dialog_state import DialogState
from pygpsclient.file_handler import FileHandler
from pygpsclient.globals import (
    BGCOL,
    CLASS,
    CONFIGFILE,
    CONNECTED,
    CONNECTED_NTRIP,
    CONNECTED_SIMULATOR,
    CONNECTED_SOCKET,
    CONNECTED_SPARTNIP,
    CONNECTED_SPARTNLB,
    DISCONNECTED,
    ERRCOL,
    FRAME,
    GNSS_EOF_EVENT,
    GNSS_ERR_EVENT,
    GNSS_EVENT,
    GNSS_TIMEOUT_EVENT,
    ICON_APP128,
    INFOCOL,
    MAINSCALE,
    MQTT_PROTOCOL,
    NOPORTS,
    NTRIP_EVENT,
    OKCOL,
    SOCKSERVER_MAX_CLIENTS,
    SPARTN_EVENT,
    SPARTN_PROTOCOL,
    STATUSPRIORITY,
    TTY_PROTOCOL,
    UNDO,
)
from pygpsclient.gnss_status import GNSSStatus
from pygpsclient.helpers import (
    brew_installed,
    check_for_updates,
    check_latest,
    set_geom,
)
from pygpsclient.menu_bar import MenuBar
from pygpsclient.nmea_handler import NMEAHandler
from pygpsclient.qgc_handler import QGCHandler
from pygpsclient.rtcm3_handler import RTCM3Handler
from pygpsclient.sbf_handler import SBFHandler
from pygpsclient.settings_frame import SettingsFrame
from pygpsclient.sqlite_handler import DBINMEM, SQLOK, SqliteHandler
from pygpsclient.status_frame import StatusFrame
from pygpsclient.stream_handler import StreamHandler
from pygpsclient.strings import (
    BREWUPDATE,
    CONFIGERR,
    DLG,
    DLGSTOPRTK,
    DLGTNTRIP,
    DLGTRECORD,
    DLGTSETTINGS,
    ENDOFFILE,
    INACTIVE_TIMEOUT,
    INTROTXTNOPORTS,
    KILLSWITCH,
    NOTCONN,
    NOWDGSWARN,
    SAVECONFIGBAD,
    SAVECONFIGOK,
    TITLE,
    UPDATEERR,
    UPDATEINPROG,
    UPDATERESTART,
    VERCHECK,
)
from pygpsclient.tty_handler import TTYHandler
from pygpsclient.ubx_handler import UBXHandler
from pygpsclient.widget_state import (
    COLSPAN,
    DEFAULT,
    HIDE,
    MAXSPAN,
    SHOW,
    VISIBLE,
    WDGCHART,
    WDGCONSOLE,
    WidgetState,
)


class App(Frame):
    """
    Main PyGPSClient GUI Application Class.
    """

    def __init__(self, master, **kwargs):  # pylint: disable=too-many-statements
        """
        Set up main application and add frames.

        :param tkinter.Tk master: reference to Tk root
        :param args: optional args
        :param kwargs: optional (CLI) kwargs
        """

        self.starttime = time()  # for run time benchmarking
        self.processtime = 0  # for process time benchmarking

        self.__master = master
        self.logger = logging.getLogger(__name__)

        super().__init__(master)

        # load config from json file
        self._deferredmsg = None
        self.widget_state = WidgetState()  # widget state
        self.file_handler = FileHandler(self)
        self.configuration = Configuration(self)  # configuration state
        configfile = kwargs.pop("config", CONFIGFILE)
        _, configerr = self.configuration.loadfile(configfile)
        # load config from CLI arguments & env variables
        self.configuration.loadcli(**kwargs)
        if configerr == "":
            self.update_widgets()  # set initial widget state
            # warning if all widgets have been disabled in config
            if self._nowidgets:
                self.status_label = (NOWDGSWARN.format(configfile), ERRCOL)

        # setup main application window
        geom = self.configuration.get("screengeom_s")
        if geom == "":
            geom = set_geom(master, MAINSCALE)
        self.__master.geometry(geom)
        self.__master.protocol("WM_DELETE_WINDOW", self.on_exit)
        self.__master.title(TITLE)
        self.__master.iconphoto(True, PhotoImage(file=ICON_APP128))

        self._server_status = -1  # socket server status -1 = inactive
        self.gnss_inqueue = Queue()  # messages from GNSS receiver
        self.gnss_outqueue = Queue()  # messages to GNSS receiver
        self.ntrip_inqueue = Queue()  # messages from NTRIP source
        self.spartn_inqueue = Queue()  # messages from SPARTN correction rcvr
        self.spartn_outqueue = Queue()  # messages to SPARTN correction rcvr
        self.socket_inqueue = Queue()  # message from socket
        self.socket_outqueue = Queue()  # message to socket
        self.dialog_state = DialogState()  # dialog state
        self.gnss_status = GNSSStatus()  # holds latest GNSS readings
        self.stream_handler = StreamHandler(self)
        self.spartn_stream_handler = StreamHandler(self)
        self.nmea_handler = NMEAHandler(self)
        self.ubx_handler = UBXHandler(self)
        self.sbf_handler = SBFHandler(self)
        self.qgc_handler = QGCHandler(self)
        self.rtcm_handler = RTCM3Handler(self)
        self.tty_handler = TTYHandler(self)
        self.ntrip_handler = GNSSNTRIPClient(self)
        self.spartn_handler = GNSSMQTTClient(self)
        self.sqlite_handler = SqliteHandler(self)
        self.frm_settings = None
        self._conn_status = DISCONNECTED
        self._rtk_conn_status = DISCONNECTED
        self._nowidgets = True
        self._last_gui_update = datetime.now()
        self._socket_thread = None
        self._socket_server = None
        self.consoledata = []
        self._recorded_commands = []  # captured by RecorderDialog
        self.recording = False  # RecordDialog status
        self.recording_type = 0  # 0 = TTY ONLY, 1 = UBX/NMEA

        # open database if database recording enabled
        dbpath = self.configuration.get("databasepath_s")
        if self.configuration.get("database_b") and dbpath != "":
            self._db_enabled = self.sqlite_handler.open(dbpath=dbpath)
        else:
            self._db_enabled = self.sqlite_handler.open(dbname=DBINMEM)
        if self._db_enabled != SQLOK:
            self.configuration.set("database_b", 0)

        self._body()
        self._do_layout()
        self._attach_events()

        # initialise widgets
        for wdg in self.widget_state.state.values():
            frm = getattr(self, wdg[FRAME])
            if hasattr(frm, "init_frame"):
                frm.update_idletasks()
                frm.init_frame()

        # display initial connection status
        self.frm_banner.update_conn_status(DISCONNECTED)
        if self.frm_settings.frm_serial.status == NOPORTS:
            self.status_label = (INTROTXTNOPORTS, ERRCOL)

        # display any deferred messages
        if isinstance(self._deferredmsg, tuple):
            self.status_label = self._deferredmsg
            self._deferredmsg = None

        # check for more recent version (if enabled)
        if self.configuration.get("checkforupdate_b") and configerr == "":
            self._check_update()

    def _body(self):
        """
        Set up frame and widgets.
        """

        self._set_default_fonts()
        self.menu = MenuBar(self)
        self.__master.config(menu=self.menu, bg=BGCOL)

        self.frm_banner = BannerFrame(self, borderwidth=2, relief="groove")
        self.frm_status = StatusFrame(self, borderwidth=2, relief="groove")
        self.frm_settings = SettingsFrame(self)
        self.frm_widgets = Frame(self.__master, bg=BGCOL)

        # instantiate widgets
        for wdg in self.widget_state.state.values():
            setattr(
                # self.frm_widgets,
                self,
                wdg[FRAME],
                wdg[CLASS](self, self.frm_widgets, borderwidth=2, relief="groove"),
            )

    def _do_layout(self):
        """
        Arrange and 'pack' visible widgets in main application frame and set
        show/hide View menu labels.

        Widget order, visibility and columnspan are defined in widget_state.
        Visible widgets are gridded in sequence, left to right, top to bottom,
        subject to a maximum columnspan defined in "maxcolumns_n" (default 4).
        A widget columnspan of 0 (MAXSPAN) signifies the widget occupies a
        full row.

        NB: PyGPSClient uses 'grid' rather than 'pack' layout management throughout:

        - grid col/row weight = 0 means non-expandable
        - grid col/row weight > 0 and `sticky=NSEW` is equivalent to
          `pack(fill = BOTH, expand = True)`

        FYI: `grid.forget()` method has potential memory leak; use sparingly!
        """

        # do main layout
        self.frm_banner.grid(column=0, row=0, columnspan=2, sticky=EW)
        self.frm_widgets.grid(column=0, row=1, sticky=NSEW)
        if isinstance(self.frm_settings, SettingsFrame):  # docked
            if self.configuration.get("showsettings_b"):
                self.frm_settings.grid(column=1, row=1, sticky=NW)
            else:
                if self.frm_settings.winfo_ismapped():
                    self.frm_settings.grid_forget()
        self.frm_status.grid(column=0, row=2, columnspan=2, sticky=EW)

        # get overall column and row spans for frm_widgets
        maxcols = self.configuration.get("maxcolumns_n")
        wcolspan = 0
        wrowspan = 1
        cols = 0
        wids = [
            wdg.get(COLSPAN, 1)
            for wdg in self.widget_state.state.values()
            if wdg[VISIBLE]
        ]
        for c in wids:
            if c == MAXSPAN or c + cols > maxcols:
                wrowspan += 2 if c == MAXSPAN and cols > 0 else 1
                cols = 0
            cols += c
            wcolspan = max(wcolspan, cols)
        wcolspan = max(1, wcolspan)

        # dynamically position widgets in frm_widgets
        col = 0
        row = 0
        men = 2
        for name, wdg in self.widget_state.state.items():
            frm = getattr(self, wdg[FRAME])
            if wdg[VISIBLE]:
                lbl = HIDE
                # enable any GNSS message output required by widget
                self.widget_enable_messages(name)
                c = wdg.get(COLSPAN, 1)
                cols = wcolspan if c == MAXSPAN else c
                # only grid if position has changed
                frmi = frm.grid_info()
                if (
                    frmi.get("column", None) != col
                    or frmi.get("row", None) != row
                    or frmi.get("columnspan", None) != cols
                ):
                    frm.grid(column=col, row=row, columnspan=cols, sticky=NSEW)
                if c == MAXSPAN or c + col >= maxcols:
                    col = 0
                    row += 1
                else:
                    col += c
            else:
                lbl = SHOW
                # only forget if gridded (memory leak!)
                if frm.winfo_ismapped():
                    frm.grid_forget()

            # update View menu label (show/hide)
            self.menu.view_menu.entryconfig(men, label=f"{lbl} {name}")
            men += 1

        # update View menu labels for Settings (dock/undock, show/hide)
        lbl = "Undock" if self.configuration.get("docksettings_b") else "Dock"
        self.menu.view_menu.entryconfig(0, label=f"{lbl} Settings")
        lbl = HIDE if self.configuration.get("showsettings_b") else SHOW
        self.menu.view_menu.entryconfig(1, label=f"{lbl} Settings")

        # set column and row weights to control 'pack' behaviour of main layout
        self.__master.grid_columnconfigure(0, weight=1)
        self.__master.grid_rowconfigure(1, weight=1)
        wcol, wrow = self.frm_widgets.grid_size()
        for col in range(wcol):
            w = 1 if col < wcolspan else 0
            self.frm_widgets.grid_columnconfigure(col, weight=w)
        for row in range(wrow):
            w = 1 if row < wrowspan else 0
            self.frm_widgets.grid_rowconfigure(row, weight=w)

    def _attach_events(self):
        """
        Bind events to main application.
        """

        self.__master.bind(GNSS_EVENT, self.on_gnss_read)
        self.__master.bind(GNSS_EOF_EVENT, self.on_gnss_eof)
        self.__master.bind(GNSS_TIMEOUT_EVENT, self.on_gnss_timeout)
        self.__master.bind(GNSS_ERR_EVENT, self.on_stream_error)
        self.__master.bind(NTRIP_EVENT, self.on_ntrip_read)
        self.__master.bind(SPARTN_EVENT, self.on_spartn_read)
        self.__master.bind_all("<Control-q>", self.on_exit)
        self.__master.bind_all("<Control-k>", self.on_killswitch)
        # <Control-u> also bound in check_updates

    def settings_toggle(self):
        """
        Toggle settings visibility.
        """

        self.configuration.set(
            "showsettings_b", not self.configuration.get("showsettings_b")
        )
        self._do_layout()

    def settings_dock(self):
        """
        Toggle settings docking.

        - If undocked, destroy any existing instance of SettingsFrame
          and launch SettingsDialog instead.
        - If docked, destroy SettingsDialog and instantiate SettingsFrame.
        """

        self.configuration.set(
            "docksettings_b", not self.configuration.get("docksettings_b")
        )
        if self.configuration.get("docksettings_b"):
            if self.dialog_state.state[DLGTSETTINGS][DLG] is not None:
                self.dialog_state.state[DLGTSETTINGS][DLG].destroy()
                self.dialog_state.state[DLGTSETTINGS][DLG] = None
                self.frm_settings = SettingsFrame(self)
        else:
            if self.dialog_state.state[DLGTSETTINGS][DLG] is None:
                if isinstance(self.frm_settings, SettingsFrame):
                    self.frm_settings.grid_forget()
                    self.frm_settings.destroy()
                self.start_dialog(DLGTSETTINGS)
                self.frm_settings = self.dialog_state.state[DLGTSETTINGS][DLG]
        self._do_layout()

    def widget_toggle(self, name: str):
        """
        Toggle widget visibility and enable or disable any
        UBX messages required by widget.

        :param str name: widget name
        """

        self.widget_state.state[name][VISIBLE] = not self.widget_state.state[name][
            VISIBLE
        ]
        self.configuration.set(name, self.widget_state.state[name][VISIBLE])
        self._do_layout()

    def widget_enable_messages(self, name: str):
        """
        Enable any GNSS messages required by widget.

        :param str name: widget name
        """

        frm = getattr(self, self.widget_state.state[name][FRAME])
        if hasattr(frm, "enable_messages"):
            frm.enable_messages(self.widget_state.state[name][VISIBLE])

    def reset_layout(self):
        """
        Reset to default layout.
        """

        for name, wdg in self.widget_state.state.items():
            vis = wdg.get(DEFAULT, False)
            wdg[VISIBLE] = vis
            self.configuration.set(name, vis)
        self.configuration.set("showsettings_b", True)
        self.configuration.set("docksettings_b", True)
        self._do_layout()

    def reset_frames(self):
        """
        Reset frames.
        """

        self.frm_mapview.reset_map_refresh()
        self.frm_spectrumview.reset()

    def reset_gnssstatus(self):
        """
        Reset gnss_status dictionary e.g. after reconnecting.
        """

        self.gnss_status = GNSSStatus()

    def _set_default_fonts(self):
        """
        Set default fonts for entire application.
        """
        # pylint: disable=attribute-defined-outside-init

        self.font_vsm = font.Font(size=8)
        self.font_sm = font.Font(size=10)
        self.font_md = font.Font(size=12)
        self.font_md2 = font.Font(size=14)
        self.font_lg = font.Font(size=18)

    def set_event(self, evt: str):
        """
        Generate master event.

        :param str evt: event type string
        """

        self.__master.event_generate(evt)

    def load_config(self):
        """
        Load configuration file menu option.
        """

        # Warn if Streaming, NTRIP or SPARTN clients are running
        if self.conn_status == DISCONNECTED and self.rtk_conn_status == DISCONNECTED:
            self.status_label = ("", OKCOL)
        else:
            self.status_label = (DLGSTOPRTK, ERRCOL)
            return

        filename, err = self.configuration.loadfile()
        if err == "":  # load succeeded
            self.update_widgets()
            for frm in (
                self.frm_settings.frm_settings,
                self.frm_settings.frm_serial,
                self.frm_settings.frm_socketclient,
            ):
                frm.reset()
            self._do_layout()
            if self._nowidgets:
                self.status_label = (NOWDGSWARN.format(filename), ERRCOL)
        elif err == "cancelled":
            pass

    def save_config(self):
        """
        Save configuration file menu option.
        """

        # save current screen geometry
        self.configuration.set("screengeom_s", self.__master.geometry())

        err = self.configuration.savefile()
        if err == "":
            self.status_label = (SAVECONFIGOK, OKCOL)
        elif err == "cancelled":
            pass
        else:  # save failed
            self.status_label = (SAVECONFIGBAD.format(err), ERRCOL)

    def update_widgets(self):
        """
        Update widget configuration (self.widget_state.state).

        If no widgets are set as "visible" in the config file, enable
        the status widget anyway to display a warning to this effect.
        """

        try:
            self._nowidgets = True
            for key, vals in self.widget_state.state.items():
                vis = self.configuration.get(key)
                vals[VISIBLE] = vis
                if vis:
                    self._nowidgets = False
            if self._nowidgets:
                self.widget_state.state["Status"][VISIBLE] = "true"
        except KeyError as err:
            self.status_label = (f"{CONFIGERR} - {err}", ERRCOL)

    def _refresh_widgets(self):
        """
        Refresh visible widgets.
        """

        self.frm_banner.update_frame()
        for wdg, wdgdata in self.widget_state.state.items():
            frm = getattr(self, wdgdata[FRAME])
            if hasattr(frm, "update_frame") and wdgdata[VISIBLE]:
                if wdg == WDGCONSOLE:
                    frm.update_frame(self.consoledata)
                    self.consoledata = []
                else:
                    frm.update_frame()

    def start_dialog(self, dlg: str):
        """
        Open a top level dialog if the dialog is not already open.

        :param str dlg: name of dialog
        """

        if self.dialog_state.state[dlg][DLG] is None:
            cls = self.dialog_state.state[dlg][CLASS]
            self.dialog_state.state[dlg][DLG] = cls(self)

    def dialog(self, dlg: str) -> Toplevel:
        """
        Get reference to dialog instance.

        :param str dlg: name of dialog
        :return: dialog instance
        :rtype: Toplevel
        """

        return self.dialog_state.state[dlg][DLG]

    def sockserver_start(self):
        """
        Start socket server thread.
        """

        cfg = self.configuration
        ntripmode = cfg.get("sockmode_b")
        host = cfg.get("sockhost_s")
        if ntripmode:  # NTRIP CASTER
            port = cfg.get("sockportntrip_n")
        else:  # SOCKET SERVER
            port = cfg.get("sockport_n")
        https = cfg.get("sockhttps_b")
        ntripuser = cfg.get("ntripcasteruser_s")
        ntrippassword = cfg.get("ntripcasterpassword_s")
        tlspempath = cfg.get("tlspempath_s")
        ntriprtcmstr = "1002(1),1006(5),1077(1),1087(1),1097(1),1127(1),1230(1)"
        self._socket_thread = Thread(
            target=self._sockserver_thread,
            args=(
                ntripmode,
                host,
                port,
                https,
                tlspempath,
                ntriprtcmstr,
                ntripuser,
                ntrippassword,
                SOCKSERVER_MAX_CLIENTS,
                self.socket_outqueue,
            ),
            daemon=True,
        )
        self._socket_thread.start()
        self.server_status = 0  # 0 = active, no clients

    def sockserver_stop(self):
        """
        Stop socket server thread.
        """

        if self._socket_server is not None:
            self._socket_server.shutdown()
        self.server_status = -1  # -1 = inactive

    def _sockserver_thread(
        self,
        ntripmode: int,
        host: str,
        port: int,
        https: int,
        tlspempath: str,
        ntriprtcmstr: str,
        ntripuser: str,
        ntrippassword: str,
        maxclients: int,
        socketqueue: Queue,
    ):
        """
        THREADED PROCESS
        Socket Server thread.

        :param int ntripmode: 0 = open socket server, 1 = NTRIP server
        :param str host: socket host name (0.0.0.0)
        :param int port: socket port (50010)
        :param int https: https enabled (0)
        :param str tlspempath: path to TLS PEM file ("$HOME/pygnssutils.pem")
        :param str ntriprtcmstr: NTRIP caster RTCM type(rate) sourcetable entry
        :param int maxclients: max num of clients (5)
        :param Queue socketqueue: socket server read queue
        """

        requesthandler = ClientHandlerTLS if https else ClientHandler
        try:
            with SocketServer(
                self,
                ntripmode,
                maxclients,
                socketqueue,
                (host, port),
                requesthandler,
                ntripuser=ntripuser,
                ntrippassword=ntrippassword,
                tlspempath=tlspempath,
                ntriprtcmstr=ntriprtcmstr,
            ) as self._socket_server:
                self._socket_server.serve_forever()
        except OSError as err:
            self.status_label = (f"Error starting socket server {err}", ERRCOL)

    def update_clients(self, clients: int):
        """
        Update number of connected clients in settings panel.
        Called by pygnssutils.socket_server.

        :param int clients: no of connected clients
        """

        self.server_status = clients

    def _shutdown(self):
        """
        Shut down running handlers.
        """

        self.sockserver_stop()
        self.stream_handler.stop()
        self.sqlite_handler.close()
        self.file_handler.close_logfile()
        self.file_handler.close_trackfile()

    def on_exit(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Quit application.
        """

        self._shutdown()
        self.__master.destroy()

    def on_killswitch(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Ctrl-K (kill switch) clicked.
        """

        try:
            self._shutdown()
            for dlg in self.dialog_state.state:
                if self.dialog(dlg) is not None:
                    self.dialog(dlg).destroy()
                    # self.stop_dialog(dlg)
            self.conn_status = DISCONNECTED
            self.rtk_conn_status = DISCONNECTED
        except Exception as err:  # pylint: disable=broad-exception-caught
            self.logger.error(err)
        self.status_label = (KILLSWITCH, ERRCOL)
        self.logger.debug(KILLSWITCH)

    def on_gnss_read(self, event):  # pylint: disable=unused-argument
        """
        EVENT TRIGGERED
        Action on <<gnss_read>> event - data available on GNSS queue.

        :param event event: read event
        """

        try:
            raw_data, parsed_data = self.gnss_inqueue.get(False)
            if raw_data is not None and parsed_data is not None:
                self.process_data(raw_data, parsed_data)
                # if socket server is running, output raw data to socket
                if self.server_status:
                    self.socket_outqueue.put(raw_data)
            self.gnss_inqueue.task_done()
        except Empty:
            pass

    def on_gnss_eof(self, event):  # pylint: disable=unused-argument
        """
        EVENT TRIGGERED
        Action on <<sgnss_eof>> event - end of file.

        :param event event: <<gnss_eof>> event
        """

        self.server_status = -1
        self._refresh_widgets()
        self.conn_status = DISCONNECTED
        self.status_label = (ENDOFFILE, ERRCOL)

    def on_gnss_timeout(self, event):  # pylint: disable=unused-argument
        """
        EVENT TRIGGERED
        Action on <<sgnss_timeout>> event - stream inactivity timeout.

        :param event event: <<gnss_timeout>> event
        """

        self.server_status = -1
        self._refresh_widgets()
        self.conn_status = DISCONNECTED
        self.status_label = (INACTIVE_TIMEOUT, ERRCOL)

    def on_stream_error(self, event):  # pylint: disable=unused-argument
        """
        EVENT TRIGGERED
        Action on "<<gnss_error>>" event - connection streaming error.

        :param event event: <<gnss_error>> event
        """

        self._refresh_widgets()
        self.conn_status = DISCONNECTED

    def on_ntrip_read(self, event):  # pylint: disable=unused-argument
        """
        EVENT TRIGGERED
        Action on <<ntrip_read>> event - data available on NTRIP queue.

        :param event event: read event
        """

        try:
            raw_data, parsed_data = self.ntrip_inqueue.get(False)
            if (
                raw_data is not None
                and parsed_data is not None
                and isinstance(raw_data, bytes)
            ):
                if self._rtk_conn_status == CONNECTED_NTRIP:
                    source = "NTRIP"
                else:
                    source = "OTHER"
                if isinstance(parsed_data, (RTCMMessage, SPARTNMessage)):
                    self.send_to_device(raw_data)
                    self.process_data(raw_data, parsed_data, source + ">>")
                elif isinstance(parsed_data, NMEAMessage):
                    # i.e. NMEA GGA sentence sent to NTRIP server
                    self.process_data(raw_data, parsed_data, source + "<<")
            self.ntrip_inqueue.task_done()
        except Empty:
            pass
        except (SerialException, SerialTimeoutException) as err:
            self.status_label = (f"Error sending to device {err}", ERRCOL)

    def on_spartn_read(self, event):  # pylint: disable=unused-argument
        """
        EVENT TRIGGERED
        Action on <<spartn_read>> event - data available on SPARTN queue.

        :param event event: read event
        """

        try:
            raw_data, parsed_data = self.spartn_inqueue.get(False)
            if raw_data is not None and parsed_data is not None:
                self.send_to_device(raw_data)
                if self._rtk_conn_status == CONNECTED_SPARTNLB:
                    source = "LBAND"
                elif self._rtk_conn_status == CONNECTED_SPARTNIP:
                    source = "MQTT"
                else:
                    source = "OTHER"
                self.process_data(
                    raw_data,
                    parsed_data,
                    source + ">>",
                )
            self.spartn_inqueue.task_done()

        except Empty:
            pass
        except (SerialException, SerialTimeoutException) as err:
            self.status_label = (f"Error sending to device {err}", ERRCOL)

    def update_ntrip_status(self, status: bool, msgt: tuple | NoneType = None):
        """
        Update NTRIP configuration dialog connection status.

        :param bool status: connected to NTRIP server yes/no
        :param tuple | None msgt: tuple of (message, color) or None
        """

        if self.dialog(DLGTNTRIP) is not None:
            self.dialog(DLGTNTRIP).set_controls(status, msgt)

    def get_coordinates(self) -> dict:
        """
        Supply current coordinates and fix data to any widget
        that requests it (mirrors NMEA GGA format).
        Called by pygnssutils.ntrip_client.

        :return: dict of coords and fix data
        :rtype: dict
        """

        try:
            sep = self.gnss_status.hae - self.gnss_status.alt
        except TypeError:
            sep = 0
        return {
            "connection": self._conn_status,
            "lat": self.gnss_status.lat,
            "lon": self.gnss_status.lon,
            "alt": self.gnss_status.alt,  # hmsl
            "hae": self.gnss_status.hae,
            "sep": sep,
            "sip": self.gnss_status.sip,
            "fix": self.gnss_status.fix,
            "hdop": self.gnss_status.hdop,
            "diffage": self.gnss_status.diff_age,
            "diffstation": self.gnss_status.diff_station,
        }

    def process_data(self, raw_data: bytes, parsed_data: object, marker: str = ""):
        """
        THIS IS THE MAIN GNSS DATA PROCESSING LOOP

        Update the various GUI widgets, data & gpx logs and database.

        :param bytes raw_data: raw message data
        :param object parsed data: NMEAMessage, UBXMessage or RTCMMessage
        :param str marker: string prepended to console entries e.g. "NTRIP>>"
        """

        start = process_time_ns()
        # self.logger.debug(f"data received {parsed_data.identity}")
        msgprot = 0
        protfilter = self.protocol_mask
        if isinstance(parsed_data, NMEAMessage):
            msgprot = NMEA_PROTOCOL
        elif isinstance(parsed_data, SBFMessage):
            msgprot = SBF_PROTOCOL
        elif isinstance(parsed_data, QGCMessage):
            msgprot = QGC_PROTOCOL
        elif isinstance(parsed_data, UBXMessage):
            msgprot = UBX_PROTOCOL
        elif isinstance(parsed_data, RTCMMessage):
            msgprot = RTCM3_PROTOCOL
        elif isinstance(parsed_data, SPARTNMessage):
            msgprot = SPARTN_PROTOCOL
        elif isinstance(parsed_data, MQTTMessage):
            msgprot = MQTT_PROTOCOL
        elif isinstance(parsed_data, str):
            if self.configuration.get("ttyprot_b"):
                msgprot = TTY_PROTOCOL
            else:
                marker = "WARNING>>"

        if msgprot == UBX_PROTOCOL and msgprot & protfilter:
            self.ubx_handler.process_data(raw_data, parsed_data)
        elif msgprot == SBF_PROTOCOL and msgprot & protfilter:
            self.sbf_handler.process_data(raw_data, parsed_data)
        elif msgprot == QGC_PROTOCOL and msgprot & protfilter:
            self.qgc_handler.process_data(raw_data, parsed_data)
        elif msgprot == NMEA_PROTOCOL and msgprot & protfilter:
            self.nmea_handler.process_data(raw_data, parsed_data)
        elif msgprot == RTCM3_PROTOCOL and msgprot & protfilter:
            self.rtcm_handler.process_data(raw_data, parsed_data)
        elif msgprot == TTY_PROTOCOL and msgprot & protfilter:
            self.tty_handler.process_data(raw_data, parsed_data)
        elif msgprot == SPARTN_PROTOCOL and msgprot & protfilter:
            pass
        elif msgprot == MQTT_PROTOCOL:
            pass

        # update chart plot if chart is visible
        if self.widget_state.state[WDGCHART][VISIBLE]:
            getattr(self, self.widget_state.state[WDGCHART][FRAME]).update_data(
                parsed_data
            )

        # update consoledata if console is visible and protocol not filtered
        if self.widget_state.state[WDGCONSOLE][VISIBLE] and (
            msgprot in (0, MQTT_PROTOCOL) or msgprot & protfilter
        ):
            self.consoledata.append((raw_data, parsed_data, marker))

        # periodically update widgets if visible
        if datetime.now() > self._last_gui_update + timedelta(
            seconds=self.configuration.get("guiupdateinterval_f")
        ):
            self._refresh_widgets()
            # update database if enabled
            if self.configuration.get("database_b"):
                self.sqlite_handler.load_data()
            self._last_gui_update = datetime.now()

        # update GPX track file if enabled
        if self.configuration.get("recordtrack_b"):
            self.file_handler.update_gpx_track()

        # update log file if enabled
        if self.configuration.get("datalog_b"):
            self.file_handler.write_logfile(raw_data, parsed_data)

        self.update_idletasks()
        self.processtime = process_time_ns() - start

    def send_to_device(self, data: object):
        """
        Send raw data to connected device.

        :param object data: raw GNSS data (NMEA, UBX, TTY, RTCM3, SPARTN)
        """

        self.logger.debug(f"Sending message {data}")
        if self.conn_status in (
            CONNECTED,
            CONNECTED_SOCKET,
            CONNECTED_SIMULATOR,
        ):
            self.gnss_outqueue.put(data)

    def _check_update(self):
        """
        Check for updated version.
        """

        latest = check_latest(TITLE)
        if latest not in (VERSION, "N/A"):
            shortcut = "" if brew_installed() else " CTRL-U to update."
            self.status_label = (
                VERCHECK.format(title=TITLE, version=latest, shortcut=shortcut),
                ERRCOL,
            )
            self.__master.bind_all("<Control-u>", self.do_app_update)
        else:
            self.__master.unbind("<Control-u>")

    def poll_version(self, protocol: int):
        """
        Poll hardware information message for device hardware & firmware version.

        :param int protocol: protocol(s)
        """

        msg = None
        if protocol & UBX_PROTOCOL:
            msg = UBXMessage("MON", "MON-VER", POLL)
        elif protocol & SBF_PROTOCOL:
            msg = b"SSSSSSSSSS\r\nesoc, COM1, ReceiverSetup\r\n"
        elif protocol & NMEA_PROTOCOL:
            msg = NMEAMessage("P", "QTMVERNO", POLL)

        if isinstance(msg, (UBXMessage, NMEAMessage)):
            self.send_to_device(msg.serialize())
            self.status_label = (f"{msg.identity} POLL message sent", INFOCOL)
        elif isinstance(msg, bytes):
            self.send_to_device(msg)
            self.status_label = ("Setup POLL message sent", INFOCOL)

    @property
    def appmaster(self) -> Tk:
        """
        Getter for application master (Tk).

        :return: reference to master Tk instance
        :rtype: Tk
        """

        return self.__master

    @property
    def conn_label(self) -> Label:
        """
        Getter for connection_label.

        :return: status label
        :rtype: Label
        """

        return self.frm_status.lbl_connection

    @conn_label.setter
    def conn_label(self, connection: str | tuple[str, str]):
        """
        Sets connection description in status bar.

        :param str | tuple connection: (connection, color)
        """

        if isinstance(connection, tuple):
            connection, color = connection
        else:
            color = INFOCOL

        # truncate very long connection description
        if len(connection) > 100:
            connection = "..." + connection[-100:]

        if hasattr(self, "frm_status"):
            self.conn_label.after(
                0, self.conn_label.config, {"text": connection, "fg": color}
            )
            self.update_idletasks()

    @property
    def status_label(self) -> Label:
        """
        Getter for status_label.

        :return: status label
        :rtype: Label
        """

        return self.frm_status.lbl_status

    @status_label.setter
    def status_label(self, message: str | tuple[str, str]):
        """
        Sets status message, or defers if frm_status not yet instantiated.

        :param str | tuple message: (message, color)
        """

        def priority(col):
            return STATUSPRIORITY.get(col, 0)

        if isinstance(message, tuple):
            message, color = message
        else:
            color = INFOCOL

        # truncate very long messages
        if len(message) > 200:
            message = "..." + message[-200:]

        if hasattr(self, "frm_status"):
            color = INFOCOL if color == "blue" else color
            self.status_label.after(
                0, self.status_label.config, {"text": message, "fg": color}
            )
            self.update_idletasks()
        else:  # defer message until frm_status is instantiated
            if isinstance(self._deferredmsg, tuple):
                defpty = priority(self._deferredmsg[1])
            else:
                defpty = 0
            if priority(color) > defpty:
                self._deferredmsg = (message, color)

    @property
    def conn_status(self) -> int:
        """
        Getter for connection status.

        :return: connection status e.g. 1 = CONNECTED
        :rtype: int
        """

        return self._conn_status

    @conn_status.setter
    def conn_status(self, status: int):
        """
        Setter for connection status.

        :param int status: connection status e.g. 1 = CONNECTED
        """

        self._conn_status = status
        self.frm_banner.update_conn_status(status)
        self.frm_settings.frm_settings.enable_controls(status)
        if status == DISCONNECTED:
            self.conn_label = (NOTCONN, INFOCOL)
        elif status in (CONNECTED, CONNECTED_SOCKET):
            for name, wdg in self.widget_state.state.items():
                if wdg[VISIBLE]:
                    # enable any GNSS message output required by widget
                    self.widget_enable_messages(name)

    @property
    def server_status(self) -> int:
        """
        Getter for socket server status.

        :return: server status
        :rtype: int
        """

        return self._server_status

    @server_status.setter
    def server_status(self, status: int):
        """
        Setter for socket server status.

        :param int status: server status
            -1 - inactive, 0 = active no clients, >0 = active clients
        """

        self._server_status = status
        self.frm_banner.update_transmit_status(status)
        self.configuration.set("sockserver_b", status >= 0)

    @property
    def rtk_conn_status(self) -> int:
        """
        Getter for RTK connection status.

        :return: connection status
        :rtype: int
        """

        return self._rtk_conn_status

    @rtk_conn_status.setter
    def rtk_conn_status(self, status: int):
        """
        Setter for RTK connection status.

        :param int status: connection status
        """

        self._rtk_conn_status = status
        self.frm_banner.update_rtk_status(status)

    @property
    def recorded_commands(self) -> list:
        """
        Getter for RTK connection status.

        :return: connection status
        :rtype: list
        """

        return self._recorded_commands

    @recorded_commands.setter
    def recorded_commands(self, msg: UBXMessage | NMEAMessage | str | NoneType = None):
        """
        Setter for recorded_commands.

        :param UBXMessage | NMEAMessage | str | NoneType msg: configuration command or None
        """

        if msg is None:
            self._recorded_commands = []
            self.recording_type = 0  # 0 = TTY ONLY
        elif msg == UNDO:
            self._recorded_commands.pop()
            if len(self._recorded_commands) == 0:
                self.recording_type = 0  # 0 = TTY ONLY
        else:
            if isinstance(msg, (UBXMessage, NMEAMessage)):
                self.recording_type = 1  # 0 = TTY ONLY, 1 = UBX/NMEA
            self._recorded_commands.append(msg)

        # update RecordDialog command count, if dialog is visible
        if hasattr(self.dialog(DLGTRECORD), "update_count"):
            self.dialog(DLGTRECORD).update_count()

    @property
    def protocol_mask(self) -> int:
        """
        Getter for protocol mask.

        :return: protocol mask as integer
        :rtype: int
        """

        cfg = self.configuration
        mask = (
            (cfg.get("nmeaprot_b") * NMEA_PROTOCOL)  # 1
            + (cfg.get("ubxprot_b") * UBX_PROTOCOL)  # 2
            + (cfg.get("rtcmprot_b") * RTCM3_PROTOCOL)  # 4
            + (cfg.get("sbfprot_b") * SBF_PROTOCOL)  # 8
            + (cfg.get("qgcprot_b") * QGC_PROTOCOL)  # 16
            + (cfg.get("spartnprot_b") * SPARTN_PROTOCOL)  # 32
            + (cfg.get("mqttprot_b") * MQTT_PROTOCOL)  # 64
            + (cfg.get("ttyprot_b") * TTY_PROTOCOL)  # 128
        )
        return mask

    @property
    def db_enabled(self) -> int | str:
        """
        Getter for database enabled status.

        :return: database enabled status or err code
        :rtype: int | str
        """

        return self._db_enabled

    def do_app_update(self, *args, **kwargs) -> int:
        """
        Update outdated application packages to latest versions.

        NB: Some platforms (e.g. Homebrew-installed Python environments)
        may block Python subprocess calls ('run') on security grounds.

        :return: return code 0 = error, 1 = OK
        :rtype: int
        """

        if brew_installed():
            self.status_label = (BREWUPDATE, INFOCOL)
            return 0

        self.status_label = (UPDATEINPROG, INFOCOL)
        updates = [
            nam for (nam, current, latest) in check_for_updates() if latest != current
        ]
        if len(updates) < 1:
            return 1

        pth = path.dirname(path.abspath(getfile(currentframe())))
        if "pipx" in pth:  # installed into venv using pipx
            cmd = [
                "pipx",
                "upgrade",
                "pygpsclient",
            ]
        else:  # installed using pip
            cmd = [
                executable,  # i.e. python3 or python
                "-m",
                "pip",
                "install",
                "--upgrade",
            ]
            for name in updates:
                cmd.append(name)

        result = None
        try:
            self.logger.debug(f"{executable=} {pth=} {cmd=}")
            result = run(cmd, check=True, capture_output=True)
            self.status_label = (UPDATERESTART, OKCOL)
            self.logger.debug(result.stdout)
            return 1
        except CalledProcessError as err:
            self.status_label = (UPDATEERR.format(err=err), ERRCOL)
            self.logger.error(result.stdout)
            return 0
