"""
scatter_frame.py

Scatterplot frame class for PyGPSClient Application.

This generates a scatterplot of positions, centered on either
the cumulative average position or a fixed reference position.

The fixed reference position can be stored in the json
configuration file as `scatterlat_f`/`scatterlon_f`.

Created 23 March 2023

Completely rewritten by semuadmin 5 Nov 2024 to use bounding
box rather than polar coordinations, and allow right-click
fixed reference selection.

:author: Nathan Michaels, semuadmin
:copyright: 2024 SEMU Consulting
:license: BSD 3-Clause
"""

from tkinter import (
    ALL,
    HORIZONTAL,
    NW,
    Canvas,
    Checkbutton,
    E,
    Entry,
    Frame,
    IntVar,
    N,
    S,
    Scale,
    Spinbox,
    StringVar,
    TclError,
    W,
)

try:
    from statistics import fmean, stdev

    HASSTATS = True
except (ImportError, ModuleNotFoundError):
    HASSTATS = False

from random import randrange

from pygpsclient.globals import (
    BGCOL,
    FGCOL,
    PNTCOL,
    RPTDELAY,
    SQRT2,
    WIDGETU1,
    Area,
    Point,
)
from pygpsclient.helpers import (
    fontheight,
    get_point_at_vector,
    in_bounds,
    ll2xy,
    reorder_range,
    scale_font,
    xy2ll,
)

AVG = "avg"
CTRAVG = "Average"
CTRFIX = "Fixed"
CRTS = (CTRAVG, CTRFIX)
INTS = (1, 2, 5, 10, 20, 50, 100)
FIXCOL = "green2"
PNTTOPCOL = "red"
CULLMID = True  # whether to cull random points from middle of array
FIXINAUTO = False  # whether to include fixed ref point in autorange
MAXPOINTS = 2000
PNT = "pnt"
STDINT = 10  # standard deviation calculation interval


class ScatterViewFrame(Frame):
    """
    Scatterplot view frame class.
    """

    def __init__(self, app, *args, **kwargs):
        """
        Constructor.

        :param Frame app: reference to main tkinter application
        :param args: Optional args to pass to Frame parent class
        :param kwargs: Optional kwargs to pass to Frame parent class
        """
        self.__app = app
        self.__master = self.__app.appmaster

        Frame.__init__(self, self.__master, *args, **kwargs)

        def_w, def_h = WIDGETU1

        self.width = kwargs.get("width", def_w)
        self.height = kwargs.get("height", def_h)
        self._font = self.__app.font_sm
        self._fonth = fontheight(self._font)
        self._maxpoints = 0
        self._points = []
        self._average = None
        self._stddev = None
        self._fixed = None
        self._bounds = None
        self._minlat = 100
        self._minlon = 200
        self._maxlat = -100
        self._maxlon = -200
        self._updcount = -1
        self._lastbounds = Area(0, 0, 0, 0)
        self._range = 0.0
        self._autorange = IntVar()
        self._interval = IntVar()
        self._centermode = StringVar()
        self._scale = IntVar()
        self._reflat = StringVar()
        self._reflon = StringVar()
        self._scale_factors = (
            5000,
            2000,
            1000,
            500,
            200,
            100,
            50,
            20,
            10,
            5,
            2,
            1,
            0.5,
            0.2,
            0.1,
            0.05,
            0.02,
            0.01,
        )  # scale factors represent plot radius in meters

        self._body()
        self.reset()
        self._attach_events()

    def _body(self):
        """Set up frame and widgets."""

        for i in range(3):
            self.grid_columnconfigure(i, weight=1, uniform="ent")
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=0)
        self.canvas = Canvas(self, width=self.width, height=self.height, bg=BGCOL)
        self._ent_reflat = Entry(
            self,
            width=12,
            textvariable=self._reflat,
            fg=FIXCOL,
            bg=BGCOL,
        )
        self._ent_reflon = Entry(
            self,
            width=12,
            textvariable=self._reflon,
            fg=FIXCOL,
            bg=BGCOL,
        )
        self._chk_autorange = Checkbutton(
            self,
            text="Autorange",
            fg=PNTCOL,
            bg=BGCOL,
            variable=self._autorange,
        )
        crng = reorder_range(CRTS, self._centermode.get())
        self._spn_center = Spinbox(
            self,
            values=crng,
            width=8,
            wrap=True,
            repeatdelay=RPTDELAY,
            repeatinterval=RPTDELAY,
            fg=PNTCOL,
            bg=BGCOL,
            readonlybackground=BGCOL,
            textvariable=self._centermode,
            state="readonly",
        )
        irng = reorder_range(INTS, self._interval.get())
        self._spn_interval = Spinbox(
            self,
            values=irng,
            width=5,
            wrap=True,
            repeatdelay=RPTDELAY,
            repeatinterval=RPTDELAY,
            fg=PNTCOL,
            bg=BGCOL,
            readonlybackground=BGCOL,
            textvariable=self._interval,
            state="readonly",
        )
        self._scl_range = Scale(
            self,
            from_=0,
            to=len(self._scale_factors) - 1,
            orient=HORIZONTAL,
            bg=FGCOL,
            troughcolor=BGCOL,
            variable=self._scale,
            showvalue=False,
        )
        self.canvas.grid(column=0, row=0, columnspan=3, sticky=(N, S, E, W))
        self._ent_reflat.grid(column=0, row=1, sticky=(W, E))
        self._ent_reflon.grid(column=1, row=1, sticky=(W, E))
        self._spn_center.grid(column=2, row=1, sticky=(W, E))
        self._chk_autorange.grid(column=0, row=2, sticky=(W, E))
        self._spn_interval.grid(column=1, row=2, sticky=(W, E))
        self._scl_range.grid(column=2, row=2, sticky=(W, E))

    def reset(self):
        """
        Reset settings to saved configuration.
        """

        self._maxpoints = MAXPOINTS
        cfg = self.__app.configuration.get("scattersettings_d")
        reflat = cfg.get("scatterlat_f")
        reflon = cfg.get("scatterlon_f")
        self._reflat.set("Reference Lat" if reflat == 0.0 else reflat)
        self._reflon.set("Reference Lon" if reflon == 0.0 else reflon)
        self._autorange.set(cfg.get("scatterautorange_b"))
        self._scale.set(cfg.get("scatterscale_n"))
        self._interval.set(cfg.get("scatterinterval_n"))
        self._centermode.set(cfg.get("scattercenter_s"))
        if self._centermode.get() != CTRFIX:
            self._centermode.set(CTRAVG)

    def _attach_events(self):
        """
        Bind events to frame.
        """

        self.bind("<Configure>", self._on_resize)
        self.canvas.bind("<Double-Button-1>", self._on_clear)
        self.canvas.bind("<Button-2>", self._on_recenter)  # mac
        self.canvas.bind("<Button-3>", self._on_recenter)  # win
        self.canvas.bind("<MouseWheel>", self._on_zoom)
        self._scale.trace_add("write", self._on_rescale)
        for setting in (
            self._autorange,
            self._interval,
            self._centermode,
            self._reflat,
            self._reflon,
        ):
            setting.trace_add("write", self._on_update_config)

    def _on_zoom(self, event):
        """
        Adjust scale using mousewheel.

        :param event: mousewheel event
        """

        sl = len(self._scale_factors) - 1
        sc = self._scale.get()
        if event.delta > 0:
            if sc < sl:
                self._scale.set(sc + 1)
        elif event.delta < 0:
            if sc > 0:
                self._scale.set(sc - 1)

    def _on_rescale(self, var, index, mode):  # pylint: disable=unused-argument
        """
        Rescale widget.
        """

        self._on_update_config(var, index, mode)
        self._on_resize(None)

    def _on_recenter(self, event):
        """
        Right click centers on cursor.

        :param Event event: right click event
        """

        w, h = self.get_size()
        pos = xy2ll(w, h, self._bounds, (event.x, event.y))
        self._reflat.set(round(pos.lat, 9))
        self._reflon.set(round(pos.lon, 9))
        try:
            self._fixed = Point(float(self._reflat.get()), float(self._reflon.get()))
        except ValueError:
            pass

    def _on_clear(self, event):  # pylint: disable=unused-argument
        """ "
        Clear plot.

        :param Event event: double-click event
        """

        self._points = []
        self._minlat = 100
        self._minlon = 200
        self._maxlat = -100
        self._maxlon = -200
        self._updcount = -1
        self._init_frame()

    def _on_update_config(self, var, index, mode):  # pylint: disable=unused-argument
        """
        Update in-memory configuration if setting is changed.
        """

        try:
            self.update()
            sst = {}
            sst["maxpoints_n"] = int(self._maxpoints)
            sst["scatterautorange_b"] = int(self._autorange.get())
            sst["scattercenter_s"] = self._centermode.get()
            sst["scatterinterval_n"] = int(self._interval.get())
            sst["scatterscale_n"] = int(self._scale.get())
            sst["scatterlat_f"] = float(self._reflat.get())
            sst["scatterlon_f"] = float(self._reflon.get())
            self.__app.configuration.set("scattersettings_d", sst)
        except (ValueError, TclError):
            pass

    def _init_frame(self):
        """
        Initialize scatter plot.
        """

        width, height = self.get_size()
        self.canvas.delete(ALL)
        self.canvas.create_line(0, height / 2, width, height / 2, fill=FGCOL)
        self.canvas.create_line(width / 2, 0, width / 2, height, fill=FGCOL)

        if self._bounds is None:
            return

        maxr = min(height / 2, width / 2)
        for i in range(1, 5):
            self.canvas.create_circle(
                width / 2, height / 2, maxr * i / 4, outline=FGCOL, width=1
            )
            rng, unt = self.get_range_label()
            if rng >= 100:
                dp = 0
            elif rng >= 10:
                dp = 1
            elif rng >= 1:
                dp = 2
            else:
                dp = 3
            dist = f"{rng * i/4:.{dp}f}{unt}"
            txt_x = width / 2 + SQRT2 * maxr * i / 4
            txt_y = height / 2 + SQRT2 * maxr * i / 4
            self.canvas.create_text(
                txt_x, txt_y, text=dist, fill=FGCOL, font=self._font
            )

        for x, y, anc in (
            (width / 2, 5, N),
            (width / 2, height - 5, S),
            (5, height / 2, W),
            (width - 5, height / 2, E),
        ):
            self.canvas.create_text(
                x, y, text=anc.upper(), fill=FGCOL, font=self._font, anchor=anc
            )

    def _draw_stats(self, lbl_font: object):
        """
        Draw the stats in the corner of the plot.

        :param font lbl_font: Font to use.
        """

        if self._average is None:
            return

        self.canvas.delete(AVG)
        y = 5
        fh = self._fonth
        avg = f"Avg: {self._average.lat:.9f}, {self._average.lon:.9f}"
        self.canvas.create_text(
            5, y, text=avg, fill=PNTCOL, font=lbl_font, anchor=NW, tags=AVG
        )
        y += fh
        if self._stddev is not None:
            std = f"Std: {self._stddev.lat:.3e}, {self._stddev.lon:.3e}"
            self.canvas.create_text(
                5, y, text=std, fill=PNTCOL, font=lbl_font, anchor=NW, tags=AVG
            )
            y += fh
        np = len(self._points)
        pts = f"Pts: {np} {'!' if np >= self._maxpoints else ''}"
        self.canvas.create_text(
            5, y, text=pts, fill=PNTCOL, font=lbl_font, anchor=NW, tags=AVG
        )

    def _draw_point(self, position: Point, color: str = PNTCOL, size: int = 2):
        """
        Draw a point on the scatterplot.

        :param Point position: The point to draw
        :param str color: point color as string e.g. "orange"
        :param int size: size of circle (2)
        """

        if not in_bounds(self._bounds, position):
            return

        w, h = self.get_size()
        x, y = ll2xy(w, h, self._bounds, position)
        self.canvas.create_circle(x, y, size, fill=color, outline=color, tags=PNT)

    def _set_average(self):
        """
        Calculate the mean and standard deviation of all the lat/lon
        pairs visible on the scatter plot. Note that this will make
        for some weird results near poles.
        """

        lp = len(self._points)
        if HASSTATS and lp > 1:
            ave_lat = fmean(p.lat for p in self._points)
            ave_lon = fmean(p.lon for p in self._points)
            if not lp % STDINT:
                self._stddev = Point(
                    stdev(p.lat for p in self._points),
                    stdev(p.lon for p in self._points),
                )
        else:
            ave_lat = sum(p.lat for p in self._points) / lp
            ave_lon = sum(p.lon for p in self._points) / lp

        self._average = Point(ave_lat, ave_lon)

    def _set_bounds(self, center: Point):
        """
        Set bounding box of canvas baed on center point and
        plot range.

        :param Point center: centre of bounding box
        """

        cw, ch = self.get_size()
        disth = self._scale_factors[self._scale.get()]
        distw = self._scale_factors[self._scale.get()] * cw / ch
        t = get_point_at_vector(center, disth, 0)
        r = get_point_at_vector(center, distw, 90)
        b = get_point_at_vector(center, disth, 180)
        l = get_point_at_vector(center, distw, 270)
        self._bounds = Area(b.lat, l.lon, t.lat, r.lon)
        self._range = disth

        if self._bounds != self._lastbounds:
            self._init_frame()
            self._lastbounds = self._bounds

    def get_range_label(self) -> tuple:
        """
        Set range value and units according to magnitude.

        :return: range, units
        :rtype: tuple
        """

        if self._range >= 1000:
            rng = self._range / 1000
            unt = "km"
        elif self._range >= 1:
            rng = self._range
            unt = "m"
        else:
            rng = self._range * 100
            unt = "cm"
        return rng, unt

    def _redraw(self):
        """
        Redraw all the points on the scatter plot.
        """

        if not self._points:
            return

        self.canvas.delete(PNT)
        lp = len(self._points) - 1
        for i, pnt in enumerate(self._points):
            if i == lp:
                break
            self._draw_point(pnt, PNTCOL)
        if self._fixed is not None:
            self._draw_point(self._fixed, FIXCOL, 3)
        self._draw_point(self._points[-1], PNTTOPCOL)

        self._draw_stats(self._font)

    def update_frame(self):
        """
        Collect scatterplot data and update the plot.
        """

        self._updcount = (self._updcount + 1) % self._interval.get()
        if self._updcount:  # plot at every nth update
            return

        lat, lon = self.__app.gnss_status.lat, self.__app.gnss_status.lon
        try:
            lat = float(lat)
            lon = float(lon)
        except ValueError:
            return  # Invalid values for lat/lon get ignored.

        if lat == 0.0 and lon == 0.0:  # assume no fix
            return
        pos = Point(lat, lon)

        if self._points and pos == self._points[-1]:
            return  # Don't repeat exactly the last point.

        self._points.append(pos)
        if len(self._points) > self._maxpoints:
            self._cull_points()

        self._set_average()

        # set plot bounds based on range and center point
        middle = self._average
        try:
            self._fixed = Point(float(self._reflat.get()), float(self._reflon.get()))
            if self._centermode.get() == CTRFIX:
                middle = self._fixed
        except ValueError:
            self._fixed = None
            self._centermode.set(CTRAVG)
        self._set_bounds(middle)

        # update plotted point bounds
        self._minlat = min(lat, self._minlat)
        self._maxlat = max(lat, self._maxlat)
        self._minlon = min(lon, self._minlon)
        self._maxlon = max(lon, self._maxlon)
        if self._autorange.get():
            self._do_autorange(middle)

        self._redraw()

    def _cull_points(self):
        """
        Limit number of points in in-memory array.
        """

        if CULLMID:  # cull randomly from middle
            self._points.pop(randrange(1, len(self._points) - 100))
        else:  # cull from start
            self._points.pop(0)

    def _do_autorange(self, middle: Point):
        """
        Adjust range until all points in bounds.

        :param Point middle: center point of plot
        """

        out = True
        while out and self._scale.get() > 0:
            out = False

            # include fixed reference point in autorange
            if FIXINAUTO and not out and self._fixed is not None:
                if not in_bounds(self._bounds, self._fixed):
                    out = True
            if not out:
                if not in_bounds(
                    self._bounds, Point(self._minlat, self._minlon)
                ) or not in_bounds(self._bounds, Point(self._maxlat, self._maxlon)):
                    out = True
            if out:
                self._scale.set(self._scale.get() - 1)
                self._set_bounds(middle)

    def _on_resize(self, event):  # pylint: disable=unused-argument
        """
        Resize frame.

        :param Event event: resize event
        """

        self.width, self.height = self.get_size()
        self._font, self._fonth = scale_font(self.width, 10, 25, 20)
        self._init_frame()
        self._redraw()

    def get_size(self) -> tuple:
        """
        Get current canvas size.

        :return: window size (width, height)
        :rtype: tuple
        """

        self.update_idletasks()  # Make sure we know about resizing
        return self.canvas.winfo_width(), self.canvas.winfo_height()
