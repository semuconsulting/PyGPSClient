"""
rover_frame.py

Rover frame class for PyGPS Application.

This plots the relative 2D position of the rover in a
fixed or moving base RTK configuration.

Created on 22 Aug 2023

:author: semuadmin
:copyright: SEMU Consulting © 2022
:license: BSD 3-Clause
"""
# pylint: disable=invalid-name

from math import cos, pi, sin
from tkinter import BOTH, YES, Frame, font

from pygpsclient.globals import BGCOL, FGCOL, WIDGETU2
from pygpsclient.helpers import setubxrate
from pygpsclient.skyview_frame import Canvas

INSET = 5
SQRT2 = 0.7071067811865476
MAXPOINTS = 100
PNTCOL = "orange"
TRKCOL = "darkorange3"
ACCCOL = "darkorange3"
TRKTOL = 5


class RoverFrame(Frame):
    """
    Rover view frame class.
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
        self.width = kwargs.get("width", def_w)
        self.height = kwargs.get("height", def_h)
        self.scale = 1
        self.range = int(min(self.width / 2, self.height / 2)) - INSET
        self.points = []
        self.lbl_font = font.Font(size=10)
        self._body()
        self._attach_events()

    def _body(self):
        """Set up frame and widgets."""

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.canvas = Canvas(self, width=self.width, height=self.height, bg=BGCOL)
        self.scale = 1
        self.canvas.pack(fill=BOTH, expand=YES)

    def _attach_events(self):
        """
        Bind events to frame.
        """

        self.bind("<Configure>", self._on_resize)
        self.canvas.bind("<Double-Button-1>", self._on_clear)

    def init_frame(self):
        """
        Initialize plot.
        """

        width, height = self.get_size()
        self.canvas.delete("all")

        self.canvas.create_line(0, height / 2, width, height / 2, fill=FGCOL)
        self.canvas.create_line(width / 2, 0, width / 2, height, fill=FGCOL)
        ls = self.lbl_font.metrics("linespace")
        self.canvas.create_text(
            width - ls,
            height / 2,
            text="90\u00b0\n E",
            fill=FGCOL,
            font=self.lbl_font,
            anchor="e",
        )
        self.canvas.create_text(
            ls,
            height / 2,
            text="270\u00b0\n W",
            fill=FGCOL,
            font=self.lbl_font,
            anchor="w",
        )
        self.canvas.create_text(
            width / 2, ls, text="0\u00b0 N", fill=FGCOL, font=self.lbl_font, anchor="n"
        )
        self.canvas.create_text(
            width / 2,
            height - ls,
            text="180\u00b0 S",
            fill=FGCOL,
            font=self.lbl_font,
            anchor="s",
        )

        for rds in range(self.range, 10, int(self.range / -4)):
            self.canvas.create_circle(
                width / 2, height / 2, rds, outline=FGCOL, width=1
            )
            if self.scale >= 1e4:
                mul = 1e5
                unt = "km"
            elif self.scale >= 1e2:
                mul = 1e2
                unt = "m"
            else:
                mul = 1
                unt = "cm"
            txt_x = width / 2 + SQRT2 * rds
            txt_y = height / 2 + SQRT2 * rds
            self.canvas.create_text(
                txt_x,
                txt_y,
                text=f"{rds*self.scale/mul:.0f} {unt}",
                fill=FGCOL,
                font=self.lbl_font,
            )

    def update_frame(self):
        """
        Collect relative position data and update the plot.
        """

        center_x = self.width / 2
        center_y = self.height / 2
        self.range = int(min(center_x, center_y) - INSET)
        hdg, dis, acchdg, accdis = (
            self.__app.gnss_status.rel_pos_heading,
            self.__app.gnss_status.rel_pos_length,
            self.__app.gnss_status.acc_heading,
            self.__app.gnss_status.acc_length,
        )
        if len(self.__app.gnss_status.rel_pos_flags) >= 5:
            fixok, diffsoln, valrp, valhdg, carrsoln, moving = (
                self.__app.gnss_status.rel_pos_flags[0],
                self.__app.gnss_status.rel_pos_flags[1],
                self.__app.gnss_status.rel_pos_flags[2],
                self.__app.gnss_status.rel_pos_flags[7],
                self.__app.gnss_status.rel_pos_flags[3],
                self.__app.gnss_status.rel_pos_flags[4],
            )
        else:
            fixok = diffsoln = valrp = valhdg = carrsoln = moving = 0

        self.store_track(hdg, dis)

        # set scale automatically
        x = 1
        while dis / x > self.range:
            x *= 2
        self.scale = x

        self.init_frame()

        # plot status information
        ls = self.lbl_font.metrics("linespace")
        self.canvas.create_text(
            ls,
            ls,
            text=f"Len {dis:.2f} ± {accdis:.2f} cm",
            fill=PNTCOL,
            anchor="nw",
            font=self.lbl_font,
        )
        self.canvas.create_text(
            ls,
            ls * 2,
            text=f"Hdg {hdg:.2f} ± {acchdg:.2f}",
            fill=PNTCOL,
            anchor="nw",
            font=self.lbl_font,
        )
        fixok = "FIX OK" if fixok else "NO FIX"
        diffsoln = "DGPS" if diffsoln else "NO DGPS"
        valrp = "VALID RP" if valrp else "INVALID RP"
        valhdg = "VALID HDG" if valhdg else "INVALID HDG"
        try:
            carrsoln = ["NO RTK", "RTK FLOAT", "RTK FIXED"][carrsoln]
        except IndexError:
            carrsoln = "NO RTK"
        moving = "MOVING" if moving else "STATIC"
        self.canvas.create_text(
            ls,
            self.height - ls,
            text=f"{fixok}\n{diffsoln}\n{valrp}\n{valhdg}\n{carrsoln}\n{moving}",
            fill=PNTCOL,
            anchor="sw",
            font=self.lbl_font,
        )

        # plot historical relative position track
        for thdg, tdis in self.points:
            x, y = self.get_point(thdg, tdis, center_x, center_y)
            self.canvas.create_circle(x, y, 2, fill=TRKCOL, outline=TRKCOL)

        # plot latest relative position
        x, y = self.get_point(hdg, dis, center_x, center_y)
        self.canvas.create_circle(x, y, accdis / self.scale, outline=ACCCOL)
        self.canvas.create_line(center_x, center_y, x, y, fill=PNTCOL, width=3)
        self.canvas.create_circle(x, y, 3, fill=PNTCOL, outline=PNTCOL)

        self.update_idletasks()

    def get_point(self, hdg: float, dis: float, cx: int, cy: int) -> tuple:
        """
        Get point on chart.

        :param float hdg: heading in degrees
        :param float dis: length in cm
        :param int cx: width / 2
        :param int cy: height / 2
        :return: x.y plot coordinates
        :rtype: tuple
        """

        rad = ((hdg - 90) % 360) * pi / 180
        dis = dis / self.scale
        x = (cos(rad) * dis) + cx
        y = (sin(rad) * dis) + cy
        return x, y

    def store_track(
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
            (hdg_1, dis_1) = self.points[-1]
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
        self.init_frame()

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
        self.lbl_font = font.Font(size=min(int(width / 25), 10))
        return (width, height)
