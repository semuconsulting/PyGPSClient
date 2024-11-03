"""
scatter_frame.py

Scatterplot frame class for PyGPSClient Application.

This generates a scatterplot of positions, centered on either
the cumulative average position or a fixed reference position.

The fixed reference position can be stored in the json
configuration file as `scatterlat_f`/`scatterlon_f`.

Created 23 March 2023

Amended by semuadmin on 4 April 2023 to eliminate dependency on
statistics and geographiclib libraries.

:author: Nathan Michaels, semuadmin
:copyright: Qualinx B.V.
:license: BSD 3-Clause
"""

from collections import namedtuple
from math import cos, radians, sin
from tkinter import (
    HORIZONTAL,
    E,
    Entry,
    Frame,
    IntVar,
    N,
    S,
    Scale,
    Spinbox,
    StringVar,
    W,
    font,
)

from pynmeagps import bearing, haversine, planar

from pygpsclient.globals import BGCOL, FGCOL, WIDGETU2
from pygpsclient.skyview_frame import Canvas

PLANAR = "Planar"
HAVERSINE = "Great Circle"
MODES = (PLANAR, HAVERSINE)
CTRDYN = "Dynamic"
CTRFIX = "Fixed"
CRTS = (CTRDYN, CTRFIX)
PNTCOL = "orange"
FIXCOL = "green2"
SQRT2 = 0.7071067811865476

Point = namedtuple("Point", ["lat", "lon"])


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
        config = self.__app.saved_config

        Frame.__init__(self, self.__master, *args, **kwargs)

        def_w, def_h = WIDGETU2

        self.width = kwargs.get("width", def_w)
        self.height = kwargs.get("height", def_h)
        self.points = []
        self.one_meter = 1.0
        self.mean = None
        self.mode = StringVar()
        self.center = StringVar()
        self.scale = IntVar()
        self.reflat = StringVar()
        self.reflon = StringVar()
        reflat = config.get("scatterlat_f", 0.0)
        reflon = config.get("scatterlon_f", 0.0)
        self.reflat.set("Reference Lat" if reflat == 0.0 else reflat)
        self.reflon.set("Reference Lon" if reflon == 0.0 else reflon)
        self.scale.set(config.get("scatterscale_n", 7))
        self.scale_factors = (100, 50, 25, 10, 5, 1, 0.5, 0.1, 0.05, 0.025, 0.01)
        self.mode.set(config.get("scattermode_s", PLANAR))
        self.mode.set(config.get("scattercenter_s", CTRDYN))
        self._body()
        self._attach_events()

    def _body(self):
        """Set up frame and widgets."""

        for i in range(4):
            self.grid_columnconfigure(i, weight=1, uniform="ent")
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=0)
        self.canvas = Canvas(self, width=self.width, height=self.height, bg=BGCOL)
        self.spn_mode = Spinbox(
            self,
            values=MODES,
            width=9,
            wrap=True,
            fg=PNTCOL,
            bg=BGCOL,
            textvariable=self.mode,
            command=self._on_remode,
        )
        self.spn_center = Spinbox(
            self,
            values=CRTS,
            width=9,
            wrap=True,
            fg=PNTCOL,
            bg=BGCOL,
            textvariable=self.center,
        )
        self.scale_widget = Scale(
            self,
            from_=0,
            to=len(self.scale_factors) - 1,
            orient=HORIZONTAL,
            bg=FGCOL,
            troughcolor=BGCOL,
            variable=self.scale,
            showvalue=False,
            command=self._on_rescale,
        )
        self.ent_reflat = Entry(
            self,
            textvariable=self.reflat,
            fg=FIXCOL,
            bg=BGCOL,
        )
        self.ent_reflon = Entry(
            self,
            textvariable=self.reflon,
            fg=FIXCOL,
            bg=BGCOL,
        )
        self.canvas.grid(column=0, row=0, columnspan=4, sticky=(N, S, E, W))
        self.spn_mode.grid(column=0, row=1, sticky=(W, E))
        self.spn_center.grid(column=1, row=1, sticky=(W, E))
        self.scale_widget.grid(column=2, row=1, columnspan=2, sticky=(W, E))
        self.ent_reflat.grid(column=0, row=2, columnspan=2, sticky=(W, E))
        self.ent_reflon.grid(column=2, row=2, columnspan=2, sticky=(W, E))

    def _attach_events(self):
        """
        Bind events to frame.
        """

        self.bind("<Configure>", self._on_resize)
        self.canvas.bind("<Double-Button-1>", self._on_clear)
        self.canvas.bind("<MouseWheel>", self._on_zoom)

    def _on_zoom(self, event):
        """
        Adjust scale using mousewheel.

        :param event: mousewheel event
        """

        sl = len(self.scale_factors) - 1
        sc = self.scale.get()
        if event.delta > 0:
            if sc < sl:
                self.scale.set(sc + 1)
        elif event.delta < 0:
            if sc > 0:
                self.scale.set(sc - 1)

    def _on_remode(self):
        """
        Adjust distance approximation mode (haversine/planar)
        """

        self._on_resize(None)

    def _on_rescale(self, scale):  # pylint: disable=unused-argument
        """
        Rescale widget.
        """

        self._on_resize(None)

    def _on_resize(self, event):  # pylint: disable=unused-argument
        """
        Resize frame.

        :param Event event: resize event
        """

        self.width, self.height = self.get_size()
        self.init_frame()
        self.redraw()

    def _on_clear(self, event):  # pylint: disable=unused-argument
        """ "
        Clear plot.

        :param Event event: clear event
        """

        self.points = []
        self.init_frame()

    def get_size(self) -> tuple:
        """
        Get current canvas size.

        :return: window size (width, height)
        :rtype: tuple
        """

        self.update_idletasks()  # Make sure we know about resizing
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        return (width, height)

    def _draw_mean(self, lbl_font: font):
        """
        Draw the mean position in the corner of the plot. Uses
        self.mean as the position to draw.

        :param font lbl_font: Font to use.
        """

        if self.mean is None:
            return

        height = lbl_font.metrics("linespace")
        lat = f"Lat {self.mean.lat:14.10f}"
        lon = f"Lon {self.mean.lon:15.10f}"
        self.canvas.create_text(5, 10, text=lat, fill=PNTCOL, font=lbl_font, anchor="w")
        self.canvas.create_text(
            5, 10 + height, text=lon, fill=PNTCOL, font=lbl_font, anchor="w"
        )

    def init_frame(self):
        """
        Initialize scatter plot.
        """

        scale = self.scale_factors[self.scale.get()]
        width, height = self.get_size()
        self.canvas.delete("all")

        lbl_font = font.Font(size=min(int(width / 25), 10))
        m_per_circle = scale
        self.canvas.create_line(0, height / 2, width, height / 2, fill=FGCOL)
        self.canvas.create_line(width / 2, 0, width / 2, height, fill=FGCOL)

        maxr = min((height / 2), (width / 2))
        for idx, rad in enumerate(((0.25, 0.5, 0.75, 1))):
            self.canvas.create_circle(
                width / 2, height / 2, maxr * rad, outline=FGCOL, width=1
            )
            distance = m_per_circle * (idx + 1)
            if len(str(distance)) > 4:
                distance = round(distance, 3)
            txt_x = width / 2 + SQRT2 * maxr * rad
            txt_y = height / 2 + SQRT2 * maxr * rad
            self.canvas.create_text(
                txt_x, txt_y, text=f"{distance}m", fill=FGCOL, font=lbl_font
            )

        self.one_meter = (maxr * 0.25) / m_per_circle
        self._draw_mean(lbl_font)

    def draw_point(self, center: Point, position: Point, color: str = PNTCOL):
        """
        Draw a Point on the scatterplot, given a center Point.

        :param Point center: The center of the plot
        :param Point position: The point to draw
        :param str color: point color as string e.g. "orange"
        """

        if self.mode.get() == PLANAR:  # use planar approximation formula (returns m)
            distance = planar(center.lat, center.lon, position.lat, position.lon)
        else:  # use haversine great circle formula (returns km)
            distance = (
                haversine(center.lat, center.lon, position.lat, position.lon) * 1000
            )
        distance *= self.one_meter  # adjust to scale
        angle = bearing(center.lat, center.lon, position.lat, position.lon)
        theta = radians(90 - angle)
        pos_x = distance * cos(theta)
        pos_y = distance * sin(theta)
        center_x = self.width / 2
        center_y = self.height / 2
        pt_x = center_x + pos_x
        pt_y = center_y - pos_y
        self.canvas.create_circle(pt_x, pt_y, 2, fill=color, outline=color)

    def _ave_pos(self):
        """
        Calculate the mean position of all the lat/lon pairs visible
        on the scatter plot. Note that this will make for some very
        weird results near poles.
        """

        num = len(self.points)
        ave_lat = sum(p.lat for p in self.points) / num
        ave_lon = sum(p.lon for p in self.points) / num
        return Point(ave_lat, ave_lon)

    def redraw(self):
        """
        Redraw all the points on the scatter plot.
        """

        if not self.points:
            return

        middle = self._ave_pos()
        if self.center.get() == CTRFIX:
            try:
                middle = Point(float(self.reflat.get()), float(self.reflon.get()))
            except ValueError:
                self.center.set(CTRDYN)
        for pnt in self.points:
            self.draw_point(middle, pnt)
        if self.center.get() == CTRFIX:
            self.draw_point(middle, middle, FIXCOL)

    def update_frame(self):
        """
        Collect scatterplot data and update the plot.
        """

        lat, lon = self.__app.gnss_status.lat, self.__app.gnss_status.lon
        try:
            lat = float(lat)
            lon = float(lon)
        except ValueError:
            return  # Invalid values for lat/lon get ignored.
        pos = Point(lat, lon)
        if self.__app.gnss_status.fix == "NO FIX":
            return  # Don't plot when we don't have a fix.
        if self.points and pos == self.points[-1]:
            return  # Don't repeat exactly the last point.

        self.points.append(pos)

        middle = self._ave_pos()
        if self.mean is not None and self.mean != middle:
            self.mean = middle
            self.init_frame()
            self.redraw()
        else:
            self.mean = middle
            self.draw_point(middle, pos)
            self.redraw()
