"""
Scatterplot frame class for PyGPS Application.

This generates a scatterplot of positions, centered on the average
position.

Created 23 March 2023

:author: Nathan Michaels
:copyright: Qualinx B.V.
:license: BSD 3-Clause
"""
from collections import namedtuple
from statistics import mean
import math
from tkinter import Frame, font, BOTH, YES, NO, IntVar, Scale, HORIZONTAL
from geographiclib.geodesic import Geodesic
from pygpsclient.globals import WIDGETU2, BGCOL, FGCOL
from pygpsclient.skyview_frame import Canvas


Point = namedtuple("Point", ["lat", "lon"])
geo = Geodesic.WGS84


# pylint: disable=too-many-instance-attributes
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

        def_w, def_h = WIDGETU2

        self.dot_col = "orange"
        self.width = kwargs.get("width", def_w)
        self.height = kwargs.get("height", def_h)
        self.fg_col = FGCOL
        self.points = []
        self.one_meter = 1
        self.mean = None
        self._body()
        self.bind("<Configure>", self._on_resize)

    def _body(self):
        """Set up frame and widgets."""

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.canvas = Canvas(self, width=self.width, height=self.height, bg=BGCOL)
        self.scale_factors = (100, 50, 25, 20, 15, 10, 5, 1, 0.1)
        self.scale = IntVar()
        self.scale.set(6)
        self.scale_widget = Scale(
            self,
            from_=0,
            to=len(self.scale_factors) - 1,
            orient=HORIZONTAL,
            relief="sunken",
            bg=BGCOL,
            variable=self.scale,
            showvalue=False,
            command=self._rescale,
        )
        self.canvas.pack(fill=BOTH, expand=YES)
        self.scale_widget.pack(fill="x", expand=NO)

    def _rescale(self, scale):
        self._on_resize(None)

    def _on_resize(self, event):  # pylint: disable=unused-argument
        """
        Resize frame

        :param event: resize event
        """

        self.width, self.height = self.get_size()
        self.init_graph()
        self.redraw()

    def get_size(self):
        """
        Get current canvas size.

        :return window size (width, height)
        """

        self.update_idletasks()  # Make sure we know about resizing
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        return (width, height)

    def _draw_mean(self, lbl_font):
        """
        Draw the mean position in the corner of the plot. Uses
        self.mean as the position to draw.

        :param lbl_font: Font to use.
        """

        if self.mean is None:
            return
        lat = f"Lon {self.mean.lat:14.10f}"
        lon = f"Lat {self.mean.lon:15.10f}"
        self.canvas.create_text(
            5, 10, text=lat, fill=self.fg_col, font=lbl_font, anchor="w"
        )
        self.canvas.create_text(
            5, 20, text=lon, fill=self.fg_col, font=lbl_font, anchor="w"
        )

    def init_graph(self):
        """
        Initialize scatter plot.
        """

        scale = self.scale_factors[self.scale.get()]
        width, height = self.get_size()
        self.canvas.delete("all")

        lbl_font = font.Font(size=min(int(width / 25), 10))
        m_per_circle = scale
        self.canvas.create_line(0, height / 2, width, height / 2, fill=self.fg_col)
        self.canvas.create_line(width / 2, 0, width / 2, height, fill=self.fg_col)

        maxr = min((height / 2), (width / 2))
        for idx, rad in enumerate(((0.25, 0.5, 0.75, 1))):
            self.canvas.create_circle(
                width / 2, height / 2, maxr * rad, outline=self.fg_col, width=1
            )
            distance = m_per_circle * (idx + 1)
            if len(str(distance)) > 4:
                distance = round(distance, 3)
            txt_x = width / 2 + math.sqrt(2) / 2 * maxr * rad
            txt_y = height / 2 + math.sqrt(2) / 2 * maxr * rad
            self.canvas.create_text(
                txt_x, txt_y, text=f"{distance}m", fill=self.fg_col, font=lbl_font
            )

        self.one_meter = (maxr * 0.25) / m_per_circle
        self._draw_mean(lbl_font)

    def draw_point(self, center, position):
        """
        Draw a Point on the scatterplot, given a center Point.

        :param Point center: The center of the plot
        :param Point position: The point to draw
        """
        inv = geo.Inverse(
            center.lat,
            center.lon,
            position.lat,
            position.lon,
            outmask=geo.AZIMUTH | geo.DISTANCE,
        )
        angle = inv["azi1"]
        distance = inv["s12"]
        distance *= self.one_meter
        theta = math.radians(90 - angle)
        pos_x = distance * math.cos(theta)
        pos_y = distance * math.sin(theta)
        center_x = self.width / 2
        center_y = self.height / 2

        pt_x = center_x + pos_x
        pt_y = center_y - pos_y
        self.canvas.create_circle(
            pt_x, pt_y, 2, fill=self.dot_col, outline=self.dot_col
        )

    def _ave_pos(self):
        """
        Calculate the mean position of all the lat/lon pairs visible
        on the scatter plot. Note that this will make for some very
        weird results near poles.
        """
        ave_lat = mean(p.lat for p in self.points)
        ave_lon = mean(p.lon for p in self.points)
        ave_pos = Point(ave_lat, ave_lon)
        return ave_pos

    def redraw(self):
        """
        Redraw all the points on the scatter plot.
        """
        if not self.points:
            return
        middle = self._ave_pos()
        for pnt in self.points:
            self.draw_point(middle, pnt)

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
            self.init_graph()
            self.redraw()
        else:
            self.mean = middle
            self.draw_point(middle, pos)
            self.redraw()
