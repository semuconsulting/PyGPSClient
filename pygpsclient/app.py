"""
PyGPSClient - Main tkinter application class

Created on 12 Sep 2020
@author: semuadmin
"""

from threading import Thread
from tkinter import Tk, Frame, N, S, E, W, PhotoImage, font

from .strings import (
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
)
from ._version import __version__
from .about_dialog import AboutDialog
from .banner_frame import BannerFrame
from .console_frame import ConsoleFrame
from .filehandler import FileHandler
from .globals import ICON_APP, DISCONNECTED
from .graphview_frame import GraphviewFrame
from .map_frame import MapviewFrame
from .menu_bar import MenuBar
from .serial_handler import SerialHandler
from .settings_frame import SettingsFrame
from .skyview_frame import SkyviewFrame
from .status_frame import StatusFrame
from .ubx_config_dialog import UBXConfigDialog
from .nmea_handler import NMEAHandler
from .ubx_handler import UBXHandler

VERSION = __version__


class App(Frame):  # pylint: disable=too-many-ancestors
    """
    Main GUI Application Class
    """

    def __init__(self, master, *args, **kwargs):
        """
        Set up main application and add frames

        :param object master: reference to Tk instance
        """

        self.__master = master

        Frame.__init__(self, self.__master, *args, **kwargs)

        self.__master.protocol("WM_DELETE_WINDOW", self.exit)
        self.__master.title(TITLE)
        self.__master.iconphoto(True, PhotoImage(file=ICON_APP))

        # Set initial widget visibility
        self._show_settings = True
        self._show_ubxconfig = False
        self._show_status = True
        self._show_console = True
        self._show_map = True
        self._show_sats = True

        # Instantiate protocol handler classes
        self.file_handler = FileHandler(self)
        self.serial_handler = SerialHandler(self)
        self.nmea_handler = NMEAHandler(self)
        self.ubx_handler = UBXHandler(self)
        self.dlg_ubxconfig = None
        self._config_thread = None

        # Load web map api key if there is one
        self.api_key = self.file_handler.load_apikey()

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

        if self.frm_settings.get_settings()["noports"]:
            self.set_status(INTROTXTNOPORTS, "red")

    def _attach_events(self):
        """
        Bind events to main application
        """

        self.__master.bind("<<ubx_read>>", self.serial_handler.on_read)
        self.__master.bind("<<ubx_readfile>>", self.serial_handler.on_read)
        self.__master.bind("<<ubx_eof>>", self.serial_handler.on_eof)
        self.__master.bind_all("<Control-q>", self.exit)

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

        self._config_thread = Thread(target=self._ubxconfig_thread, daemon=False)
        self._config_thread.start()

    def _ubxconfig_thread(self):
        """
        THREADED PROCESS UBX Configuration Dialog
        """

        self.dlg_ubxconfig = UBXConfigDialog(self)

    def stop_config_thread(self):
        """
        Stop UBX Configuration dialog thread.
        """

        if self._config_thread is not None:
            self._config_thread.join()

    def get_master(self):
        """
        Returns application master (Tk)
        """

        return self.__master

    def exit(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Kill any running processes and quit application
        """

        self.serial_handler.stop_read_thread()
        self.serial_handler.stop_readfile_thread()
        self.stop_config_thread()
        self.serial_handler.disconnect()
        self.__master.destroy()


if __name__ == "__main__":
    ROOT = Tk()
    APP = App(ROOT)
    ROOT.mainloop()
