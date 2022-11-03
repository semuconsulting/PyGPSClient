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
from pygnssutils import GNSSNTRIPClient
from pygnssutils.socket_server import SocketServer, ClientHandler
from pygpsclient.strings import (
    TITLE,
    MENUHIDESE,
    MENUSHOWSE,
    MENUHIDESB,
    MENUSHOWSB,
    MENUHIDECON,
    MENUSHOWCON,
    MENUHIDEMAP,
    MENUSHOWMAP,
    MENUHIDESATS,
    MENUSHOWSATS,
    INTROTXTNOPORTS,
    NOTCONN,
)
from pygpsclient.gnss_status import GNSSStatus
from pygpsclient.about_dialog import AboutDialog
from pygpsclient.banner_frame import BannerFrame
from pygpsclient.console_frame import ConsoleFrame
from pygpsclient.file_handler import FileHandler
from pygpsclient.globals import (
    ICON_APP,
    CONNECTED,
    DISCONNECTED,
    NOPORTS,
    GUI_UPDATE_INTERVAL,
    GPX_TRACK_INTERVAL,
    SOCKSERVER_MAX_CLIENTS,
    SOCKSERVER_HOST,
)
from pygpsclient.graphview_frame import GraphviewFrame
from pygpsclient.map_frame import MapviewFrame
from pygpsclient.menu_bar import MenuBar
from pygpsclient.stream_handler import StreamHandler
from pygpsclient.settings_frame import SettingsFrame
from pygpsclient.skyview_frame import SkyviewFrame
from pygpsclient.status_frame import StatusFrame
from pygpsclient.ubx_config_dialog import UBXConfigDialog
from pygpsclient.ntrip_client_dialog import NTRIPConfigDialog
from pygpsclient.nmea_handler import NMEAHandler
from pygpsclient.ubx_handler import UBXHandler


class App(Frame):  # pylint: disable=too-many-ancestors
    """
    Main PyGPSClient GUI Application Class
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
        self._user_port = kwargs.pop("port", getenv("PYGPSCLIENT_USERPORT", ""))

        Frame.__init__(self, self.__master, *args, **kwargs)

        self.__master.protocol("WM_DELETE_WINDOW", self.on_exit)
        self.__master.title(TITLE)
        self.__master.iconphoto(True, PhotoImage(file=ICON_APP))
        self.gnss_status = GNSSStatus()  # holds latest GNSS readings
        self._last_gui_update = datetime.now()
        self._last_track_update = datetime.now()

        # Set initial widget visibility
        self._show_settings = True
        self._show_ubxconfig = False
        self._show_status = True
        self._show_console = True
        self._show_map = True
        self._show_sats = True

        # Instantiate protocol handler classes
        self.msgqueue = Queue()
        self.ntripqueue = Queue()
        self.socketqueue = Queue()
        self.file_handler = FileHandler(self)
        self.stream_handler = StreamHandler(self)
        self.nmea_handler = NMEAHandler(self)
        self.ubx_handler = UBXHandler(self)
        self._conn_status = DISCONNECTED
        self.ntrip_handler = GNSSNTRIPClient(self, verbosity=0)
        self.dlg_ubxconfig = None
        self.dlg_ntripconfig = None
        self._ubx_config_thread = None
        self._ntrip_config_thread = None
        self._socket_thread = None
        self._socket_server = None

        # Load web map api key if there is one
        self.api_key = self.file_handler.load_apikey()

        # Load console color tags from file
        self.colortags = self.file_handler.load_colortags()

        self._body()
        self._do_layout()
        self._attach_events()

        # Initialise widgets
        self.frm_satview.init_sats()
        self.frm_graphview.init_graph()
        self.frm_banner.update_conn_status(DISCONNECTED)

    def _body(self):
        """
        Set up frame and widgets
        """

        # these grid weights are what gives the grid its
        # 'pack to window size' behaviour
        self.__master.grid_columnconfigure(0, weight=1)
        self.__master.grid_columnconfigure(1, weight=2)
        self.__master.grid_columnconfigure(2, weight=2)
        self.__master.grid_rowconfigure(0, weight=0)
        self.__master.grid_rowconfigure(1, weight=2)
        self.__master.grid_rowconfigure(2, weight=1)
        self._set_default_fonts()

        self.menu = MenuBar(self)
        self.frm_status = StatusFrame(self, borderwidth=2, relief="groove")
        self.frm_banner = BannerFrame(self, borderwidth=2, relief="groove")
        self.frm_settings = SettingsFrame(self, borderwidth=2, relief="groove")
        self.frm_console = ConsoleFrame(self, borderwidth=2, relief="groove")
        self.frm_mapview = MapviewFrame(self, borderwidth=2, relief="groove")
        self.frm_satview = SkyviewFrame(self, borderwidth=2, relief="groove")
        self.frm_graphview = GraphviewFrame(self, borderwidth=2, relief="groove")

        self.__master.config(menu=self.menu)

    def _do_layout(self):
        """
        Arrange widgets in main application frame
        """

        self.frm_banner.grid(
            column=0, row=0, columnspan=5, padx=2, pady=2, sticky=(N, S, E, W)
        )
        self._grid_console()
        self._grid_sats()
        self._grid_map()
        self._grid_status()
        self._grid_settings()

        if self.frm_settings.serial_settings().status == NOPORTS:
            self.set_status(INTROTXTNOPORTS, "red")

    def _attach_events(self):
        """
        Bind events to main application
        """

        self.__master.bind("<<stream_read>>", self.on_read)
        self.__master.bind("<<gnss_eof>>", self.stream_handler.on_eof)
        self.__master.bind("<<ntrip_read>>", self.on_ntrip_read)
        self.__master.bind_all("<Control-q>", self.on_exit)

    def _set_default_fonts(self):
        """
        Set default fonts for entire application
        """
        # pylint: disable=attribute-defined-outside-init

        self.font_vsm = font.Font(size=8)
        self.font_sm = font.Font(size=10)
        self.font_md = font.Font(size=12)
        self.font_md2 = font.Font(size=14)
        self.font_lg = font.Font(size=18)

    def toggle_settings(self):
        """
        Toggle Settings Frame on or off
        """

        self._show_settings = not self._show_settings
        self._grid_settings()

    def _grid_settings(self):
        """
        Set grid position of Settings Frame
        """

        if self._show_settings:
            self.frm_settings.grid(
                column=4, row=1, rowspan=2, padx=2, pady=2, sticky=(N, W, E)
            )
            self.menu.view_menu.entryconfig(0, label=MENUHIDESE)
        else:
            self.frm_settings.grid_forget()
            self.menu.view_menu.entryconfig(0, label=MENUSHOWSE)

    def toggle_status(self):
        """
        Toggle Status Bar on or off
        """

        self._show_status = not self._show_status
        self._grid_status()

    def _grid_status(self):
        """
        Position Status Bar in grid
        """

        if self._show_status:
            self.frm_status.grid(
                column=0, row=3, columnspan=5, padx=2, pady=2, sticky=(W, E)
            )
            self.menu.view_menu.entryconfig(1, label=MENUHIDESB)
        else:
            self.frm_status.grid_forget()
            self.menu.view_menu.entryconfig(1, label=MENUSHOWSB)

    def toggle_console(self):
        """
        Toggle Console frame on or off
        """

        self._show_console = not self._show_console
        self._grid_console()
        self._grid_sats()
        self._grid_map()

    def _grid_console(self):
        """
        Position Console Frame in grid
        """

        if self._show_console:
            self.frm_console.grid(
                column=0, row=1, columnspan=4, padx=2, pady=2, sticky=(N, S, E, W)
            )
            self.menu.view_menu.entryconfig(2, label=MENUHIDECON)
        else:
            self.frm_console.grid_forget()
            self.menu.view_menu.entryconfig(2, label=MENUSHOWCON)

    def toggle_sats(self):
        """
        Toggle Satview and Graphview frames on or off
        """

        self._show_sats = not self._show_sats
        self._grid_sats()
        self._grid_map()

    def _grid_sats(self):
        """
        Position Satview and Graphview Frames in grid
        """

        if self._show_sats:
            self.frm_satview.grid(column=0, row=2, padx=2, pady=2, sticky=(N, S, E, W))
            self.frm_graphview.grid(
                column=1, row=2, padx=2, pady=2, sticky=(N, S, E, W)
            )
            self.menu.view_menu.entryconfig(4, label=MENUHIDESATS)
        else:
            self.frm_satview.grid_forget()
            self.frm_graphview.grid_forget()
            self.menu.view_menu.entryconfig(4, label=MENUSHOWSATS)

    def toggle_map(self):
        """
        Toggle Map Frame on or off
        """

        self._show_map = not self._show_map
        self._grid_map()

    def _grid_map(self):
        """
        Position Map Frame in grid
        """

        if self._show_map:
            self.frm_mapview.grid(column=2, row=2, padx=2, pady=2, sticky=(N, S, E, W))
            self.menu.view_menu.entryconfig(3, label=MENUHIDEMAP)
        else:
            self.frm_mapview.grid_forget()
            self.menu.view_menu.entryconfig(3, label=MENUSHOWMAP)

    @property
    def user_port(self) -> str:
        """
        Getter for user-defined port passed as optional
        command line keyword argument.
        """

        return self._user_port

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

    def set_connection(self, message, color="blue"):
        """
        Sets connection description in status bar.

        :param str message: message to be displayed in connection label
        :param str color: rgb color string

        """

        self.frm_status.set_connection(message, color)

    def set_status(self, message, color="black"):
        """
        Sets text of status bar

        :param str message: message to be displayed in status label
        :param str color: rgb color string

        """

        self.frm_status.set_status(message, color)

    def about(self):
        """
        Open About dialog
        """

        AboutDialog(self)

    def ubxconfig(self):
        """
        Start UBX Config dialog thread
        """

        if self._ubx_config_thread is None:
            self._ubx_config_thread = Thread(
                target=self._ubxconfig_thread, daemon=False
            )
            self._ubx_config_thread.start()

    def _ubxconfig_thread(self):
        """
        THREADED PROCESS UBX Configuration Dialog
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
        Start NTRIP Config dialog thread
        """

        if self._ntrip_config_thread is None:
            self._ntrip_config_thread = Thread(
                target=self._ntripconfig_thread, daemon=False
            )
            self._ntrip_config_thread.start()

    def _ntripconfig_thread(self):
        """
        THREADED PROCESS NTRIP Configuration Dialog
        """

        self.dlg_ntripconfig = NTRIPConfigDialog(self)

    def stop_ntripconfig_thread(self):
        """
        Stop UBX Configuration dialog thread.
        """

        if self._ntrip_config_thread is not None:
            self._ntrip_config_thread = None
            self.dlg_ntripconfig = None

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
                self.socketqueue,
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

    @property
    def appmaster(self) -> object:
        """
        Getter for application master (Tk).
        """

        return self.__master

    def get_master(self):
        """
        Getter for application master (Tk)

        :return: reference to application master (Tk)
        """

        return self.__master

    def on_exit(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Kill any running processes and quit application
        """

        self.file_handler.close_logfile()
        self.file_handler.close_trackfile()
        self.stop_sockserver_thread()
        self.stream_handler.stop_read_thread()
        self.stop_ubxconfig_thread()
        self.stop_ntripconfig_thread()
        self.__master.destroy()

    def on_read(self, event):  # pylint: disable=unused-argument
        """
        EVENT TRIGGERED
        Action on <<stream_read>> event - read any data on the message queue.

        :param event event: read event
        """

        try:
            raw_data, parsed_data = self.msgqueue.get(False)
            if raw_data is not None and parsed_data is not None:
                self.process_data(raw_data, parsed_data)
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
            raw_data, parsed_data = self.ntripqueue.get(False)
            if raw_data is not None and parsed_data is not None:
                if protocol(raw_data) == RTCM3_PROTOCOL:
                    if self.conn_status == CONNECTED:
                        self.stream_handler.serial_write(raw_data)
                    self.process_data(raw_data, parsed_data, "NTRIP>>")
                else:  # e.g. NMEA GGA sentence sent to NTRIP server
                    self.process_data(raw_data, parsed_data, "NTRIP<<")
        except Empty:
            pass
        except (SerialException, SerialTimeoutException) as err:
            self.set_status(f"Error sending to device {err}", "red")

    def update_ntrip_status(self, status: bool, msg: tuple = None):
        """
        Update NTRIP configuration dialog connection status.

        :param bool status: connected to NTRIP server yes/no
        :param tuple msg: tuple of (message, color)
        """

        if self.dlg_ntripconfig is not None:
            self.dlg_ntripconfig.set_controls(status, msg)

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
        if isinstance(parsed_data, str):
            marker = "WARNING  "

        if msgprot == UBX_PROTOCOL and msgprot & protfilter:
            if marker == "":
                self.ubx_handler.process_data(raw_data, parsed_data)
            else:
                parsed_data = marker + str(parsed_data)
        elif msgprot == NMEA_PROTOCOL and msgprot & protfilter:
            if marker == "":
                self.nmea_handler.process_data(raw_data, parsed_data)
            else:
                parsed_data = marker + str(parsed_data)
        elif msgprot == RTCM3_PROTOCOL and msgprot & protfilter:
            if marker != "":
                parsed_data = marker + str(parsed_data)
        else:
            return

        self.frm_console.update_console(raw_data, parsed_data)

        if datetime.now() > self._last_gui_update + timedelta(
            seconds=GUI_UPDATE_INTERVAL
        ):
            self.frm_banner.update_banner()
            self.frm_mapview.update_map()
            self.frm_satview.update_sats()
            self.frm_graphview.update_graph()
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
