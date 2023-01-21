"""
gpxviewer.py

Simple illustration of how to display a GPX track from a file.
Uses a MapQuest static map API which requires a free 32-char API key:
https://developer.mapquest.com/user/login/sign-up

The API key can be passed as command line keyword, or saved
as environment variable MQAPIKEY.

Usage:

python3 gpxviewer.py filename=pygpstrack.gpx

Optional command line keyword arguments:

width (800)
height (600)
zoom (12)
col ("ff00ff" = purple)
mqapikey (environment variable MQAPIKEY)

Created on 20 Sep 2020

:author: semuadmin
:copyright: SEMU Consulting © 2020
:license: BSD 3-Clause
"""
# pylint: disable=invalid-name

import sys
from os import getenv
from math import ceil
from xml.dom import minidom
from io import BytesIO
from tkinter import Tk, Frame, Canvas, font, NW, N, S, W, E
from PIL import ImageTk, Image
from requests import (
    get,
    RequestException,
    ConnectionError as ConnError,
    ConnectTimeout,
    HTTPError,
)

MAPURL = (
    "https://www.mapquestapi.com/staticmap/v5/map?key={}&size={},{}"
    + "&zoom={}&locations={},{}||{},{}&defaultMarker=marker-num"
    + "&zoom={}&locations={},{}||{},{}&defaultMarker=marker-num"
    + "&shape=weight:2|border:{}|{}&scalebar=true|bottom"
)
AXIS_XL = 35  # x axis left offset
AXIS_XL = 35  # x axis left offset
AXIS_XR = 10  # x axis right offset
AXIS_Y = 25  # y axis bottom offset
PROFILE_Y = 25  # % height occupied by elevation profile


class GPXViewer(Frame):
    """GPXViewer Frame class."""

    def __init__(self, master, *args, **kwargs):
        """Constructor."""

        self.__master = master  # link to root Tk window

        # get keyword arguments, including GPX file name
        self.gpxfile = kwargs.pop("filename", "pygpstrack.gpx")
        self.width = int(kwargs.pop("width", 800))
        self.height = int(kwargs.pop("height", 800))
        self.zoom = int(kwargs.pop("zoom", 12))
        self.col = kwargs.pop("col", "ff00ff")
        self._mqapikey = kwargs.pop("mqapikey", getenv("MQAPIKEY"))
        # height of map canvas
        self.mheight = int(self.height - self.height * PROFILE_Y / 100)
        # height of elevation profile canvas
        self.pheight = int(self.height * PROFILE_Y / 100)
        self.mapimg = None

        Frame.__init__(self, self.__master, *args, **kwargs)

        self._body()
        self._do_layout()
        self._reset()

    def _body(self):
        """
        Create widgets.
        """

        self.__master.title("GPX VIEWER")
        self.__master.geometry(f"{self.width}x{self.height}")
        self._canvas_map = Canvas(self.__master, width=self.width, height=self.mheight)
        self._canvas_profile = Canvas(
            self.__master, width=self.width, height=self.pheight, bg="#f0f0e8"
        )

    def _do_layout(self):
        """
        Arrange widgets.
        """

        self._canvas_map.grid(column=0, row=0, sticky=(N, S, E, W))
        self._canvas_profile.grid(column=0, row=1, sticky=(W, E))

    def _reset(self):
        """
        Reset application.
        """

        track = self._get_track(self.gpxfile)
        self.draw_map(track)
        self.draw_profile(track)

    @property
    def appmaster(self):
        """
        Get reference to application Tk root.
        """

        return self.__master

    def _get_track(self, filename: str) -> list:
        """
        Get track and elevation profile from GPX file.
        """

        with open(filename, "r", encoding="utf-8") as gpx:

            parser = minidom.parse(gpx)
            pts = parser.getElementsByTagName("trkpt")
            track = []
            for pt in pts:
                lat = float(pt.attributes["lat"].value)
                lon = float(pt.attributes["lon"].value)
                ele = float(pt.getElementsByTagName("ele")[0].firstChild.data)
                track.append((lat, lon, ele))
            return track

    def draw_map(self, track: list) -> ImageTk.PhotoImage:
        """
        Draw static map image via MapQuest API.
        """

        lat1, lon1, _ = track[0]  # start point, labelled 1
        lat2, lon2, _ = track[-1]  # end point, labelled 2
        tstr = ""
        for (lat, lon, _) in track:
            tstr += f"{lat},{lon}|"

        try:
            url = MAPURL.format(
                self._mqapikey,
                self.width,
                self.mheight,
                self.zoom,
                lat1,
                lon1,
                lat2,
                lon2,
                self.col,
                tstr,
            )
            response = get(url, timeout=5)
            response.raise_for_status()  # raise Exception on HTTP error
            self.mapimg = ImageTk.PhotoImage(Image.open(BytesIO(response.content)))
        except (ConnError, ConnectTimeout, RequestException, HTTPError) as err:
            print(f"Request error: {err}")

        self._canvas_map.delete("all")
        self._canvas_map.create_image(0, 0, image=self.mapimg, anchor=NW)

    def _get_point(self, maxy: int, maxx: int, ele: float, pnt: int) -> tuple:
        """
        Convert elevation values to canvas pixel coordinates (x,y).
        """

        x = AXIS_XL + ((self.width - AXIS_XL - AXIS_XR) * pnt / maxx)
        y = self.pheight - AXIS_Y - ((self.pheight - AXIS_Y) * ele / maxy)
        return int(x), int(y)

    def draw_profile(self, track: list):
        """
        Plot elevation profile with auto-ranged axes.
        """

        self._canvas_profile.delete("all")
        # find maximum extents for x and y axes
        maxx = len(track)
        maxy = 0
        for (_, _, ele) in track:
            maxy = max(maxy, ele)
        for i in (50, 100, 250, 500, 1000, 2500, 5000, 10000, 25000):
            if maxy < i:
                maxy = i
                break

        # plot y (elevation) axis grid
        fnt = font.Font(size=10)
        for ele in range(0, maxy, int(maxy / 5)):
            x1, y1 = self._get_point(maxy, maxx, ele, 0)
            x2, y2 = self._get_point(maxy, maxx, ele, maxx)
            self._canvas_profile.create_line(x1, y1, x2 + 1, y1, fill="grey")
            self._canvas_profile.create_text(
                x1 - 2, y1, text=f"{ele}", fill="grey", font=fnt, anchor="e"
            )
        self._canvas_profile.create_text(
            5, -15 + self.pheight / 2, text="m", fill="grey", anchor="w"
        )

        # plot x (trackpoint) axis grid
        for n in range(0, maxx, int(maxx / 10)):
            x1, y1 = self._get_point(maxy, maxx, 0, n)
            x2, y2 = self._get_point(maxy, maxx, maxy, n)
            self._canvas_profile.create_line(x1, y1 - 1, x1, y2, fill="grey")
            self._canvas_profile.create_text(
                x1, y1 + 8, text=f"{ceil(n*100/maxx)}%", fill="grey", font=fnt
            )

        # plot elevation
        x2 = AXIS_XL
        y2 = self.pheight - AXIS_Y
        for i, (_, _, ele) in enumerate(track):
            x1, y1 = x2, y2
            x2, y2 = self._get_point(maxy, maxx, ele, i)
            if i:
                self._canvas_profile.create_line(x1, y1, x2, y2, fill="red", width=2)


if __name__ == "__main__":

    root = Tk()
    GPXViewer(root, **dict(arg.split("=") for arg in sys.argv[1:]))
    root.mainloop()
