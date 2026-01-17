"""
canvas_subclasses.py

Multi-purpose CanvasContainer, CanvasGraph and CanvasCompass subclasses
for PyGPSClient application.

Simplifies plotting of graphs and compass representations.

(see also canvas_map.py)

Created on 20 Nov 2025

:author: semuadmin (Steve Smith)
:copyright: 2020 semuadmin
:license: BSD 3-Clause
"""

# pylint: disable=attribute-defined-outside-init

from datetime import timedelta
from math import ceil, cos, radians, sin
from tkinter import (
    ALL,
    EW,
    HORIZONTAL,
    NE,
    NS,
    NSEW,
    NW,
    SE,
    VERTICAL,
    Canvas,
    E,
    Frame,
    N,
    S,
    Scrollbar,
    W,
    font,
)
from typing import Literal

from pygpsclient.globals import GRIDLEGEND, GRIDMAJCOL, GRIDMINCOL, SQRT2, TIME0

TAG_DATA = "dat"
TAG_GRID = "grd"
TAG_XLABEL = "xlb"
TAG_YLABEL = "ylb"
MODE_CEL = "ele"
MODE_POL = "lin"
DEFRADII = {"ele": (0, 30, 45, 60, 75, 90), "lin": range(10, 1, -2)}


class CanvasContainer(Canvas):
    """
    Custom expandable and scrollable Canvas Container class,
    used to contain frames whose dimensions exceed the current
    application window size.
    """

    def __init__(self, app, container, *args, **kwargs):
        """
        Constructor.

        :param app: Application
        :param container: Container frame
        """

        self.__app = app  # Reference to main application class
        self.__master = self.__app.appmaster  # Reference to root class (Tk)
        self.x_scrollbar = Scrollbar(container, orient=HORIZONTAL)
        self.y_scrollbar = Scrollbar(container, orient=VERTICAL)

        super().__init__(
            container,
            xscrollcommand=self.x_scrollbar.set,
            yscrollcommand=self.y_scrollbar.set,
            *args,
            **kwargs,
        )

        self.frm_container = Frame(self, borderwidth=2, relief="groove")
        self.grid(column=0, row=0, sticky=NSEW)
        self.show_scroll()
        self.x_scrollbar.config(command=self.xview)
        self.y_scrollbar.config(command=self.yview)
        # ensure container canvas expands to accommodate child frames
        self.create_window((0, 0), window=self.frm_container, anchor=NW)
        self.bind("<Configure>", lambda e: self.config(scrollregion=self.bbox(ALL)))
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(0, weight=1)

    def show_scroll(self, show: bool = True):
        """
        Show or hide scrollbars.

        :param bool show: show or hide
        """

        if show:
            self.x_scrollbar.grid(column=0, row=1, sticky=EW)
            self.y_scrollbar.grid(column=1, row=0, sticky=NS)
        else:
            self.x_scrollbar.grid_forget()
            self.y_scrollbar.grid_forget()


class CanvasGraph(Canvas):
    """
    Custom Canvas Graph class.
    """

    def __init__(self, app, container, *args, **kwargs):
        """
        Constructor.

        :param app: Application
        :param container: Container frame
        """

        self.__app = app  # Reference to main application class
        self.__master = self.__app.appmaster  # Reference to root class (Tk)
        super().__init__(container, *args, **kwargs)

    def create_graph(
        self,
        xdatamax: float = 10,
        xdatamin: float = 0,
        ydatamax: tuple = (10,),
        ydatamin: tuple = (0,),
        xtickmaj: int = 10,
        ytickmaj: int = 10,
        xtickmin: int = 0,
        ytickmin: int = 0,
        fillmaj: str = GRIDMAJCOL,
        fillmin: str = GRIDMINCOL,
        xdp: int = 0,
        ydp: tuple = (0,),
        xlegend: str = "",
        xtimeformat: str = "",
        ylegend: tuple = ("",),
        xcol: str = "#000000",
        ycol: tuple = ("#000000",),
        xlabels: bool = False,
        xlabelsfrm: str = "000",
        ylabels: bool = False,
        fontscale: int = 30,
        **kwargs,
    ) -> int:
        """
        Extends tkinter.Canvas Class to simplify drawing graphs on canvas.
        Accommodates multiple Y axis channels.

        :param float xdatamax: x maximum data value
        :param float xdatamin: x minimum data value
        :param tuple ydatamax: y channel(s) maximum data value
        :param tuple ydatamin: y channel(s) minimum data value
        :param int xtickmaj: x major ticks
        :param int ytickmaj: y major ticks
        :param int xtickmin: x minor ticks
        :param int ytickmin: y minor ticks
        :param str fillmaj: major axis color
        :param str fillmin: minor axis color
        :param int xdp: x label decimal places
        :param tuple ydp: y channel(s) label decimal places
        :param str xlegend: x legend
        :param str xtimeformat: x label time format e.g. "%H:%M:%S"
        :param tuple ylegend: y channels legend
        :param str xcol: x label color
        :param tuple ycol: y channel(s) color
        :param bool xlabels: x labels on/off
        :param str xlabelsfrm: xlabel format string e.g. "000"
        :param bool ylabels: y labels on/off
        :param int fontscale: font scaling factor (higher is smaller)
        :return: return code
        :rtype: int
        :raises: ValueError if Y channel args have dissimilar lengths
        """

        # pylint: disable=unnecessary-list-index-lookup

        def linspace(num: int, start: float, stop: float):
            """Generator for linear grid"""

            step = (stop - start) / (num - 1)
            for i in range(num):
                yield round(start + step * i, 4)

        # delete stale tags
        self.delete(TAG_DATA)
        tags = kwargs.pop("tags", (TAG_GRID, TAG_XLABEL, TAG_YLABEL))
        for tag in tags:
            self.delete(tag)

        # convert single y channel arguments to tuples
        if not isinstance(ydatamax, tuple):
            ydatamax = (ydatamax,)
        if not isinstance(ydatamin, tuple):
            ydatamin = (ydatamin,)
        if not isinstance(ydp, tuple):
            ydp = (ydp,)
        if not isinstance(ylegend, tuple):
            ylegend = (ylegend,)
        if not isinstance(ydatamin, tuple):
            ycol = (ycol,)
        for arg in ydatamin, ydp, ylegend, ycol:
            if len(arg) != len(ydatamax):
                raise ValueError("Y channel tuple arguments must have same length")

        self.width = w = self.winfo_width()
        self.height = h = self.winfo_height()
        rc = 0
        self.font = kwargs.pop("font", font.Font(size=int(min(w, h) / fontscale)))
        # instance attributes can be accessed by other Canvas graph methods
        self.fnth = self.font.metrics("linespace")
        self.xoffl = self.fnth * ceil(len(ydatamax) / 2) * 1.5
        self.xoffr = self.xoffl
        xangle = kwargs.pop("xangle", 0)
        if xangle == 0:
            self.yoffb = self.fnth * 1.5
        else:  # add extra Y offset for slanted X labels
            self.yoffb = self.font.measure(xlabelsfrm) * cos(radians(xangle)) * 1.2
        self.yofft = self.fnth
        self.xdatamax = xdatamax
        self.xdatamin = xdatamin
        self.ydatamax = ydatamax
        self.ydatamin = ydatamin
        self.xcol = xcol
        self.ycol = ycol
        self.yscale = [
            ((ydatamax[i] - ydatamin[i]) / (h - self.yoffb - self.yofft))
            for i in range(len(ydatamax))
        ]
        self.xscale = (self.xdatamax - self.xdatamin) / (w - self.xoffr - self.xoffl)

        # draw minor and major x axes
        for jn, (tik, fl) in enumerate(((xtickmin, fillmin), (xtickmaj, fillmaj))):
            if tik > 0:  # if num ticks > 0
                for i, x in enumerate(linspace(tik + 1, self.xoffl, w - self.xoffr)):
                    if TAG_GRID in tags:
                        rc = self.create_line(
                            x,
                            self.yofft,
                            x,
                            h - self.yoffb,
                            fill=fl,
                            width=1,
                            tags=TAG_GRID,
                            **kwargs,
                        )
                    if xlabels and jn and TAG_XLABEL in tags:  # major x axis
                        # draw x labels
                        xval = self.xdatamin + (x - self.xoffl) * self.xscale
                        if i == 0:
                            an = NW
                        elif i == tik:
                            an = NE
                        else:
                            an = N
                        if xtimeformat == "":  # format as float
                            xval = f"{xval:.{xdp}f}"
                        else:  # format as time string
                            dt = TIME0 + timedelta(seconds=xval)
                            xval = dt.strftime(xtimeformat)
                        rc = self.create_text(
                            x,
                            h - self.yoffb,
                            text=xval,
                            font=self.font,
                            fill=xcol,
                            anchor=an,
                            angle=xangle,
                            tags=TAG_XLABEL,
                        )

        # draw minor and major y axes
        for jn, (tik, fl) in enumerate(((ytickmin, fillmin), (ytickmaj, fillmaj))):
            if tik > 0:  # if num ticks > 0
                for i, y in enumerate(
                    linspace(tik + 1, h - self.yoffb, self.yofft)
                ):  # bottom to top
                    if TAG_GRID in tags:
                        rc = self.create_line(
                            self.xoffl,
                            y,
                            w - self.xoffr,
                            y,
                            fill=fl,
                            width=1,
                            tags=TAG_GRID,
                            **kwargs,
                        )
                    if ylabels and jn == 1 and TAG_YLABEL in tags:  # major y axis
                        # draw y channel label(s)
                        for chn, _ in enumerate(self.ydatamin):
                            yval = (
                                self.ydatamin[chn]
                                + (self.height - y - self.yoffb) * self.yscale[chn]
                            )
                            # alternate left (odd channels) and right (even channels)
                            # re-anchor labels at ends of axes
                            coff = self.fnth * int(chn / 2)
                            x, an2 = (
                                (w - self.xoffr + coff, N)
                                if chn % 2
                                else (self.xoffl - coff, S)
                            )
                            if i == 0:
                                an = f"{an2}{W}"
                            elif i == tik:
                                an = f"{an2}{E}"
                            else:
                                an = f"{an2}"
                            # draw label
                            rc = self.create_text(
                                x,
                                y,
                                text=f"{yval:.{ydp[chn]}f}",
                                font=self.font,
                                fill=ycol[chn],
                                anchor=an,
                                angle=90,
                                tags=TAG_YLABEL,
                            )

        # draw x axis legend
        if xlabels and xlegend != "" and TAG_XLABEL in tags:
            rc = self.create_text(
                w - self.xoffr,
                h - self.yoffb,
                text=xlegend,
                font=self.font,
                fill=xcol,
                anchor=SE,
                tags=TAG_XLABEL,
            )
        # draw y channel legend(s)
        if ylabels and TAG_YLABEL in tags:
            for chn, _ in enumerate(ylegend):
                if ylegend[chn] != "":
                    # alternate left (odd channels) and right (even channels)
                    coff = self.fnth * int((len(ylegend) - 1 - chn) / 2)
                    x, an = (
                        (w - self.xoffr - coff, SE)
                        if chn % 2
                        else (self.xoffl + coff, NE)
                    )
                    rc = self.create_text(
                        x,
                        self.yofft,
                        text=ylegend[chn],
                        font=self.font,
                        fill=ycol[chn],
                        anchor=an,
                        angle=90,
                        tags=TAG_YLABEL,
                    )

        return rc

    def d2xy(self, datax: float, datay: float, chn: int = 0) -> tuple:
        """
        Convert cartesian data point to pixel x,y in graph units.

        :param float datax: x data value
        :param float datay: y data value
        :param int chn: y data channel
        :return: canvas x,y pixel coordinates
        :rtype: tuple
        """

        try:
            x = self.xoffl + (datax - self.xdatamin) / self.xscale
            y = (
                self.height
                - self.yoffb
                - (datay - self.ydatamin[chn]) / self.yscale[chn]
            )
            return x, y
        except ZeroDivisionError:
            return 0, 0

    def xy2d(self, x: float, y: float, chn: int = 0) -> tuple:
        """
        Convert pixel x,y to cartesian data point in graph units.

        :param float x: x pixel value
        :param float y: y pixel value
        :param int chn: y data channel
        :return: graph datax,datay coordinates
        :rtype: tuple
        """

        datax = self.xdatamin + (x - self.xoffl) * self.xscale
        datay = self.ydatamin[chn] + (self.height - y - self.yoffb) * self.yscale[chn]
        return datax, datay

    def create_gline(
        self: Canvas,
        datax0: float,
        datay0: float,
        datax1: float,
        datay1: float,
        chn: int = 0,
        **kwargs,
    ) -> int:
        """
        Create line in graph units.

        :param float datax0: x0 data value
        :param float datay0: y0 data value
        :param float datax1: x1 data value
        :param float datay1: y1 data value
        :param int chn: y data channel
        :return: create_line return code
        :rtype: int
        """

        fill = kwargs.pop("fill", self.ycol[chn])
        tags = kwargs.pop("tags", (TAG_DATA,))
        x0, y0 = self.d2xy(datax0, datay0, chn)
        x1, y1 = self.d2xy(datax1, datay1, chn)
        return self.create_line(x0, y0, x1, y1, fill=fill, tags=tags, **kwargs)

    def create_gcircle(
        self: Canvas, datax: float, datay: float, datar: float, **kwargs
    ) -> int:
        """
        Create circle in graph units.

        :param float datax: x data value
        :param float datay: y data value
        :param float datar: radius data value
        :return: create_oval return code
        :rtype: int
        """

        x0, y0 = self.d2xy(datax - datar, datay - datar)
        x1, y1 = self.d2xy(datax + datar, datay + datar)
        return self.create_oval(x0, y0, x1, y1, **kwargs)


class CanvasCompass(Canvas):
    """
    Custom Canvas Compass class.
    """

    def __init__(
        self,
        app: object,
        container: Frame,
        mode: Literal["ele", "lin"],
        *args,
        **kwargs,
    ):
        """
        Constructor.

        :param app: Application
        :param container: Container frame
        :param int mode: ele (celestial) or lin (polar) coordinate system
        """

        if mode not in (MODE_CEL, MODE_POL):
            raise ValueError(
                f"invalid mode '{mode}' - must be '{MODE_CEL}' or '{MODE_POL}'"
            )

        self.__app = app  # Reference to main application class
        self.__master = self.__app.appmaster  # Reference to root class (Tk)
        self._mode = mode
        super().__init__(container, *args, **kwargs)

    def create_compass(
        self,
        scale: float = 1,
        dp: int = 0,
        unit: str = "°",
        fontscale: int = 25,
        **kwargs,
    ) -> int:
        """
        Extends tkinter.Canvas class to simplify drawing compass grids on canvas.

        :param float scale: radii marker scale
        :param int dp: radii marker decimal places
        :param str unit: radii marker units
        :param int fontscale: font scaling factor,
        :return: return code
        :rtype: int
        :raises: ValueError if invalid mode
        """

        # delete stale tags
        self.delete(TAG_DATA)
        tags = kwargs.pop("tags", (TAG_GRID, TAG_XLABEL))
        for tag in tags:
            self.delete(tag)

        self.width = self.winfo_width()
        self.height = self.winfo_height()
        rc = 0
        self.font = kwargs.pop(
            "font", font.Font(size=int(min(self.width, self.height) / fontscale))
        )
        self.fnth = self.font.metrics("linespace")
        outline = kwargs.get("fill", GRIDMAJCOL)
        legend = kwargs.pop("legend", GRIDLEGEND)
        fill = kwargs.pop("fill", GRIDMAJCOL)
        radii = kwargs.pop("radii", DEFRADII.get(self.mode))
        self.maxgrid = radii[0]
        self.scal = scale

        xc = self.width / 2
        yc = self.height / 2
        # offset max radius by height of font
        self.maxr = (min(self.width, self.height) / 2) - self.fnth

        # draw x,y axes
        if TAG_GRID in tags:
            for x0, y0, x1, y1 in (
                (xc, yc - self.maxr, xc, yc + self.maxr),
                (xc + self.maxr, yc, xc - self.maxr, yc),
            ):
                rc = self.create_line(
                    x0, y0, x1, y1, fill=fill, tags=TAG_GRID, **kwargs
                )

        # draw compass points
        if TAG_XLABEL in tags:
            for p, a, x0, y0 in (
                ("N 0°", N, xc, yc - self.maxr),
                ("S 180°", S, xc, yc + self.maxr),
                ("W 270°", W, xc - self.maxr, yc),
                ("90° E", E, xc + self.maxr, yc),
            ):
                rc = self.create_text(
                    x0,
                    y0,
                    text=p,
                    anchor=a,
                    font=self.font,
                    fill=legend,
                    tags=TAG_XLABEL,
                    **kwargs,
                )

        # draw radials with legend
        for rad in radii:
            if self._mode == MODE_CEL:  # celestial
                s = sin(radians(90 - rad)) * self.maxr
            else:  # polar
                s = rad / self.maxgrid * self.maxr
            if TAG_GRID in tags:
                rc = self.create_oval(
                    xc - s,
                    yc - s,
                    xc + s,
                    yc + s,
                    outline=outline,
                    tags=TAG_GRID,
                    width=1,
                )
            if TAG_XLABEL in tags:
                rc = self.create_text(
                    xc + SQRT2 * s,
                    yc - SQRT2 * s,
                    text=f"{rad*scale:.{dp}f}{unit}",
                    font=self.font,
                    fill=legend,
                    tags=TAG_XLABEL,
                    **kwargs,
                )

        return rc

    def d2xy(self: Canvas, azi: float, datay: float) -> tuple:
        """
        Convert polar (azimuth/distance) or celestial (azimuth/elevation)
        coordinates to pixel x,y in compass units.

        :param float azi: azimuth in degrees
        :param float datay: elevation or distance
        :return: canvas x,y pixel coordinates
        :rtype: tuple
        """

        try:
            azi = radians((azi - 90) % 360)  # adjust so North is up
            if self._mode == MODE_POL:  # polar coordinates
                x = (
                    cos(azi) * datay * self.maxr / (self.scal * self.maxgrid)
                    + self.width / 2
                )
                y = (
                    sin(azi) * datay * self.maxr / (self.scal * self.maxgrid)
                    + self.height / 2
                )
            else:  # celestial coordinates
                ele = radians(datay)
                x = cos(azi) * cos(ele) * self.maxr + self.width / 2
                y = sin(azi) * cos(ele) * self.maxr + self.height / 2
            return x, y
        except ZeroDivisionError:
            return 0, 0

    @property
    def mode(self) -> str:
        """
        Getter for mode.

        :return: mode as string
        :rtype: str
        """

        return self._mode
