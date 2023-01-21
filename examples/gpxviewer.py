"""
gpxviewer.py

Simple illustration of how to display a GPX track from a file.
Uses a MapQuest static map API which requires a free 32-char API key:
https://developer.mapquest.com/user/login/sign-up

Assumes this API key is saved in environment variable MQAPIKEY.

Usage:

python3 gpxviewer.py filename=pygpstrack.gpx

Optional command line arguments:

width (800)
height (600)
zoom (12)
col as hex RGB string ("ff00ff" = purple)

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
from tkinter import Tk, font, Canvas, NW, N, S, W, E
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
    + "&shape=weight:2|border:{}|{}&scalebar=true|bottom"
)
AXIS_XL = 35  # x axis left offset
AXIS_XR = 10  # x axis right offset
AXIS_Y = 25  # y axis bottom offset
PROFILE_Y = 0.25  # % height occupied by elevation profile


def get_track(filename: str) -> list:
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


def get_map(
    width: int, height: int, track: list, zoom: int, col: str
) -> ImageTk.PhotoImage:
    """
    Get static map image via MapQuest API.
    """

    img = None
    lat1, lon1, _ = track[0]  # start point, labelled 1
    lat2, lon2, _ = track[-1]  # end point, labelled 2
    tstr = ""
    for (lat, lon, _) in track:
        tstr += f"{lat},{lon}|"

    try:
        apikey = getenv("MQAPIKEY")
        url = MAPURL.format(
            apikey, width, height, zoom, lat1, lon1, lat2, lon2, col, tstr
        )
        response = get(url, timeout=5)
        response.raise_for_status()  # raise Exception on HTTP error
        img = ImageTk.PhotoImage(Image.open(BytesIO(response.content)))
    except (ConnError, ConnectTimeout, RequestException, HTTPError) as err:
        print(f"Request error: {err}")

    return img


def get_point(
    width: int, height: int, maxy: int, maxx: int, ele: float, pnt: int
) -> tuple:
    """
    Convert elevation values to canvas pixel coordinates (x,y).
    """

    x = AXIS_XL + ((width - AXIS_XL - AXIS_XR) * pnt / maxx)
    y = height - AXIS_Y - ((height - AXIS_Y) * ele / maxy)
    return int(x), int(y)


def get_profile(canvas: Canvas, width: int, height: int, track: list):
    """
    Plot elevation profile with auto-ranged axes.
    """

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
        x1, y1 = get_point(width, height, maxy, maxx, ele, 0)
        x2, y2 = get_point(width, height, maxy, maxx, ele, maxx)
        canvas.create_line(x1, y1, x2 + 1, y1, fill="grey")
        canvas.create_text(x1 - 2, y1, text=f"{ele}", fill="grey", font=fnt, anchor="e")

    # plot x (trackpoint) axis grid
    for n in range(0, maxx, int(maxx / 10)):
        x1, y1 = get_point(width, height, maxy, maxx, 0, n)
        x2, y2 = get_point(width, height, maxy, maxx, maxy, n)
        canvas.create_line(x1, y1 - 1, x1, y2, fill="grey")
        canvas.create_text(
            x1, y1 + 8, text=f"{ceil(n*100/maxx)}%", fill="grey", font=fnt
        )

    # plot elevation
    x2 = AXIS_XL
    y2 = height - AXIS_Y
    for i, (_, _, ele) in enumerate(track):
        x1, y1 = x2, y2
        x2, y2 = get_point(width, height, maxy, maxx, ele, i)
        if i:
            canvas.create_line(x1, y1, x2, y2, fill="red", width=2)


def main(**kwargs):
    """
    Main routine.
    """

    # get keyword arguments, including GPX file name
    gpxfile = kwargs.get("filename", "pygpstrack.gpx")
    width = int(kwargs.get("width", 800))
    height = int(kwargs.get("height", 800))
    zoom = int(kwargs.get("zoom", 12))
    col = kwargs.get("col", "ff00ff")

    # get track from GPX file
    track = get_track(gpxfile)

    # create an instance of tkinter frame
    win = Tk()
    win.title("GPX VIEWER")
    win.geometry(f"{width}x{height}")

    # get static map image from MapQuest API and display
    # on canvas
    profy = int(PROFILE_Y * height)
    canvas_map = Canvas(win, width=width, height=height - profy)
    img = get_map(width, height - profy, track, zoom, col)
    if map is not None:
        canvas_map.delete("all")
        canvas_map.create_image(0, 0, image=img, anchor=NW)

    # plot elevation profile on canvas
    canvas_profile = Canvas(win, width=width, height=profy, bg="#f0f0e8")
    get_profile(canvas_profile, width, profy, track)

    # arrange the canvases in the window
    canvas_map.grid(column=0, row=0, sticky=(N, S, E, W))
    canvas_profile.grid(column=0, row=1, sticky=(W, E))
    win.mainloop()


if __name__ == "__main__":

    # call main routine with keyword arguments
    main(**dict(arg.split("=") for arg in sys.argv[1:]))
