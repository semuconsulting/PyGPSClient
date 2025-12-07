"""
map_frame.py

Mapview frame class for PyGPSClient application.

This handles a frame containing a location map which can be either:

 - one or more fixed offline maps based on user-provided georeferenced
   images e.g. geoTIFF (defaults to Mercator world image).
 - dynamic online map or satellite image accessed via a MapQuest API.

NOTE: The free MapQuest API key is subject to a limit of 15,000
transactions / month, or roughly 500 / day, so the map updates are only
run periodically (once a minute). This utility is NOT intended to be used for
real time navigation.

Created on 13 Sep 2020

:author: semuadmin (Steve Smith)
:copyright: 2020 semuadmin
:license: BSD 3-Clause
"""

from time import time
from tkinter import (
    DISABLED,
    EW,
    NORMAL,
    NSEW,
    Checkbutton,
    Frame,
    IntVar,
    Label,
    Spinbox,
    StringVar,
    W,
)

from pygpsclient.canvas_map import HYB, MAP, MAPTYPES, SAT, TAG_CLOCK, CanvasMap
from pygpsclient.globals import (
    BGCOL,
    ERRCOL,
    PNTCOL,
    READONLY,
    TRACEMODE_WRITE,
    WIDGETU2,
    WORLD,
    Point,
)
from pygpsclient.mapquest_handler import (
    MAX_ZOOM,
    MIN_UPDATE_INTERVAL,
    MIN_ZOOM,
)
from pygpsclient.strings import LBLSHOWTRACK, NOWEBMAPFIX

ZOOMCOL = ERRCOL
ZOOMEND = "lightgray"
POSCOL = ERRCOL
TRK_COL = "magenta"  # color of track
INSET = 4


class MapviewFrame(Frame):
    """
    Map frame class.
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
        self._img = None
        self._last_map_update = 0
        self._lastmaptype = ""
        self._lastmappath = ""
        self._bounds = None
        self._maptype = StringVar()
        self._maptype.set(self.__app.configuration.get("maptype_s"))
        self._showtrack = IntVar()
        self._showtrack.set(self.__app.configuration.get("showtrack_b"))
        self._mapzoom = IntVar()
        self._mapzoom.set(self.__app.configuration.get("mapzoom_n"))
        self._body()
        self._do_layout()
        self._reset()
        self._attach_events()

    def _body(self):
        """
        Set up frame and widgets.
        """

        self._can_mapview = CanvasMap(
            self.__app,
            self,
            height=self.height,
            width=self.width,
            bg=BGCOL,
        )
        self._frm_options = Frame(self, bg=BGCOL)
        self._spn_maptype = Spinbox(
            self._frm_options,
            values=MAPTYPES,
            width=7,
            wrap=True,
            textvariable=self._maptype,
            state=READONLY,
            background=BGCOL,
            readonlybackground=BGCOL,
            foreground=PNTCOL,
            buttonbackground=BGCOL,
        )
        self._lbl_zoom = Label(
            self._frm_options, width=5, text="Zoom", bg=BGCOL, fg=PNTCOL
        )
        self._spn_zoom = Spinbox(
            self._frm_options,
            from_=MIN_ZOOM,
            to=MAX_ZOOM,
            width=4,
            wrap=False,
            textvariable=self._mapzoom,
            state=READONLY,
            background=BGCOL,
            readonlybackground=BGCOL,
            disabledbackground=BGCOL,
            disabledforeground="grey",
            foreground=PNTCOL,
            buttonbackground=BGCOL,
        )
        self._chk_showtrack = Checkbutton(
            self._frm_options,
            text=LBLSHOWTRACK,
            variable=self._showtrack,
            background=BGCOL,
            foreground=PNTCOL,
        )

    def _do_layout(self):
        """
        Arrange widgets in frame.
        """

        self._can_mapview.grid(column=0, row=0, sticky=NSEW)
        self._frm_options.grid(column=0, row=1, sticky=EW)
        self._spn_maptype.grid(column=0, row=0, padx=1, sticky=W)
        self._lbl_zoom.grid(column=1, row=0, padx=1, sticky=W)
        self._spn_zoom.grid(column=2, row=0, padx=1, sticky=W)
        self._chk_showtrack.grid(column=3, row=0, padx=1, sticky=W)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._can_mapview.grid_columnconfigure(0, weight=1)
        self._can_mapview.grid_rowconfigure(0, weight=1)

    def _attach_events(self):
        """
        Bind events to frame.
        """

        self.bind("<Configure>", self._on_resize)
        self._maptype.trace_add(TRACEMODE_WRITE, self.on_maptype)
        self._mapzoom.trace_add(TRACEMODE_WRITE, self.on_mapzoom)
        self._showtrack.trace_add(TRACEMODE_WRITE, self.on_showtrack)
        self._can_mapview.bind("<Double-Button-1>", self.on_refresh)
        self._lbl_zoom.bind(
            "<Double-Button-1>",
            lambda event, val=0: self._setzoom(val),
        )
        self._lbl_zoom.bind(
            "<Double-Button-2>",
            lambda event, val=MAX_ZOOM: self._setzoom(val),
        )
        self._lbl_zoom.bind(
            "<Double-Button-3>",
            lambda event, val=MAX_ZOOM: self._setzoom(val),
        )

    def _reset(self):
        """
        Initialise mapview panel.
        """

        self._maptype.set(self.__app.configuration.get("maptype_s"))
        self.on_maptype(None, None, None)
        self._mapzoom.set(self.__app.configuration.get("mapzoom_n"))
        self._showtrack.set(self.__app.configuration.get("showtrack_b"))

    def on_refresh(self, event):  # pylint: disable=unused-argument
        """
        Trigger refresh of web map.

        :param event: event
        """

        self._last_map_update = 0

    def on_maptype(self, var, index, mode):  # pylint: disable=unused-argument
        """
        Set maptype event binding.
        """

        if self._maptype.get() == self._lastmaptype:
            return

        if self._maptype.get() == WORLD:
            self._lbl_zoom.config(state=DISABLED)
            self._spn_zoom.config(state=DISABLED)
        else:
            self._lbl_zoom.config(state=NORMAL)
            self._spn_zoom.config(state=READONLY)

        self.__app.configuration.set("maptype_s", self._maptype.get())
        self._lastmaptype = self._maptype.get()
        self.on_refresh(None)

    def on_mapzoom(self, var, index, mode):  # pylint: disable=unused-argument
        """
        Set mapzoom event binding.
        """

        self.__app.configuration.set("mapzoom_n", self._mapzoom.get())
        self.on_refresh(None)

    def _setzoom(self, val: int = 0):
        """
        Set zoom level.

        :param int val: zoom value
        """

        if val < 1:
            val = int((MAX_ZOOM + MIN_ZOOM) / 2)
        self._mapzoom.set(val)

    def on_showtrack(self, var, index, mode):  # pylint: disable=unused-argument
        """
        Set show track event binding.
        """

        self.__app.configuration.set("showtrack_b", self._showtrack.get())
        if not self._showtrack.get():
            self._can_mapview.track = None
        self.on_refresh(None)

    def update_frame(self):
        """
        Draw map and mark current known position and horizontal accuracy (where available).
        """

        lat = self.__app.gnss_status.lat
        lon = self.__app.gnss_status.lon
        hacc = self.__app.gnss_status.hacc
        map_update_interval = max(
            self.__app.configuration.get("mapupdateinterval_n"),
            MIN_UPDATE_INTERVAL,
        )
        self._maptype.set(self.__app.configuration.get("maptype_s"))

        # if no valid position, display warning message
        # fix = kwargs.get("fix", 0)
        if (
            lat in (None, "")
            or lon in (None, "")
            or (lat == 0 and lon == 0)
            # or fix in (0, 5)  # no fix or time only
        ):
            self.reset_map_refresh()
            self._can_mapview.draw_msg(NOWEBMAPFIX)
            return

        # record track if Show Track checkbox ticked
        if self._showtrack.get():
            self._can_mapview.track = Point(lat, lon)

        # limit mapquest calls to specified interval to avoid cost
        maptype = self._maptype.get()
        if maptype in (MAP, SAT, HYB):
            now = time()
            if now - self._last_map_update < map_update_interval:
                self._can_mapview.draw_countdown(
                    (-360 / map_update_interval) * (now - self._last_map_update)
                )
                return
            self._last_map_update = now
        else:
            self._can_mapview.delete(TAG_CLOCK)

        self._can_mapview.draw_map(
            maptype=self._maptype.get(),
            location=Point(lat, lon),
            track=self._can_mapview.track,
            marker=self._can_mapview.marker,
            hacc=hacc,
            zoom=self._mapzoom.get(),
        )
        self._bounds = self._can_mapview.bounds

        if self._can_mapview.zoommin:
            self._spn_zoom.config(highlightbackground=ERRCOL, highlightthickness=3)
        else:
            self._spn_zoom.config(highlightbackground="gray90", highlightthickness=3)

    def reset_map_refresh(self):
        """
        Reset map refresh counter to zero
        """

        self._last_map_update = 0

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
        return self._can_mapview.winfo_width(), self._can_mapview.winfo_height()
