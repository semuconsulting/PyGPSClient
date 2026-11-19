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

from copy import deepcopy
from tkinter import NSEW, Frame, Tk

from pygpsclient.custom_classes import (
    MODE_CEL,
    TAG_DATA,
    TAG_GRID,
    TAG_WAIT,
    TAG_XLABEL,
    CanvasCompass,
)
from pygpsclient.globals import BGCOL, GNSS_LIST
from pygpsclient.helpers import col2contrast, snr2col
from pygpsclient.widget_frame import WidgetFrame

OL_WID = 4
FONTSCALE = 30


class SkyviewFrame(WidgetFrame):
    """
    Skyview frame class.
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

        super().__init__(app, parent, *args, **kwargs)

    def _body(self):
        """
        Set up frame and widgets.
        """

        self._canvas = CanvasCompass(
            self.__app,
            self,
            MODE_CEL,
            width=self.width,
            height=self.height,
            bg=BGCOL,
        )

    def _do_layout(self):
        """
        Arrange frame and widgets in grid.
        """

        self._canvas.grid(column=0, row=0, sticky=NSEW)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

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

        try:
            data = deepcopy(
                self.__app.gnss_status.gsv_data
            )  # to avoid thread contention
            siv = len(data)
            sel = sum(
                1 for (_, _, ele, _, _, _) in data.values() if ele not in ("", None)
            )
            # ignore if elevation values are all null
            if siv <= 0 or sel <= 0:
                return

            self._waiting = False
            self.init_frame()
            for gnssId, svid, ele, azi, cno, _ in sorted(
                data.values(), key=lambda x: x[4]
            ):  # sort by ascending C/N0
                if not isinstance(ele, (int, float)) or not isinstance(
                    azi, (int, float)
                ):
                    continue
                x, y = self._canvas.d2xy(azi, ele)
                _, ol_col = GNSS_LIST[gnssId]
                bg_col = snr2col(abs(cno))
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
                    text=f"{svid:02}",
                    fill=col2contrast(bg_col),
                    font=self._canvas.font,
                    tags=TAG_DATA,
                )
        except ValueError:  # some values can be null on startup
            pass
        except RuntimeError as err:
            self.logger.exception(err)
