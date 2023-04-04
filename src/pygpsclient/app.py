"""
PyGPSClient - Main tkinter application class.

Created on 12 Sep 2020

:author: semuadmin
:copyright: SEMU Consulting © 2020
:license: BSD 3-Clause
"""

from os import getenv
from threading import Thread
from queue import Queue, Empty
from datetime import datetime, timedelta
from tkinter import Frame, N, S, E, W, PhotoImage, font
from serial import SerialException, SerialTimeoutException
from pyubx2 import (
    protocol,
    NMEA_PROTOCOL,
    UBX_PROTOCOL,
    RTCM3_PROTOCOL,
)
from pygnssutils import GNSSNTRIPClient, GNSSMQTTClient
from pygnssutils.socket_server import SocketServer, ClientHandler
from pygpsclient.globals import (
    ICON_APP,
    CONNECTED,
    DISCONNECTED,
    NOPORTS,
    GUI_UPDATE_INTERVAL,
    SOCKSERVER_MAX_CLIENTS,
    SOCKSERVER_HOST,
    MAXCOLSPAN,
    MAXROWSPAN,
    CHECK_FOR_UPDATES,
    WIDGETU4,
    GNSS_EVENT,
    GNSS_EOF_EVENT,
    NTRIP_EVENT,
    SPARTN_EVENT,
    OKCOL,
    BADCOL,
    CONFIGFILE,
    MAP_UPDATE_INTERVAL,
)
from pygpsclient._version import __version__ as VERSION
from pygpsclient.helpers import check_latest
from pygpsclient.strings import (
    LOADCONFIGOK,
    LOADCONFIGBAD,
    SAVECONFIGOK,
    SAVECONFIGBAD,
    TITLE,
    INTROTXTNOPORTS,
    NOTCONN,
    HIDE,
    SHOW,
    WDGBANNER,
    WDGSETTINGS,
    WDGSTATUS,
    WDGCONSOLE,
    WDGSATS,
    WDGLEVELS,
    WDGMAP,
    WDGSPECTRUM,
    WDGSCATTER,
    VERCHECK,
    CONFIGERR,
)
from pygpsclient.gnss_status import GNSSStatus
from pygpsclient.about_dialog import AboutDialog
from pygpsclient.banner_frame import BannerFrame
from pygpsclient.console_frame import ConsoleFrame
from pygpsclient.file_handler import FileHandler
from pygpsclient.graphview_frame import GraphviewFrame
from pygpsclient.map_frame import MapviewFrame
from pygpsclient.menu_bar import MenuBar
from pygpsclient.stream_handler import StreamHandler
from pygpsclient.settings_frame import SettingsFrame
from pygpsclient.skyview_frame import SkyviewFrame
from pygpsclient.spectrum_frame import SpectrumviewFrame
from pygpsclient.scatter_frame import ScatterViewFrame
from pygpsclient.status_frame import StatusFrame
from pygpsclient.ubx_config_dialog import UBXConfigDialog
from pygpsclient.ntrip_client_dialog import NTRIPConfigDialog
from pygpsclient.spartn_dialog import SPARTNConfigDialog
from pygpsclient.gpx_dialog import GPXViewerDialog
from pygpsclient.nmea_handler import NMEAHandler
from pygpsclient.ubx_handler import UBXHandler
from pygpsclient.rtcm3_handler import RTCM3Handler

SPARTN_PROTOCOL = 9
DEFAULT_WIDGETS = (
    WDGBANNER,
    WDGCONSOLE,
    WDGSATS,
    WDGLEVELS,
    WDGMAP,
    WDGSETTINGS,
    WDGSTATUS,
)


class App(Frame):  # pylint: disable=too-many-ancestors
    """
    Main PyGPSClient GUI Application Class.
    """

    def __init__(self, master, *args, **kwargs):
        """
        Set up main application and add frames.

        :param tkinter.Tk master: reference to Tk root
        :param args: optional args
        :param kwargs: optional kwargs
        """

        self.__master = master

        # user-defined serial port can be passed as environment variable
        # or command line keyword argument
        configfile = kwargs.pop("config", CONFIGFILE)
        self._user_port = kwargs.pop("userport", getenv("PYGPSCLIENT_USERPORT", ""))
        self._spartn_user_port = kwargs.pop(
            "spartnport", getenv("PYGPSCLIENT_SPARTNPORT", "")
        )
        self._mqapikey = kwargs.pop("mqapikey", getenv("MQAPIKEY", ""))
        self._mqttclientid = kwargs.pop("mqttclientid", getenv("MQTTCLIENTID", ""))

        Frame.__init__(self, self.__master, *args, **kwargs)

        self.__master.protocol("WM_DELETE_WINDOW", self.on_exit)
        self.__master.title(TITLE)
        self.__master.iconphoto(True, PhotoImage(file=ICON_APP))
        self.gnss_status = GNSSStatus()  # holds latest GNSS readings
        self._last_gui_update = datetime.now()
        # dict containing widget grid positions
        self._widget_grid = {}

        # Instantiate protocol handler classes
        self.gnss_inqueue = Queue()  # messages from GNSS receiver
        self.gnss_outqueue = Queue()  # messages to GNSS receiver
        self.ntrip_inqueue = Queue()  # messages from NTRIP source
        self.spartn_inqueue = Queue()  # messages from SPARTN correction rcvr
        self.spartn_outqueue = Queue()  # messages to SPARTN correction rcvr
        self.socket_inqueue = Queue()  # message from socket
        self.socket_outqueue = Queue()  # message to socket
        self.file_handler = FileHandler(self)
        self.stream_handler = StreamHandler(self)
        self.spartn_stream_handler = StreamHandler(self)
        self.nmea_handler = NMEAHandler(self)
        self.ubx_handler = UBXHandler(self)
        self.rtcm_handler = RTCM3Handler(self)
        self.ntrip_handler = GNSSNTRIPClient(self, verbosity=0)
        self.spartn_handler = GNSSMQTTClient(self, verbosity=0)
        self.dlg_ubxconfig = None
        self.dlg_ntripconfig = None
        self.dlg_spartnconfig = None
        self.dlg_gpxviewer = None
        self.config = None
        self._conn_status = DISCONNECTED
        self._rtk_conn_status = DISCONNECTED
        self._map_update_interval = MAP_UPDATE_INTERVAL
        self._ubx_config_thread = None
        self._gpxviewer_thread = None
        self._ntrip_config_thread = None
        self._spartn_config_thread = None
        self._socket_thread = None
        self._socket_server = None
        self._colcount = 0
        self._rowcount = 0

        # FOLLOWING FILE LOADS ARE DEPRECATED - USE CONFIG FILE INSTEAD
        # (ANY CONFIG FILE SETTINGS WILL OVERRIDE THESE)
        # Load MapQuest web map api key if not already defined
        if self._mqapikey == "":
            self._mqapikey = self.file_handler.load_mqapikey()
        # Load console color tags from file
        self._colortags = self.file_handler.load_colortags()
        # Load user-defined UBX command presets from file
        self._ubxpresets = self.file_handler.load_ubx_presets()

        # Load configuration from file if it exists
        config_loaded = False
        _, self.config = self.file_handler.load_config(configfile)
        if isinstance(self.config, dict):  # load succeeded
            config_loaded = True
            self.app_config = self.config  # do this before initialising widgets

        self._body()
        self._do_layout()
        self._attach_events()

        # Initialise widgets
        if config_loaded:
            self.widget_config = self.config
            self.frm_settings.config = self.config
            self.frm_status.set_status(f"{LOADCONFIGOK} {configfile}", OKCOL)
        else:
            # self.config is str containing error msg
            if "No such file or directory" in self.config:
                self.frm_status.set_status(f"Configuration file not found {configfile}")
            else:
                self.frm_status.set_status(
                    f"{LOADCONFIGBAD} {configfile} {self.config}"
                )
            self.config = {}
        self.frm_satview.init_sats()
        self.frm_graphview.init_graph()
        self.frm_spectrumview.init_graph()
        self.frm_scatterview.init_graph()
        self.frm_banner.update_conn_status(DISCONNECTED)

        if self.frm_settings.serial_settings.status == NOPORTS:
            self.set_status(INTROTXTNOPORTS, BADCOL)

        # Check for more recent version (if enabled)
        if CHECK_FOR_UPDATES:
            self._check_update()

    def _body(self):
        """
        Set up frame and widgets.
        """

        self._set_default_fonts()

        self.menu = MenuBar(self)
        self.frm_status = StatusFrame(self, borderwidth=2, relief="groove")
        self.frm_banner = BannerFrame(self, borderwidth=2, relief="groove")
        self.frm_settings = SettingsFrame(self, borderwidth=2, relief="groove")
        self.frm_console = ConsoleFrame(self, borderwidth=2, relief="groove")
        self.frm_mapview = MapviewFrame(self, borderwidth=2, relief="groove")
        self.frm_satview = SkyviewFrame(self, borderwidth=2, relief="groove")
        self.frm_graphview = GraphviewFrame(self, borderwidth=2, relief="groove")
        self.frm_spectrumview = SpectrumviewFrame(self, borderwidth=2, relief="groove")
        self.frm_scatterview = ScatterViewFrame(self, borderwidth=2, relief="groove")

        self.__master.config(menu=self.menu)

    def _do_layout(self):
        """
        Arrange widgets in main application frame, and set
        initial widget visibility and menu label (show/hide).

        Dynamic widgets will be automatically positioned in sequence
        and will expand or collapse to fit available space unless
        otherwise specified in this widget_grid.
        """

        self._widget_grid = {
            # fixed relative position
            WDGBANNER: {
                "menu": None,
                "frm": "frm_banner",
                "visible": True,
            },
            WDGSETTINGS: {
                "menu": 0,
                "frm": "frm_settings",
                "visible": True,
                "sticky": (N, W, E),
            },
            WDGSTATUS: {
                "menu": 1,
                "frm": "frm_status",
                "visible": True,
                "sticky": (W, E),
            },
            # dynamic relative position
            WDGCONSOLE: {
                "menu": 2,
                "frm": "frm_console",
                "visible": True,
                "colspan": MAXCOLSPAN,
            },
            WDGSATS: {
                "menu": 3,
                "frm": "frm_satview",
                "visible": True,
            },
            WDGLEVELS: {
                "menu": 4,
                "frm": "frm_graphview",
                "visible": True,
            },
            WDGMAP: {
                "menu": 5,
                "frm": "frm_mapview",
                "visible": True,
            },
            WDGSPECTRUM: {
                "menu": 6,
                "frm": "frm_spectrumview",
                "visible": False,
            },
            WDGSCATTER: {
                "menu": 7,
                "frm": "frm_scatterview",
                "visible": False,
            },
            # add any new widgets here and update View menu
        }

        self._grid_widgets()

    def _grid_widgets(self):
        """
        Arrange widgets in grid, and set column and row 'weights'.
        These govern whether a widget will expand or collapse
        in either direction to fill the available space.
        """

        col = mcol = 0
        row = mrow = 1
        for i, nam in enumerate(self._widget_grid):
            if i > 2:  # only position dynamic widgets
                col, row = self._grid_widget(nam, col, row)
            mcol = max(col, mcol)
            mrow = max(row, mrow)

        for col in range(MAXCOLSPAN + 1):
            self.__master.grid_columnconfigure(col, weight=0 if col > mcol - 1 else 1)
        for row in range(1, MAXROWSPAN + 2):
            self.__master.grid_rowconfigure(row, weight=0 if row > mrow else 1)

        self._grid_widget(WDGSETTINGS, mcol, 1, 1, mrow)  # always on top
        self._grid_widget(WDGBANNER, 0, 0, mcol + 1, 1)  # always on right
        self._grid_widget(WDGSTATUS, 0, mrow + 1, mcol + 1, 1)  # always on bottom

    def _grid_widget(
        self, nam: str, col: int, row: int, colspan: int = 1, rowspan: int = 1
    ) -> tuple:
        """
        Arrange individual widget and update menu label (show/hide).

        :param str nam: name of widget
        :param int col: column
        :param int row: row
        :param int colspan: optional columnspan
        :param int rowspan: optional rowspan
        :return: next available (col, row)
        :rtype: tuple
        """

        wdg = self._widget_grid[nam]
        if wdg["visible"]:
            colspan = wdg.get("colspan", colspan)
            rowspan = wdg.get("rowspan", rowspan)
            if col >= MAXCOLSPAN and nam != WDGSETTINGS:
                col = 0
                row += rowspan
            # keep track of cumulative cols & rows
            ccol = wdg.get("col", col)
            crow = wdg.get("row", row)
            getattr(self, wdg["frm"]).grid(
                column=ccol,
                row=crow,
                columnspan=colspan,
                rowspan=rowspan,
                padx=2,
                pady=2,
                sticky=wdg.get("sticky", (N, S, W, E)),
            )
            col += colspan
            lbl = HIDE
        else:
            getattr(self, wdg["frm"]).grid_forget()
            lbl = SHOW

        # update menu label (show/hide)
        if wdg["menu"] is not None:
            self.menu.view_menu.entryconfig(wdg["menu"], label=f"{lbl} {nam}")

        if nam == WDGSPECTRUM:
            # enable MON-SPAN messages if spectrum widget is visible
            self.frm_spectrumview.enable_MONSPAN(wdg["visible"])

        # force widget to rescale
        getattr(self, wdg["frm"]).event_generate("<Configure>")
        return col, row

    def toggle_widget(self, widget: str):
        """
        Toggle widget visibility.

        :param str widget: widget name
        """

        self._widget_grid[widget]["visible"] = not self._widget_grid[widget]["visible"]
        self._grid_widgets()

    def reset_widgets(self):
        """
        Reset widgets to default layout.
        """

        for nam, wdg in self._widget_grid.items():
            wdg["visible"] = nam in DEFAULT_WIDGETS
        self._grid_widgets()

    def _attach_events(self):
        """
        Bind events to main application.
        """

        self.__master.bind(GNSS_EVENT, self.on_gnss_read)
        self.__master.bind(GNSS_EOF_EVENT, self.stream_handler.on_eof)
        self.__master.bind(NTRIP_EVENT, self.on_ntrip_read)
        self.__master.bind(SPARTN_EVENT, self.on_spartn_read)
        self.__master.bind_all("<Control-q>", self.on_exit)

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

    def set_connection(self, message, color="green"):
        """
        Sets connection description in status bar.

        :param str message: message to be displayed in connection label
        :param str color: rgb color string

        """

        self.frm_status.set_connection(message, color=color)

    def set_status(self, message, color="green"):
        """
        Sets text of status bar.

        :param str message: message to be displayed in status label
        :param str color: rgb color string

        """

        self.frm_status.set_status(message, color)

    def load_config(self):
        """
        Load configuration file menu option.
        """

        data = self.file_handler.load_config(None)
        if data is None:
            return
        filename, self.config = data
        if isinstance(self.config, str):  # load failed
            self.set_status(f"{LOADCONFIGBAD} {self.config}", BADCOL)
            self.config = None
        else:
            self.set_status(f"{LOADCONFIGOK} {filename}", OKCOL)
            self.frm_settings.config = self.config
            self.widget_config = self.config
            self.app_config = self.config

    def save_config(self):
        """
        Save configuration file menu option.
        """

        # combine the various config sections into one dict
        self.config = {
            **self.frm_settings.config,
            **self.widget_config,
            **self.app_config,
        }
        rcd = self.file_handler.save_config(self.config, None)
        if rcd is None:
            return
        if isinstance(rcd, str):  # save failed
            self.set_status(f"{SAVECONFIGBAD} {self.config}", BADCOL)
            self.config = None
        else:
            self.set_status(SAVECONFIGOK, OKCOL)

    def on_about(self):
        """
        Open About dialog.
        """

        AboutDialog(self)

    def ubxconfig(self):
        """
        Start UBX Config dialog thread.
        """

        if self._ubx_config_thread is None:
            self._ubx_config_thread = Thread(
                target=self._ubxconfig_thread, daemon=False
            )
            self._ubx_config_thread.start()

    def _ubxconfig_thread(self):
        """
        THREADED PROCESS UBX Configuration Dialog.
        """

        self.dlg_ubxconfig = UBXConfigDialog(self)

    def stop_ubxconfig_thread(self):
        """
        Stop UBX Configuration dialog thread.
        """

        if self._ubx_config_thread is not None:
            self._ubx_config_thread = None
            self.dlg_ubxconfig = None

    def ntripconfig(self):
        """
        Start NTRIP Config dialog thread.
        """

        if self._ntrip_config_thread is None:
            self._ntrip_config_thread = Thread(
                target=self._ntripconfig_thread, daemon=False
            )
            self._ntrip_config_thread.start()

    def _ntripconfig_thread(self):
        """
        THREADED PROCESS NTRIP Configuration Dialog.
        """

        self.dlg_ntripconfig = NTRIPConfigDialog(self)

    def stop_ntripconfig_thread(self):
        """
        Stop NTRIP Configuration dialog thread.
        """

        if self._ntrip_config_thread is not None:
            self._ntrip_config_thread = None
            self.dlg_ntripconfig = None

    def spartnconfig(self):
        """
        Start SPARTN Config dialog thread.
        """

        if self._spartn_config_thread is None:
            self._spartn_config_thread = Thread(
                target=self._spartnconfig_thread, daemon=False
            )
            self._spartn_config_thread.start()

    def _spartnconfig_thread(self):
        """
        THREADED PROCESS SPARTN Configuration Dialog.
        """

        self.dlg_spartnconfig = SPARTNConfigDialog(self)

    def stop_spartnconfig_thread(self):
        """
        Stop SPARTN Configuration dialog thread.
        """

        if self._spartn_config_thread is not None:
            self._spartn_config_thread = None
            self.dlg_spartnconfig = None

    def gpxviewer(self):
        """
        Start GPX Viewer dialog thread.
        """

        if self._gpxviewer_thread is None:
            self._gpxviewer_thread = Thread(target=self._gpx_thread, daemon=False)
            self._gpxviewer_thread.start()

    def _gpx_thread(self):
        """
        THREADED PROCESS GPX Viewer Dialog.
        """

        width, height = WIDGETU4
        self.dlg_gpxviewer = GPXViewerDialog(self, width=width, height=height)

    def stop_gpxviewer_thread(self):
        """
        Stop GPX Viewer dialog thread.
        """

        if self._gpxviewer_thread is not None:
            self._gpxviewer_thread = None
            self.dlg_gpxviewer = None

    def start_sockserver_thread(self):
        """
        Start socket server thread.
        """

        settings = self.frm_settings.config
        port = int(settings["sockport"])
        ntripmode = settings["sockmode"]
        self._socket_thread = Thread(
            target=self._sockserver_thread,
            args=(
                ntripmode,
                SOCKSERVER_HOST,
                port,
                SOCKSERVER_MAX_CLIENTS,
                self.socket_outqueue,
            ),
            daemon=True,
        )
        self._socket_thread.start()
        self.frm_banner.update_transmit_status(0)

    def stop_sockserver_thread(self):
        """
        Stop socket server thread.
        """

        self.frm_banner.update_transmit_status(-1)
        if self._socket_server is not None:
            self._socket_server.shutdown()

    def _sockserver_thread(
        self, ntripmode: int, host: str, port: int, maxclients: int, socketqueue: Queue
    ):
        """
        THREADED
        Socket Server thread.

        :param int ntripmode: 0 = open socket server, 1 = NTRIP server
        :param str host: socket host name (0.0.0.0)
        :param int port: socket port (50010)
        :param int maxclients: max num of clients (5)
        :param Queue socketqueue: socket server read queue
        """

        try:
            with SocketServer(
                self, ntripmode, maxclients, socketqueue, (host, port), ClientHandler
            ) as self._socket_server:
                self._socket_server.serve_forever()
        except OSError as err:
            self.set_status(f"Error starting socket server {err}", BADCOL)

    def update_clients(self, clients: int):
        """
        Update number of connected clients in settings panel.

        :param int clients: no of connected clients
        """

        self.frm_settings.clients = clients

    def on_exit(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Kill any running processes and quit application.
        """

        self.file_handler.close_logfile()
        self.file_handler.close_trackfile()
        self.stop_sockserver_thread()
        self.stream_handler.stop_read_thread()
        self.stop_ubxconfig_thread()
        self.stop_ntripconfig_thread()
        self.__master.destroy()

    def on_gnss_read(self, event):  # pylint: disable=unused-argument
        """
        EVENT TRIGGERED
        Action on <<gnss_read>> event - read any data on the message queue.

        :param event event: read event
        """

        try:
            raw_data, parsed_data = self.gnss_inqueue.get(False)
            if raw_data is not None and parsed_data is not None:
                self.process_data(raw_data, parsed_data)
            self.gnss_inqueue.task_done()
        except Empty:
            pass

    def on_ntrip_read(self, event):  # pylint: disable=unused-argument
        """
        EVENT TRIGGERED
        Action on <<ntrip_read>> event - read data from NTRIP queue.

        :param event event: read event
        """

        try:
            raw_data, parsed_data = self.ntrip_inqueue.get(False)
            if raw_data is not None and parsed_data is not None:
                if protocol(raw_data) == RTCM3_PROTOCOL:
                    if self.conn_status == CONNECTED:
                        self.gnss_outqueue.put(raw_data)
                    self.process_data(raw_data, parsed_data, "NTRIP>>")
                else:  # e.g. NMEA GGA sentence sent to NTRIP server
                    self.process_data(raw_data, parsed_data, "NTRIP<<")
            self.ntrip_inqueue.task_done()
        except Empty:
            pass
        except (SerialException, SerialTimeoutException) as err:
            self.set_status(f"Error sending to device {err}", BADCOL)

    def on_spartn_read(self, event):  # pylint: disable=unused-argument
        """
        EVENT TRIGGERED
        Action on <<spartn_read>> event - read data from SPARTN queue.

        :param event event: read event
        """

        try:
            raw_data, parsed_data = self.spartn_inqueue.get(False)
            if raw_data is not None and parsed_data is not None:
                if self.conn_status == CONNECTED:
                    self.gnss_outqueue.put(raw_data)
                self.process_data(raw_data, parsed_data, "SPARTN>>")
            self.spartn_inqueue.task_done()

        except Empty:
            pass
        except (SerialException, SerialTimeoutException) as err:
            self.set_status(f"Error sending to device {err}", BADCOL)

    def update_ntrip_status(self, status: bool, msgt: tuple = None):
        """
        Update NTRIP configuration dialog connection status.

        :param bool status: connected to NTRIP server yes/no
        :param tuple msgt: tuple of (message, color)
        """

        if self.dlg_ntripconfig is not None:
            self.dlg_ntripconfig.set_controls(status, msgt)

    def update_spartn_status(self, status: bool, msgt: tuple = None):
        """
        Update SPARTN configuration dialog connection status.

        :param bool status: connected to SPARTN server (NONE, IP, LBAND)
        :param tuple msgt: tuple of (message, color)
        """

        if self.dlg_spartnconfig is not None:
            self.dlg_spartnconfig.set_controls(status, msgt)

    def get_coordinates(self) -> tuple:
        """
        Get current coordinates.

        :return: tuple (conn_status, lat, lon, alt, sep)
        :rtype: tuple
        """

        return (
            self._conn_status,
            self.gnss_status.lat,
            self.gnss_status.lon,
            self.gnss_status.alt,
            self.gnss_status.sep,
        )

    def process_data(self, raw_data: bytes, parsed_data: object, marker: str = ""):
        """
        Update the various GUI widgets, GPX track and log file.

        :param bytes raw_data: raw message data
        :param object parsed data: NMEAMessage, UBXMessage or RTCMMessage
        :param str marker: string prepended to console entries e.g. "NTRIP>>"
        """

        settings = self.frm_settings.config

        protfilter = settings["protocol"]
        msgprot = protocol(raw_data)
        if isinstance(parsed_data, str):  # error message rather than parsed data
            marker = "WARNING  "
            msgprot = 0

        if msgprot == UBX_PROTOCOL and msgprot & protfilter:
            self.ubx_handler.process_data(raw_data, parsed_data)
        elif msgprot == NMEA_PROTOCOL and msgprot & protfilter:
            self.nmea_handler.process_data(raw_data, parsed_data)
        elif msgprot == RTCM3_PROTOCOL and msgprot & protfilter:
            self.rtcm_handler.process_data(raw_data, parsed_data)

        # update console if visible
        if self._widget_grid["Console"]["visible"]:
            if msgprot == 0 or msgprot & protfilter:
                self.frm_console.update_console(raw_data, parsed_data, marker)

        # periodically update widgets if visible
        if datetime.now() > self._last_gui_update + timedelta(
            seconds=GUI_UPDATE_INTERVAL
        ):
            self.frm_banner.update_frame()
            for _, widget in self._widget_grid.items():
                frm = getattr(self, widget["frm"])
                if hasattr(frm, "update_frame") and widget["visible"]:
                    frm.update_frame()
            self._last_gui_update = datetime.now()

        # update GPX track file if enabled
        if settings["recordtrack"]:
            self.file_handler.update_gpx_track()

        # update log file if enabled
        if settings["datalog"]:
            self.file_handler.write_logfile(raw_data, parsed_data)

    def _check_update(self):
        """
        Check for updated version.
        """

        latest = check_latest("PyGPSClient")
        if latest not in (VERSION, "N/A"):
            self.set_status(VERCHECK.format(latest), BADCOL)

    @property
    def app_config(self) -> dict:
        """
        Getter for app config.

        This contains user-defined ports, various API keys
        and colortagging values.
        """

        config = {
            "mapupdateinterval": self._map_update_interval,
            "userport": self._user_port,
            "spartnport": self._spartn_user_port,
            "mqapikey": self._mqapikey,
            "mqttclientid": self._mqttclientid,
            "colortags": self._colortags,
            "ubxpresets": self._ubxpresets,
        }
        return config

    @app_config.setter
    def app_config(self, config):
        """
        Setter for app config.

        :param dict config: configuration as dict
        """

        self._map_update_interval = config.get("mapupdateinterval", MAP_UPDATE_INTERVAL)
        self._user_port = config.get("userport", self._user_port)
        self._spartn_user_port = config.get("spartnport", self._spartn_user_port)
        self._mqapikey = config.get("mqapikey", self._mqapikey)
        self._mqttclientid = config.get("mqttclientid", self._mqttclientid)
        self._colortags = config.get("colortags", self._colortags)
        self._ubxpresets = config.get("ubxpresets", self._ubxpresets)

    @property
    def widget_config(self) -> dict:
        """
        Getter for widget configuration.

        :return: widget configuration as dict
        :rtype: dict
        """

        return {key: vals["visible"] for key, vals in self._widget_grid.items()}

    @widget_config.setter
    def widget_config(self, config):
        """
        Setter for widget config.

        This contains the visibility of the various widgets.

        :param dict config: configuration as dict
        """

        try:
            for key, vals in self._widget_grid.items():
                vals["visible"] = config[key]
        except KeyError as err:
            self.set_status(f"{CONFIGERR} - {err}", BADCOL)

        self._grid_widgets()

    @property
    def appmaster(self) -> object:
        """
        Getter for application master (Tk).
        """

        return self.__master

    @property
    def conn_status(self) -> int:
        """
        Getter for connection status.

        :param int status: connection status e.g. 1 = CONNECTED
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
            self.set_connection(NOTCONN)
            self.set_status("")

    @property
    def rtk_conn_status(self) -> int:
        """
        Getter for SPARTN connection status.

        :param int status: connection status
        """

        return self._rtk_conn_status

    @rtk_conn_status.setter
    def rtk_conn_status(self, status: int):
        """
        Setter for SPARTN connection status.

        :param int status: connection status
        """

        self._rtk_conn_status = status
        self.frm_banner.update_rtk_status(status)
