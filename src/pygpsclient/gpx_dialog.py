"""
gpx_dialog.py

This is the pop-up dialog for the GPX Viewer function.

Created on 10 Jan 2023

:author: semuadmin (Steve Smith)
:copyright: 2020 semuadmin
:license: BSD 3-Clause
"""

# pylint: disable=unused-argument

import logging
from datetime import datetime, timedelta, timezone
from tkinter import (
    ALL,
    NE,
    NW,
    Button,
    Canvas,
    E,
    Frame,
    IntVar,
    Label,
    N,
    S,
    Spinbox,
    StringVar,
    W,
    font,
)
from xml.dom import minidom
from xml.parsers import expat

from pygpsclient.globals import (
    BGCOL,
    CUSTOM,
    ERRCOL,
    GRIDCOL,
    HOME,
    INFOCOL,
    KM2M,
    KM2MIL,
    KM2NMIL,
    KPH2KNT,
    KPH2MPH,
    KPH2MPS,
    M2FT,
    READONLY,
    UI,
    UIK,
    UMK,
    Area,
    Point,
    TrackPoint,
)
from pygpsclient.helpers import haversine, isot2dt
from pygpsclient.map_canvas import HYB, MAP, SAT, MapCanvas
from pygpsclient.strings import (
    DLGGPXERROR,
    DLGGPXLOAD,
    DLGGPXNULL,
    DLGGPXOPEN,
    DLGGPXWAIT,
    DLGTGPX,
)
from pygpsclient.toplevel_dialog import ToplevelDialog

# profile chart parameters:
AXIS_XL = 35  # x axis left offset
AXIS_XR = 35  # x axis right offset
AXIS_Y = 15  # y axis bottom offset
ELEAX_COL = "green4"  # color of elevation plot axis
ELE_COL = "palegreen3"  # color of elevation plot
SPD_COL = "coral"  # color of speed plot
TRK_COL = "magenta"  # color of track
MD_LINES = 2  # number of lines of metadata
MINDIM = (400, 500)


class GPXViewerDialog(ToplevelDialog):
    """GPXViewerDialog class."""

    def __init__(self, app, *args, **kwargs):
        """Constructor."""

        self.__app = app
        self.logger = logging.getLogger(__name__)
        # self.__master = self.__app.appmaster  # link to root Tk window
        super().__init__(app, DLGTGPX, MINDIM)
        self._mapzoom = IntVar()
        self._maptype = StringVar()
        zoom = int(kwargs.get("zoom", 12))
        self._mapzoom.set(zoom)
        self._info = []
        for _ in range(MD_LINES):
            self._info.append(StringVar())
        self._mtt = None
        self._mtz = None
        self._mapimg = None
        self._track = None
        self._gpxfile = None
        self._metadata = {}
        self._bounds = None
        self._center = None
        self._initdir = HOME

        self._body()
        self._do_layout()
        self._reset()
        self._attach_events()
        self._finalise()

    def _body(self):
        """
        Create widgets.
        """

        self._frm_body = Frame(self.container, borderwidth=2, relief="groove")
        self._frm_map = Frame(self._frm_body, borderwidth=2, relief="groove", bg=BGCOL)
        self._frm_profile = Frame(
            self._frm_body, borderwidth=2, relief="groove", bg=BGCOL
        )
        self._frm_info = Frame(self._frm_body, borderwidth=2, relief="groove")
        self._frm_controls = Frame(self._frm_body, borderwidth=2, relief="groove")
        self._can_mapview = MapCanvas(
            self.__app,
            self._frm_map,
            height=self.height * 0.75,
            width=self.width,
            bg=BGCOL,
        )
        self._can_profile = Canvas(
            self._frm_profile,
            height=self.height * 0.25,
            width=self.width,
            bg="#f0f0e8",
        )
        self._lbl_info = []
        for i in range(MD_LINES):
            self._lbl_info.append(
                Label(self._frm_info, textvariable=self._info[i], anchor=W)
            )
        self._btn_load = Button(
            self._frm_controls,
            image=self.img_load,
            width=40,
            command=self._on_load,
        )
        self._lbl_maptype = Label(self._frm_controls, text="Map Type")
        self._spn_maptype = Spinbox(
            self._frm_controls,
            values=(HYB, SAT, MAP, CUSTOM),
            width=7,
            wrap=True,
            textvariable=self._maptype,
            state=READONLY,
        )
        self._lbl_zoom = Label(self._frm_controls, text="Zoom")
        self._spn_zoom = Spinbox(
            self._frm_controls,
            from_=1,
            to=20,
            width=5,
            wrap=False,
            textvariable=self._mapzoom,
            state=READONLY,
        )
        self._btn_redraw = Button(
            self._frm_controls,
            image=self.img_redraw,
            width=40,
            command=self._on_redraw,
        )

    def _do_layout(self):
        """
        Arrange widgets.
        """

        self._frm_body.grid(column=0, row=0, sticky=(N, S, E, W))
        self._frm_map.grid(column=0, row=0, sticky=(N, S, E, W))
        self._frm_profile.grid(column=0, row=1, sticky=(W, E))
        self._frm_info.grid(column=0, row=2, sticky=(W, E))
        self._frm_controls.grid(column=0, row=3, columnspan=7, sticky=(W, E))
        self._can_mapview.grid(column=0, row=0, sticky=(N, S, E, W))
        self._can_profile.grid(column=0, row=0, sticky=(N, S, E, W))
        for i in range(MD_LINES):
            self._lbl_info[i].grid(column=0, row=i, padx=3, pady=1, sticky=(W, E))
        self._btn_load.grid(column=0, row=1, padx=3, pady=3)
        self._lbl_maptype.grid(
            column=1,
            row=1,
            padx=3,
            pady=3,
        )
        self._spn_maptype.grid(
            column=2,
            row=1,
            padx=3,
            pady=3,
        )
        self._lbl_zoom.grid(
            column=3,
            row=1,
            padx=3,
            pady=3,
        )
        self._spn_zoom.grid(
            column=4,
            row=1,
            padx=3,
            pady=3,
        )

        self._btn_redraw.grid(
            column=5,
            row=1,
            padx=3,
            pady=3,
        )

        # set column and row weights
        # NB!!! these govern the 'pack' behaviour of the frames on resize
        self.container.grid_columnconfigure(0, weight=10)
        self.container.grid_rowconfigure(0, weight=10)
        self.grid_columnconfigure(0, weight=10)
        self.grid_rowconfigure(0, weight=10)
        self._frm_body.grid_columnconfigure(0, weight=10)
        self._frm_body.grid_rowconfigure(0, weight=10)  # map
        self._frm_body.grid_rowconfigure(1, weight=3)  # profile
        self._frm_map.grid_columnconfigure(0, weight=10)
        self._frm_map.grid_rowconfigure(0, weight=10)
        self._can_mapview.grid_columnconfigure(0, weight=10)
        self._can_mapview.grid_rowconfigure(0, weight=10)
        self._frm_profile.grid_columnconfigure(0, weight=10)
        self._frm_profile.grid_rowconfigure(0, weight=10)

    def _attach_events(self):
        """
        Bind events to window.
        """

        self._mtt = self._maptype.trace_add("write", self._on_maptype)
        self._mtz = self._mapzoom.trace_add("write", self._on_mapzoom)

    def _detach_events(self):
        """
        Unbind events to window.
        """

        self._maptype.trace_remove("write", self._mtt)
        self._mapzoom.trace_remove("write", self._mtz)

    def _reset(self):
        """
        Reset application.
        """

        self._can_mapview.delete(ALL)
        self._can_profile.delete(ALL)
        self._maptype.set(self.__app.configuration.get("gpxmaptype_s"))
        self._mapzoom.set(self.__app.configuration.get("gpxmapzoom_n"))
        for i in range(MD_LINES):
            self._info[i].set("")
        self._can_mapview.draw_msg(DLGGPXOPEN, INFOCOL)

    def _on_maptype(self, var, index, mode):  # pylint: disable=unused-argument
        """
        Map type has changed.
        """

        self.__app.configuration.set("gpxmaptype_s", self._maptype.get())
        self._on_redraw()

    def _on_mapzoom(self, var, index, mode):  # pylint: disable=unused-argument
        """
        Map zoom has changed.
        """

        self.__app.configuration.set("gpxmapzoom_n", self._mapzoom.get())
        self._on_redraw()

    def _on_redraw(self, *args, **kwargs):
        """
        Handle redraw button press.
        """

        self._detach_events()
        self._reset()
        self.set_status(DLGGPXWAIT, INFOCOL)
        self._spn_zoom.config(highlightbackground="gray90", highlightthickness=3)
        self._draw_map()
        self._draw_profile(self._track)
        self._format_metadata(self._metadata)
        self.set_status("", INFOCOL)
        self._attach_events()

    def _open_gpxfile(self) -> str:
        """
        Open gpx file.
        """

        return self.__app.file_handler.open_file(
            "gpx",
            (("gpx files", "*.gpx"), ("all files", "*.*")),
        )

    def _on_load(self):
        """
        Load gpx track from file.
        """

        self._gpxfile = self._open_gpxfile()
        if self._gpxfile is None:  # user cancelled
            return

        self.set_status(DLGGPXLOAD, INFOCOL)

        with open(self._gpxfile, "r", encoding="utf-8") as gpx:
            try:
                parser = minidom.parse(gpx)
                trkpts = parser.getElementsByTagName("trkpt")
                self._process_track(trkpts)
                self.set_status("")
            except (TypeError, AttributeError, expat.ExpatError) as err:
                self.set_status(f"{DLGGPXERROR}\n{repr(err)}", ERRCOL)

    def _process_track(self, trkpts: list):
        """
        Process trackpoint data.

        :param list trk: list of trackpoints
        """

        rng = len(trkpts)
        if rng == 0:
            self.set_status(DLGGPXNULL, ERRCOL)
            return

        minlat = minlon = 400
        maxlat = maxlon = -400
        track = []
        start = end = dist = lat1 = lon1 = tim1 = maxele = spd = spd1 = maxspd = 0
        minele = minspd = 1e10
        tm = datetime.now(timezone.utc).timestamp()
        for i, trkpt in enumerate(trkpts):
            lat = float(trkpt.attributes["lat"].value)
            lon = float(trkpt.attributes["lon"].value)
            # establish bounding box
            minlat = min(minlat, lat)
            minlon = min(minlon, lon)
            maxlat = max(maxlat, lat)
            maxlon = max(maxlon, lon)
            try:
                tim = isot2dt(trkpt.getElementsByTagName("time")[0].firstChild.data)
            except IndexError:
                tim = tm + i  # use synthetic timestamp if gpx has no time element
            if i == 0:
                lat1, lon1, tim1 = lat, lon, tim
                start = tim
            else:
                leg = haversine(lat1, lon1, lat, lon)  # km
                dist += leg
                if tim > tim1:
                    spd = leg * 3600 / (tim - tim1)  # km/h
                else:
                    spd = spd1
                spd1 = spd
                maxspd = max(spd, maxspd)
                minspd = min(spd, minspd)
                lat1, lon1, tim1 = lat, lon, tim
                end = tim
            try:
                ele = float(trkpt.getElementsByTagName("ele")[0].firstChild.data)
                maxele = max(ele, maxele)
                minele = min(ele, minele)
            except IndexError:  # 'ele' element does not exist
                ele = 0.0
            track.append(TrackPoint(lat, lon, tim, ele, spd))

        self._bounds = Area(minlat, minlon, maxlat, maxlon)
        self._center = Point((maxlat + minlat) / 2, (maxlon + minlon) / 2)
        elapsed = end - start
        self._track = track
        self._metadata["points"] = rng
        self._metadata["elapsed"] = elapsed
        self._metadata["distance"] = dist
        self._metadata["min_elevation"] = minele
        self._metadata["max_elevation"] = maxele
        self._metadata["min_speed"] = minspd
        self._metadata["max_speed"] = maxspd

        self._draw_map()
        self._draw_profile(self._track)
        self._format_metadata(self._metadata)

    def _val2xy(
        self, width: int, height: int, maxy: int, maxx: int, ele: float, pnt: int
    ) -> tuple:
        """
        Convert elevation & speed values to canvas pixel coordinates (x,y).

        :param int width: width of panel in pixels
        :param int height: height of panel in pixels
        :param int maxy: max extent of y axis
        :param int maxx: max extent of x axis
        :param int ele: elevation value
        :param int pnt: point value
        :return: (x,y)
        :rtype: tuple
        """

        x = AXIS_XL + ((width - AXIS_XL - AXIS_XR) * pnt / maxx)
        y = height - AXIS_Y - ((height - AXIS_Y) * ele / maxy)
        return int(x), int(y)

    def _draw_map(self):
        """
        Draw map on canvas.
        """

        location = self._center
        maptype = self._maptype.get()
        zoom = self._mapzoom.get()
        bounds = self._can_mapview.zoom_bounds(
            self.height, self.width, location, zoom, maptype
        )
        points = [Point(pnt.lat, pnt.lon) for pnt in self._track]
        self._can_mapview.draw_map(
            maptype,
            location=location,
            track=points,
            bounds=bounds,
            zoom=zoom,
            marker=self._can_mapview.marker,
        )

        if self._can_mapview.zoommin:
            self._spn_zoom.config(highlightbackground=ERRCOL, highlightthickness=3)
        else:
            self._spn_zoom.config(highlightbackground="gray90", highlightthickness=3)

    def _draw_profile(
        self, track: list
    ):  # pylint: disable = too-many-branches, too-many-statements
        """
        Plot elevation profile with auto-ranged axes.
        :param list track: list of lat/lon points
        """

        w, h = self._frm_profile.winfo_width(), self._frm_profile.winfo_height()
        fnt = font.Font(size=10)
        if track in ({}, None):
            return

        _, _, ele_u, ele_c, spd_u, spd_c = self._get_units()

        mid = int(len(track) / 2)
        self._can_profile.delete(ALL)
        # find maximum extents for x and y axes
        _, _, tim1, _, _ = self._track[0]  # start point, labelled 1
        _, _, timm, _, _ = self._track[mid]  # mid point
        _, _, tim2, _, _ = self._track[-1]  # end point, labelled 2
        maxx = len(track)
        maxe = self._metadata["max_elevation"] * ele_c
        maxs = self._metadata["max_speed"] * spd_c
        for i in (50, 100, 250, 500, 1000, 2500, 5000, 10000, 25000):
            if maxe < i:
                maxe = i
                break
        for i in (5, 10, 25, 50, 100, 200, 500, 1000):
            if maxs < i:
                maxs = i
                break

        # plot elevation & speed
        x2e = AXIS_XL
        y2e = h - AXIS_Y
        x2s = AXIS_XL
        y2s = h - AXIS_Y
        for i, trk in enumerate(track):
            if trk.ele is not None:
                x1e, y1e = x2e, y2e  # self._val2xy(w, h, maxe, maxx, 0, i)
                x2e, y2e = self._val2xy(w, h, maxe, maxx, trk.ele * ele_c, i)
                if i:
                    self._can_profile.create_line(
                        x1e, y1e, x2e, y2e, fill=ELE_COL, width=2
                    )
            if trk.spd is not None:
                x1s, y1s = x2s, y2s
                x2s, y2s = self._val2xy(w, h, maxs, maxx, trk.spd * spd_c, i)
                if i:
                    self._can_profile.create_line(
                        x1s, y1s, x2s, y2s, fill=SPD_COL, width=1
                    )

        # plot elevation (yL) axis grid
        for ele in range(0, maxe, int(maxe / 5)):
            if ele is not None:
                x1, y1 = self._val2xy(w, h, maxe, maxx, ele, 0)
                x2, y2 = self._val2xy(w, h, maxe, maxx, ele, maxx)
                self._can_profile.create_line(x1, y1, x2 + 1, y1, fill=GRIDCOL)
                self._can_profile.create_text(
                    x1 - 2, y1, text=f"{ele}", fill=ELEAX_COL, font=fnt, anchor=E
                )
        self._can_profile.create_text(
            AXIS_XL - 2,
            h / 2 - 8,
            text=ele_u,
            fill=ELEAX_COL,
            font=fnt,
            anchor=E,
        )

        # plot speed (yR) axis grid
        for spd in range(0, int(maxs), int(maxs / 5)):
            if spd is not None:
                x1, y1 = self._val2xy(w, h, maxs, maxx, spd, maxx)
                x2, y2 = self._val2xy(w, h, maxs, maxx, spd, maxx - 5)
                self._can_profile.create_text(
                    w - AXIS_XR,
                    y1,
                    text=f"{spd}",
                    fill=SPD_COL,
                    font=fnt,
                    anchor=W,
                )
        self._can_profile.create_text(
            w - AXIS_XR + 1,
            h / 2 - 8,
            text=spd_u,
            fill=SPD_COL,
            font=fnt,
            anchor=W,
        )

        # plot trackpoint (X) axis grid
        step = int(maxx / 10) if maxx > 10 else 1
        for n in range(0, maxx, step):
            x1, y1 = self._val2xy(w, h, maxe, maxx, 0, n)
            x2, y2 = self._val2xy(w, h, maxe, maxx, maxe, n)
            self._can_profile.create_line(x1, y1 - 1, x1, y2, fill=GRIDCOL)
            for xtick in (
                (tim1, 0, NW),
                (timm, maxx / 2, N),
                (tim2, maxx, NE),
            ):
                x, y = self._val2xy(w, h, maxe, maxx, 0, xtick[1])
                hms = datetime.fromtimestamp(xtick[0]).strftime("%H:%M:%S")
                self._can_profile.create_text(
                    x,
                    y - 2,
                    text=f"{hms}",
                    fill=GRIDCOL,
                    font=fnt,
                    anchor=xtick[2],
                )

    def _format_metadata(self, metadata: dict) -> str:
        """
        Format metadata as string.
        """

        if metadata in ({}, None):
            return

        dst_u, dst_c, ele_u, ele_c, spd_u, spd_c = self._get_units()

        elapsed = self._metadata["elapsed"] / 3600  # h
        dist = self._metadata["distance"]  # km
        minele = self._metadata["min_elevation"]  # m
        maxele = self._metadata["max_elevation"]  # m
        maxspd = self._metadata["max_speed"]  # km/h

        if maxele == 0 and minele == 1e10:
            ele = "N/A"
        else:
            ele = (
                f"({ele_u}) min: {minele*ele_c:,.2f} max: {maxele*ele_c:,.2f} "
                f"diff: {(maxele-minele)*ele_c:,.2f}"
            )
        metadata = []
        metadata.append(
            (
                f"Dist ({dst_u}): {dist*dst_c:,.2f}; "
                f"Elapsed (hours): {elapsed:,.2f}; "
                f"Speed ({spd_u}) avg: {(dist/elapsed)*spd_c:,.2f} "
                f"max: {maxspd*spd_c:,.2f};"
            )
        )
        metadata.append(f"Elevation {ele}; Points: {self._metadata['points']:,}")
        for i in range(MD_LINES):
            self._info[i].set(metadata[i])

    def _get_units(self) -> tuple:
        """
        Get speed and elevation units and conversions.
        Default is metric.

        :return: tuple of (dst_u, dst_c, ele_u, ele_C, spd_u, spd_c)
        :rtype: tuple
        """

        units = self.__app.configuration.get("units_s")

        if units == UI:
            dst_u = "miles"
            dst_c = KM2MIL
            ele_u = "ft"
            ele_c = M2FT
            spd_u = "mph"
            spd_c = KPH2MPH
        elif units == UIK:
            dst_u = "naut miles"
            dst_c = KM2NMIL
            ele_u = "ft"
            ele_c = M2FT
            spd_u = "knt"
            spd_c = KPH2KNT
        elif units == UMK:
            dst_u = "km"
            dst_c = 1
            ele_u = "m"
            ele_c = 1
            spd_u = "kph"
            spd_c = 1
        else:  # UMM
            dst_u = "m"
            dst_c = KM2M
            ele_u = "m"
            ele_c = 1
            spd_u = "m/s"
            spd_c = KPH2MPS

        return (dst_u, dst_c, ele_u, ele_c, spd_u, spd_c)

    @property
    def metadata(self) -> dict:
        """
        Getter for metadata.
        """

        return self._metadata

    @property
    def track(self) -> str:
        """
        Getter for track.
        """

        return self._track
