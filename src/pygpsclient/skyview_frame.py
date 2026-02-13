"""
skyview_frame.py

Satview frame class for PyGPSClient application.

This handles a frame containing a 2D plot of satellite visibility.

Created on 13 Sep 2020

:author: semuadmin (Steve Smith)
:copyright: 2020 semuadmin
:license: BSD 3-Clause
"""

# pylint: disable = no-member

from tkinter import NSEW, Frame

from pygpsclient.canvas_subclasses import (
    MODE_CEL,
    TAG_DATA,
    TAG_GRID,
    TAG_WAIT,
    TAG_XLABEL,
    CanvasCompass,
)
from pygpsclient.globals import (
    BGCOL,
    FGCOL,
    GNSS_LIST,
    WIDGETU2,
)
from pygpsclient.helpers import col2contrast, snr2col
from pygpsclient.strings import DLGWAITAZI

OL_WID = 4
FONTSCALE = 30


class SkyviewFrame(Frame):
    """
    Skyview frame class.
    """

    def __init__(self, app: Frame, parent: Frame, *args, **kwargs):
        """
        Constructor.

        :param Frame app: reference to main tkinter application
        :param Frame parent: reference to parent frame
        :param args: optional args to pass to Frame parent class
        :param kwargs: optional kwargs to pass to Frame parent class
        """

        self.__app = app  # Reference to main application class
        self.__master = self.__app.appmaster  # Reference to root class (Tk)

        super().__init__(parent, *args, **kwargs)

        def_w, def_h = WIDGETU2
        self.width = kwargs.get("width", def_w)
        self.height = kwargs.get("height", def_h)
        self.bg_col = BGCOL
        self.fg_col = FGCOL
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
        self._canvas = CanvasCompass(
            self.__app,
            self,
            MODE_CEL,
            width=self.width,
            height=self.height,
            bg=self.bg_col,
        )
        self._canvas.grid(column=0, row=0, sticky=NSEW)

    def _attach_events(self):
        """
        Bind events to frame.
        """

        self.bind("<Configure>", self._on_resize)

    def init_frame(self):
        """
        Initialise satellite view
        """

        # only redraw the tags that have changed
        tags = (TAG_GRID, TAG_XLABEL, TAG_WAIT) if self._redraw else ()
        self._canvas.create_compass(
            fontscale=FONTSCALE,
            tags=tags,
        )
        self._redraw = False

    def update_frame(self):
        """
        Plot satellites' elevation and azimuth position.
        """

        data = self.__app.gnss_status.gsv_data
        siv = len(data)
        sel = sum(1 for (_, _, ele, _, _, _) in data.values() if ele not in ("", None))
        # ignore if elevation values are all null
        if siv <= 0 or sel <= 0:
            return

        self._waiting = False
        self.init_frame()

        for val in sorted(data.values(), key=lambda x: x[4]):  # sort by ascending C/N0
            try:
                gnssId, prn, ele, azi, cno, _ = val
                if ele in ("", None) or azi in ("", None):
                    continue
                x, y = self._canvas.d2xy(int(azi), int(ele))
                _, ol_col = GNSS_LIST[gnssId]
                prn = f"{int(prn):02}"
                bg_col = snr2col(cno)
                self._canvas.create_circle(
                    x,
                    y,
                    self._canvas.maxr / 10,
                    outline=ol_col,
                    fill=bg_col,
                    width=OL_WID,
                    tags=TAG_DATA,
                )
                self._canvas.create_text(
                    x,
                    y,
                    text=prn,
                    fill=col2contrast(bg_col),
                    font=self._canvas.font,
                    tags=TAG_DATA,
                )
            except ValueError:
                pass

            self.update_idletasks()

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
            self._canvas.create_alert(DLGWAITAZI, tags=TAG_WAIT)

    def get_size(self):
        """
        Get current canvas size.

        :return: window size (width, height)
        :rtype: tuple
        """

        self.update_idletasks()  # Make sure we know about any resizing
        return self._canvas.winfo_width(), self._canvas.winfo_height()
