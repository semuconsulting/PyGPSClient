"""
Mapview frame class for PyGPSClient application.

This handles a frame containing a location map downloaded via a MapQuest API.

NOTE: The free MapQuest API key is subject to a limit of 15,000
transactions / month, or roughly 500 / day, so the map updates are only
run periodically (once a minute). This utility is NOT intended to be used for
real time navigation.

Created on 13 Sep 2020

:author: semuadmin
:copyright: SEMU Consulting © 2020
:license: BSD 3-Clause
"""
# pylint: disable=invalid-name

from io import BytesIO
from time import time
from tkinter import Frame, Canvas, font, NW, N, S, E, W
from http.client import responses
from PIL import ImageTk, Image
from requests import get, RequestException, ConnectionError as ConnError, ConnectTimeout

from pygpsclient.globals import (
    WIDGETU2,
    MAPURL,
    MAP_UPDATE_INTERVAL,
    IMG_WORLD,
    ICON_POS,
    BGCOL,
)
from pygpsclient.strings import (
    NOWEBMAPFIX,
    NOWEBMAPCONN,
    NOWEBMAPHTTP,
    NOWEBMAPKEY,
)


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
        self.__master = self.__app.get_master()  # Reference to root class (Tk)

        Frame.__init__(self, self.__master, *args, **kwargs)

        def_w, def_h = WIDGETU2
        self.width = kwargs.get("width", def_w)
        self.height = kwargs.get("height", def_h)
        self._img = None
        self._marker = None
        self._last_map_update = 0
        self._body()

        self.bind("<Configure>", self._on_resize)

    def _body(self):
        """
        Set up frame and widgets.
        """

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.can_mapview = Canvas(self, width=self.width, height=self.height, bg=BGCOL)
        self.can_mapview.grid(column=0, row=0, sticky=(N, S, E, W))

    def update_map(self):
        """
        Draw map and mark current known position and horizontal accuracy (where available).
        """

        lat = self.__app.gnss_status.lat
        lon = self.__app.gnss_status.lon
        hacc = self.__app.gnss_status.hacc

        if self.__app.frm_settings.webmap:
            static = False
        else:
            static = True

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

        if static:
            self._draw_static_map(lat, lon)
        else:
            if hacc is None or hacc == "":
                hacc = 0
            self._draw_web_map(lat, lon, hacc)

    def _draw_static_map(self, lat: float, lon: float):
        """
        Draw fixed scale Mercator world map

        :param float lat: latitude
        :param float lon: longitude
        """

        OFFSET_X = 0
        OFFSET_Y = 0

        w, h = self.width, self.height
        self.can_mapview.delete("all")
        self._img = ImageTk.PhotoImage(
            Image.open(IMG_WORLD).resize((w, h), Image.ANTIALIAS)
        )
        self._marker = ImageTk.PhotoImage(Image.open(ICON_POS))
        self.can_mapview.create_image(0, 0, image=self._img, anchor=NW)
        x = (w / 2) + int((lon * (w / 360))) + OFFSET_X
        y = (h / 2) - int((lat * (h / 180))) + OFFSET_Y
        self.can_mapview.create_image(x, y, image=self._marker, anchor=S)

    def _draw_web_map(self, lat: float, lon: float, hacc: float):
        """
        Draw scalable web map via MapQuest API

        :param float lat: latitude
        :param float lon: longitude
        :param float hacc: horizontal accuracy
        """

        sc = "NO CONNECTION"
        msg = ""

        apikey = self.__app.api_key
        if apikey == "":
            self._disp_error(NOWEBMAPKEY)
            return

        now = time()
        if now - self._last_map_update < MAP_UPDATE_INTERVAL:
            self._draw_countdown(
                (-360 / MAP_UPDATE_INTERVAL) * (now - self._last_map_update)
            )
            return
        self._last_map_update = now

        url = self._format_url(apikey, lat, lon, hacc)

        try:
            response = get(url)
            sc = responses[response.status_code]  # get descriptive HTTP status
            response.raise_for_status()  # raise Exception on HTTP error
            if sc == "OK":
                img_data = response.content
                self._img = ImageTk.PhotoImage(Image.open(BytesIO(img_data)))
                self.can_mapview.delete("all")
                self.can_mapview.create_image(0, 0, image=self._img, anchor=NW)
                self.can_mapview.update_idletasks()
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

        self.can_mapview.create_oval((5, 5, 20, 20), fill="#616161", outline="")
        self.can_mapview.create_arc(
            (5, 5, 20, 20), start=90, extent=wait, fill="#ffffff", outline=""
        )

    def _format_url(self, apikey: str, lat: float, lon: float, hacc: float):
        """
        Formats URL for web map download.

        :param str apikey: MapQuest API key
        :param float lat: latitude
        :param float lon: longitude
        :param float hacc: horizontal accuracy
        :return: formatted MapQuest URL
        :rtype: str
        """

        w, h = self.width, self.height
        radius = str(hacc / 1000)  # km

        return MAPURL.format(
            apikey, lat, lon, self.__app.frm_settings.mapzoom, radius, lat, lon, w, h
        )

    def _disp_error(self, msg):
        """
        Display error message in webmap widget.

        :param str msg: error message
        """

        w, h = self.width, self.height
        resize_font = font.Font(size=min(int(w / 20), 14))

        self.can_mapview.delete("all")
        self.can_mapview.create_text(
            w / 2,
            h / 2 - (w / 20),
            text=msg,
            fill="orange",
            font=resize_font,
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

    def get_size(self):
        """
        Get current canvas size.

        :return: window size (width, height)
        :rtype: tuple
        """

        self.update_idletasks()  # Make sure we know about any resizing
        width = self.can_mapview.winfo_width()
        height = self.can_mapview.winfo_height()
        return (width, height)
