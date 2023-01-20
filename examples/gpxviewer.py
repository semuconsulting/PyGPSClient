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

import sys
from os import getenv
from xml.dom import minidom
from io import BytesIO
from tkinter import Tk, Canvas, NW
from PIL import ImageTk, Image
from requests import (
    get,
    RequestException,
    ConnectionError as ConnError,
    ConnectTimeout,
    HTTPError,
)

MAPURL = (
    "https://www.mapquestapi.com/staticmap/v5/map?key={}&size={},{}&zoom={}"
    + "&defaultMarker=marker-sm-616161-ff4444&shape=weight:2|border:{}|{}"
    + "&scalebar=true|bottom"
)


def get_track(filename: str) -> str:
    """Get track from GPX file."""

    with open(filename, "r", encoding="utf-8") as gpx:

        parser = minidom.parse(gpx)
        pts = parser.getElementsByTagName("trkpt")
        track = ""
        for data in pts:
            lat = data.attributes["lat"].value
            lon = data.attributes["lon"].value
            track += f"{lat},{lon}|"
        return track


def get_map(
    width: int, height: int, track: list, zoom: int, col: str
) -> ImageTk.PhotoImage:
    """Get map image from MapQuest API."""

    img = None
    try:
        apikey = getenv("MQAPIKEY")
        url = MAPURL.format(apikey, width, height, zoom, col, track)
        response = get(url, timeout=5)
        response.raise_for_status()  # raise Exception on HTTP error
        img = ImageTk.PhotoImage(Image.open(BytesIO(response.content)))
    except (ConnError, ConnectTimeout, RequestException, HTTPError) as err:
        print(f"Request error: {err}")

    return img


def main(**kwargs):
    """Main routine."""

    # get keyword arguments, including GPX file name
    gpxfile = kwargs.get("filename", "pygpstrack.gpx")
    width = int(kwargs.get("width", 800))
    height = int(kwargs.get("height", 600))
    zoom = int(kwargs.get("zoom", 12))
    col = kwargs.get("col", "ff00ff")

    # create an instance of tkinter frame
    win = Tk()
    win.title("GPX VIEWER")
    win.geometry(f"{width}x{height}")

    # create image canvas
    canvas = Canvas(win, width=width, height=height)
    canvas.pack()

    # get track from file
    track = get_track(gpxfile)

    # get static map image from MapQuest API and display on canvas
    img = get_map(width, height, track, zoom, col)
    if img is not None:
        canvas.delete("all")
        canvas.create_image(0, 0, image=img, anchor=NW)

    win.mainloop()


if __name__ == "__main__":

    # call main routine with keyword arguments
    main(**dict(arg.split("=") for arg in sys.argv[1:]))
