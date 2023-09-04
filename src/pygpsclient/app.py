"""
app.py

PyGPSClient - Main tkinter application class.

- Loads configuration from json file (if available)
- Instantiates all frames, widgets, and protocol handlers.
- Starts and stops threaded dialog and protocol handler processes.
- Maintains current serial and RTK connection status.
- Reacts to various message events, processes navigation data
  placed on input message queue by serial, socket or file stream reader
  and assigns to appropriate NMEA, UBX or RTCM protocol handler.
- Maintains central dictionary of current key navigation data as
  `gnss_status`, for use by user-selectable widgets.

Created on 12 Sep 2020

:author: semuadmin
:copyright: SEMU Consulting © 2020
:license: BSD 3-Clause
"""
# pylint: disable=too-many-ancestors, no-member

from datetime import datetime, timedelta
from os import getenv, path
from pathlib import Path
from queue import Empty, Queue
from socket import AF_INET, AF_INET6
from threading import Thread
from tkinter import E, Frame, N, PhotoImage, S, TclError, Tk, Toplevel, W, font

from pygnssutils import GNSSMQTTClient, GNSSNTRIPClient, MQTTMessage
from pygnssutils.socket_server import ClientHandler, SocketServer
from pyubx2 import NMEA_PROTOCOL, RTCM3_PROTOCOL, UBX_PROTOCOL, protocol
from serial import SerialException, SerialTimeoutException

from pygpsclient._version import __version__ as VERSION
from pygpsclient.dialog_state import dialog_state
from pygpsclient.file_handler import FileHandler
from pygpsclient.globals import (
    BADCOL,
    CFG,
    CHECK_FOR_UPDATES,
    CLASS,
    CONFIGFILE,
    CONNECTED,
    DISCONNECTED,
    DLG,
    DLGTNTRIP,
    FRAME,
    GNSS_EOF_EVENT,
    GNSS_ERR_EVENT,
    GNSS_EVENT,
    GUI_UPDATE_INTERVAL,
    ICON_APP,
    MQTT_PROTOCOL,
    NOPORTS,
    NTRIP_EVENT,
    OKCOL,
    SOCKSERVER_MAX_CLIENTS,
    SPARTN_EVENT,
    SPARTN_OUTPORT,
    SPARTN_PPSERVER,
    THD,
)
from pygpsclient.gnss_status import GNSSStatus
from pygpsclient.helpers import check_latest
from pygpsclient.menu_bar import MenuBar
from pygpsclient.nmea_handler import NMEAHandler
from pygpsclient.rtcm3_handler import RTCM3Handler
from pygpsclient.stream_handler import StreamHandler
from pygpsclient.strings import (
    CONFIGERR,
    DLGSTOPRTK,
    ENDOFFILE,
    INTROTXTNOPORTS,
    LOADCONFIGBAD,
    LOADCONFIGNONE,
    LOADCONFIGOK,
    NOTCONN,
    NOWDGSWARN,
    SAVECONFIGBAD,
    SAVECONFIGOK,
    TITLE,
    VERCHECK,
)
from pygpsclient.ubx_handler import UBXHandler
from pygpsclient.widget_state import (
    COLSPAN,
    DEFAULT,
    HIDE,
    MAXCOLSPAN,
    MAXROWSPAN,
    MENU,
    ROWSPAN,
    SHOW,
    STICKY,
    VISIBLE,
    WDGBANNER,
    WDGSETTINGS,
    WDGSTATUS,
    widget_state,
)


class App(Frame):
    """
    Main PyGPSClient GUI Application Class.
    """

    def __init__(self, master, *args, **kwargs):  # pylint: disable=too-many-statements
        """
        Set up main application and add frames.

        :param tkinter.Tk master: reference to Tk root
        :param args: optional args
        :param kwargs: optional kwargs
        """

        self.__master = master

        # user-defined serial port can be passed as environment variable
        # or command line keyword argument
        self._configfile = kwargs.pop("config", CONFIGFILE)
        self.user_port = kwargs.pop("userport", getenv("PYGPSCLIENT_USERPORT", ""))
        self.spartn_user_port = kwargs.pop(
            "spartnport", getenv("PYGPSCLIENT_SPARTNPORT", "")
        )
        self.mqapikey = kwargs.pop("mqapikey", getenv("MQAPIKEY", ""))
        self.mqttclientid = kwargs.pop("mqttclientid", getenv("MQTTCLIENTID", ""))
        self.mqttclientregion = kwargs.pop(
            "mqttclientregion", getenv("MQTTCLIENTREGION", "eu")
        )
        self.mqttclientmode = int(
            kwargs.pop("mqttclientmode", getenv("MQTTCLIENTMODE", "0"))
        )
        self.ntripcaster_user = kwargs.pop(
            "ntripuser", getenv("PYGPSCLIENT_USER", "anon")
        )
        self.ntripcaster_password = kwargs.pop(
            "ntrippassword", getenv("PYGPSCLIENT_USER", "password")
        )

        Frame.__init__(self, self.__master, *args, **kwargs)

        self.__master.protocol("WM_DELETE_WINDOW", self.on_exit)
        self.__master.title(TITLE)
        self.__master.iconphoto(True, PhotoImage(file=ICON_APP))
        self.gnss_status = GNSSStatus()  # holds latest GNSS readings
        self._last_gui_update = datetime.now()
        self._nowidgets = True

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
        self.saved_config = {}
        self._conn_status = DISCONNECTED
        self._rtk_conn_status = DISCONNECTED
        self._socket_thread = None
        self._socket_server = None
        self._colcount = 0
        self._rowcount = 0

        # Load configuration from file if it exists
        self._colortags = []
        self._ubxpresets = []
        (_, config, configerr) = self.file_handler.load_config(self._configfile)
        if configerr == "":  # load succeeded
            self.saved_config = config
            # update configs needed to instantiate widgets and protocol handlers
            self.update_widgets()
        else:  # load failed - invalid json or attribute types
            self.saved_config = {}

        # update NTRIP and SPARTN client handlers with initial config
        self.update_NTRIP_handler()
        self.update_SPARTN_handler()

        self._body()
        self._do_layout()
        self._attach_events()

        # display config load status once status frame has been instantiated
        if configerr == "":
            if self._nowidgets:  # if all widgets have been disabled in config
                self.set_status(NOWDGSWARN.format(self._configfile), BADCOL)
            else:
                self.set_status(LOADCONFIGOK.format(self._configfile), OKCOL)
        else:
            if "No such file or directory" in configerr:
                self.set_status(LOADCONFIGNONE.format(self._configfile), BADCOL)
            else:
                self.set_status(
                    LOADCONFIGBAD.format(self._configfile, configerr), BADCOL
                )

        # initialise widgets
        for value in widget_state.values():
            frm = getattr(self, value[FRAME])
            if hasattr(frm, "init_frame"):
                frm.init_frame()

        self.frm_banner.update_conn_status(DISCONNECTED)
        if self.frm_settings.frm_serial.status == NOPORTS:
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
        self.__master.config(menu=self.menu)

        # dynamically instantiate widgets defined in widgets_grid
        for value in widget_state.values():
            _ = setattr(
                self, value[FRAME], value[CLASS](self, borderwidth=2, relief="groove")
            )

    def _do_layout(self):
        """
        Arrange widgets in main application frame, and set
        widget visibility and menu label (show/hide).
        """

        col = mcol = 0
        row = mrow = 1
        for i, nam in enumerate(widget_state):
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

        wdg = widget_state[nam]
        frm = getattr(self, wdg[FRAME])
        if wdg[VISIBLE]:
            colspan = wdg.get(COLSPAN, colspan)
            rowspan = wdg.get(ROWSPAN, rowspan)
            if col >= MAXCOLSPAN and nam != WDGSETTINGS:
                col = 0
                row += rowspan
            # keep track of cumulative cols & rows
            ccol = wdg.get("col", col)
            crow = wdg.get("row", row)
            frm.grid(
                column=ccol,
                row=crow,
                columnspan=colspan,
                rowspan=rowspan,
                padx=2,
                pady=2,
                sticky=wdg.get(STICKY, (N, S, W, E)),
            )
            col += colspan
            lbl = HIDE
        else:
            frm.grid_forget()
            lbl = SHOW

        # update menu label (show/hide)
        if wdg[MENU] is not None:
            self.menu.view_menu.entryconfig(wdg[MENU], label=f"{lbl} {nam}")

        # force widget to rescale
        frm.event_generate("<Configure>")

        # enable or disable any UBX messages required by widget
        if hasattr(frm, "enable_messages"):
            frm.enable_messages(wdg[VISIBLE])

        return col, row

    def toggle_widget(self, widget: str):
        """
        Toggle widget visibility.

        :param str widget: widget name
        """

        widget_state[widget][VISIBLE] = not widget_state[widget][VISIBLE]
        self._do_layout()

    def reset_widgets(self):
        """
        Reset widgets to default layout.
        """

        for _, wdg in widget_state.items():
            wdg[VISIBLE] = wdg[DEFAULT]
        self._do_layout()

    def reset_gnssstatus(self):
        """
        Reset gnss_status dict e.g. after reconnecting.
        """

        self.gnss_status = GNSSStatus()

    def _attach_events(self):
        """
        Bind events to main application.
        """

        self.__master.bind(GNSS_EVENT, self.on_gnss_read)
        self.__master.bind(GNSS_EOF_EVENT, self.on_gnss_eof)
        self.__master.bind(GNSS_ERR_EVENT, self.on_stream_error)
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

    def set_connection(self, message, color=OKCOL):
        """
        Sets connection description in status bar.

        :param str message: message to be displayed in connection label
        :param str color: rgb color string

        """

        self.frm_status.set_connection(message, color=color)

    def set_status(self, message, color=OKCOL):
        """
        Sets text of status bar.

        :param str message: message to be displayed in status label
        :param str color: rgb color string

        """

        self.frm_status.set_status(message, color)

    def set_event(self, evt: str):
        """
        Generate event

        :param str evt: event type string
        """

        self.__master.event_generate(evt)

    def load_config(self):
        """
        Load configuration file menu option.
        """

        # Warn if Streaming, NTRIP or SPARTN clients are running
        if self.conn_status == DISCONNECTED and self.rtk_conn_status == DISCONNECTED:
            self.set_status("", OKCOL)
        else:
            self.set_status(DLGSTOPRTK, BADCOL)
            return

        (filename, config, configerr) = self.file_handler.load_config(None)
        if configerr == "":  # load succeeded
            self.saved_config = config
            self.update_widgets()
            self.update_NTRIP_handler()
            self.update_SPARTN_handler()
            for frm in (
                self.frm_settings,
                self.frm_settings.frm_serial,
                self.frm_settings.frm_socketclient,
                self.frm_settings.frm_socketserver,
            ):
                frm.reset()
            self._do_layout()
            if self._nowidgets:
                self.set_status(NOWDGSWARN.format(filename), BADCOL)
            else:
                self.set_status(LOADCONFIGOK.format(filename), OKCOL)
        elif configerr == "cancelled":  # user cancelled
            return
        else:  # config error
            self.set_status(LOADCONFIGBAD.format(filename), BADCOL)

    def save_config(self):
        """
        Save configuration file menu option.

        Configuration is held in two places:
        - app.config - widget visibility and CLI parameters
        - frm_settings.config - current frame and protocol handler config
        """

        self.saved_config = {
            **self.widget_config,
            **self.frm_settings.config,
        }
        err = self.file_handler.save_config(self.saved_config, None)
        if err == "":
            self.set_status(SAVECONFIGOK, OKCOL)
        else:  # save failed
            self.set_status(SAVECONFIGBAD.format(err), BADCOL)

    def update_widgets(self):
        """
        Update widget configuration (widget_state).

        If no widgets are set as "visible" in the config file, enable
        the status widget anyway to display a warning to this effect.
        """

        try:
            self._nowidgets = True
            for key, vals in widget_state.items():
                vis = self.saved_config.get(key, False)
                vals[VISIBLE] = vis
                if vis:
                    self._nowidgets = False
            if self._nowidgets:
                widget_state["Status"][VISIBLE] = "true"
        except KeyError as err:
            self.set_status(f"{CONFIGERR} - {err}", BADCOL)

    def update_NTRIP_handler(self):
        """
        Initial configuration of NTRIP handler (pygnssutils.GNSSNTRIPClient).
        """

        try:
            ntripsettings = {}
            ntripsettings["server"] = self.saved_config.get("ntripclientserver_s", "")
            ntripsettings["port"] = self.saved_config.get("ntripclientport_n", 2101)
            ntripsettings["ipprot"] = (
                AF_INET6
                if self.saved_config.get("ntripclientprotocol_s") == "IPv6"
                else AF_INET
            )
            ntripsettings["flowinfo"] = self.saved_config.get(
                "ntripclientflowinfo_n", 0
            )
            ntripsettings["scopeid"] = self.saved_config.get("ntripclientscopeid_n", 0)
            ntripsettings["mountpoint"] = self.saved_config.get(
                "ntripclientmountpoint_s", ""
            )
            ntripsettings["sourcetable"] = []  # this is generated by the NTRIP caster
            ntripsettings["version"] = self.saved_config.get(
                "ntripclientversion_s", "2.0"
            )
            ntripsettings["ntripuser"] = self.saved_config.get(
                "ntripclientuser_s", "anon"
            )
            ntripsettings["ntrippassword"] = self.saved_config.get(
                "ntripclientpassword_s", "password"
            )
            ntripsettings["ggainterval"] = self.saved_config.get(
                "ntripclientggainterval_n", -1
            )
            ntripsettings["ggamode"] = self.saved_config.get(
                "ntripclientggamode_b", 0
            )  # GGALIVE
            ntripsettings["reflat"] = self.saved_config.get("ntripclientreflat_f", 0.0)
            ntripsettings["reflon"] = self.saved_config.get("ntripclientreflon_f", 0.0)
            ntripsettings["refalt"] = self.saved_config.get("ntripclientrefalt_f", 0.0)
            ntripsettings["refsep"] = self.saved_config.get("ntripclientrefsep_f", 0.0)
            self.ntrip_handler.settings = ntripsettings

        except (KeyError, ValueError, TypeError, TclError) as err:
            self.set_status(f"Error processing config data: {err}", BADCOL)

    def update_SPARTN_handler(self):
        """
        Initial configuration of SPARTN handler (pygnssutils.GNSSMQTTClient).
        """

        try:
            spartnsettings = {}
            spartnsettings["server"] = self.saved_config.get(
                "mqttclientserver_s", SPARTN_PPSERVER
            )
            spartnsettings["port"] = self.saved_config.get(
                "mqttclientport_n", SPARTN_OUTPORT
            )
            spartnsettings["clientid"] = self.saved_config.get(
                "mqttclientid_s", self.mqttclientid
            )
            spartnsettings["region"] = self.saved_config.get(
                "mgttclientregion_s", self.mqttclientregion
            )
            spartnsettings["mode"] = self.saved_config.get(
                "mgttclientmode_n", self.mqttclientmode
            )
            spartnsettings["topic_ip"] = self.saved_config.get("mgttclienttopicip_b", 1)
            spartnsettings["topic_mga"] = self.saved_config.get(
                "mgttclienttopicmga_b", 1
            )
            spartnsettings["topic_key"] = self.saved_config.get(
                "mgttclienttopickey_b", 1
            )
            spartnsettings["tlscrt"] = self.saved_config.get(
                "mgttclienttlscrt_s",
                path.join(Path.home(), f"device-{self.mqttclientid}-pp-cert.crt"),
            )
            spartnsettings["tlskey"] = self.saved_config.get(
                "mgttclienttlskey_s",
                path.join(Path.home(), f"device-{self.mqttclientid}-pp-key.pem"),
            )
            spartnsettings["output"] = self.spartn_inqueue
            self.spartn_handler.settings = spartnsettings

        except (KeyError, ValueError, TypeError, TclError) as err:
            self.set_status(f"Error processing config data: {err}", BADCOL)

    def start_dialog(self, dlg: str):
        """
        Start a threaded dialog task if the dialog is not already open.

        :param str dlg: name of dialog
        """

        if dialog_state[dlg][THD] is None:
            dialog_state[dlg][THD] = Thread(
                target=self._dialog_thread, args=(dlg,), daemon=False
            )
            dialog_state[dlg][THD].start()

    def _dialog_thread(self, dlg: str):
        """
        THREADED PROCESS

        Dialog thread.

        :param str dlg: name of dialog
        """

        config = self.saved_config if dialog_state[dlg][CFG] else {}
        cls = dialog_state[dlg][CLASS]
        dialog_state[dlg][DLG] = cls(self, saved_config=config)

    def stop_dialog(self, dlg: str):
        """
        Register dialog as closed.

        :param str dlg: name of dialog
        """

        dialog_state[dlg][THD] = None
        dialog_state[dlg][DLG] = None

    def dialog(self, dlg: str) -> Toplevel:
        """
        Get reference to dialog instance.

        :param str dlg: name of dialog
        :return: dialog instance
        :rtype: Toplevel
        """

        return dialog_state[dlg][DLG]

    def start_sockserver_thread(self):
        """
        Start socket server thread.
        """

        settings = self.frm_settings.config
        host = settings["sockhost_s"]
        port = int(settings["sockport_n"])
        ntripmode = int(settings["sockmode_b"])
        ntripuser = settings["ntripcasteruser_s"]
        ntrippassword = settings["ntripcasterpassword_s"]
        self._socket_thread = Thread(
            target=self._sockserver_thread,
            args=(
                ntripmode,
                host,
                port,
                ntripuser,
                ntrippassword,
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
        self,
        ntripmode: int,
        host: str,
        port: int,
        ntripuser: str,
        ntrippassword: str,
        maxclients: int,
        socketqueue: Queue,
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
                self,
                ntripmode,
                maxclients,
                socketqueue,
                (host, port),
                ClientHandler,
                ntripuser=ntripuser,
                ntrippassword=ntrippassword,
            ) as self._socket_server:
                self._socket_server.serve_forever()
        except OSError as err:
            self.set_status(f"Error starting socket server {err}", BADCOL)

    def update_clients(self, clients: int):
        """
        Update number of connected clients in settings panel.

        :param int clients: no of connected clients
        """

        self.frm_settings.frm_socketserver.clients = clients

    def on_exit(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Kill any running processes and quit application.
        """

        self.file_handler.close_logfile()
        self.file_handler.close_trackfile()
        self.stop_sockserver_thread()
        self.stream_handler.stop_read_thread()
        self.__master.destroy()

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
        self.conn_status = DISCONNECTED
        self.set_status(ENDOFFILE)

    def on_ntrip_read(self, event):  # pylint: disable=unused-argument
        """
        EVENT TRIGGERED
        Action on <<ntrip_read>> event - data available on NTRIP queue.

        :param event event: read event
        """

        try:
            raw_data, parsed_data = self.ntrip_inqueue.get(False)
            if raw_data is not None and parsed_data is not None:
                if protocol(raw_data) == RTCM3_PROTOCOL:
                    if self.conn_status == CONNECTED:
                        self.gnss_outqueue.put(raw_data)
                    self.process_data(raw_data, parsed_data, "NTRIP>>")
                elif (
                    protocol(raw_data) == NMEA_PROTOCOL
                ):  # e.g. NMEA GGA sentence sent to NTRIP server
                    self.process_data(raw_data, parsed_data, "NTRIP<<")
            self.ntrip_inqueue.task_done()
        except Empty:
            pass
        except (SerialException, SerialTimeoutException) as err:
            self.set_status(f"Error sending to device {err}", BADCOL)

    def on_spartn_read(self, event):  # pylint: disable=unused-argument
        """
        EVENT TRIGGERED
        Action on <<spartn_read>> event - data available on SPARTN queue.

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

    def on_stream_error(self, event):  # pylint: disable=unused-argument
        """
        EVENT TRIGGERED
        Action on "<<gnss_error>>" event - connection streaming error.

        :param event event: <<gnss_error>> event
        """

        self.conn_status = DISCONNECTED

    def update_ntrip_status(self, status: bool, msgt: tuple = None):
        """
        Update NTRIP configuration dialog connection status.

        :param bool status: connected to NTRIP server yes/no
        :param tuple msgt: tuple of (message, color)
        """

        if self.dialog(DLGTNTRIP) is not None:
            self.dialog(DLGTNTRIP).set_controls(status, msgt)

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

        protfilter = settings["protocol_n"]
        msgprot = protocol(raw_data)
        if isinstance(parsed_data, MQTTMessage):
            msgprot = MQTT_PROTOCOL
        elif isinstance(parsed_data, str):
            marker = "WARNING  "
            msgprot = 0

        if msgprot == UBX_PROTOCOL and msgprot & protfilter:
            self.ubx_handler.process_data(raw_data, parsed_data)
        elif msgprot == NMEA_PROTOCOL and msgprot & protfilter:
            self.nmea_handler.process_data(raw_data, parsed_data)
        elif msgprot == RTCM3_PROTOCOL and msgprot & protfilter:
            self.rtcm_handler.process_data(raw_data, parsed_data)
        elif msgprot == MQTT_PROTOCOL:
            pass

        # update console if visible
        if widget_state["Console"][VISIBLE]:
            if msgprot == 0 or msgprot & protfilter:
                self.frm_console.update_console(raw_data, parsed_data, marker)

        # periodically update widgets if visible
        if datetime.now() > self._last_gui_update + timedelta(
            seconds=GUI_UPDATE_INTERVAL
        ):
            self.frm_banner.update_frame()
            for _, widget in widget_state.items():
                frm = getattr(self, widget["frm"])
                if hasattr(frm, "update_frame") and widget[VISIBLE]:
                    frm.update_frame()
            self._last_gui_update = datetime.now()

        # update GPX track file if enabled
        if settings["recordtrack_b"]:
            self.file_handler.update_gpx_track()

        # update log file if enabled
        if settings["datalog_b"]:
            self.file_handler.write_logfile(raw_data, parsed_data)

    def _check_update(self):
        """
        Check for updated version.
        """

        latest = check_latest("PyGPSClient")
        if latest not in (VERSION, "N/A"):
            self.set_status(VERCHECK.format(latest), BADCOL)

    @property
    def widget_config(self) -> dict:
        """
        Getter for widget configuration.

        :return: configuration
        :rtype: dict
        """

        return {key: vals[VISIBLE] for key, vals in widget_state.items()}

    @property
    def widgets(self) -> dict:
        """
        Getter for widget state.

        :return: widget state
        :rtype: dict
        """

        return widget_state

    @property
    def dialogs(self) -> dict:
        """
        Getter for dialog state.

        :return: dialog state
        :rtype: dict
        """

        return dialog_state

    @property
    def appmaster(self) -> Tk:
        """
        Getter for application master (Tk).

        :return: reference to master Tk instance
        :rtype: Tk
        """

        return self.__master

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
            self.set_connection(NOTCONN)

    @property
    def rtk_conn_status(self) -> int:
        """
        Getter for SPARTN connection status.

        :return: connection status
        :rtype: int
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

    def svin_countdown(self, dur: int, valid: bool, active: bool):
        """
        Countdown survey-in duration for NTRIP caster mode.

        :param int dur: elapsed time
        :param bool valid: valid flag
        :param bool active: active flag
        """

        if self.frm_settings.frm_socketserver is not None:
            self.frm_settings.frm_socketserver.svin_countdown(dur, valid, active)
