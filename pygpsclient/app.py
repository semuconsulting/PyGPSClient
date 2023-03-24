"""
PyGPSClient - Main tkinter application class.

Hosts the various GUI widgets and update routines.
Holds a GNSSStatus object containing the latest
GNSS receiver readings.

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
    GPX_TRACK_INTERVAL,
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
)
from pygpsclient._version import __version__ as VERSION
from pygpsclient.helpers import check_latest
from pygpsclient.strings import (
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


class App(Frame):  # pylint: disable=too-many-ancestors
    """
    Main PyGPSClient GUI Application Class.
    """

    def __init__(self, master, *args, **kwargs):
        """
        Set up main application and add frames

        :param tkinter.Tk master: reference to Tk root
        :param args: optional args
        :param kwargs: optional kwargs
        """

        self.__master = master

        # user-defined serial port can be passed as environment variable
        # or command line keyword argument
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
        self._last_track_update = datetime.now()

        # dict containing widget grid positions
        self._widget_grid = {}

        # Instantiate protocol handler classes
        self._gnss_inqueue = Queue()  # messages from GNSS receiver
        self._gnss_outqueue = Queue()  # messages to GNSS receiver
        self._ntrip_inqueue = Queue()  # messages from NTRIP source
        self._spartn_inqueue = Queue()  # messages from SPARTN correction rcvr
        self._spartn_outqueue = Queue()  # messages to SPARTN correction rcvr
        self._socket_inqueue = Queue()  # message from socket
        self._socket_outqueue = Queue()  # message to socket
        self.file_handler = FileHandler(self)
        self.stream_handler = StreamHandler(self)
        self.spartn_stream_handler = StreamHandler(self)
        self.nmea_handler = NMEAHandler(self)
        self.ubx_handler = UBXHandler(self)
        self.rtcm_handler = RTCM3Handler(self)
        self.ntrip_handler = GNSSNTRIPClient(self, verbosity=0)
        self.spartn_handler = GNSSMQTTClient(self, verbosity=0)
        self._conn_status = DISCONNECTED
        self._rtk_conn_status = DISCONNECTED
        self.dlg_ubxconfig = None
        self.dlg_ntripconfig = None
        self.dlg_spartnconfig = None
        self.dlg_gpxviewer = None
        self._ubx_config_thread = None
        self._gpxviewer_thread = None
        self._ntrip_config_thread = None
        self._spartn_config_thread = None
        self._socket_thread = None
        self._socket_server = None

        # Load MapQuest web map api key if not already defined
        if self._mqapikey == "":
            self._mqapikey = self.file_handler.load_mqapikey()

        # Load console color tags from file
        self.colortags = self.file_handler.load_colortags()

        self._body()
        self._do_layout()
        self._attach_events()

        # Initialise widgets
        self.frm_satview.init_sats()
        self.frm_graphview.init_graph()
        self.frm_spectrumview.init_graph()
        self.frm_scatterview.init_graph()
        self.frm_banner.update_conn_status(DISCONNECTED)

        # Check for more recent version
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
        Arrange widgets in main application frame.
        """

        # Set initial widget visibility and menu index
        self._widget_grid = {
            WDGBANNER: {
                "menu": None,
                "frm": "frm_banner",
                "visible": True,
                "colspan": MAXCOLSPAN + 1,
            },
            WDGCONSOLE: {
                "menu": 2,
                "frm": "frm_console",
                "colspan": MAXCOLSPAN,
                "visible": True,
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
            WDGSTATUS: {
                "menu": 1,
                "frm": "frm_status",
                "visible": True,
                "sticky": (W, E),
                "colspan": MAXCOLSPAN + 1,
            },
            WDGSETTINGS: {
                "menu": 0,
                "frm": "frm_settings",
                "visible": True,
                "rowspan": 2,
                "sticky": (N, W, E),
            },
        }

        self._grid_widgets()

        # NB: these column and row weights define the grid's
        # 'pack by size' behaviour
        for col in range(MAXCOLSPAN):
            self.__master.grid_columnconfigure(col, weight=1)
        for row in range(1, MAXROWSPAN):
            self.__master.grid_rowconfigure(row, weight=1)

        if self.frm_settings.serial_settings.status == NOPORTS:
            self.set_status(INTROTXTNOPORTS, "red")

    def _grid_widgets(self):
        """
        Arrange widgets in grid.
        """

        col = row = 0
        for nam in self._widget_grid:
            if nam == WDGSETTINGS:  # always on top right
                col = MAXCOLSPAN
                row = 1
            if nam == WDGSTATUS:  # always on bottom left
                col = 0
                row = MAXROWSPAN
            col, row = self._grid_widget(nam, col, row)

    def _grid_widget(self, nam: str, col: int, row: int) -> tuple:
        """
        Arrange individual widget and update show/hide menu label.

        :param str nam: name of widget
        :param int col: column
        :param int row: row
        :return: next (col, row)
        :rtype: tuple
        """

        wdg = self._widget_grid[nam]
        if wdg["visible"]:
            colspan = wdg.get("colspan", 1)
            rowspan = wdg.get("rowspan", 1)
            if col >= MAXCOLSPAN and nam != WDGSETTINGS:
                col = 0
                row += rowspan
            getattr(self, wdg["frm"]).grid(
                column=col,
                row=row,
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

        if wdg["menu"] is not None:
            self.menu.view_menu.entryconfig(wdg["menu"], label=f"{lbl} {nam}")

        if nam == WDGSPECTRUM:
            self.frm_spectrumview.enable_MONSPAN(wdg["visible"])

        return col, row

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
            wdg["visible"] = nam not in (WDGSPECTRUM, WDGSCATTER)
        self._grid_widgets()

    def set_connection(self, message, color="blue"):
        """
        Sets connection description in status bar.

        :param str message: message to be displayed in connection label
        :param str color: rgb color string

        """

        self.frm_status.set_connection(message, color)

    def set_status(self, message, color="black"):
        """
        Sets text of status bar.

        :param str message: message to be displayed in status label
        :param str color: rgb color string

        """

        self.frm_status.set_status(message, color)

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

        port = self.frm_settings.server_port
        ntripmode = self.frm_settings.server_mode
        self._socket_thread = Thread(
            target=self._sockserver_thread,
            args=(
                ntripmode,
                SOCKSERVER_HOST,
                port,
                SOCKSERVER_MAX_CLIENTS,
                self._socket_outqueue,
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
            self.set_status(f"Error starting socket server {err}", "red")

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
            raw_data, parsed_data = self._gnss_inqueue.get(False)
            if raw_data is not None and parsed_data is not None:
                self.process_data(raw_data, parsed_data)
            self._gnss_inqueue.task_done()
        except Empty:
            pass

    def on_ntrip_read(self, event):  # pylint: disable=unused-argument
        """
        EVENT TRIGGERED
        Action on <<ntrip_read>> event - read data from NTRIP queue.
        If it's RTCM3 data, send to connected receiver and display on console.
        If it's NMEA, just display on console.

        :param event event: read event
        """

        try:
            raw_data, parsed_data = self._ntrip_inqueue.get(False)
            if raw_data is not None and parsed_data is not None:
                if protocol(raw_data) == RTCM3_PROTOCOL:
                    if self.conn_status == CONNECTED:
                        self._gnss_outqueue.put(raw_data)
                    self.process_data(raw_data, parsed_data, "NTRIP>>")
                else:  # e.g. NMEA GGA sentence sent to NTRIP server
                    self.process_data(raw_data, parsed_data, "NTRIP<<")
            self._ntrip_inqueue.task_done()
        except Empty:
            pass
        except (SerialException, SerialTimeoutException) as err:
            self.set_status(f"Error sending to device {err}", "red")

    def on_spartn_read(self, event):  # pylint: disable=unused-argument
        """
        EVENT TRIGGERED
        Action on <<spartn_read>> event - read data from SPARTN queue.
        If it's RXM-PMP data, send to connected receiver and display on console
        with a "SPARTN>>" marker. Anything else, just display on console with a
        "SPARTN>>" marker.

        :param event event: read event
        """

        try:
            raw_data, parsed_data = self._spartn_inqueue.get(False)
            if raw_data is not None and parsed_data is not None:
                if self.conn_status == CONNECTED:
                    self._gnss_outqueue.put(raw_data)
                self.process_data(raw_data, parsed_data, "SPARTN>>")
            self._spartn_inqueue.task_done()

        except Empty:
            pass
        except (SerialException, SerialTimeoutException) as err:
            self.set_status(f"Error sending to device {err}", "red")

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
        Update the various GUI widgets, GPX track and log file
        with the latest data. Parsed data tagged with a 'marker' is
        written to the console for information but not processed further.

        :param bytes raw_data: raw message data
        :param object parsed data: NMEAMessage, UBXMessage or RTCMMessage
        :param str marker: string prepended to console entries e.g. "NTRIP>>"
        """

        protfilter = self.frm_settings.protocol
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
        if self.frm_settings.record_track:
            self._update_gpx_track()

        # update log file if enabled
        if self.frm_settings.datalogging:
            self.file_handler.write_logfile(raw_data, parsed_data)

    def _update_gpx_track(self):
        """
        Update GPX track with latest valid position readings.
        """

        # must have valid coords
        if self.gnss_status.lat == "" or self.gnss_status.lon == "":
            return

        if datetime.now() > self._last_track_update + timedelta(
            seconds=GPX_TRACK_INTERVAL
        ):
            today = datetime.now()
            gpstime = self.gnss_status.utc
            trktime = datetime(
                today.year,
                today.month,
                today.day,
                gpstime.hour,
                gpstime.minute,
                gpstime.second,
                gpstime.microsecond,
            )
            time = f"{trktime.isoformat()}Z"
            if self.gnss_status.diff_corr:
                fix = "dgps"
            elif self.gnss_status.fix == "3D":
                fix = "3d"
            elif self.gnss_status.fix == "2D":
                fix = "2d"
            else:
                fix = "none"
            diff_age = self.gnss_status.diff_age
            diff_station = self.gnss_status.diff_station
            if diff_age in [None, "", 0] or diff_station in [None, "", 0]:
                self.file_handler.add_trackpoint(
                    self.gnss_status.lat,
                    self.gnss_status.lon,
                    ele=self.gnss_status.alt,
                    time=time,
                    fix=fix,
                    sat=self.gnss_status.sip,
                    pdop=self.gnss_status.pdop,
                )
            else:
                self.file_handler.add_trackpoint(
                    self.gnss_status.lat,
                    self.gnss_status.lon,
                    ele=self.gnss_status.alt,
                    time=time,
                    fix=fix,
                    sat=self.gnss_status.sip,
                    pdop=self.gnss_status.pdop,
                    ageofdgpsdata=diff_age,
                    dgpsid=diff_station,
                )

            self._last_track_update = datetime.now()

    def _check_update(self):
        """
        Check for updated version.
        """

        latest = check_latest("PyGPSClient")
        if latest not in (VERSION, "N/A"):
            self.set_status(VERCHECK.format(latest), "red")

    @property
    def appmaster(self) -> object:
        """
        Getter for application master (Tk).
        """

        return self.__master

    @property
    def user_port(self) -> str:
        """
        Getter for user-defined port passed as optional
        command line keyword argument.
        """

        return self._user_port

    @property
    def spartn_user_port(self) -> str:
        """
        Getter for user-defined spartn port passed as optional
        command line keyword argument.
        """

        return self._spartn_user_port

    @property
    def mqapikey(self) -> str:
        """
        Getter for MapQuerst API Key.
        """

        return self._mqapikey

    @property
    def mqttclientid(self) -> str:
        """
        Getter for MQTT Client ID.
        """

        return self._mqttclientid

    @property
    def gnss_inqueue(self) -> Queue:
        """
        Getter for GNSS message input queue.
        """

        return self._gnss_inqueue

    @property
    def gnss_outqueue(self) -> Queue:
        """
        Getter for GNSS message output queue.
        """

        return self._gnss_outqueue

    @property
    def socket_inqueue(self) -> Queue:
        """
        Getter for socket input queue.
        """

        return self._socket_inqueue

    @property
    def socket_outqueue(self) -> Queue:
        """
        Getter for socket output queue.
        """

        return self._socket_outqueue

    @property
    def ntrip_inqueue(self) -> Queue:
        """
        Getter for NTRIP input queue.
        """

        return self._ntrip_inqueue

    @property
    def spartn_inqueue(self) -> Queue:
        """
        Getter for SPARTN input queue.
        """

        return self._spartn_inqueue

    @property
    def spartn_outqueue(self) -> Queue:
        """
        Getter for SPARTN output queue.
        """

        return self._spartn_outqueue

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
            self.set_connection(NOTCONN, "red")
            self.set_status("", "blue")

    @property
    def rtk_conn_status(self) -> int:
        """
        Getter for SPARTN connection status.

        :param int status: connection status
        CONNECTED_NTRIP / CONNECTED_SPARTNLB / CONNECTED_SPARTNIP
        """

        return self._rtk_conn_status

    @rtk_conn_status.setter
    def rtk_conn_status(self, status: int):
        """
        Setter for SPARTN connection status
        CONNECTED_NTRIP / CONNECTED_SPARTNLB / CONNECTED_SPARTNIP

        :param int status: connection status
        """

        self._rtk_conn_status = status
        self.frm_banner.update_rtk_status(status)
