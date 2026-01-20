"""
rover_frame.py

Rover frame class for PyGPS Application.

This plots the relative 2D position of the rover in a
fixed or moving base RTK configuration.

Created on 22 Aug 2023

:author: semuadmin (Steve Smith)
:copyright: 2020 semuadmin
:license: BSD 3-Clause
"""

# pylint: disable=invalid-name, no-member

from tkinter import NSEW, NW, SW, Frame

from pygpsclient.canvas_subclasses import (
    MODE_POL,
    TAG_DATA,
    TAG_GRID,
    TAG_XLABEL,
    CanvasCompass,
)
from pygpsclient.globals import (
    BGCOL,
    PNTCOL,
    WIDGETU2,
)
from pygpsclient.helpers import setubxrate
from pygpsclient.strings import NA

MAXPOINTS = 100
INSET = 4
TRKCOL = "#CD6600"
TRKTOL = 5
# setup ranges from 10cm to 5000km
RANGES = [int(i * 10**n) for n in range(1, 9) for i in (1, 2, 5)]


class RoverFrame(Frame):
    """
    Rover view frame class.
    """

    def __init__(self, app: Frame, parent: Frame, *args, **kwargs):
        """
        Constructor.

        :param Frame app: reference to main tkinter application
        :param Frame parent: reference to parent frame
        :param args: Optional args to pass to Frame parent class
        :param kwargs: Optional kwargs to pass to Frame parent class
        """
        self.__app = app
        self.__master = self.__app.appmaster

        super().__init__(parent, *args, **kwargs)

        def_w, def_h = WIDGETU2
        self.width = kwargs.get("width", def_w)
        self.height = kwargs.get("height", def_h)
        self._range = 1
        self._temprange = 1
        self._scale_c = 1
        self._scale_u = "cm"
        self.points = []
        self._redraw = True
        self._maxdist = 0
        self._body()
        self._attach_events()

    def _body(self):
        """Set up frame and widgets."""

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._canvas = CanvasCompass(
            self.__app, self, MODE_POL, width=self.width, height=self.height, bg=BGCOL
        )
        self._canvas.grid(column=0, row=0, sticky=NSEW)

    def _attach_events(self):
        """
        Bind events to frame.
        """

        self.bind("<Configure>", self._on_resize)
        self._canvas.bind("<Double-Button-1>", self._on_clear)

    def init_frame(self):
        """
        Initialize plot.
        """

        # only redraw the tags that have changed
        tags = (TAG_GRID, TAG_XLABEL) if self._redraw else ()
        maxgrid = 10
        scale = self._range / maxgrid / self._scale_c
        self._canvas.create_compass(
            radii=range(maxgrid, 1, -2),
            unit=self._scale_u,
            dp=0,
            scale=scale,
            tags=tags,
        )
        self._redraw = False

    def update_frame(self):
        """
        Collect relative position data and update the plot.
        """

        center_x = self.width / 2
        center_y = self.height / 2
        hdg = self.__app.gnss_status.rel_pos_heading
        dis = self.__app.gnss_status.rel_pos_length
        acchdg = self.__app.gnss_status.acc_heading
        accdis = self.__app.gnss_status.acc_length
        try:
            fixok, diffsoln, valrp, valhdg, carrsoln, moving = (
                self.__app.gnss_status.rel_pos_flags[0],
                self.__app.gnss_status.rel_pos_flags[1],
                self.__app.gnss_status.rel_pos_flags[2],
                self.__app.gnss_status.rel_pos_flags[7],
                self.__app.gnss_status.rel_pos_flags[3],
                self.__app.gnss_status.rel_pos_flags[4],
            )
        except IndexError:
            valrp = moving = NA
            fixok = hdg != 0
            valhdg = hdg != 0
            if "RTK-FIXED" in self.__app.gnss_status.fix:
                carrsoln = 2
                diffsoln = 1
            elif "RTK" in self.__app.gnss_status.fix:
                carrsoln = 1
                diffsoln = 1
            else:
                carrsoln = 0
                diffsoln = 0

        self._store_track(hdg, dis)

        self._set_range(dis)  # set range and scale automatically

        self.init_frame()

        # plot status information
        fh = self._canvas.fnth
        self._canvas.create_text(
            INSET,
            INSET,
            text=f"Len {dis:,.2f} ± {accdis:.2f} cm",
            fill=PNTCOL,
            anchor=NW,
            font=self._canvas.font,
            tags=TAG_DATA,
        )
        self._canvas.create_text(
            INSET,
            INSET + fh,
            text=f"Hdg {hdg:.2f} ± {acchdg:.2f}",
            fill=PNTCOL,
            anchor=NW,
            font=self._canvas.font,
            tags=TAG_DATA,
        )
        fixok = {0: "NO FIX", 1: "FIX OK"}.get(fixok, "FIX NA")
        diffsoln = {0: "NO DGPS", 1: "DGPS"}.get(diffsoln, "DGPS NA")
        valrp = {0: "INVALID RP", 1: "VALID RP"}.get(valrp, "RP NA")
        valhdg = {0: "INVALID HDG", 1: "VALID HDG"}.get(valhdg, "HDG NA")
        carrsoln = {0: "NO RTK", 1: "RTK FLOAT", 2: "RTK FIXED"}.get(carrsoln, "RTK NA")
        moving = {0: "STATIC", 1: "MOVING"}.get(moving, "MOVING NA")
        self._canvas.create_text(
            INSET,
            self.height - INSET,
            text=f"{fixok}\n{diffsoln}\n{valrp}\n{valhdg}\n{carrsoln}\n{moving}",
            fill=PNTCOL,
            anchor=SW,
            font=self._canvas.font,
            tags=TAG_DATA,
        )

        # plot historical relative position track
        for thdg, tdis in self.points:
            x, y = self._canvas.d2xy(thdg, tdis / self._scale_c)
            self._canvas.create_circle(
                x,
                y,
                2,
                fill=TRKCOL,
                outline=TRKCOL,
                tags=TAG_DATA,
            )
            self.update_idletasks()

        # plot latest relative position with accuracy radius
        x, y = self._canvas.d2xy(hdg, dis / self._scale_c)
        self._canvas.create_circle(
            x,
            y,
            accdis / (self._range / 10 / self._scale_c),
            outline=TRKCOL,
            tags=TAG_DATA,
        )
        self._canvas.create_line(
            center_x,
            center_y,
            x,
            y,
            fill=PNTCOL,
            width=3,
            tags=TAG_DATA,
        )
        self._canvas.create_circle(x, y, 3, fill=PNTCOL, outline=PNTCOL, tags=TAG_DATA)

    def _set_range(self, distance: float):
        """
        Set range and scale.

        :param float distance: distance in cm
        """

        self._temprange = self._range
        # set range and scale automatically
        self._maxdist = max(distance, self._maxdist)
        r = RANGES[0]
        for r in RANGES:
            if self._maxdist < r:
                break
        self._range = r
        if self._range >= 1e4:
            self._scale_c = 1e5
            self._scale_u = "km"
        elif self._range >= 1e2:
            self._scale_c = 1e2
            self._scale_u = "m"
        else:
            self._scale_c = 1
            self._scale_u = "cm"
        # force redraw if range has changed
        self._redraw = self._redraw | self._temprange != self._range

    def _store_track(
        self,
        hdg: float,
        dis: float,
        mx: int = MAXPOINTS,
        dp: int = TRKTOL,
    ):
        """
        Append historical track of relative position.
        Remove every nth point if track is full.

        :param float hdg: heading in degrees
        :param float dis: length in cm
        :param int mx: maximum points in track
        :param int dp: decimal places tolerance
        """

        nth = 3
        numpt = len(self.points)
        if numpt > 0:
            hdg_1, dis_1 = self.points[-1]
            if round(hdg, dp) == round(hdg_1, dp) and round(dis, dp) == round(
                dis_1, dp
            ):
                return
        self.points.append((hdg, dis))
        if numpt > mx:
            del self.points[nth - 1 :: nth]

    def enable_messages(self, status: int):
        """
        Enable/disable UBX NAV-RELPOSNED message on
        default port(s).

        :param int status: 0 = off, 1 = on
        """

        setubxrate(self.__app, "NAV-RELPOSNED", status)

    def _on_resize(self, event):  # pylint: disable=unused-argument
        """
        Resize frame.

        :param Event event: resize event
        """

        self.width, self.height = self.get_size()
        self._redraw = True

    def _on_clear(self, event):  # pylint: disable=unused-argument
        """ "
        Clear plot.

        :param Event event: clear event
        """

        self.points = []
        self._maxdist = 0
        self._redraw = True

    def get_size(self) -> tuple:
        """
        Get current canvas size.

        :return: window size (width, height)
        :rtype: tuple
        """

        self.update_idletasks()  # Make sure we know about resizing
        return self._canvas.winfo_width(), self._canvas.winfo_height()
