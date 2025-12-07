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
import traceback
from statistics import mean, median
from tkinter import (
    ALL,
    EW,
    NSEW,
    Button,
    Frame,
    IntVar,
    Label,
    N,
    Spinbox,
    StringVar,
    W,
)
from xml.dom import minidom
from xml.parsers import expat

from pynmeagps import haversine, planar

from pygpsclient.canvas_map import HYB, MAP, SAT, CanvasMap
from pygpsclient.canvas_plot import CanvasGraph
from pygpsclient.globals import (
    BGCOL,
    CUSTOM,
    ERRCOL,
    FGCOL,
    HOME,
    INFOCOL,
    PLOTCOLS,
    READONLY,
    ROUTE,
    TRACEMODE_WRITE,
    TRACK,
    WAYPOINT,
    Area,
    Point,
    TrackPoint,
)
from pygpsclient.helpers import get_range, get_units, isot2dt
from pygpsclient.strings import (
    DLGGPXERROR,
    DLGGPXLOAD,
    DLGGPXLOADED,
    DLGGPXNOMINAL,
    DLGGPXNULL,
    DLGGPXOPEN,
    DLGGPXWAIT,
    DLGTGPX,
    NA,
)
from pygpsclient.toplevel_dialog import ToplevelDialog

MD_LINES = 3  # number of lines of metadata
MINDIM = (400, 500)

GPXTYPES = {TRACK: "trkpt", WAYPOINT: "wpt", ROUTE: "rtept"}
AXISLBLTAG = "axl"
CHARTMINY = 0
CHANELE = 0
CHANSPD = 1
PLOTCOLS = ("yellow", "cyan", "magenta", "deepskyblue")
YLBLRANGE = {
    0: (50, 100, 250, 500, 1000, 2500, 5000, 10000, 25000),
    1: (5, 10, 25, 50, 100, 200, 500, 1000),
}
OL_WID = 1


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
        self._gpxtype = StringVar()
        zoom = int(kwargs.get("zoom", 12))
        self._mapzoom.set(zoom)
        self._info = []
        for _ in range(MD_LINES):
            self._info.append(StringVar())
        self._mtt = None
        self._mtz = None
        self._mtg = None
        self._mapimg = None
        self._track = None
        self._gpxfile = None
        self._bounds = None
        self._center = None
        self._initdir = HOME
        self._no_time = False
        self._no_ele = False

        # elevation/speed profile parameters
        self._font = self.__app.font_vsm
        self._fonth = self._font.metrics("linespace")
        self._num_chans = 2
        self._plotcols = PLOTCOLS
        self._mintim = 1e20
        self._maxtim = 0
        self._rng = 0
        self._elapsed = 0
        self._dist = 0
        self._minele = self._minspd = 1e20
        self._maxele = self._maxspd = -1e20

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
        self._frm_info = Frame(self._frm_body, borderwidth=2, relief="groove", bg=BGCOL)
        self._frm_controls = Frame(self._frm_body, borderwidth=2, relief="groove")
        self._can_mapview = CanvasMap(
            self.__app,
            self._frm_map,
            height=self.height * 0.75,
            width=self.width,
            bg=BGCOL,
        )
        self._can_profile = CanvasGraph(
            self.__app,
            self._frm_profile,
            height=self.height * 0.25,
            width=self.width,
            bg=BGCOL,
        )
        self._lbl_info = []
        for i in range(MD_LINES):
            fg = PLOTCOLS[i - 1] if i else FGCOL
            self._lbl_info.append(
                Label(
                    self._frm_info,
                    textvariable=self._info[i],
                    anchor=W,
                    bg=BGCOL,
                    fg=fg,
                )
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
        self._spn_gpxtype = Spinbox(
            self._frm_controls,
            values=list(GPXTYPES.keys()),
            width=6,
            wrap=True,
            textvariable=self._gpxtype,
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

        self._frm_body.grid(column=0, row=0, sticky=NSEW)
        self._frm_map.grid(column=0, row=0, sticky=NSEW)
        self._frm_profile.grid(column=0, row=1, sticky=EW)
        self._frm_info.grid(column=0, row=2, sticky=EW)
        self._frm_controls.grid(column=0, row=3, columnspan=7, sticky=EW)
        self._can_mapview.grid(column=0, row=0, sticky=NSEW)
        self._can_profile.grid(column=0, row=0, sticky=NSEW)
        for i in range(MD_LINES):
            self._lbl_info[i].grid(column=0, row=i, padx=1, pady=1, sticky=EW)
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
        self._spn_gpxtype.grid(
            column=3,
            row=1,
            padx=3,
            pady=3,
        )
        self._lbl_zoom.grid(
            column=4,
            row=1,
            padx=3,
            pady=3,
        )
        self._spn_zoom.grid(
            column=5,
            row=1,
            padx=3,
            pady=3,
        )
        self._btn_redraw.grid(
            column=6,
            row=1,
            padx=3,
            pady=3,
        )

        # set column and row weights
        # NB!!! these govern the 'pack' behaviour of the frames on resize
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._frm_body.grid_columnconfigure(0, weight=1)
        self._frm_body.grid_rowconfigure(0, weight=20)  # map
        self._frm_body.grid_rowconfigure(1, weight=1)  # profile
        self._frm_body.grid_rowconfigure(2, weight=0)  # info
        self._frm_map.grid_columnconfigure(0, weight=1)
        self._frm_map.grid_rowconfigure(0, weight=1)
        self._frm_profile.grid_columnconfigure(0, weight=1)
        self._frm_profile.grid_rowconfigure(0, weight=1)

    def _attach_events(self):
        """
        Bind events to window.
        """

        self._mtt = self._maptype.trace_add(TRACEMODE_WRITE, self._on_maptype)
        self._mtz = self._mapzoom.trace_add(TRACEMODE_WRITE, self._on_mapzoom)
        self._mtg = self._gpxtype.trace_add(TRACEMODE_WRITE, self._on_gpxtype)

    def _detach_events(self):
        """
        Unbind events to window.
        """

        if self._mtt is not None:
            self._maptype.trace_remove(TRACEMODE_WRITE, self._mtt)
        if self._mtz is not None:
            self._mapzoom.trace_remove(TRACEMODE_WRITE, self._mtz)
        if self._mtg is not None:
            self._gpxtype.trace_remove(TRACEMODE_WRITE, self._mtg)

    def _reset(self):
        """
        Reset application.
        """

        self._can_mapview.delete(ALL)
        self._can_profile.delete(ALL)
        self._maptype.set(self.__app.configuration.get("gpxmaptype_s"))
        self._mapzoom.set(self.__app.configuration.get("gpxmapzoom_n"))
        self._gpxtype.set(self.__app.configuration.get("gpxtype_s"))
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

    def _on_gpxtype(self, var, index, mode):  # pylint: disable=unused-argument
        """
        GPX type has changed.
        """

        self.__app.configuration.set("gpxtype_s", self._gpxtype.get())

    def _on_redraw(self, *args, **kwargs):
        """
        Handle redraw button press.
        """

        self.status_label = (DLGGPXWAIT, INFOCOL)
        self._detach_events()
        self._reset()
        self._spn_zoom.config(highlightbackground="gray90", highlightthickness=3)
        self._parse_gpx()
        self._draw_map()
        self._draw_profile()
        self._draw_metadata()
        self._attach_events()

    def _open_gpxfile(self) -> str:
        """
        Open gpx file.
        """

        return self.__app.file_handler.open_file(
            self,
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
        self.status_label = (DLGGPXLOAD, INFOCOL)
        self._parse_gpx()

    def _parse_gpx(self):

        if self._gpxfile is None:
            return
        ptyp = GPXTYPES[self._gpxtype.get()]
        with open(self._gpxfile, "r", encoding="utf-8") as gpx:
            try:
                parser = minidom.parse(gpx)
                trkpts = parser.getElementsByTagName(f"{ptyp}")
                self._process_track(trkpts, ptyp)
            except (TypeError, AttributeError, expat.ExpatError) as err:
                self.status_label = (f"{DLGGPXERROR}\n{repr(err)}", ERRCOL)
                self.logger.error(traceback.format_exc())

    def _process_track(self, trkpts: list, ptyp: str):
        """
        Process trackpoint data.

        :param list trk: list of trackpoints
        :param str ptyp: element type
        """

        self._rng = len(trkpts)
        self._no_time = False
        self._no_ele = False
        if self._rng == 0:
            self.status_label = (DLGGPXNULL.format(ptyp), ERRCOL)
            return

        minlat = minlon = 400
        maxlat = maxlon = -400
        track = []
        start = end = 0
        self._dist = 0
        lat1 = lon1 = 0
        tm = tim1 = spd = spd1 = 0
        self._minele = self._minspd = 1e10
        self._maxele = self._maxspd = -1e20
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
            except IndexError:  # time element does not exist
                self._no_time = True
                tim = tm + i  # use synthetic timestamp if gpx has no time element
            if i == 0:
                lat1, lon1, tim1 = lat, lon, tim
                start = tim
            else:
                leg = planar(lat1, lon1, lat, lon)  # m
                if leg > 1000:
                    leg = haversine(lat1, lon1, lat, lon) / 1000  # m
                self._dist += leg
                if tim > tim1:
                    spd = leg / (tim - tim1)  # m/s
                else:
                    spd = spd1
                spd1 = spd
                self._maxspd = max(spd, self._maxspd)
                self._minspd = min(spd, self._minspd)
                lat1, lon1, tim1 = lat, lon, tim
                end = tim
            try:
                ele = float(trkpt.getElementsByTagName("ele")[0].firstChild.data)
                self._maxele = max(ele, self._maxele)
                self._minele = min(ele, self._minele)
            except IndexError:  # 'ele' element does not exist
                self._no_ele = True
                ele = 0.0

            track.append(TrackPoint(lat, lon, tim, ele, spd))

        self._bounds = Area(minlat, minlon, maxlat, maxlon)
        self._center = Point((maxlat + minlat) / 2, (maxlon + minlon) / 2)
        self._elapsed = end - start
        self._mintim = start
        self._maxtim = end
        self._track = track

        self._draw_map()
        self._draw_profile()
        self._draw_metadata()
        self.status_label = (DLGGPXLOADED, INFOCOL)

    def _draw_map(self):
        """
        Draw map on canvas.
        """

        if self._track is None:
            return
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

    def _draw_profile(self):
        """
        Update elevation/speed profile with data.
        """

        # pylint: disable=no-member

        if self._track is None:
            return

        _, _, ele_u, ele_c, spd_u, spd_c = get_units(
            self.__app.configuration.get("units_s")
        )
        maxele = get_range(self._maxele * ele_c, YLBLRANGE[CHANELE])
        maxspd = get_range(self._maxspd * spd_c, YLBLRANGE[CHANSPD])

        # Initialise graph
        self._can_profile.delete(ALL)
        self._can_profile.create_graph(
            xdatamax=self._maxtim,
            xdatamin=self._mintim,
            ydatamax=(maxele, maxspd),
            ydatamin=(CHARTMINY, CHARTMINY),
            xtickmaj=5,
            xtickmin=15,
            ytickmaj=2,
            ytickmin=10,
            xdp=0,
            ydp=(0, 0),
            xlegend="time",
            xtimeformat="%H:%M:%S",
            xcol=FGCOL,
            ylegend=(f"hmsl ({ele_u})", f"spd ({spd_u})"),
            ycol=(
                PLOTCOLS[CHANELE],
                PLOTCOLS[CHANSPD],
            ),
            xlabels=True,
            ylabels=True,
            fontscale=10,
        )

        # plot each channel's data points
        for chn in range(self._num_chans):
            tm2 = self._mintim
            vl2 = 0
            for n, pnt in enumerate(self._track):
                try:
                    val = pnt.ele * ele_c if chn == CHANELE else pnt.spd * spd_c
                except KeyError:
                    val = None
                if val is None:
                    continue

                tm1, vl1 = tm2, vl2
                tm2, vl2 = pnt.tim, val
                if n:
                    self._can_profile.create_gline(
                        tm1,
                        vl1,
                        tm2,
                        vl2,
                        fill=self._can_profile.ycol[chn],
                        width=OL_WID,
                        chn=chn,
                        tags="spd" if chn else "ele",
                    )

        if self._no_time:
            self._timelegend()

    def _timelegend(self):
        """
        Draw nominal time legend.
        """

        # pylint: disable = no-member

        self._can_profile.create_text(
            self._can_profile.winfo_width() / 2,
            2,
            text=DLGGPXNOMINAL,
            fill=FGCOL,
            font=self._can_profile.font,
            anchor=N,
            tags=AXISLBLTAG,
        )

    def _draw_metadata(self) -> str:
        """
        Draw metadata as lines of text.
        """

        if self._rng == 0:
            return

        dst_u, dst_c, ele_u, ele_c, spd_u, spd_c = get_units(
            self.__app.configuration.get("units_s")
        )

        if self._elapsed > 3600:
            elapsed = self._elapsed / 3600
            elp_u = "hours"
        else:
            elapsed = self._elapsed
            elp_u = "seconds"
        self._info[0].set(
            (
                f"Track elements: {self._rng:,}; "
                f"Distance ({dst_u}): {self._dist*dst_c:,.2f}; "
                f"Elapsed ({elp_u}): {elapsed:,.2f}"
            )
        )

        if self._no_ele:
            ele = NA
        else:
            elelist = [i.ele * ele_c for i in self._track]
            ele_median = median(elelist)
            ele_mean = mean(elelist)
            ele_min = min(elelist)
            ele_max = max(elelist)
            ele = (
                f"({ele_u}) min: {ele_min:,.2f} "
                f"max: {ele_max:,.2f} "
                f"avg: {ele_mean:,.2f} med: {ele_median:,.2f} "
                f"dif: {(ele_max-ele_min):,.2f}"
            )
        self._info[1].set(f"Ele {ele}")

        if self._no_time:
            spd = NA
        else:
            spdlist = [i.spd * spd_c for i in self._track]
            spd_median = median(spdlist)
            spd_mean = mean(spdlist)
            spd_min = min(spdlist)
            spd_max = max(spdlist)
            spd = (
                f"({spd_u}) min: {spd_min:,.2f} "
                f"max: {spd_max:,.2f} "
                f"avg: {spd_mean:,.2f} med: {spd_median:,.2f}"
            )
        self._info[2].set(f"Spd {spd}")
