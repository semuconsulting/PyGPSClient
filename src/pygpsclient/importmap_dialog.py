"""
importmap_dialog.py

This is the pop-up dialog for the custom map import function.

Created on 14 Sep 2024

:author: semuadmin
:copyright: 2020 SEMU Consulting
:license: BSD 3-Clause
"""

# pylint: disable=unused-argument

from tkinter import (
    ALL,
    BOTH,
    DISABLED,
    NORMAL,
    NW,
    YES,
    Button,
    Canvas,
    E,
    Entry,
    Frame,
    Label,
    N,
    S,
    StringVar,
    Toplevel,
    W,
)

from PIL import Image, ImageTk

try:
    from rasterio import open as openraster  # pylint: disable=import-error
    from rasterio.warp import transform_bounds  # pylint: disable=import-error

    HASRASTERIO = True
except (ImportError, ModuleNotFoundError):
    HASRASTERIO = False

from pygpsclient.globals import (
    BGCOL,
    ERRCOL,
    HOME,
    ICON_EXIT,
    ICON_LOAD,
    ICON_SEND,
    INFOCOL,
    POPUP_TRANSIENT,
)
from pygpsclient.strings import DLGTIMPORTMAP

# profile chart parameters:
AXIS_XL = 35  # x axis left offset
AXIS_XR = 35  # x axis right offset
AXIS_Y = 15  # y axis bottom offset
ELEAX_COL = "green4"  # color of elevation plot axis
ELE_COL = "palegreen3"  # color of elevation plot
SPD_COL = INFOCOL  # color of speed plot
MD_LINES = 2  # number of lines of metadata


class ImportMapDialog(Toplevel):
    """ImportMapDialog class."""

    def __init__(self, app, *args, **kwargs):
        """Constructor."""

        self.__app = app
        # self.__master = self.__app.appmaster  # link to root Tk window
        Toplevel.__init__(self, app)
        if POPUP_TRANSIENT:
            self.transient(self.__app)
        self.resizable(True, True)
        self.title(DLGTIMPORTMAP)  # pylint: disable=E1102
        self.protocol("WM_DELETE_WINDOW", self.on_exit)
        self._img_load = ImageTk.PhotoImage(Image.open(ICON_LOAD))
        self._img_send = ImageTk.PhotoImage(Image.open(ICON_SEND))
        self._img_exit = ImageTk.PhotoImage(Image.open(ICON_EXIT))
        self.width = int(kwargs.get("width", 400))
        self.height = int(kwargs.get("height", 400))
        self.mheight = int(self.height * 0.75)
        self._lonmin = StringVar()
        self._latmin = StringVar()
        self._lonmax = StringVar()
        self._latmax = StringVar()
        self._mapimg = None
        self._thmbimg = None
        self._initdir = HOME
        self._custommap = ""

        self._body()
        self._do_layout()
        self._attach_events()
        self._reset()

    def _body(self):
        """
        Create widgets.
        """

        self._frm_map = Frame(self, borderwidth=2, relief="groove", bg=BGCOL)
        self._frm_controls = Frame(self, borderwidth=2, relief="groove")
        self._canvas_map = Canvas(
            self._frm_map, width=self.width, height=self.mheight, bg=BGCOL
        )
        self._btn_load = Button(
            self._frm_controls,
            image=self._img_load,
            width=40,
            command=self._on_load,
        )
        self._btn_import = Button(
            self._frm_controls,
            image=self._img_send,
            width=40,
            command=self._on_import,
        )
        self._lbl_min = Label(self._frm_controls, text="Minimum:")
        self._lbl_minlat = Label(self._frm_controls, text="Latitude")
        self._ent_minlat = Entry(
            self._frm_controls, width=10, textvariable=self._latmin
        )
        self._lbl_minlon = Label(self._frm_controls, text="Longitude")
        self._ent_minlon = Entry(
            self._frm_controls, width=10, textvariable=self._lonmin
        )
        self._lbl_max = Label(self._frm_controls, text="Maximum:")
        self._lbl_maxlat = Label(self._frm_controls, text="Latitude")
        self._ent_maxlat = Entry(
            self._frm_controls, width=10, textvariable=self._latmax
        )
        self._lbl_maxlon = Label(self._frm_controls, text="Longitude")
        self._ent_maxlon = Entry(
            self._frm_controls, width=10, textvariable=self._lonmax
        )
        self._btn_exit = Button(
            self._frm_controls,
            image=self._img_exit,
            width=40,
            command=self.on_exit,
        )
        self._lbl_status = Label(self._frm_controls, text="", anchor=W)

    def _do_layout(self):
        """
        Arrange widgets.
        """

        self._frm_map.grid(column=0, row=0, sticky=(N, S, E, W))
        self._frm_controls.grid(column=0, row=1, sticky=(W, E))
        self._canvas_map.pack(fill=BOTH, expand=YES)
        self._btn_load.grid(column=0, row=0, padx=3, pady=3)
        self._btn_import.grid(column=1, row=0, padx=3, pady=3)
        self._btn_exit.grid(column=4, row=0, padx=3, pady=3, sticky=E)

        self._lbl_min.grid(column=0, row=1, padx=3, pady=3, sticky=W)
        self._lbl_minlat.grid(column=1, row=1, padx=3, pady=3, sticky=E)
        self._ent_minlat.grid(column=2, row=1, padx=3, pady=3)
        self._lbl_minlon.grid(column=3, row=1, padx=3, pady=3, sticky=E)
        self._ent_minlon.grid(column=4, row=1, padx=3, pady=3)
        self._lbl_max.grid(column=0, row=2, padx=3, pady=3, sticky=W)
        self._lbl_maxlat.grid(column=1, row=2, padx=3, pady=3, sticky=E)
        self._ent_maxlat.grid(column=2, row=2, padx=3, pady=3)
        self._lbl_maxlon.grid(column=3, row=2, padx=3, pady=3, sticky=E)
        self._ent_maxlon.grid(column=4, row=2, padx=3, pady=3)
        self._lbl_status.grid(
            column=0, row=3, columnspan=5, padx=3, pady=3, sticky=(W, E)
        )

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=3)
        self.grid_rowconfigure(1, weight=1)

    def _attach_events(self):
        """
        Bind events to window.
        """

        self.bind("<Configure>", self._on_resize)

    def _reset(self):
        """
        Reset application.
        """

        self._canvas_map.delete(ALL)
        self._btn_import.config(state=DISABLED)
        if not HASRASTERIO:
            self._show_status(
                "Warning: rasterio library is not installed - bounds must be entered manually"
            )
        else:
            self._show_status()

    def on_exit(self, *args, **kwargs):
        """
        Handle Exit button press.
        """

        self.__app.stop_dialog(DLGTIMPORTMAP)
        self.destroy()

    def get_size(self):
        """
        Get current frame size.

        :return: window size (width, height)
        :rtype: tuple
        """

        return (self.winfo_width(), self.winfo_height())

    def _on_resize(self, event):
        """
        Resize frame

        :param event event: resize event
        """

        self.width, self.height = self.get_size()
        self.mheight = self._frm_map.winfo_height()

    def _open_mapfile(self) -> str:
        """
        Open custom map file.
        """

        return self.__app.file_handler.open_file(
            "tif",
            (("GeoTiff files", "*.tif"), ("all files", "*.*")),
        )

    def _on_load(self):
        """
        Load custom map from file.
        """

        self._show_status()
        self._custommap = self._open_mapfile()
        if self._custommap is not None:
            self._get_bounds(self._custommap)
            self._draw_map(self._custommap)
            self._btn_import.config(state=NORMAL)

    def _get_bounds(self, mappath) -> tuple:
        """
        Get bounds of custom map image file.

        :param str mappath: fully qualified path to map file
        """

        lonmin = latmin = lonmax = latmax = 0.0
        if HASRASTERIO:
            try:
                ras = openraster(mappath)
                lonmin, latmin, lonmax, latmax = transform_bounds(
                    ras.crs.to_epsg(), 4326, *ras.bounds
                )
            except Exception:  # pylint: disable=broad-exception-caught
                self._show_status(
                    "Warning: image is not georeferenced - bounds must be entered manually"
                )

        self._lonmin.set(round(lonmin, 8))
        self._latmin.set(round(latmin, 8))
        self._lonmax.set(round(lonmax, 8))
        self._latmax.set(round(latmax, 8))

    def _draw_map(self, mappath="") -> ImageTk.PhotoImage:
        """
        Display selected custom map image.

        :param str mappath: fully qualified path to map file
        """

        if mappath != "":
            self._mapimg = ImageTk.PhotoImage(
                Image.open(mappath).resize((self.width, self.mheight)),
                Image.Resampling.BILINEAR,
            )
            self._canvas_map.create_image(0, 0, image=self._mapimg, anchor=NW)

    def _on_import(self):
        """
        Validate bounds and import custom file into saved config.
        """

        try:
            lonmin = float(self._lonmin.get())
            lonmax = float(self._lonmax.get())
            latmin = float(self._latmin.get())
            latmax = float(self._latmax.get())
        except ValueError:
            self._show_status("Error: invalid bounds")
            return

        if lonmax + 180 <= lonmin + 180 or latmax + 90 <= latmin + 90:
            self._show_status("Error: minimum must be less than maximum")
        else:
            usermaps = self.__app.configuration.get("usermaps_l")
            usermaps.append([self._custommap, [latmin, lonmin, latmax, lonmax]])
            self.__app.configuration.set("usermaps_l", usermaps)
            self._show_status("Custom map imported", INFOCOL)

    def _show_status(self, msg: str = "", col: str = ERRCOL):
        """
        Show error message in status label

        :param str msg: error message
        :param str col: text colour
        """

        self._lbl_status.config(text=msg, fg=col)
        self.update_idletasks()
