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

:author: semuadmin
:copyright: 2020 SEMU Consulting
:license: BSD 3-Clause
"""

from http.client import responses
from io import BytesIO
from time import time
from tkinter import ALL, CENTER, NW, Canvas, E, Frame, N, S, StringVar, W

from PIL import Image, ImageTk, UnidentifiedImageError
from requests import ConnectionError as ConnError
from requests import ConnectTimeout, RequestException, get

from pygpsclient.globals import (
    BGCOL,
    CUSTOM,
    ERRCOL,
    ICON_END,
    ICON_POS,
    ICON_START,
    IMG_WORLD,
    IMG_WORLD_CALIB,
    MAP,
    WIDGETU2,
    WORLD,
    Point,
)
from pygpsclient.helpers import (
    fontheight,
    limittrack,
    ll2xy,
    points2area,
    scale_font,
    xy2ll,
)
from pygpsclient.mapquest import (
    MAPQTIMEOUT,
    MAX_ZOOM,
    MIN_UPDATE_INTERVAL,
    MIN_ZOOM,
    format_mapquest_request,
)
from pygpsclient.strings import (
    MAPCONFIGERR,
    MAPOPENERR,
    NOCONN,
    NOWEBMAPCONN,
    NOWEBMAPFIX,
    NOWEBMAPHTTP,
    NOWEBMAPKEY,
    OUTOFBOUNDS,
)

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
        self._marker = None
        self._last_map_update = 0
        self._marker = ImageTk.PhotoImage(Image.open(ICON_POS))
        self._img_start = ImageTk.PhotoImage(Image.open(ICON_START))
        self._img_end = ImageTk.PhotoImage(Image.open(ICON_END))
        self._zoom = int((MAX_ZOOM - MIN_ZOOM) / 2)
        self._lastmaptype = ""
        self._lastmappath = ""
        self._mapimage = None
        self._bounds = None
        self._pos = None
        self._track = []
        self._maptype = StringVar()
        self._font = self.__app.font_sm
        self._fonth = fontheight(self._font)
        self._body()
        self._attach_events()

    def _body(self):
        """
        Set up frame and widgets.
        """

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._can_mapview = Canvas(self, width=self.width, height=self.height, bg=BGCOL)
        self._can_mapview.grid(column=0, row=0, sticky=(N, S, E, W))

    def _attach_events(self):
        """
        Bind events to frame.
        """

        self.bind("<Configure>", self._on_resize)
        self._maptype.trace_add("write", self.on_maptype)
        self._can_mapview.bind("<Double-Button-1>", self.on_refresh)  # double-click
        # self._can_mapview.bind("<Button-1>", self.on_zoom)  # left-click

    def init_frame(self):
        """
        Initialise map.
        """

        self._zoom = self.__app.configuration.get("mapzoom_n")

    def on_maptype(self, var, index, mode):  # pylint: disable=unused-argument
        """
        Set maptype event binding.
        """

        if self._maptype.get() == CUSTOM:
            self._can_mapview.unbind("<Button-1>")
            self._can_mapview.bind("<Button-2>", self.on_mark)
            self._can_mapview.bind("<Button-3>", self.on_mark)
        else:
            self._can_mapview.bind("<Button-1>", self.on_zoom)
            self._can_mapview.bind("<Button-2>", self.on_zoom)  # right click Posix
            self._can_mapview.bind("<Button-3>", self.on_zoom)  # right-click Windows

    def on_refresh(self, event):  # pylint: disable=unused-argument
        """
        Trigger refresh of web map.

        :param event: event
        """

        self._last_map_update = 0
        self._pos = None

    def on_zoom(self, event):  # pylint: disable=unused-argument
        """
        Trigger zoom in or out.

        Left click (event.num = 1) increments zoom by 1.
        Right click (event.num = 2/3) increments zoom to maximum extent.

        :param event: event
        """

        refresh = False
        w, h = self.width, self.height
        _, zfh = scale_font(self.width, 16, 10, 20)
        # zoom out (-) if not already at min
        zinc = 0
        if w > event.x > w - INSET - zfh and h > event.y > h - INSET - zfh:
            if self._zoom > MIN_ZOOM:
                zinc = -1 if event.num == 1 else MIN_ZOOM - self._zoom
                refresh = True
        # zoom in (+) if not already at max
        elif (
            w > event.x > w - INSET - zfh
            and h - INSET - zfh * 2 > event.y > h - INSET - zfh * 3
        ):
            if self._zoom < MAX_ZOOM:
                zinc = 1 if event.num == 1 else MAX_ZOOM - self._zoom
                refresh = True

        if refresh:
            self._zoom += zinc
            self.__app.configuration.set("mapzoom_n", self._zoom)
            self.on_refresh(event)

    def on_mark(self, event):
        """
        Mouse click shows position in custom view.

        :param event: right click event
        """

        w, h = self.get_size()
        self._can_mapview.delete("pos")
        x, y = event.x, event.y
        self._pos = xy2ll(w, h, self._bounds, (x, y))
        self._can_mapview.create_circle(
            x, y, 2, outline=POSCOL, fill=POSCOL, tags="pos"
        )
        self._can_mapview.create_text(
            x,
            y - 3,
            text=f"{self._pos.lat:.08f},{self._pos.lon:.08f}",
            anchor=S,
            fill=POSCOL,
            tags="pos",
        )

    def update_frame(self):
        """
        Draw map and mark current known position and horizontal accuracy (where available).
        """

        lat = self.__app.gnss_status.lat
        lon = self.__app.gnss_status.lon
        hacc = self.__app.gnss_status.hacc

        # if no valid position, display warning message
        # fix = kwargs.get("fix", 0)
        if (
            lat in (None, "")
            or lon in (None, "")
            or (lat == 0 and lon == 0)
            # or fix in (0, 5)  # no fix or time only
        ):
            self.reset_map_refresh()
            self._disp_error(NOWEBMAPFIX)
            return

        self._maptype.set(self.__app.configuration.get("maptype_s"))
        # record track if Show Track checkbox ticked
        if self.__app.configuration.get("showtrack_b"):
            if len(self._track) > 0:  # only record if different from previous
                if round(self._track[-1].lat, 8) != round(lat, 8) or round(
                    self._track[-1].lon, 8
                ) != round(lon, 8):
                    self._track.append(Point(lat, lon))
            else:
                self._track.append(Point(lat, lon))
        else:
            self._track = [Point(lat, lon)]
        self._track = limittrack(self._track)  # limit size of track list
        if self._maptype.get() in (WORLD, CUSTOM):
            self._draw_offline_map(lat, lon, self._maptype.get())
        else:
            self._draw_online_map(lat, lon, self._maptype.get(), hacc)

    def _draw_offline_map(
        self,
        lat: float,
        lon: float,
        maptype: str = WORLD,
    ):  # pylint: disable = too-many-branches, too-many-statements, no-member
        """
        Draw fixed offline map using optional user-provided georeferenced
        image path(s) and calibration bounding box(es).

        Defaults to Mercator world image with bounding box [90, -180, -90, 180]
        if location is not within bounds of any custom map.

        :param float lat: latitude
        :param float lon: longitude
        :param str maptype: "world" or "custom"
        """

        w, h = self.width, self.height
        self._lastmaptype = maptype
        bounds = IMG_WORLD_CALIB
        err = ""

        if maptype == CUSTOM:
            err = OUTOFBOUNDS
            usermaps = self.__app.configuration.get("usermaps_l")
            for mp in usermaps:
                try:
                    mpath, bounds = mp
                    bounds = points2area((bounds[0], bounds[1], bounds[2], bounds[3]))
                    if (bounds.lat1 <= lat <= bounds.lat2) and (
                        bounds.lon1 <= lon <= bounds.lon2
                    ):
                        if self._lastmappath != mpath:
                            self._mapimage = Image.open(mpath)
                            self._lastmappath = mpath
                        err = ""
                        break
                except (ValueError, IndexError):
                    err = MAPCONFIGERR
                    break
                except (FileNotFoundError, UnidentifiedImageError):
                    err = MAPOPENERR.format(mpath.split("/")[-1])
                    break

        if maptype == WORLD or err != "":
            if self._lastmappath != IMG_WORLD:
                self._mapimage = Image.open(IMG_WORLD)
                self._lastmappath = IMG_WORLD
            bounds = IMG_WORLD_CALIB

        # Area is minlat, minlon, maxlat, maxlon
        self._bounds = bounds
        self._can_mapview.delete(ALL)
        self._img = ImageTk.PhotoImage(self._mapimage.resize((w, h)))
        self._can_mapview.create_image(0, 0, image=self._img, anchor=NW)

        # draw track
        i = 0
        for i, pnt in enumerate(self._track):
            x, y = ll2xy(w, h, self._bounds, pnt)
            if i:
                x2, y2 = x, y
                self._can_mapview.create_line(
                    x1, y1, x2, y2, fill=TRK_COL, width=3, tags="track"
                )
                x1, y1 = x2, y2
            else:
                x1, y1 = x, y
                xstart, ystart = x, y
        if i:
            self._can_mapview.create_image(
                xstart, ystart, image=self._img_start, anchor=S, tags="track"
            )
            self._can_mapview.create_image(
                x2, y2, image=self._img_end, anchor=S, tags="track"
            )
        else:
            self._can_mapview.create_image(
                xstart, ystart, image=self._marker, anchor=CENTER, tags="track"
            )

        # mark any selected point
        if self._pos is not None:
            (x, y) = ll2xy(w, h, self._bounds, self._pos)
            self._can_mapview.create_circle(
                x, y, 2, outline=POSCOL, fill=POSCOL, tags="pos"
            )
            self._can_mapview.create_text(
                x,
                y - 3,
                text=f"{self._pos.lat:.08f},{self._pos.lon:.08f}",
                anchor=S,
                fill=POSCOL,
                tags="pos",
            )

        if err != "":
            self._can_mapview.create_text(w / 2, h / 2, text=err, fill="orange")

    def _draw_online_map(
        self, lat: float, lon: float, maptype: str = MAP, hacc: float = 0
    ):  # pylint: disable=unused-argument
        """
        Draw scalable web map or satellite image via online MapQuest API.

        :param float lat: latitude
        :param float lon: longitude
        :param str maptype: "map" or "sat"
        :param float hacc: horizontal accuracy
        """

        sc = NOCONN
        msg = ""
        hacc = hacc if isinstance(hacc, (float, int)) else 0

        if maptype != self._lastmaptype:
            self._lastmaptype = maptype
            self.reset_map_refresh()

        mqapikey = self.__app.configuration.get("mqapikey_s")
        if mqapikey == "":
            self._disp_error(NOWEBMAPKEY)
            return
        map_update_interval = max(
            self.__app.configuration.get("mapupdateinterval_n"),
            MIN_UPDATE_INTERVAL,
        )

        now = time()
        if now - self._last_map_update < map_update_interval:
            self._draw_countdown(
                (-360 / map_update_interval) * (now - self._last_map_update)
            )
            return
        self._last_map_update = now

        url = format_mapquest_request(
            mqapikey,
            maptype,
            self.width,
            self.height,
            self._zoom,
            self._track,
            # (Point(lat, lon),),  # must be tuple
            None,  # bbox
            hacc,
        )

        try:
            response = get(url, timeout=MAPQTIMEOUT)
            sc = responses[response.status_code]  # get descriptive HTTP status
            response.raise_for_status()  # raise Exception on HTTP error
            if sc == "OK":
                img_data = response.content
                self._img = ImageTk.PhotoImage(Image.open(BytesIO(img_data)))
                self._can_mapview.delete(ALL)
                self._can_mapview.create_image(0, 0, image=self._img, anchor=NW)
                self._draw_zoom()
                self._can_mapview.update_idletasks()
                return
        except (ConnError, ConnectTimeout):
            msg = NOWEBMAPCONN
        except RequestException:
            msg = NOWEBMAPHTTP.format(sc)

        self._disp_error(msg)

    def _draw_countdown(self, wait):
        """
        Draw clock icon indicating time until next scheduled map refresh.

        :param int wait: wait time in seconds
        """

        self._can_mapview.create_oval((5, 5, 20, 20), fill="#616161", outline="")
        self._can_mapview.create_arc(
            (5, 5, 20, 20), start=90, extent=wait, fill="#ffffff", outline=""
        )

    def _draw_zoom(self):
        """
        Draw +/- zoom icons.
        """

        w, h = self.width, self.height
        zfnt, zfh = scale_font(self.width, 16, 10, 20)
        x = w - INSET - zfh / 2
        y = h - INSET
        self._can_mapview.create_text(
            x,
            y - zfh * 2,
            text="+",
            font=zfnt,
            fill=ZOOMCOL if self._zoom < MAX_ZOOM else ZOOMEND,
            anchor=S,
        )
        self._can_mapview.create_text(
            x,
            y - zfh,
            text=self._zoom,
            fill=ZOOMCOL,
            font=zfnt,
            anchor=S,
        )
        self._can_mapview.create_text(
            x,
            y,
            text="\u2212",
            font=zfnt,
            fill=ZOOMCOL if self._zoom > MIN_ZOOM else ZOOMEND,
            anchor=S,
        )

    def _disp_error(self, msg):
        """
        Display error message in webmap widget.

        :param str msg: error message
        """

        w, h = self.width, self.height

        self._can_mapview.delete(ALL)
        self._can_mapview.create_text(
            w / 2,
            h / 2,
            text=msg,
            fill="orange",
            font=self._font,
            anchor=S,
        )

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
        self._font, self._fonth = scale_font(self.width, 10, 25, 20)

    def get_size(self):
        """
        Get current canvas size.

        :return: window size (width, height)
        :rtype: tuple
        """

        self.update_idletasks()  # Make sure we know about any resizing
        return self._can_mapview.winfo_width(), self._can_mapview.winfo_height()
