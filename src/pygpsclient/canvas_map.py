"""
canvas_map.py

Multi-purpose CanvasMap subclass for offline and online maps.

This handles a canvas containing a location map which can be either:

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

# pylint: disable=too-many-positional-arguments, too-many-arguments, unused-argument

from http.client import responses
from io import BytesIO
from math import sqrt
from random import randrange
from tkinter import (
    ALL,
    CENTER,
    Canvas,
    S,
)

from PIL import Image, ImageTk, UnidentifiedImageError
from pynmeagps import planar
from requests import ConnectionError as ConnError
from requests import ConnectTimeout, RequestException, get

from pygpsclient.globals import (
    BGCOL,
    CUSTOM,
    ERRCOL,
    ICON_END,
    ICON_START,
    IMG_WORLD,
    IMG_WORLD_BOUNDS,
    IMPORT,
    PNTCOL,
    WORLD,
    Area,
    AreaXY,
    Point,
)
from pygpsclient.helpers import (
    area_in_bounds,
    get_track_bounds,
    ll2xy,
    normalise_area,
    point_in_bounds,
    scale_font,
)
from pygpsclient.mapquest_handler import (
    HYB,
    MAP,
    MAPQTIMEOUT,
    POINTLIMIT,
    SAT,
    format_mapquest_request,
)
from pygpsclient.strings import (
    DLGGPXOOB,
    MAPCONFIGERR,
    MAPOPENERR,
    NOCONN,
    NOWEBMAPCONN,
    NOWEBMAPFIX,
    NOWEBMAPHTTP,
    NOWEBMAPKEY,
    OUTOFBOUNDS,
)

ZOOM = 10
POSCOL = ERRCOL
TRK_COL = "magenta"  # color of track
HACCCOL = "skyblue"
MARKERCOL = "red"
TAG_TRACK = "trak"
TAG_MARKER = "mark"
TAG_HACC = "hacc"
TAG_CLOCK = "clok"
TAG_LOCATION = "loc"
MARKERSIZE = 6
MAX_SIZE = 100000000  # 154,746,100 pixels for PIL/Image
"""Maximum image size allowed by PIL Image library"""
MAPTYPES = (WORLD, MAP, SAT, HYB, CUSTOM)
""" Map Types """


class CanvasMap(Canvas):  # pylint: disable=too-many-ancestors
    """
    Canvas Map class.
    """

    def __init__(self, app, container, *args, **kwargs):
        """
        Constructor.

        :param Frame app: reference to main tkinter application
        :param Frame container: reference to container frame
        :param args: optional args to pass to Frame parent class
        :param kwargs: optional kwargs to pass to Frame parent class
        """

        self.__app = app  # Reference to main application class
        self.__master = self.__app.appmaster  # Reference to root class (Tk)
        self.__container = container  # container frame
        self.width = kwargs.get("width", 400)
        self.height = kwargs.get("height", 400)
        self._img_start = ImageTk.PhotoImage(Image.open(ICON_START))
        self._img_end = ImageTk.PhotoImage(Image.open(ICON_END))
        self._img = None
        self._mapimage = None
        self._bounds = None
        self._native_bounds = None
        self._track = None
        self._marker = None
        self._zoom = None
        self._zoommin = False
        self._last_map_update = 0
        self._last_image = None
        self._last_bounds = None
        self._lastmaptype = ""
        self._lastmappath = ""
        self._font = self.__app.font_sm
        self._fonth = self._font.metrics("linespace")

        super().__init__(self.__container, *args, **kwargs)

        self.config(background=BGCOL)
        self.bind("<Configure>", self._on_resize)
        self.bind("<Double-Button-2>", self.on_clear)
        self.bind("<Double-Button-3>", self.on_clear)

    def draw_map(
        self,
        maptype: str = WORLD,
        location: Point = None,
        marker: Point = None,
        track: list = None,
        hacc: float = None,
        mappath: str = None,
        bounds: Area = None,
        zoom: int = ZOOM,
    ):
        """
        Draw selected map type on canvas.

        :param str maptype: map type (CUSTOM/IMPORT/MAP/SAT/WORLD)
        :param Point location: location to draw on map
        :param Point marker: marker to draw on map
        :param list track: track to draw on map
        :param float hacc: horizontal accuracy in meters
        :param str mappath: path to map image (if known)
        :param Area bounds: bounds (extent) of map image (if known)
        :param int zoom: zoom level
        """

        self._zoom = zoom
        if maptype in (WORLD, CUSTOM, IMPORT):
            self._draw_offline_map(
                maptype, location, marker, track, hacc, mappath, bounds, zoom
            )
        elif maptype in (MAP, SAT, HYB):
            self._draw_online_map(maptype, location, marker, track, hacc, bounds, zoom)

    def _draw_offline_map(
        self,
        maptype: str,
        location: Point,
        marker: Point,
        track: list,
        hacc: float,
        mappath: str = None,
        bounds: Area = None,
        zoom: int = ZOOM,
    ):  # pylint: disable=unused-argument
        """
        Draw fixed offline map using optional user-provided georeferenced
        image path(s) and calibration bounding box(es).

        Defaults to Mercator world image with bounding box [90, -180, -90, 180]
        if location is not within bounds of any custom map.

        :param str maptype: offline map type (CUSTOM/IMPORT/WORLD)
        :param Point location: location to draw on map
        :param Point marker: marker to draw on map
        :param list track: track to draw on map
        :param float hacc: horizontal accuracy in meters
        :param str mappath: path to map image (if known)
        :param Area bounds: bounds (extent) of map image (if known)
        :param int zoom: zoom level
        """

        err = self.open_offline_map(maptype, location, mappath, bounds)
        if err != "":
            self.draw_msg(err, ERRCOL)
            return

        self._lastmaptype = maptype
        self.delete(ALL)
        if (
            zoom is None
            or location is None
            or maptype == WORLD
            or self.__app.configuration.get("mapzoom_disabled_b")
        ):
            image = self._mapimage
        else:
            image, self._bounds = self._zoom_offline_map(
                self._mapimage, self._native_bounds, location, zoom
            )
            self._last_image = image
            self._last_bounds = self._bounds
        if image is None:
            self.draw_msg(DLGGPXOOB, ERRCOL)
            return
        self._img = ImageTk.PhotoImage(image.resize((self.width, self.height)))
        self.create_image(
            self.width / 2, self.height / 2, image=self._img, anchor=CENTER
        )

        if location is not None:
            self.draw_marker(location, TAG_LOCATION)
        if marker is not None:
            self.draw_marker(marker, TAG_MARKER)
        if track is not None:
            self.draw_track(track)
        if location is not None and hacc is not None:
            self.draw_hacc(location, hacc)

    def open_offline_map(
        self,
        maptype: str,
        location: Point,
        mappath: str = None,
        bounds: Area = None,
    ) -> str:
        """
        Open map image at path, or find first available map image
        from usermaps_l list which includes location.

        :param str maptype: map type (CUSTOM/IMPORT/WORLD)
        :param Point location: location
        :param str mappath: path to map image, if known
        :param Area bounds: bounds (extent) of map image, if known
        :return: error code
        :rtype: str
        """

        err = OUTOFBOUNDS.format("unknown")
        try:
            mpath = None
            if maptype == IMPORT:
                mpath = mappath
                self._bounds = bounds
            elif maptype == WORLD:
                mpath = IMG_WORLD
                self._bounds = IMG_WORLD_BOUNDS
            else:
                mpath = self._find_offline_map(location, bounds)
            if mpath is None:
                err = OUTOFBOUNDS.format("bounds" if bounds is not None else "location")
            elif self._lastmappath == mpath:  # don't bother opening again
                err = ""
            else:
                self._mapimage = Image.open(mpath)
                self._lastmappath = mpath
                err = ""
        except (ValueError, IndexError):
            err = MAPCONFIGERR
        except (FileNotFoundError, UnidentifiedImageError):
            err = MAPOPENERR.format(mpath.split("/")[-1])

        return err

    def _find_offline_map(self, location: Point, bounds: Area) -> str:
        """
        Find first map image with bounds containing location.

        :param Point location: location
        :param Area bounds: native extents of map image, if known
        :return: map path
        :rtype: str
        """
        # pylint: disable=arguments-out-of-order

        mpath = None
        usermaps = self.__app.configuration.get("usermaps_l")
        for fpath, extent in usermaps:
            extents = normalise_area((extent[0], extent[1], extent[2], extent[3]))
            # check if bounds or location are within map extents
            if (bounds is not None and area_in_bounds(extents, bounds)) or (
                location is not None and point_in_bounds(extents, location)
            ):
                mpath = fpath
                self._bounds = extents
                self._native_bounds = extents
                break
        return mpath

    def _zoom_offline_map(
        self, image: Image, extents: Area, location: Point, zoom: int
    ) -> tuple:
        """
        Zoom (crop) offline image centered at location and
        calculate new bounding box.

        Automatically increments zoom until image is
        entirely within zoom bounds.

        ;param Image image: native map image
        :param Area extents: native map extents
        :param Point location: location (center point)
        :param int zoom: zoom level
        :return: tuple of (zoomed image, zoomed bounds)
        :rtype: tuple
        """

        zoombounds = self.zoom_bounds(self.height, self.width, location, zoom, CUSTOM)
        self._zoom = zoom
        (x1, y1), (x2, y2) = [
            ll2xy(image.width, image.height, extents, pnt)
            for pnt in (
                Point(zoombounds.lat2, zoombounds.lon1),
                Point(zoombounds.lat1, zoombounds.lon2),
            )
        ]

        # check if cropped image exceeds PIL's max permissible size
        size = (x2 - x1) * (y2 - y1)
        if size >= MAX_SIZE:
            self._zoommin = True
            return self._last_image, self._last_bounds

        self._zoommin = False
        return image.crop(AreaXY(x1, y1, x2, y2)), zoombounds

    def _draw_online_map(
        self,
        maptype: str,
        location: Point,
        marker: Point,
        track: list,
        hacc: float,
        bounds: Area = None,
        zoom: int = ZOOM,
    ):  # pylint: disable=unused-argument
        """
        Draw scalable web map or satellite image via online MapQuest API.

        :param str maptype: online map type (MAP/SAT)
        :param Point location: location to draw on map
        :param Point marker: marker to draw on map
        :param list track: track to draw on map
        :param float hacc: horizontal accuracy in meters
        :param Area bounds: bounds (extent) of map image, if known
        :param int zoom: zoom level
        """

        sc = NOCONN
        err = ""
        hacc = hacc if isinstance(hacc, (float, int)) else 0

        if maptype != self._lastmaptype:
            self._lastmaptype = maptype

        mqapikey = self.__app.configuration.get("mqapikey_s")
        if mqapikey == "":
            self.draw_msg(NOWEBMAPKEY, ERRCOL)
            return

        if track is not None:
            points = track
        elif location is not None:
            points = [
                location,
            ]
        else:
            self.draw_msg(NOWEBMAPFIX, ERRCOL)
            return

        if bounds is None:
            # set bounds relative to location and zoom
            if zoom > 1:
                bounds = self.zoom_bounds(
                    self.height, self.width, location, zoom, maptype
                )
        url = format_mapquest_request(
            mqapikey,
            maptype,
            self.width,
            self.height,
            zoom,
            points,  # list
            bounds,  # bbox
            hacc,
        )

        try:
            response = get(url, timeout=MAPQTIMEOUT)
            sc = responses[response.status_code]  # get descriptive HTTP status
            response.raise_for_status()  # raise Exception on HTTP error
            if sc == "OK":
                self._bounds = bounds
                img_data = response.content
                self._img = ImageTk.PhotoImage(Image.open(BytesIO(img_data)))
                self.delete(ALL)
                self.create_image(
                    self.width / 2, self.height / 2, image=self._img, anchor=CENTER
                )
                self.update_idletasks()
                return
        except (ConnError, ConnectTimeout):
            err = NOWEBMAPCONN
        except RequestException:
            err = NOWEBMAPHTTP.format(sc)

        self.draw_msg(err, ERRCOL)

    def draw_track(self, track: list):
        """
        Draw track on canvas.

        :param list track: list of track points
        """

        self.delete(TAG_TRACK)
        i = 0
        for i, pnt in enumerate(track):
            x, y = ll2xy(self.width, self.height, self._bounds, Point(pnt.lat, pnt.lon))
            if i:
                x2, y2 = x, y
                self.create_line(x1, y1, x2, y2, fill=TRK_COL, width=3, tags=TAG_TRACK)
                x1, y1 = x2, y2
            else:
                x1, y1 = x, y
                xstart, ystart = x, y
        if i:
            self.create_image(
                xstart, ystart, image=self._img_start, anchor=S, tags=TAG_TRACK
            )
            self.create_image(x2, y2, image=self._img_end, anchor=S, tags=TAG_TRACK)

    def draw_marker(self, marker: Point, markertype: str = TAG_LOCATION):
        """
        Draw marker point on canvas

        :param Point marker: marker point
        :param str markertype: marker type
        """

        x, y = ll2xy(self.width, self.height, self._bounds, marker)
        if markertype == TAG_MARKER:
            self.delete(TAG_MARKER)
            self.create_circle(
                x, y, 2, outline=MARKERCOL, fill=MARKERCOL, tags=TAG_MARKER
            )
            self.create_text(
                x,
                y,
                text=f"{marker.lat:.08f}\n{marker.lon:.08f}",
                anchor=CENTER,
                fill=MARKERCOL,
                tags=TAG_MARKER,
            )
        else:
            self.delete(TAG_LOCATION)
            self.create_line(
                x,
                y - MARKERSIZE,
                x,
                y + MARKERSIZE,
                fill=MARKERCOL,
                width=2,
                tags=TAG_LOCATION,
            )
            self.create_line(
                x - MARKERSIZE,
                y,
                x + MARKERSIZE,
                y,
                fill=MARKERCOL,
                width=2,
                tags=TAG_LOCATION,
            )

    def draw_hacc(self, location: Point, hacc: float):
        """
        Draw horizontal accuracy perimeter on canvas.

        :param float hacc: horizontal accurancy in meters
        """

        # FYI not possible to draw translucent circles in tkinter
        # other than by messing around with stippled polygons
        self.delete(TAG_HACC)
        radius = int(
            sqrt(self.height**2 + self.width**2)
            * hacc
            / planar(
                self._bounds.lat1,
                self._bounds.lon1,
                self._bounds.lat2,
                self._bounds.lon2,
            )
        )
        x, y = ll2xy(self.width, self.height, self._bounds, location)
        self.create_circle(x, y, radius, outline=HACCCOL, fill="", tags=TAG_HACC)

    def draw_countdown(self, wait: int):
        """
        Draw clock icon indicating time until next scheduled map refresh.

        :param int wait: wait time in seconds
        """

        self.delete(TAG_CLOCK)
        self.create_oval((5, 5, 20, 20), fill="", outline="black", tags=TAG_CLOCK)
        self.create_arc(
            (5, 5, 20, 20),
            start=90,
            extent=wait,
            fill="black",
            outline="black",
            tags=TAG_CLOCK,
        )

    def draw_msg(self, msg: str, color: str = PNTCOL):
        """
        Draw message on canvas.

        :param str msg: message
        :param str color: color
        """

        w, h = self.get_size()
        self.delete(ALL)
        self.create_text(
            w / 2,
            h / 2,
            text=msg,
            fill=color,
            font=self._font,
            anchor=CENTER,
        )

    def on_clear(self, event):  # pylint: disable=unused-argument
        """
        Clear map image.
        """

        self.delete(ALL)
        self._marker = None

    def _on_resize(self, event):  # pylint: disable=unused-argument
        """
        Resize frame

        :param event event: resize event
        """

        self.width, self.height = self.get_size()
        self._font, self._fonth = scale_font(self.width, 10, 25, 20)

    def get_size(self) -> tuple:
        """
        Get current canvas size.

        :return: window size (width, height)
        :rtype: tuple
        """

        self.update_idletasks()  # Make sure we know about any resizing
        return self.winfo_width(), self.winfo_height()

    @staticmethod
    def zoom_bounds(
        height: int, width: int, location: Point, zoom: int, maptype: str = CUSTOM
    ) -> Area:
        """
        Get map bounds for given zoom level.

        :param int height: height
        :param int width: width
        :param Point location: location
        :param int zoom: zoom level
        :param str maptype: map type
        :return: zoom bounds
        :rtype: Area
        """

        if location is None:
            return None
        xoff = 90 / 2**zoom
        yoff = xoff * height / width
        return Area(
            location.lat - yoff,
            location.lon - xoff,
            location.lat + yoff,
            location.lon + xoff,
        )

    @property
    def bounds(self) -> Area:
        """
        Getter for custom map bounds.

        :return: bounds of displayed map
        :rtype: Area or None
        """

        return self._bounds

    @property
    def marker(self) -> Point:
        """
        Getter for marker.

        :return: marked location
        :rtype: Point
        """

        return self._marker

    @property
    def track(self) -> list:
        """
        Getter for track.

        :return: recorded track
        :rtype: list or None
        """

        return self._track

    @property
    def trackbounds(self) -> tuple:
        """
        Getter for track bounds and center.

        :return: tuple of (bounds, center point)
        :rtype: (Area, Point)
        """

        if isinstance(self._track, list):
            if len(self._track) > 0:
                return get_track_bounds(self._track)
        return None, None

    @property
    def zoom(self) -> int:
        """
        Getter for zoom.

        :return: applied zoom
        :rtype: int or None
        """

        return self._zoom

    @property
    def zoommin(self) -> bool:
        """
        Getter for zoommin flag.

        :return: if max zoom reached
        :rtype: bool
        """

        return self._zoommin

    @track.setter
    def track(self, location: Point):
        """
        Update or reset track list.
        Set location to None to reset.

        :param Point location: location
        """

        if location is None:
            self._track = None
            return
        if self._track is None:
            self._track = []

        if len(self._track) > 0:  # only record if different from previous
            if round(self._track[-1][0], 8) != round(location.lat, 8) or round(
                self._track[-1][1], 8
            ) != round(location.lon, 8):
                self._track.append(Point(location.lat, location.lon))
        else:
            self._track.append(Point(location.lat, location.lon))
        # limit size of track list
        while len(self._track) > POINTLIMIT:
            self._track.pop(randrange(1, len(self._track) - 1))
