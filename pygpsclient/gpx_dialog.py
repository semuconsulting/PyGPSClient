"""
gpx_dialog.py

This is the pop-up dialog for the GPX Viewer function.

Created on 10 Jan 2023

:author: semuadmin
:copyright: SEMU Consulting © 2023
:license: BSD 3-Clause
"""
# pylint: disable=invalid-name, unused-argument

from math import ceil
from xml.dom import minidom
from io import BytesIO
from pathlib import Path
from datetime import datetime
from tkinter import (
    Toplevel,
    Frame,
    Canvas,
    Spinbox,
    Label,
    Button,
    font,
    filedialog,
    StringVar,
    IntVar,
    NW,
    N,
    S,
    W,
    E,
)
from http.client import responses
from requests import (
    get,
    RequestException,
    ConnectionError as ConnError,
    ConnectTimeout,
    HTTPError,
)
from PIL import ImageTk, Image
from pygpsclient.globals import (
    ICON_LOAD,
    ICON_EXIT,
    ICON_REDRAW,
    POPUP_TRANSIENT,
    BGCOL,
    ENTCOL,
    READONLY,
)
from pygpsclient.strings import DLGGPXVIEWER, READTITLE
from pygpsclient.helpers import mapq_compress, haversine

HOME = str(Path.home())
MAPURL = (
    "https://www.mapquestapi.com/staticmap/v5/map?key={}&size={},{}"
    + "&zoom={}&locations={},{}||{},{}&defaultMarker=marker-num"
    + "&shape=weight:2|border:{}|{}&scalebar=true|bottom"
)
TRKLIMIT = 500  # max number of polygon points supported by MapQuest API
# profile chart parameters:
AXIS_XL = 30  # x axis left offset
AXIS_XR = 20  # x axis right offset
AXIS_Y = 15  # y axis bottom offset
ELEAX_COL = "green4"  # color of elevation plot axis
ELE_COL = "palegreen3"  # color of elevation plot
SPD_COL = "blue"  # color of speed plot


class GPXViewerDialog(Toplevel):
    """GPXViewerDialog class."""

    def __init__(self, app, *args, **kwargs):
        """Constructor."""

        self.__app = app
        self.__master = self.__app.get_master()  # link to root Tk window
        Toplevel.__init__(self, app)
        if POPUP_TRANSIENT:
            self.transient(self.__app)
        self.resizable(False, False)
        self.title(DLGGPXVIEWER)
        self.protocol("WM_DELETE_WINDOW", self.on_exit)
        self._img_load = ImageTk.PhotoImage(Image.open(ICON_LOAD))
        self._img_redraw = ImageTk.PhotoImage(Image.open(ICON_REDRAW))
        self._img_exit = ImageTk.PhotoImage(Image.open(ICON_EXIT))
        self.width = int(kwargs.get("width", 800))
        self.height = int(kwargs.get("height", 800))
        self.mheight = int(self.height * 0.75)
        self.pheight = int(self.height * 0.25)
        self._zoom = IntVar()
        self._info = StringVar()
        self._zoom.set(12)
        self._mapimg = None
        self._track = None
        self._gpxfile = None
        self._metadata = {}

        self._body()
        self._do_layout()
        self._reset()

    def _body(self):
        """
        Create widgets.
        """

        self._frm_map = Frame(self, borderwidth=2, relief="groove", bg=BGCOL)
        self._frm_profile = Frame(self, borderwidth=2, relief="groove", bg=BGCOL)
        self._frm_info = Frame(self, borderwidth=2, relief="groove")
        self._frm_controls = Frame(self, borderwidth=2, relief="groove")
        self._canvas_map = Canvas(
            self._frm_map, width=self.width, height=self.mheight, bg=BGCOL
        )
        self._canvas_profile = Canvas(
            self._frm_profile, width=self.width, height=self.pheight, bg="#f0f0e8"
        )
        self._lbl_info = Label(self._frm_info, textvariable=self._info, anchor="w")
        self._btn_load = Button(
            self._frm_controls,
            image=self._img_load,
            width=40,
            command=self._on_load,
        )
        self._lbl_zoom = Label(self._frm_controls, text="Zoom")
        self._spn_zoom = Spinbox(
            self._frm_controls,
            from_=1,
            to=20,
            width=5,
            readonlybackground=ENTCOL,
            wrap=True,
            textvariable=self._zoom,
            state=READONLY,
        )
        self._btn_redraw = Button(
            self._frm_controls,
            image=self._img_redraw,
            width=40,
            command=self._on_redraw,
        )
        self._btn_exit = Button(
            self._frm_controls,
            image=self._img_exit,
            width=40,
            command=self.on_exit,
        )

    def _do_layout(self):
        """
        Arrange widgets.
        """

        self._frm_map.grid(column=0, row=0, sticky=(N, S, E, W))
        self._frm_profile.grid(column=0, row=1, sticky=(W, E))
        self._frm_info.grid(column=0, row=2, sticky=(W, E))
        self._frm_controls.grid(column=0, row=3, columnspan=7, sticky=(W, E))
        self._canvas_map.grid(
            column=0,
            row=0,
        )
        self._canvas_profile.grid(
            column=0,
            row=0,
        )
        self._lbl_info.grid(column=0, row=0, padx=3, pady=3, sticky=(W, E))
        self._btn_load.grid(column=0, row=1, padx=3, pady=3)
        self._lbl_zoom.grid(
            column=1,
            row=1,
            padx=3,
            pady=3,
        )
        self._spn_zoom.grid(
            column=2,
            row=1,
            padx=3,
            pady=3,
        )
        self._btn_redraw.grid(
            column=3,
            row=1,
            padx=3,
            pady=3,
        )
        self._btn_exit.grid(column=4, row=1, padx=3, pady=3, sticky=(E))

    def _reset(self):
        """
        Reset application.
        """

        self._canvas_map.delete("all")
        self._canvas_profile.delete("all")
        self._info.set("")

    def on_exit(self, *args, **kwargs):
        """
        Handle Exit button press.
        """

        self.__app.stop_gpxviewer_thread()
        self.destroy()

    def _on_select_profile(self, event):
        """
        Handle select profile event.
        """

        # print(f"profile = {self._profile.get()}")

    def _on_redraw(self, *args, **kwargs):
        """
        Handle redraw button press.
        """

        self._reset()
        self._draw_map(self._track)
        self._draw_profile(self._track)
        self._format_metadata(self._metadata)

    def get_size(self):
        """
        Get current frame size.

        :return: window size (width, height)
        :rtype: tuple
        """

        self.__master.update_idletasks()  # Make sure we know about any resizing
        return (self.winfo_width(), self.winfo_height())

    def _open_gpxfile(self) -> str:
        """
        Open gpx file.
        """

        gpxfile = filedialog.askopenfilename(
            parent=self,
            title=READTITLE,
            initialdir=HOME,
            filetypes=(
                ("gpx files", "*.gpx"),
                ("all files", "*.*"),
            ),
        )
        if gpxfile in ((), ""):
            return None  # User cancelled
        return gpxfile

    def _on_load(self):
        """
        Load gpx track from file.
        """

        self._gpxfile = self._open_gpxfile()
        if self._gpxfile is None:  # user cancelled
            return

        self._do_mapalert("LOADING GPX TRACK ...")

        with open(self._gpxfile, "r", encoding="utf-8") as gpx:

            try:
                parser = minidom.parse(gpx)
                trk = parser.getElementsByTagName("trkpt")
                self._process_track(trk)
            except (TypeError, AttributeError) as err:
                self._do_mapalert("GPX PARSING ERROR!")
                print(err)

    def _process_track(self, trk: list):
        """
        Process trackpoint data.

        :param list trk: list of track elements
        """

        rng = len(trk)
        if rng == 0:
            self._do_mapalert("NO TRACKPOINTS IN GPX FILE!")
            return

        stp = 1
        # if the number of trackpoints exceeds the MapQuest API limit,
        # increase step count until the number is within limits
        while rng / stp > TRKLIMIT:
            stp += 1

        points = []
        track = []
        start = end = dist = lat1 = lon1 = tim1 = maxele = spd = maxspd = 0
        minele = minspd = 1e10
        for i in range(0, rng, stp):
            lat = float(trk[i].attributes["lat"].value)
            lon = float(trk[i].attributes["lon"].value)
            tim = trk[i].getElementsByTagName("time")[0].firstChild.data
            if tim[-1] == "Z":  # strip timezone label
                tim = tim[0:-1]
            if tim[-4] == ".":  # has microseconds
                tfm = "%Y-%m-%dT%H:%M:%S.%f"
            else:
                tfm = "%Y-%m-%dT%H:%M:%S"
            tim = datetime.strptime(tim, tfm).timestamp()
            if i == 0:
                lat1, lon1, tim1 = lat, lon, tim
                start = tim
            else:
                leg = haversine(lat1, lon1, lat, lon)  # km
                dist += leg
                spd = leg * 3600 / (tim - tim1)  # km/h
                maxspd = max(spd, maxspd)
                minspd = min(spd, minspd)
                lat1, lon1, tim1 = lat, lon, tim
                end = tim
            try:
                ele = float(trk[i].getElementsByTagName("ele")[0].firstChild.data)
                maxele = max(ele, maxele)
                minele = min(ele, minele)
            except IndexError:  # 'ele' element does not exist
                ele = 0.0
            track.append((lat, lon, tim, ele, spd))
            points.append(lat)
            points.append(lon)

        elapsed = end - start
        self._track = track
        self._metadata["points"] = rng
        self._metadata["elapsed"] = elapsed
        self._metadata["distance"] = dist
        self._metadata["min_elevation"] = minele
        self._metadata["max_elevation"] = maxele
        self._metadata["min_speed"] = minspd
        self._metadata["max_speed"] = maxspd
        self._draw_map(self._track)
        self._draw_profile(self._track)
        self._format_metadata(self._metadata)

    def _draw_map(self, track: list) -> ImageTk.PhotoImage:
        """
        Draw static map image via MapQuest API.

        :param list track: list of lat/lon points
        :return: image of map as PhotoImage
        :rtype: ImageTk.PhotoImage
        """
        # pylint: disable=unused-variable

        apikey = self.__app.api_key
        lat1, lon1, tim, ele, spd = self._track[0]  # start point, labelled 1
        lat2, lon2, tim, ele, spd = self._track[-1]  # end point, labelled 2
        # tstr = ""
        points = []
        for (lat, lon, tim, ele, spd) in track:
            # tstr += f"{lat},{lon}|"
            points.append(lat)
            points.append(lon)

        # compress polygon for MapQuest API
        comp = mapq_compress(points, 6)
        tstr = f"cmp6|enc:{comp}"

        try:
            url = MAPURL.format(
                apikey,
                self.width,
                self.mheight,
                self._zoom.get(),
                lat1,
                lon1,
                lat2,
                lon2,
                "ff00ff",
                tstr,
            )
            response = get(url, timeout=5)
            response.raise_for_status()  # raise Exception on HTTP error
            self._mapimg = ImageTk.PhotoImage(Image.open(BytesIO(response.content)))
        except (ConnError, ConnectTimeout, RequestException, HTTPError):
            self._do_mapalert(
                f"MAPQUEST API ERROR: HTTP code {response.status_code} "
                + f"{responses[response.status_code]}\n\n{response.text}"
            )

        self._canvas_map.create_image(0, 0, image=self._mapimg, anchor=NW)

    def _get_point(self, maxy: int, maxx: int, ele: float, pnt: int) -> tuple:
        """
        Convert elevation values to canvas pixel coordinates (x,y).

        :param int maxy: max extent of y axis
        :param int maxx: max extent of x axis
        :param int ele: elevation value
        :param int pnt: point value
        :return: (x,y)
        :rtype: tuple
        """

        x = AXIS_XL + ((self.width - AXIS_XL - AXIS_XR) * pnt / maxx)
        y = self.pheight - AXIS_Y - ((self.pheight - AXIS_Y) * ele / maxy)
        return int(x), int(y)

    def _draw_profile(self, track: list):
        """
        Plot elevation profile with auto-ranged axes.
        :param list track: list of lat/lon points
        """
        # pylint: disable=unused-variable

        self._canvas_profile.delete("all")
        # find maximum extents for x and y axes
        maxx = len(track)
        maxe = self._metadata["max_elevation"]
        maxs = self._metadata["max_speed"]
        for i in (50, 100, 250, 500, 1000, 2500, 5000, 10000, 25000):
            if maxe < i:
                maxe = i
                break
        for i in (5, 10, 25, 50, 100, 200, 500, 1000):
            if maxs < i:
                maxs = i
                break

        # plot elevation and speed
        x2 = x4 = AXIS_XL
        y2 = y4 = self.pheight - AXIS_Y
        for i, (lat, lon, tim, ele, spd) in enumerate(track):

            if ele is None:
                continue
            x1, y1 = self._get_point(maxe, maxx, 0, i)
            x2, y2 = self._get_point(maxe, maxx, ele, i)
            if i:
                self._canvas_profile.create_line(x1, y1, x2, y2, fill=ELE_COL, width=2)

            if spd is None:
                continue
            x3, y3 = x4, y4
            x4, y4 = self._get_point(maxs, maxx, spd, i)
            if i:
                self._canvas_profile.create_line(x3, y3, x4, y4, fill=SPD_COL, width=1)

        # plot elevation (yL) axis grid
        fnt = font.Font(size=10)
        for ele in range(0, maxe, int(maxe / 5)):
            if ele is None:
                continue
            x1, y1 = self._get_point(maxe, maxx, ele, 0)
            x2, y2 = self._get_point(maxe, maxx, ele, maxx)
            self._canvas_profile.create_line(x1, y1, x2 + 1, y1, fill="grey")
            self._canvas_profile.create_text(
                x1 - 2, y1, text=f"{ele}", fill=ELEAX_COL, font=fnt, anchor="e"
            )
        self._canvas_profile.create_text(
            5, -8 + self.pheight / 2, text="m", fill=ELEAX_COL, anchor="w"
        )

        # plot speed (yR) axis grid
        fnt = font.Font(size=10)
        for spd in range(0, maxs, int(maxs / 5)):
            if spd is None:
                continue
            x1, y1 = self._get_point(maxs, maxx, spd, maxx)
            x2, y2 = self._get_point(maxs, maxx, spd, maxx - 5)
            self._canvas_profile.create_text(
                self.width - AXIS_XR,
                y1,
                text=f"{spd}",
                fill=SPD_COL,
                font=fnt,
                anchor="w",
            )
        self._canvas_profile.create_text(
            self.width - 5,
            -8 + self.pheight / 2,
            text="km/h",
            fill=SPD_COL,
            angle=90,
        )

        # plot trackpoint (X) axis grid
        for n in range(0, maxx, int(maxx / 10)):
            x1, y1 = self._get_point(maxe, maxx, 0, n)
            x2, y2 = self._get_point(maxe, maxx, maxe, n)
            self._canvas_profile.create_line(x1, y1 - 1, x1, y2, fill="grey")
            self._canvas_profile.create_text(
                x1, y1 + 8, text=f"{ceil(n*100/maxx)}%", fill="grey", font=fnt
            )

    def _format_metadata(self, metadata: dict) -> str:
        """
        Format metadata as string.
        """

        elapsed = self._metadata["elapsed"] / 3600  # h
        dist = self._metadata["distance"]  # km
        minele = self._metadata["min_elevation"]  # m
        maxele = self._metadata["max_elevation"]  # m
        maxspd = self._metadata["max_speed"]  # km/h

        if maxele == 0 and minele == 1e10:
            ele = "N/A"
        else:
            ele = (
                f"(m) min: {minele:,.3f} max: {maxele:,.3f} "
                + f"ascent {maxele-minele:,.3f}; "
            )
        metadata = (
            f"Points: {self._metadata['points']:,}; Dist (km): {dist:,.3f}; "
            + f"Elapsed (hours): {elapsed:,.3f}; "
            + f"Speed (km/h) avg: {(dist/elapsed):,.3f} "
            + f"max: {maxspd:,.3f}; Elevation "
            + ele
        )
        self._info.set(metadata)

    def _do_mapalert(self, msg: str):
        """
        Display alert on map canvas.
        """

        self._reset()
        self._canvas_map.create_text(
            self.width / 2,
            self.mheight / 2,
            text=msg,
            fill="orange",
        )
        self.update_idletasks()

    @property
    def metadata(self) -> dict:
        """
        Getter for metadata.
        """

        return self._metadata

    @property
    def track(self) -> str:
        """
        Getter for track.
        """

        return self._track

    @property
    def mapimage(self) -> ImageTk.PhotoImage:
        """
        Getter for image of map.
        """

        return self._mapimg
