"""
importmap_dialog.py

This is the pop-up dialog for the custom map import function.

Created on 14 Sep 2024

:author: semuadmin (Steve Smith)
:copyright: 2020 semuadmin
:license: BSD 3-Clause
"""

# pylint: disable=unused-argument

from tkinter import (
    ALL,
    DISABLED,
    EW,
    NORMAL,
    NSEW,
    Button,
    Checkbutton,
    E,
    Entry,
    Frame,
    IntVar,
    Label,
    StringVar,
    Tk,
    W,
)

try:
    from rasterio import open as openraster  # pylint: disable=import-error
    from rasterio.errors import RasterioIOError  # pylint: disable=import-error
    from rasterio.warp import transform_bounds  # pylint: disable=import-error

    HASRASTERIO = True
except (ImportError, ModuleNotFoundError):
    HASRASTERIO = False

from pygpsclient.canvas_map import CanvasMap
from pygpsclient.globals import (
    BGCOL,
    CLICK_CURSOR,
    ERRCOL,
    IMPORT,
    INFOCOL,
    OKCOL,
    VALFLOAT,
    Area,
)
from pygpsclient.helpers import validate  # pylint: disable=unused-import
from pygpsclient.strings import DLGTIMPORTMAP
from pygpsclient.toplevel_dialog import ToplevelDialog


class ImportMapDialog(ToplevelDialog):
    """ImportMapDialog class."""

    def __init__(self, app: Tk, *args, **kwargs):
        """Constructor."""

        self.__app = app

        super().__init__(app, DLGTIMPORTMAP)
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

        self._frm_body = Frame(self.container)
        self._can_mapview = CanvasMap(
            self.__app, self._frm_body, width=self.width, height=self.height, bg=BGCOL
        )
        self._frm_controls = Frame(self._frm_body, borderwidth=2, relief="groove")
        self._btn_load = Button(
            self._frm_controls,
            image=self.img_load,
            width=40,
            command=self._on_load,
            cursor=CLICK_CURSOR,
        )
        self._btn_import = Button(
            self._frm_controls,
            image=self.img_send,
            width=40,
            command=self._on_import,
            cursor=CLICK_CURSOR,
        )
        self._btn_redraw = Button(
            self._frm_controls,
            image=self.img_redraw,
            width=40,
            command=self._on_redraw,
            cursor=CLICK_CURSOR,
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
        self._frm_body.grid(column=0, row=0, sticky=NSEW)
        self._can_mapview.grid(column=0, row=0, sticky=NSEW)
        self._frm_controls.grid(column=0, row=1, sticky=EW)
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
        # self._btn_import["state"]=DISABLED
        if not HASRASTERIO:
            self.set_status_label(
                "Rasterio library is not installed - "
                "extents must be entered manually",
                INFOCOL,
            )
        else:
            self.status_label = ""

    def _valid_entries(self) -> bool:
        """
        Validate bounds entries.

        :return: True/False
        :rtype: bool
        """

        valid = True
        valid = valid & self._ent_minlat.validate(VALFLOAT, -90, 90)
        valid = valid & self._ent_maxlat.validate(VALFLOAT, -90, 90)
        valid = valid & self._ent_minlon.validate(VALFLOAT, -180, 180)
        valid = valid & self._ent_maxlon.validate(VALFLOAT, -180, 180)
        if valid:
            self.set_status_label("")
            self._btn_import["state"] = NORMAL
        else:
            self.set_status_label("Error: invalid entry", ERRCOL)
            self._btn_import["state"] = DISABLED
        return valid

    def _on_load(self):
        """
        Load custom map from file.
        """

        self.set_status_label("")
        self._custommap = self._open_mapfile()
        if self._custommap is not None:
            bounds = self._get_bounds(self._custommap)
            self._can_mapview.draw_map(
                maptype=IMPORT, mappath=self._custommap, bounds=bounds, zoom=None
            )
            self._btn_import["state"] = NORMAL
        else:
            self._btn_import["state"] = DISABLED

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

        :return: fully qualified path to map file
        :rtype: str
        """

        return self.__app.file_handler.open_file(
            self,
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
                extents = transform_bounds(ras.crs.to_epsg(), 4326, *ras.bounds)
                lonmin, latmin, lonmax, latmax = extents
            except AttributeError:
                self.set_status_label(
                    "Image is not georeferenced - extents must be entered manually",
                    ERRCOL,
                )
            except RasterioIOError:
                self.set_status_label("Image is not a supported file format", ERRCOL)
            except Exception as err:  # pylint: disable=broad-exception-caught
                self.set_status_label(str(err), ERRCOL)

        self._lonmin.set(str(round(lonmin, 8)))
        self._latmin.set(str(round(latmin, 8)))
        self._lonmax.set(str(round(lonmax, 8)))
        self._latmax.set(str(round(latmax, 8)))
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

        if not self._valid_entries():
            return

        lonmin = float(self._lonmin.get())
        lonmax = float(self._lonmax.get())
        latmin = float(self._latmin.get())
        latmax = float(self._latmax.get())

        if lonmax + 180 <= lonmin + 180 or latmax + 90 <= latmin + 90:
            self.set_status_label("Error: minimum must be less than maximum", ERRCOL)
        else:
            usermaps = self.__app.configuration.get("usermaps_l")
            idx = 0 if self._first.get() else len(usermaps) + 1
            usermaps.insert(idx, [self._custommap, [latmin, lonmin, latmax, lonmax]])
            self.__app.configuration.set("usermaps_l", usermaps)
            self.set_status_label("Custom map imported", OKCOL)
