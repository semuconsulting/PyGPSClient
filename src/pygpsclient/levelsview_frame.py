"""
levelsview_frame.py

Level view frame class for PyGPSClient application.

This handles a frame containing a graph of current satellite cno levels.

Created on 14 Sep 2020

:author: semuadmin (Steve Smith)
:copyright: 2020 semuadmin
:license: BSD 3-Clause
"""

# pylint: disable=no-member

from tkinter import NE, NSEW, Frame, Tk, font

from pygpsclient.canvas_subclasses import (
    TAG_DATA,
    TAG_GRID,
    TAG_WAIT,
    TAG_XLABEL,
    TAG_YLABEL,
    CanvasGraph,
)
from pygpsclient.globals import (
    BGCOL,
    FGCOL,
    GNSS_LIST,
    GRIDMAJCOL,
    MAX_SNR,
    WIDGETU2,
)
from pygpsclient.helpers import col2contrast, fitfont, unused_sats
from pygpsclient.strings import DLGWAITCNO

OL_WID = 1
FONTSCALELG = 40
XLBLANGLE = 35
XLBLFMT = "000"


class LevelsviewFrame(Frame):
    """
    Levelsview frame class.
    """

    def __init__(self, app: Tk, parent: Frame, *args, **kwargs):
        """
        Constructor.

        :param Tk app: reference to main tkinter application
        :param Frame parent: reference to parent frame
        :param args: optional args to pass to Frame parent class
        :param kwargs: optional kwargs to pass to Frame parent class
        """

        self.__app = app  # Reference to main application class

        super().__init__(parent, *args, **kwargs)

        def_w, def_h = WIDGETU2
        self.width = kwargs.get("width", def_w)
        self.height = kwargs.get("height", def_h)
        self._redraw = True
        self._waiting = True
        self._body()
        self._attach_events()

    def _body(self):
        """
        Set up frame and widgets.
        """

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._canvas = CanvasGraph(
            self.__app, self, width=self.width, height=self.height, bg=BGCOL
        )
        self._canvas.grid(column=0, row=0, sticky=NSEW)

    def _attach_events(self):
        """
        Bind events to frame.
        """

        self.bind("<Configure>", self._on_resize)
        self._canvas.bind("<Double-Button-1>", self._on_legend)

    def _on_legend(self, event):  # pylint: disable=unused-argument
        """
        On double-click - toggle legend on/off.

        :param event: event
        """

        self.__app.configuration.set(
            "legend_b", not self.__app.configuration.get("legend_b")
        )
        self._redraw = True

    def init_frame(self):
        """
        Initialise graph view
        """

        # only redraw the tags that have changed
        tags = (TAG_GRID, TAG_XLABEL, TAG_YLABEL, TAG_WAIT) if self._redraw else ()
        self._canvas.create_graph(
            xdatamax=10,
            ydatamax=(MAX_SNR,),
            xtickmaj=5,
            ytickmaj=int(MAX_SNR / 10),
            ylegend=("C/No dBHz",),
            ycol=(FGCOL,),
            ylabels=True,
            xlabelsfrm=XLBLFMT,
            xangle=XLBLANGLE,
            fontscale=FONTSCALELG,
            tags=tags,
        )
        self._redraw = False

    def _draw_legend(self):
        """
        Draw GNSS color code legend
        """

        w = self.width / 12
        h = self.height / 18

        lgfont = font.Font(size=int(min(self.width, self.height) / FONTSCALELG))
        for i, (_, (gnssName, gnssCol)) in enumerate(GNSS_LIST.items()):
            x = (self._canvas.xoffl * 2) + w * i
            self._canvas.create_rectangle(
                x,
                self._canvas.yofft,
                x + w - 5,
                self._canvas.yofft + h,
                outline=GRIDMAJCOL,
                fill=gnssCol,
                width=OL_WID,
                tags=TAG_XLABEL,
            )
            self._canvas.create_text(
                (x + x + w - 5) / 2,
                self._canvas.yofft + h / 2,
                text=gnssName,
                fill=col2contrast(gnssCol),
                font=lgfont,
                tags=TAG_XLABEL,
            )

    def update_frame(self):
        """
        Plot satellites' signal-to-noise ratio (cno).
        Automatically adjust y axis according to number of satellites in view.
        """

        show_unused = self.__app.configuration.get("unusedsat_b")
        data = self.__app.gnss_status.gsv_data
        siv = len(data)
        siv = siv if show_unused else siv - unused_sats(data)
        if siv <= 0:
            return

        self._waiting = False
        w, h = self.width, self.height
        self.init_frame()

        offset = self._canvas.xoffl
        colwidth = (w - self._canvas.xoffl - self._canvas.xoffr + 1) / siv
        xfnt, _, _, _ = fitfont(XLBLFMT, colwidth, self._canvas.yoffb, XLBLANGLE)
        for val in sorted(data.values()):  # sort by ascending gnssid, svid
            gnssId, prn, _, _, cno, _ = val
            snr_y = int(cno) * (h - self._canvas.yoffb - 1) / MAX_SNR
            _, ol_col = GNSS_LIST[gnssId]
            self._canvas.create_rectangle(
                offset,
                h - self._canvas.yoffb - 1,
                offset + colwidth - OL_WID,
                h - self._canvas.yoffb - 1 - snr_y,
                outline=GRIDMAJCOL,
                fill=ol_col,
                width=OL_WID,
                tags=TAG_DATA,
            )
            self._canvas.create_text(
                offset + colwidth / 2,
                h - self._canvas.yoffb - 1,
                text=f"{int(prn):02}",
                fill=FGCOL,
                font=xfnt,
                angle=XLBLANGLE,
                anchor=NE,
                tags=TAG_DATA,
            )
            offset += colwidth
            self.update_idletasks()

        if self.__app.configuration.get("legend_b"):
            self._draw_legend()

    def _on_resize(self, event):  # pylint: disable=unused-argument
        """
        Resize frame

        :param event event: resize event
        """

        self.width, self.height = self.get_size()
        self._redraw = True
        self._on_waiting()

    def _on_waiting(self):
        """
        Display 'waiting for data' alert.
        """

        if self._waiting:
            self._canvas.create_alert(DLGWAITCNO, tags=TAG_WAIT)

    def get_size(self):
        """
        Get current canvas size.

        :return: window size (width, height)
        :rtype: tuple
        """

        self.update_idletasks()  # Make sure we know about any resizing
        return self._canvas.winfo_width(), self._canvas.winfo_height()
