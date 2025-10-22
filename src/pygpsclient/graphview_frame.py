"""
graphview_frame.py

Graphview frame class for PyGPSClient application.

This handles a frame containing a graph of current satellite reception.

Created on 14 Sep 2020

:author: semuadmin (Steve Smith)
:copyright: 2020 semuadmin
:license: BSD 3-Clause
"""

from tkinter import ALL, BOTH, YES, Canvas, E, Frame

from pygpsclient.globals import (
    AXISCOL,
    BGCOL,
    FGCOL,
    GNSS_LIST,
    GRIDCOL,
    MAX_SNR,
    WIDGETU2,
)
from pygpsclient.helpers import col2contrast, fontheight, scale_font

# Relative offsets of graph axes and legend
AXIS_XL = 19
AXIS_XR = 10
AXIS_Y = 22
OL_WID = 1
LEG_XOFF = AXIS_XL + 10
LEG_YOFF = 5
LEG_GAP = 5


class GraphviewFrame(Frame):
    """
    Graphview frame class.
    """

    def __init__(self, app, *args, **kwargs):
        """
        Constructor.

        :param Frame app: reference to main tkinter application
        :param args: optional args to pass to Frame parent class
        :param kwargs: optional kwargs to pass to Frame parent class
        """

        self.__app = app  # Reference to main application class
        self.__master = self.__app.appmaster  # Reference to root class (Tk)

        Frame.__init__(self, self.__master, *args, **kwargs)

        def_w, def_h = WIDGETU2
        self.width = kwargs.get("width", def_w)
        self.height = kwargs.get("height", def_h)
        self._font = self.__app.font_vsm
        self._fonth = fontheight(self._font)
        self._body()
        self._attach_events()

    def _body(self):
        """
        Set up frame and widgets.
        """

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.can_graphview = Canvas(
            self, width=self.width, height=self.height, bg=BGCOL
        )
        self.can_graphview.pack(fill=BOTH, expand=YES)

    def _attach_events(self):
        """
        Bind events to frame.
        """

        self.bind("<Configure>", self._on_resize)
        self.can_graphview.bind("<Double-Button-1>", self._on_legend)

    def _on_legend(self, event):  # pylint: disable=unused-argument
        """
        On double-click - toggle legend on/off.

        :param event: event
        """

        self.__app.configuration.set(
            "legend_b", not self.__app.configuration.get("legend_b")
        )

    def init_frame(self):
        """
        Initialise graph view
        """

        w, h = self.width, self.height
        ticks = int(MAX_SNR / 10)
        self.can_graphview.delete(ALL)
        for i in range(ticks, 0, -1):
            y = (h - AXIS_Y) * i / ticks
            self.can_graphview.create_line(
                AXIS_XL, y, w - AXIS_XR + 2, y, fill=AXISCOL if i == ticks else GRIDCOL
            )
            self.can_graphview.create_text(
                10,
                y,
                text=str(MAX_SNR - (i * 10)),
                angle=90,
                fill=FGCOL,
                font=self._font,
            )
        self.can_graphview.create_line(AXIS_XL, 5, AXIS_XL, h - AXIS_Y, fill=AXISCOL)
        self.can_graphview.create_text(
            AXIS_XR,
            5,
            text="dB",
            angle=90,
            fill=FGCOL,
            anchor=E,
            font=self._font,
        )

        if self.__app.configuration.get("legend_b"):
            self._draw_legend()

    def _draw_legend(self):
        """
        Draw GNSS color code legend
        """

        w = self.width / 10
        h = self.height / 15

        for i, (_, (gnssName, gnssCol)) in enumerate(GNSS_LIST.items()):
            x = LEG_XOFF + w * i
            self.can_graphview.create_rectangle(
                x,
                LEG_YOFF,
                x + w - LEG_GAP,
                LEG_YOFF + h,
                # outline=gnssCol,
                # fill=BGCOL,
                outline=GRIDCOL,
                fill=gnssCol,
                width=OL_WID,
            )
            self.can_graphview.create_text(
                (x + x + w - LEG_GAP) / 2,
                LEG_YOFF + h / 2,
                text=gnssName,
                fill=col2contrast(gnssCol),
                font=self._font,
            )

    def update_frame(self):
        """
        Plot satellites' signal-to-noise ratio (cno).
        Automatically adjust y axis according to number of satellites in view.
        """

        data = self.__app.gnss_status.gsv_data
        siv = len(self.__app.gnss_status.gsv_data)

        if siv == 0:
            return

        w, h = self.width, self.height
        self.init_frame()

        offset = AXIS_XL + 2
        colwidth = (w - AXIS_XL - AXIS_XR + 1) / siv
        # scale x axis label according to siv
        svfont, _ = scale_font(self.width, 6, siv, 14)
        for d in sorted(data.values()):  # sort by ascending gnssid, svid
            gnssId, prn, _, _, snr = d
            if snr in ("", "0", 0):
                snr = 1  # show 'place marker' in graph
            else:
                snr = int(snr)
            snr_y = int(snr) * (h - AXIS_Y - 1) / MAX_SNR
            (_, ol_col) = GNSS_LIST[gnssId]
            prn = f"{int(prn):02}"
            self.can_graphview.create_rectangle(
                offset,
                h - AXIS_Y - 1,
                offset + colwidth - OL_WID,
                h - AXIS_Y - 1 - snr_y,
                outline=GRIDCOL,
                # fill=snr2col(snr),
                fill=ol_col,
                width=OL_WID,
            )
            self.can_graphview.create_text(
                offset + colwidth / 2,
                h - 10,
                text=prn,
                fill=FGCOL,
                font=svfont,
                angle=35,
            )
            offset += colwidth

        self.can_graphview.update_idletasks()

    def _on_resize(self, event):  # pylint: disable=unused-argument
        """
        Resize frame

        :param event event: resize event
        """

        self.width, self.height = self.get_size()
        self._font, self._fonth = scale_font(self.width, 8, 25, 16)

    def get_size(self):
        """
        Get current canvas size.

        :return: window size (width, height)
        :rtype: tuple
        """

        self.update_idletasks()  # Make sure we know about any resizing
        return self.can_graphview.winfo_width(), self.can_graphview.winfo_height()
