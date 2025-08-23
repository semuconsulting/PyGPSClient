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
    DISABLED,
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
    StringVar,
    W,
)

try:
    from rasterio import open as openraster  # pylint: disable=import-error
    from rasterio.warp import transform_bounds  # pylint: disable=import-error

    HASRASTERIO = True
except (ImportError, ModuleNotFoundError):
    HASRASTERIO = False

from pygpsclient.globals import (
    BGCOL,
    ERRCOL,
    IMPORT,
    INFOCOL,
    Area,
)
from pygpsclient.map_canvas import MapCanvas
from pygpsclient.strings import DLGTIMPORTMAP
from pygpsclient.toplevel_dialog import ToplevelDialog

# profile chart parameters:
AXIS_XL = 35  # x axis left offset
AXIS_XR = 35  # x axis right offset
AXIS_Y = 15  # y axis bottom offset
ELEAX_COL = "green4"  # color of elevation plot axis
ELE_COL = "palegreen3"  # color of elevation plot
SPD_COL = INFOCOL  # color of speed plot
MD_LINES = 2  # number of lines of metadata
MINDIM = (456, 418)


class ImportMapDialog(ToplevelDialog):
    """ImportMapDialog class."""

    def __init__(self, app, *args, **kwargs):
        """Constructor."""

        self.__app = app
        # self.__master = self.__app.appmaster  # link to root Tk window
        super().__init__(app, DLGTIMPORTMAP, MINDIM)
        self.width = int(kwargs.get("width", 400))
        self.height = int(kwargs.get("height", 400))
        self._first = IntVar()
        self._lonmin = StringVar()
        self._latmin = StringVar()
        self._lonmax = StringVar()
        self._latmax = StringVar()
        self._custommap = ""

        self._body()
        self._do_layout()
        self._attach_events()
        self._reset()
        self._finalise()

    def _body(self):
        """
        Create widgets.
        """

        self._frm_body = Frame(self.container, borderwidth=2, relief="groove")
        self._can_mapview = MapCanvas(
            self.__app, self._frm_body, width=self.width, height=self.height, bg=BGCOL
        )
        self._frm_controls = Frame(self._frm_body, borderwidth=2, relief="groove")
        self._btn_load = Button(
            self._frm_controls,
            image=self.img_load,
            width=40,
            command=self._on_load,
        )
        self._btn_import = Button(
            self._frm_controls,
            image=self.img_send,
            width=40,
            command=self._on_import,
        )
        self._btn_redraw = Button(
            self._frm_controls,
            image=self.img_redraw,
            width=40,
            command=self._on_redraw,
        )
        self._chk_first = Checkbutton(
            self._frm_controls, text="First?", variable=self._first
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

    def _do_layout(self):
        """
        Arrange widgets.
        """
        self._frm_body.grid(column=0, row=0, sticky=(N, S, E, W))
        self._can_mapview.grid(column=0, row=0, sticky=(N, S, E, W))
        self._frm_controls.grid(column=0, row=1, sticky=(W, E))
        self._btn_load.grid(column=0, row=0, padx=3, pady=3)
        self._btn_redraw.grid(column=1, row=0, padx=3, pady=3)
        self._btn_import.grid(column=2, row=0, padx=3, pady=3)
        self._chk_first.grid(column=3, row=0, padx=3, pady=3)
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
        self.container.grid_columnconfigure(0, weight=10)
        self.container.grid_rowconfigure(0, weight=10)
        self.grid_columnconfigure(0, weight=10)
        self.grid_rowconfigure(0, weight=10)
        self._frm_body.grid_columnconfigure(0, weight=10)
        self._frm_body.grid_rowconfigure(0, weight=10)
        self._can_mapview.grid_columnconfigure(0, weight=10)
        self._can_mapview.grid_rowconfigure(0, weight=10)

    def _attach_events(self):
        """
        Bind events to window.
        """

        self.container.bind("<Configure>", self._on_resize)

    def _reset(self):
        """
        Reset application.
        """

        self._first.set(0)
        self._can_mapview.delete(ALL)
        # self._btn_import.config(state=DISABLED)
        if not HASRASTERIO:
            self.set_status(
                "Warning: rasterio library is not installed - bounds must be entered manually",
                INFOCOL,
            )
        else:
            self.set_status("")

    def _on_load(self):
        """
        Load custom map from file.
        """

        self.set_status("")
        self._custommap = self._open_mapfile()
        if self._custommap is not None:
            bounds = self._get_bounds(self._custommap)
            self._can_mapview.draw_map(
                maptype=IMPORT, mappath=self._custommap, bounds=bounds, zoom=None
            )
            self._btn_import.config(state=NORMAL)
        else:
            self._btn_import.config(state=DISABLED)

    def _on_redraw(self, *args, **kwargs):
        """
        Handle redraw button press.
        """

        self._reset()
        self._can_mapview.draw_map(
            maptype=IMPORT,
            mappath=self._custommap,
            bounds=self._can_mapview.bounds,
            marker=self._can_mapview.marker,
            zoom=None,
        )

    def _open_mapfile(self) -> str:
        """
        Open custom map file.
        """

        return self.__app.file_handler.open_file(
            "tif",
            (("GeoTiff files", "*.tif"), ("all files", "*.*")),
        )

    def _get_bounds(self, mappath) -> Area:
        """
        Get bounds of custom map image file.

        :param str mappath: fully qualified path to map file
        :return: bounds (extent)
        :rtype: Area
        """

        lonmin = latmin = lonmax = latmax = 0.0
        if HASRASTERIO:
            try:
                ras = openraster(mappath)
                lonmin, latmin, lonmax, latmax = transform_bounds(
                    ras.crs.to_epsg(), 4326, *ras.bounds
                )
            except Exception:  # pylint: disable=broad-exception-caught
                self.set_status(
                    "Warning: image is not georeferenced - bounds must be entered manually",
                    ERRCOL,
                )

        self._lonmin.set(round(lonmin, 8))
        self._latmin.set(round(latmin, 8))
        self._lonmax.set(round(lonmax, 8))
        self._latmax.set(round(latmax, 8))
        return Area(
            float(self._latmin.get()),
            float(self._lonmin.get()),
            float(self._latmax.get()),
            float(self._lonmax.get()),
        )

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
            self.set_status("Error: invalid bounds", ERRCOL)
            return

        if lonmax + 180 <= lonmin + 180 or latmax + 90 <= latmin + 90:
            self.set_status("Error: minimum must be less than maximum", ERRCOL)
        else:
            usermaps = self.__app.configuration.get("usermaps_l")
            idx = 0 if self._first.get() else len(usermaps) + 1
            usermaps.insert(idx, [self._custommap, [latmin, lonmin, latmax, lonmax]])
            self.__app.configuration.set("usermaps_l", usermaps)
            self.set_status("Custom map imported", INFOCOL)
