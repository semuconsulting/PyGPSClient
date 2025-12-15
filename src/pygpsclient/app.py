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

# pylint: disable=too-many-ancestors, no-member, too-many-lines

import logging
from datetime import datetime, timedelta
from inspect import currentframe, getfile
from os import path
from queue import Empty, Queue
from subprocess import CalledProcessError, run
from sys import executable
from threading import Thread
from time import process_time_ns, time
from tkinter import NSEW, Frame, Label, PhotoImage, Tk, Toplevel, font
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
from pygpsclient.configuration import Configuration
from pygpsclient.dialog_state import DialogState
from pygpsclient.file_handler import FileHandler
from pygpsclient.globals import (
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
from pygpsclient.helpers import check_latest
from pygpsclient.menu_bar import MenuBar
from pygpsclient.nmea_handler import NMEAHandler
from pygpsclient.qgc_handler import QGCHandler
from pygpsclient.rtcm3_handler import RTCM3Handler
from pygpsclient.sbf_handler import SBFHandler
from pygpsclient.sqlite_handler import DBINMEM, SQLOK, SqliteHandler
from pygpsclient.stream_handler import StreamHandler
from pygpsclient.strings import (
    CONFIGERR,
    DLG,
    DLGSTOPRTK,
    DLGTNTRIP,
    DLGTRECORD,
    ENDOFFILE,
    INACTIVE_TIMEOUT,
    INTROTXTNOPORTS,
    KILLSWITCH,
    LOADCONFIGBAD,
    LOADCONFIGOK,
    NOTCONN,
    NOWDGSWARN,
    SAVECONFIGBAD,
    SAVECONFIGOK,
    TITLE,
    VERCHECK,
)
from pygpsclient.tty_handler import TTYHandler
from pygpsclient.ubx_handler import UBXHandler
from pygpsclient.widget_state import (
    COL,
    COLSPAN,
    DEFAULT,
    HIDE,
    MAXCOLS,
    MAXCOLSPAN,
    MAXROWSPAN,
    MENU,
    ROW,
    ROWSPAN,
    SHOW,
    STICKY,
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

        # Init Frame class
        Frame.__init__(self, self.__master)

        self.__master.protocol("WM_DELETE_WINDOW", self.on_exit)
        self.__master.title(TITLE)
        self.__master.iconphoto(True, PhotoImage(file=ICON_APP128))

        self._deferredmsg = None
        self.gnss_inqueue = Queue()  # messages from GNSS receiver
        self.gnss_outqueue = Queue()  # messages to GNSS receiver
        self.ntrip_inqueue = Queue()  # messages from NTRIP source
        self.spartn_inqueue = Queue()  # messages from SPARTN correction rcvr
        self.spartn_outqueue = Queue()  # messages to SPARTN correction rcvr
        self.socket_inqueue = Queue()  # message from socket
        self.socket_outqueue = Queue()  # message to socket
        self.widget_state = WidgetState()  # widget state
        self.dialog_state = DialogState()  # dialog state
        self.configuration = Configuration(self)  # configuration state
        self.gnss_status = GNSSStatus()  # holds latest GNSS readings
        self.file_handler = FileHandler(self)
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

        # load config from json file
        configfile = kwargs.pop("config", CONFIGFILE)
        _, configerr = self.configuration.loadfile(configfile)
        # load config from CLI arguments & env variables
        self.configuration.loadcli(**kwargs)
        if configerr == "":
            self.update_widgets()  # set initial widget state
            # warning if all widgets have been disabled in config
            if self._nowidgets:
                self.status_label = (NOWDGSWARN.format(configfile), ERRCOL)

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

        # instantiate widgets
        for value in self.widget_state.state.values():
            frm = getattr(self, value[FRAME])
            if hasattr(frm, "init_frame"):
                frm.update_idletasks()
                frm.init_frame()

        # display initial connection status
        self.frm_banner.update_conn_status(DISCONNECTED)
        if self.frm_settings.frm_serial.status == NOPORTS:
            self.status_label = (INTROTXTNOPORTS, ERRCOL)

        # check for more recent version (if enabled)
        if self.configuration.get("checkforupdate_b") and configerr == "":
            self._check_update()

        # display any deferred messages
        if isinstance(self._deferredmsg, tuple):
            self.status_label = self._deferredmsg
            self._deferredmsg = None

    def _body(self):
        """
        Set up frame and widgets.
        """

        self._set_default_fonts()
        self.menu = MenuBar(self)
        self.__master.config(menu=self.menu)

        # initialise widget state
        for value in self.widget_state.state.values():
            setattr(
                self,
                value[FRAME],
                value[CLASS](self, borderwidth=2, relief="groove"),
            )

    def _do_layout(self):
        """
        Arrange widgets in main application frame, and set
        widget visibility and menu label (show/hide).

        NB: PyGPSClient generally favours 'grid' rather than 'pack'
        layout management throughout:
        - grid weight = 0 means fixed, non-expandable
        - grid weight > 0 means expandable
        """

        col = 0
        row = 1
        maxcol = 0
        maxrow = 0
        men = 0
        for name in self.widget_state.state:
            col, row, maxcol, maxrow, men = self._widget_grid(
                name, col, row, maxcol, maxrow, men
            )

        for col in range(MAXCOLSPAN + 1):
            self.__master.grid_columnconfigure(col, weight=0)
        for row in range(MAXROWSPAN + 2):
            self.__master.grid_rowconfigure(row, weight=0)
        for col in range(maxcol):
            self.__master.grid_columnconfigure(col, weight=5)
        for row in range(1, maxrow + 1):
            self.__master.grid_rowconfigure(row, weight=5)

    def _widget_grid(
        self, name: str, col: int, row: int, maxcol: int, maxrow: int, men: int
    ) -> tuple:
        """
        Arrange widgets and update menu label (show/hide).

        Widgets with explicit COL(umn) settings will be placed in fixed
        positions; widgets with no COL(umn) setting will be arranged
        dynamically (left to right, top to bottom).

        :param str name: name of widget
        :param int col: col
        :param int row: row
        :param int maxcol: max cols
        :param int maxrow: max rows
        :param int men: menu position
        :return: max row & col
        :rtype: tuple
        """

        maxcols = self.configuration.get("maxcolumns_n")  # type: ignore
        wdg = self.widget_state.state[name]
        dynamic = wdg.get(COL, None) is None
        frm = getattr(self, wdg[FRAME])
        if wdg[VISIBLE]:
            self.widget_enable_messages(name)
            fcol = wdg.get(COL, col)
            frow = wdg.get(ROW, row)
            colspan = wdg.get(COLSPAN, 1)
            if colspan == MAXCOLS:
                colspan = maxcols
            rowspan = wdg.get(ROWSPAN, 1)
            if dynamic and fcol + colspan > maxcols:
                fcol = 0
                frow += 1
            frm.grid(
                column=fcol,
                row=frow,
                columnspan=colspan,
                rowspan=rowspan,
                padx=2,
                pady=2,
                sticky=wdg.get(STICKY, NSEW),
            )
            lbl = HIDE
            if dynamic:
                col += colspan
                if col >= maxcols:  # type: ignore
                    col = 0
                    row += rowspan
                maxcol = max(maxcol, fcol + colspan)
                maxrow = max(maxrow, frow)
        else:
            frm.grid_forget()
            lbl = SHOW

        # update menu label (show/hide)
        if wdg.get(MENU, True):
            self.menu.view_menu.entryconfig(men, label=f"{lbl} {name}")
            men += 1

        # force widget to rescale
        # frm.event_generate("<Configure>")

        return col, row, maxcol, maxrow, men

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

    def widget_reset(self):
        """
        Reset widgets to default layout.
        """

        for nam, wdg in self.widget_state.state.items():
            vis = wdg.get(DEFAULT, False)
            wdg[VISIBLE] = vis
            self.configuration.set(nam, vis)
        self._do_layout()

    def reset_gnssstatus(self):
        """
        Reset gnss_status dictionary e.g. after reconnecting.
        """

        self.gnss_status = GNSSStatus()

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
                self.frm_settings,
                self.frm_settings.frm_serial,
                self.frm_settings.frm_socketclient,
                self.frm_settings.frm_socketserver,
            ):
                frm.reset()
            self._do_layout()
            if self._nowidgets:
                self.status_label = (NOWDGSWARN.format(filename), ERRCOL)
            else:
                self.status_label = (LOADCONFIGOK.format(filename), OKCOL)
        elif err == "cancelled":  # user cancelled
            return
        else:  # config error
            self.status_label = (LOADCONFIGBAD.format(filename), ERRCOL)

    def save_config(self):
        """
        Save configuration file menu option.
        """

        err = self.configuration.savefile()
        if err == "":
            self.status_label = (SAVECONFIGOK, OKCOL)
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
        self._socket_thread = Thread(
            target=self._sockserver_thread,
            args=(
                ntripmode,
                host,
                port,
                https,
                ntripuser,
                ntrippassword,
                SOCKSERVER_MAX_CLIENTS,
                self.socket_outqueue,
            ),
            daemon=True,
        )
        self._socket_thread.start()
        self.frm_banner.update_transmit_status(0)

    def sockserver_stop(self):
        """
        Stop socket server thread.
        """

        self.frm_banner.update_transmit_status(-1)
        if self._socket_server is not None:
            self._socket_server.shutdown()

    def _sockserver_thread(
        self,
        ntripmode: int,
        host: str,
        port: int,
        https: int,
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

        self.frm_settings.frm_socketserver.clients = clients

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
            if self.frm_settings.frm_socketserver.socketserving:
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

        self.frm_settings.frm_socketserver.socketserving = (
            False  # turn off socket server
        )
        self._refresh_widgets()
        self.conn_status = DISCONNECTED
        self.status_label = (ENDOFFILE, ERRCOL)

    def on_gnss_timeout(self, event):  # pylint: disable=unused-argument
        """
        EVENT TRIGGERED
        Action on <<sgnss_timeout>> event - stream inactivity timeout.

        :param event event: <<gnss_timeout>> event
        """

        self.frm_settings.frm_socketserver.socketserving = (
            False  # turn off socket server
        )
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
            self.status_label = (f"{VERCHECK} {latest}", ERRCOL)

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
        self.frm_settings.enable_controls(status)
        if status == DISCONNECTED:
            self.conn_label = (NOTCONN, INFOCOL)

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

    def do_app_update(self, updates: list) -> int:
        """
        Update outdated application packages to latest versions.

        NB: Some platforms (e.g. Homebrew-installed Python environments)
        may block Python subprocess calls ('run') on security grounds.

        :param list updates: list of packages to be updated
        :return: return code 0 = error, 1 = OK
        :rtype: int
        """

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
            for pkg in updates:
                cmd.append(pkg)

        result = None
        try:
            self.logger.debug(f"{executable=} {pth=} {cmd=}")
            result = run(cmd, check=True, capture_output=True)
            self.logger.debug(result.stdout)
            return 1
        except CalledProcessError:
            self.logger.error(result.stdout)
            return 0
