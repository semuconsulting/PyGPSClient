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
    NE,
    NW,
    SE,
    SW,
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
)
from xml.dom import minidom
from xml.parsers import expat

from pynmeagps import haversine, planar

from pygpsclient.globals import (
    AXISCOL,
    BGCOL,
    CUSTOM,
    ERRCOL,
    FGCOL,
    GRIDCOL,
    HOME,
    INFOCOL,
    M2FT,
    M2KM,
    M2MIL,
    M2NMIL,
    MPS2KNT,
    MPS2KPH,
    MPS2MPH,
    READONLY,
    ROUTE,
    TRACK,
    UI,
    UIK,
    UMK,
    WAYPOINT,
    Area,
    AreaXY,
    Point,
    TrackPoint,
)
from pygpsclient.helpers import (
    data2xy,
    fontheight,
    get_grid,
    isot2dt,
    time2str,
)
from pygpsclient.map_canvas import HYB, MAP, SAT, MapCanvas
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

# profile chart parameters:
AXIS_XL = 35  # x axis left offset
AXIS_XR = 35  # x axis right offset
AXIS_Y = 15  # y axis bottom offset
ELEAX_COL = "green4"  # color of elevation plot axis
ELE_COL = "palegreen3"  # color of elevation plot
SPD_COL = "coral"  # color of speed plot
TRK_COL = "magenta"  # color of track
MD_LINES = 3  # number of lines of metadata
MINDIM = (400, 500)

GPXTYPES = {TRACK: "trkpt", WAYPOINT: "wpt", ROUTE: "rtept"}
AXISTAG = "axt"
AXISLBLTAG = "axl"
ERRCOL = "coral"
LBLCOL = "white"
CONTRASTCOL = "black"
CHARTMINY = 0
CHARTMAXY = 100
CHARTSCALE = 1
MAXCHANS = 2
CHANELE = 0
CHANSPD = 1
RESFONT = 28  # font size relative to widget size
MINFONT = 8  # minimum font size
PLOTWID = 1
PLOTCOLS = ("yellow", "cyan", "magenta", "deepskyblue")
GRIDMINCOL = "grey30"
LBLGRID = 5
GRIDSTEPS = get_grid(5)
XLBLSTEPS = get_grid(LBLGRID)
YLBLSTEPS = get_grid(3)
YLBLRANGE = {
    0: (50, 100, 250, 500, 1000, 2500, 5000, 10000, 25000),
    1: (5, 10, 25, 50, 100, 200, 500, 1000),
}


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
        self._fonth = fontheight(self._font)
        self._num_chans = 2
        self._xoff = 20  # chart X offset for labels
        self._yoff = 20  # chart Y offset for labels
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
        self._init_profile()
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

        self._frm_body.grid(column=0, row=0, sticky=(N, S, E, W))
        self._frm_map.grid(column=0, row=0, sticky=(N, S, E, W))
        self._frm_profile.grid(column=0, row=1, sticky=(W, E))
        self._frm_info.grid(column=0, row=2, sticky=(W, E))
        self._frm_controls.grid(column=0, row=3, columnspan=7, sticky=(W, E))
        self._can_mapview.grid(column=0, row=0, sticky=(N, S, E, W))
        self._can_profile.grid(column=0, row=0, sticky=(N, S, E, W))
        for i in range(MD_LINES):
            self._lbl_info[i].grid(column=0, row=i, padx=1, pady=1, sticky=(W, E))
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

        self._mtt = self._maptype.trace_add("write", self._on_maptype)
        self._mtz = self._mapzoom.trace_add("write", self._on_mapzoom)
        self._mtg = self._gpxtype.trace_add("write", self._on_gpxtype)

    def _detach_events(self):
        """
        Unbind events to window.
        """

        if self._mtt is not None:
            self._maptype.trace_remove("write", self._mtt)
        if self._mtz is not None:
            self._mapzoom.trace_remove("write", self._mtz)
        if self._mtg is not None:
            self._gpxtype.trace_remove("write", self._mtg)

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

        self.set_status(DLGGPXWAIT, INFOCOL)
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
                self.set_status(f"{DLGGPXERROR}\n{repr(err)}", ERRCOL)
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
            self.set_status(DLGGPXNULL.format(ptyp), ERRCOL)
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
        self.set_status(DLGGPXLOADED, INFOCOL)

    def _get_units(self) -> tuple:
        """
        Get speed and elevation units and conversions.
        Default is metric - meters and meters per second.

        :return: tuple of (dst_u, dst_c, ele_u, ele_C, spd_u, spd_c)
        :rtype: tuple
        """

        units = self.__app.configuration.get("units_s")

        if units == UI:
            dst_u = "miles"
            dst_c = M2MIL
            ele_u = "ft"
            ele_c = M2FT
            spd_u = "mph"
            spd_c = MPS2MPH
        elif units == UIK:
            dst_u = "naut miles"
            dst_c = M2NMIL
            ele_u = "ft"
            ele_c = M2FT
            spd_u = "knt"
            spd_c = MPS2KNT
        elif units == UMK:
            dst_u = "km"
            dst_c = M2KM
            ele_u = "m"
            ele_c = 1
            spd_u = "kph"
            spd_c = MPS2KPH
        else:  # UMM
            dst_u = "m"
            dst_c = 1
            ele_u = "m"
            ele_c = 1
            spd_u = "m/s"
            spd_c = 1

        return dst_u, dst_c, ele_u, ele_c, spd_u, spd_c

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

    def _init_profile(self):
        """
        Initialise elevation/speed profile.
        """

        self.update_idletasks()  # Make sure we know about any resizing
        w, h = self._can_profile.winfo_width(), self._can_profile.winfo_height()
        self._xoff = self._fonth * self._num_chans / 2 + 3  # chart X offset for labels
        self._yoff = self._fonth + 3  # chart Y offset for labels
        self._can_profile.delete(ALL)

        # draw grid
        for i, p in enumerate(GRIDSTEPS):
            y = (h - self._yoff) * p
            col = AXISCOL if p in (0, 1.0) else GRIDMINCOL if i % LBLGRID else GRIDCOL
            self._can_profile.create_line(
                self._xoff, y, w - self._xoff, y, fill=col, tags=AXISTAG
            )
            x = self._xoff + (w - self._xoff * 2) * p
            self._can_profile.create_line(
                x, 0, x, h - self._yoff, fill=col, tags=AXISTAG
            )

    def _draw_profile(self):
        """
        Update elevation/speed profile with data.
        """

        if self._track is None:
            return
        self._init_profile()

        w, h = self._can_profile.winfo_width(), self._can_profile.winfo_height()
        _, _, ele_u, ele_c, spd_u, spd_c = self._get_units()

        # set default ranges for all channels
        minval = [CHARTMINY] * self._num_chans
        maxval = [CHARTMAXY] * self._num_chans
        scale = [CHARTSCALE] * self._num_chans
        label = [""] * self._num_chans
        scale[CHANELE] = ele_c
        label[CHANELE] = f"hmsl ({ele_u})"
        scale[CHANSPD] = spd_c
        label[CHANSPD] = f"speed ({spd_u})"

        # get X axis (time) range for all channels and draw labels
        mintim, maxtim = self._mintim, self._maxtim
        bounds = AreaXY(mintim, CHARTMINY, maxtim, CHARTMAXY)
        self._can_profile.delete(AXISLBLTAG)
        self._draw_xaxis_labels(w, h, bounds, mintim, maxtim)

        # plot each channel's data points
        for chn in range(self._num_chans):

            chncol = self._plotcols[chn]
            minval[chn] = 0
            # autorange max y values
            if chn == CHANELE:
                for i in YLBLRANGE[chn]:
                    if self._maxele * ele_c < i:
                        maxval[chn] = i
                        break
            elif chn == CHANSPD:
                for i in YLBLRANGE[chn]:
                    if self._maxspd * spd_c < i:
                        maxval[chn] = i
                        break

            bounds = AreaXY(mintim, minval[chn], maxtim, maxval[chn])

            # draw Y axis (data value) labels for this channel
            self._draw_yaxis_labels(
                w, h, bounds, minval[chn], maxval[chn], chn, label[chn]
            )

            # plot each track element
            inr = False
            for pnt in self._track:
                tim = pnt.tim
                try:
                    val = pnt.ele if chn == CHANELE else pnt.spd
                except KeyError:
                    val = None

                if val is None:
                    continue

                if scale[chn] != 1:
                    val *= scale[chn]  # scale data

                # convert datapoint to canvas x,y coordinates
                x, y = data2xy(
                    w - self._xoff * 2,
                    h - self._yoff,
                    bounds,
                    tim,
                    val,
                    self._xoff,
                )
                if x <= self._xoff:
                    inr = False
                # plot line
                if inr:
                    x2, y2 = x, y
                    self._can_profile.create_line(
                        x1,
                        y1,
                        x2,
                        y2,
                        fill=chncol,
                        width=PLOTWID,
                        tags=f"plot_{chn:1d}",
                    )
                    x1, y1 = x2, y2
                else:
                    x1, y1 = max(x, self._xoff), y
                inr = True

        if self._no_time:
            self._timelegend(w)

    def _draw_xaxis_labels(
        self, w: int, h: int, bounds: AreaXY, mintim: float, maxtim: float
    ):
        """
        Draw X axis (time) labels.

        :param int w: canvas width
        :param int h: canvas height
        :param AreaXY bounds: data bounds
        :param float mintim: minimum time
        :param float maxtim: maximum time
        """
        # pylint: disable=too-many-arguments, too-many-positional-arguments

        for g in XLBLSTEPS:
            xval = mintim + (maxtim - mintim) * g
            x, _ = data2xy(w - self._xoff * 2, h - self._yoff, bounds, xval, 0)
            if g == 0:
                anc = NW
            elif g == 1:
                anc = NE
            else:
                anc = N
            self._can_profile.create_text(
                x + self._xoff,
                h - self._yoff,
                text=time2str(xval),
                anchor=anc,
                fill=AXISCOL,
                font=self._font,
                tags=AXISLBLTAG,
            )

    def _draw_yaxis_labels(
        self,
        w: int,
        h: int,
        bounds: AreaXY,
        minval: float,
        maxval: float,
        chn: int,
        lbl: str,
    ):
        """
        Draw Y axis (data value) labels for this channel.

        :param int w: canvas width
        :param int h: canvas height
        :param AreaXY bounds: data bounds
        :param float minval: minimum val for chn
        :param float maxval: maximum val for chn
        :param int chn: channel
        """
        # pylint: disable=too-many-arguments, too-many-positional-arguments

        col = self._plotcols[chn]
        yo = 2  # avoid edges
        # y axis labels alternate left and right
        if chn % 2:  # odd channels
            x = w - yo - self._fonth * ((chn - 1) / 2)
        else:  # even channels
            x = yo + self._fonth * (chn / 2)

        for g in YLBLSTEPS:
            yval = minval + (maxval - minval) * g
            _, y = data2xy(
                w - self._xoff * MAXCHANS / 2, h - self._yoff, bounds, 0, yval
            )
            if g == 0:
                anc = SW if chn % 2 else NW
            elif g == 1:
                y += yo * 2  # avoid edges
                anc = SE if chn % 2 else NE
            else:
                anc = S if chn % 2 else N
            self._can_profile.create_text(
                x,
                y,
                text=int(yval),
                fill=col,
                font=self._font,
                angle=90,
                anchor=anc,
                tags=AXISLBLTAG,
            )

        # legend
        self._can_profile.create_text(
            w - yo * 2 - self._fonth if chn % 2 else yo * 2 + self._fonth,
            2,
            text=lbl,
            fill=self._plotcols[chn],
            font=self._font,
            anchor=NE if chn % 2 else NW,
            tags=AXISLBLTAG,
        )

    def _timelegend(self, w: int):
        """
        Draw nominal time legend.
        """

        self._can_profile.create_text(
            w / 2,
            2,
            text=DLGGPXNOMINAL,
            fill=AXISCOL,
            font=self._font,
            anchor=N,
            tags=AXISLBLTAG,
        )

    def _draw_metadata(self) -> str:
        """
        Draw metadata as lines of text.
        """

        if self._rng == 0:
            return

        dst_u, dst_c, ele_u, ele_c, spd_u, spd_c = self._get_units()

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
