"""
Spectrum Analysis frame class for PyGPSClient application.

This handles a frame containing a spectrum analysis chart from
a MON-SPAN message.

Created on 23 Dec 2022

:author: semuadmin
:copyright: SEMU Consulting © 2022
:license: BSD 3-Clause
"""
# pylint: disable=invalid-name

from math import ceil, floor
from tkinter import Frame, Canvas, font, BOTH, YES
from pygpsclient.globals import WIDGETU2, BGCOL, FGCOL

# Relative offsets of graph axes and legends
AXIS_XL = 19
AXIS_XR = 10
AXIS_Y = 22
OL_WID = 2
LEG_XOFF = AXIS_XL + 10
LEG_YOFF = 5
LEG_GAP = 5
MIN_DB = 0
MAX_DB = 160
MIN_HZ = 1.50
MAX_HZ = 1.66
TICK_DB = 20
TICK_GHZ = 0.02
TICK_COL = "grey"
RF_LIST = {
    0: "aquamarine2",
    1: "green",
    2: "cyan",
    3: "indigo",
    4: "violet",
    5: "red",
    6: "orange",
}


class SpectrumviewFrame(Frame):
    """
    Spectrumview frame class.
    """

    def __init__(self, app, *args, **kwargs):
        """
        Constructor.

        :param Frame app: reference to main tkinter application
        :param args: optional args to pass to Frame parent class
        :param kwargs: optional kwargs to pass to Frame parent class
        """

        self.__app = app  # Reference to main application class
        self.__master = self.__app.get_master()  # Reference to root class (Tk)

        Frame.__init__(self, self.__master, *args, **kwargs)

        def_w, def_h = WIDGETU2
        self.width = kwargs.get("width", def_w)
        self.height = kwargs.get("height", def_h)
        self._mindb = MIN_DB
        self._maxdb = MAX_DB
        self._minhz = MIN_HZ
        self._maxhz = MAX_HZ
        self._body()

        self.bind("<Configure>", self._on_resize)

    def _body(self):
        """
        Set up frame and widgets.
        """

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.can_spectrumview = Canvas(
            self, width=self.width, height=self.height, bg=BGCOL
        )
        self.can_spectrumview.pack(fill=BOTH, expand=YES)

    def init_graph(self):
        """
        Initialise graph view
        """

        w, h = self.width, self.height
        resize_font = font.Font(size=min(int(h / 25), 10))

        self.can_spectrumview.delete("all")
        self.can_spectrumview.create_line(AXIS_XL, 5, AXIS_XL, h - AXIS_Y, fill=FGCOL)
        self.can_spectrumview.create_line(
            w - AXIS_XR + 2, 5, w - AXIS_XR + 2, h - AXIS_Y, fill=FGCOL
        )

        # plot y axis ticks
        ticks = int((h - AXIS_Y) * TICK_DB / (self._maxdb - self._mindb))  # 20 dB tick
        i = 0
        y = h - AXIS_Y
        while y > LEG_YOFF:
            lbl = "dB" if i == 3 else ""
            self.can_spectrumview.create_line(
                AXIS_XL, y, w - AXIS_XR + 2, y, fill=TICK_COL
            )
            self.can_spectrumview.create_text(
                10,
                y,
                text=f"{self._mindb + (i * TICK_DB)}  {lbl}",
                angle=90,
                fill=FGCOL,
                font=resize_font,
            )
            y -= ticks
            i += 1

        # plot x axis ticks
        ticks = int(
            (w - AXIS_XL - AXIS_XR) * TICK_GHZ / (self._maxhz - self._minhz)
        )  # 0.05 GHz tick
        i = 0
        x = AXIS_XL
        while x < w - AXIS_XR:
            lbl = "GHz" if i == 3 else ""
            self.can_spectrumview.create_line(
                x,
                h - AXIS_Y,
                x,
                LEG_YOFF,
                fill=TICK_COL,
            )
            self.can_spectrumview.create_text(
                x,
                h - AXIS_Y + 10,
                text=f"{self._minhz + (i * TICK_GHZ):.2f}  {lbl}",
                fill=FGCOL,
                font=resize_font,
            )
            x += ticks
            i += 1

    def update_graph(self):
        """
        Plot MON-SPAN spectrum analysis.

        spectrum_data is list of tuples (spec, spn, res, ctr, pga),
        one item per RF block
        """

        w, h = self.width, self.height
        resize_font = font.Font(size=min(int(h / 25), 10))
        rfblocks = self.__app.gnss_status.spectrum_data
        numrf = len(rfblocks)
        if numrf == 0:
            return

        rfhz, self._minhz, self._maxhz, self._mindb, self._maxdb = self._get_points(
            rfblocks
        )
        self.init_graph()

        # for each RF block in MON-SPAN message
        for i, rfblock in enumerate(rfhz):
            col = RF_LIST[i % len(RF_LIST)]

            # draw legend for this RF block
            x = LEG_XOFF + (w / 9) * i
            self.can_spectrumview.create_line(
                x,
                LEG_YOFF + (h / 15),
                x + (w / 9) - LEG_GAP,
                LEG_YOFF + (h / 15),
                fill=col,
                width=OL_WID,
            )
            self.can_spectrumview.create_text(
                (x + x + (w / 9) - LEG_GAP) / 2,
                LEG_YOFF + (h / 30),
                text=f"RF {i + 1}",
                fill=FGCOL,
                font=resize_font,
            )

            # plot spectrum for this RF block
            x2 = AXIS_XL
            y2 = h - AXIS_Y
            for n, (hz, db) in enumerate(rfblock):
                x1 = x2
                y1 = y2
                y2 = h - AXIS_Y - ((h - AXIS_Y) * (db / (self._maxdb - self._mindb)))
                xwid = w - AXIS_XL - AXIS_XR
                x2 = AXIS_XL + (xwid * (hz - self._minhz) / (self._maxhz - self._minhz))
                if n > 0:
                    self.can_spectrumview.create_line(
                        x1, y1, x2, y2, fill=col, width=OL_WID
                    )

        self.can_spectrumview.update_idletasks()

    def _get_points(self, rfblocks) -> tuple:
        """
        Get plot points and axis limits for all RF blocks

        :param list rfblocks: RF Blocks
        :return: tuple of points and axis limits
        :rtype: tuple
        """

        minhz = 999 * 1e9
        maxhz = 0
        mindb = 0
        maxdb = 0
        rfhz = []
        # for each RF block in MON-SPAN message
        for i, rfblock in enumerate(rfblocks):
            (spec, spn, res, ctr, pga) = rfblock
            minhz = min(minhz, ctr - res * (spn / res) / 2)
            maxhz = max(maxhz, ctr + res * (spn / res) / 2)
            spanhz = []
            for i, db in enumerate(spec):
                # mindb = min(mindb, db - pga) # fix min = 0 dB
                maxdb = max(maxdb, db - pga)
                hz = minhz + (res * (i + 1))
                spanhz.append((round(hz / 1e9, 3), db - pga))
            rfhz.append(spanhz)

        return (
            rfhz,
            floor(minhz * 100 / 1e9) / 100,
            ceil(maxhz * 100 / 1e9) / 100,
            floor(mindb / 10) * 10,
            ceil((maxdb + 10) / 10) * 10,
        )

    def _on_resize(self, event):  # pylint: disable=unused-argument
        """
        Resize frame

        :param event event: resize event
        """

        self.width, self.height = self.get_size()

    def get_size(self):
        """
        Get current canvas size.

        :return: window size (width, height)
        :rtype: tuple
        """

        self.update_idletasks()  # Make sure we know about any resizing
        width = self.can_spectrumview.winfo_width()
        height = self.can_spectrumview.winfo_height()
        return (width, height)
