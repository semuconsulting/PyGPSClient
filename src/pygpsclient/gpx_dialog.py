"""
gpx_dialog.py

This is the pop-up dialog for the GPX Viewer function.

Created on 10 Jan 2023

:author: semuadmin
:copyright: SEMU Consulting © 2023
:license: BSD 3-Clause
"""
# pylint: disable=unused-argument

from datetime import datetime
from http.client import responses
from io import BytesIO
from tkinter import (
    BOTH,
    NW,
    YES,
    Button,
    Canvas,
    E,
    Frame,
    IntVar,
    Label,
    N,
    S,
    Spinbox,
    StringVar,
    Toplevel,
    W,
    filedialog,
    font,
)
from xml.dom import minidom

from PIL import Image, ImageTk
from requests import ConnectionError as ConnError
from requests import ConnectTimeout, HTTPError, RequestException, get

from pygpsclient.globals import (
    BGCOL,
    DLGTGPX,
    HOME,
    ICON_EXIT,
    ICON_LOAD,
    ICON_REDRAW,
    KM2M,
    KM2MIL,
    KM2NMIL,
    KPH2KNT,
    KPH2MPH,
    KPH2MPS,
    M2FT,
    POPUP_TRANSIENT,
    READONLY,
    UI,
    UIK,
    UMK,
)
from pygpsclient.helpers import haversine
from pygpsclient.mapquest import GPXLIMIT, GPXMAPURL, MAPQTIMEOUT, mapq_compress
from pygpsclient.strings import (
    DLGGPXERROR,
    DLGGPXLOAD,
    DLGGPXNULL,
    DLGGPXPROMPT,
    DLGGPXVIEWER,
    READTITLE,
)

# profile chart parameters:
AXIS_XL = 35  # x axis left offset
AXIS_XR = 35  # x axis right offset
AXIS_Y = 15  # y axis bottom offset
ELEAX_COL = "green4"  # color of elevation plot axis
ELE_COL = "palegreen3"  # color of elevation plot
SPD_COL = "blue"  # color of speed plot
MD_LINES = 2  # number of lines of metadata


class GPXViewerDialog(Toplevel):
    """GPXViewerDialog class."""

    def __init__(self, app, *args, **kwargs):
        """Constructor."""

        self.__app = app
        # self.__master = self.__app.appmaster  # link to root Tk window
        Toplevel.__init__(self, app)
        if POPUP_TRANSIENT:
            self.transient(self.__app)
        self.resizable(True, True)
        self.title(DLGGPXVIEWER)  # pylint: disable=E1102
        self.protocol("WM_DELETE_WINDOW", self.on_exit)
        self._img_load = ImageTk.PhotoImage(Image.open(ICON_LOAD))
        self._img_redraw = ImageTk.PhotoImage(Image.open(ICON_REDRAW))
        self._img_exit = ImageTk.PhotoImage(Image.open(ICON_EXIT))
        self.width = int(kwargs.get("width", 600))
        self.height = int(kwargs.get("height", 600))
        self.mheight = int(self.height * 0.75)
        self.pheight = int(self.height * 0.25)
        self._zoom = IntVar()
        zoom = int(kwargs.get("zoom", 12))
        self._zoom.set(zoom)
        self._info = []
        for _ in range(MD_LINES):
            self._info.append(StringVar())
        self._mapimg = None
        self._track = None
        self._gpxfile = None
        self._metadata = {}

        self._body()
        self._do_layout()
        self._attach_events()
        self._reset()

        self._do_mapalert(DLGGPXPROMPT)

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
        self._lbl_info = []
        for i in range(MD_LINES):
            self._lbl_info.append(
                Label(self._frm_info, textvariable=self._info[i], anchor="w")
            )
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
        self._canvas_map.pack(fill=BOTH, expand=YES)
        self._canvas_profile.pack(fill=BOTH, expand=YES)
        for i in range(MD_LINES):
            self._lbl_info[i].grid(column=0, row=i, padx=3, pady=1, sticky=(W, E))
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
        self._btn_exit.grid(column=4, row=1, padx=3, pady=3, sticky=E)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=3)
        self.grid_rowconfigure(1, weight=1)

    def _attach_events(self):
        """
        Bind events to window.
        """

        self.bind("<Configure>", self._on_resize)

    def _reset(self):
        """
        Reset application.
        """

        self._canvas_map.delete("all")
        self._canvas_profile.delete("all")
        for i in range(MD_LINES):
            self._info[i].set("")

    def on_exit(self, *args, **kwargs):
        """
        Handle Exit button press.
        """

        self.__app.stop_dialog(DLGTGPX)
        self.destroy()

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

        # self.update_idletasks()  # Make sure we know about any resizing
        return (self.winfo_width(), self.winfo_height())

    def _on_resize(self, event):
        """
        Resize frame

        :param event event: resize event
        """

        self.width, self.height = self.get_size()
        self.mheight = self._frm_map.winfo_height()
        self.pheight = self._frm_profile.winfo_height() - 5

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

        self._do_mapalert(DLGGPXLOAD)

        with open(self._gpxfile, "r", encoding="utf-8") as gpx:
            try:
                parser = minidom.parse(gpx)
                trkpts = parser.getElementsByTagName("trkpt")
                self._process_track(trkpts)
            except (TypeError, AttributeError) as err:
                self._do_mapalert(DLGGPXERROR)
                raise (err) from err

    def _process_track(self, trkpts: list):
        """
        Process trackpoint data.

        :param list trk: list of trackpoints
        """

        rng = len(trkpts)
        if rng == 0:
            self._do_mapalert(DLGGPXNULL)
            return

        track = []
        start = end = dist = lat1 = lon1 = tim1 = maxele = spd = spd1 = maxspd = 0
        minele = minspd = 1e10
        for i, trkpt in enumerate(trkpts):
            lat = float(trkpt.attributes["lat"].value)
            lon = float(trkpt.attributes["lon"].value)
            tim = self._get_time(trkpt.getElementsByTagName("time")[0].firstChild.data)
            if i == 0:
                lat1, lon1, tim1 = lat, lon, tim
                start = tim
            else:
                leg = haversine(lat1, lon1, lat, lon)  # km
                dist += leg
                if tim > tim1:
                    spd = leg * 3600 / (tim - tim1)  # km/h
                else:
                    spd = spd1
                spd1 = spd
                maxspd = max(spd, maxspd)
                minspd = min(spd, minspd)
                lat1, lon1, tim1 = lat, lon, tim
                end = tim
            try:
                ele = float(trkpt.getElementsByTagName("ele")[0].firstChild.data)
                maxele = max(ele, maxele)
                minele = min(ele, minele)
            except IndexError:  # 'ele' element does not exist
                ele = 0.0
            track.append((lat, lon, tim, ele, spd))

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

    def _get_time(self, tim: str) -> datetime:
        """
        Format datetime from ISO time element.

        :param str tim: iso time from trackpoint
        :return: datetime
        :rtype: datetime
        """

        if tim[-1] == "Z":  # strip timezone label
            tim = tim[0:-1]
        if tim[-4] == ".":  # has microseconds
            tfm = "%Y-%m-%dT%H:%M:%S.%f"
        else:
            tfm = "%Y-%m-%dT%H:%M:%S"
        return datetime.strptime(tim, tfm).timestamp()

    def _draw_map(self, track: list) -> ImageTk.PhotoImage:
        """
        Draw static map image via MapQuest API.

        :param list track: list of lat/lon points
        :return: image of map as PhotoImage
        :rtype: ImageTk.PhotoImage
        """
        # pylint: disable=unused-variable

        mqapikey = self.__app.config.get("mqapikey", "")
        lat1, lon1, _, _, _ = self._track[0]  # start point, labelled 1
        lat2, lon2, _, _, _ = self._track[-1]  # end point, labelled 2
        points = []

        # if the number of trackpoints exceeds the MapQuest API limit,
        # increase step count until the number is within limits
        stp = 1
        rng = len(track)
        while rng / stp > GPXLIMIT:
            stp += 1
        for i, (lat, lon, _, _, _) in enumerate(track):
            if i % stp == 0:
                points.append(lat)
                points.append(lon)

        # compress polygon for MapQuest API
        comp = mapq_compress(points, 6)
        tstr = f"cmp6|enc:{comp}"
        # seems to be bug in MapQuest API which causes error
        # if scalebar displayed at maximum zoom
        scalebar = "true" if self._zoom.get() < 20 else "false"

        try:
            url = GPXMAPURL.format(
                mqapikey,
                lat1,
                lon1,
                lat2,
                lon2,
                self._zoom.get(),
                self.width,
                self.mheight,
                "ff00ff",
                tstr,
                scalebar,
            )
            response = get(url, timeout=MAPQTIMEOUT)
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

        _, _, ele_u, ele_c, spd_u, spd_c = self._get_units()

        mid = int(len(track) / 2)
        self._canvas_profile.delete("all")
        # find maximum extents for x and y axes
        _, _, tim1, _, _ = self._track[0]  # start point, labelled 1
        _, _, timm, _, _ = self._track[mid]  # mid point
        _, _, tim2, _, _ = self._track[-1]  # end point, labelled 2
        maxx = len(track)
        maxe = self._metadata["max_elevation"] * ele_c
        maxs = self._metadata["max_speed"] * spd_c
        for i in (50, 100, 250, 500, 1000, 2500, 5000, 10000, 25000):
            if maxe < i:
                maxe = i
                break
        for i in (5, 10, 25, 50, 100, 200, 500, 1000):
            if maxs < i:
                maxs = i
                break

        # plot elevation
        x2 = AXIS_XL
        y2 = self.pheight - AXIS_Y
        for i, (_, _, _, ele, _) in enumerate(track):
            if ele is None:
                continue
            x1, y1 = self._get_point(maxe, maxx, 0, i)
            x2, y2 = self._get_point(maxe, maxx, ele * ele_c, i)
            if i:
                self._canvas_profile.create_line(x1, y1, x2, y2, fill=ELE_COL, width=2)

        # plot speed
        x2 = AXIS_XL
        y2 = self.pheight - AXIS_Y
        for i, (_, _, _, _, spd) in enumerate(track):
            if spd is None:
                continue
            x1, y1 = x2, y2
            x2, y2 = self._get_point(maxs, maxx, spd * spd_c, i)
            if i:
                self._canvas_profile.create_line(x1, y1, x2, y2, fill=SPD_COL, width=1)

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
            AXIS_XL - 2,
            self.pheight / 2 - 8,
            text=ele_u,
            fill=ELEAX_COL,
            font=fnt,
            anchor="e",
        )

        # plot speed (yR) axis grid
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
            self.width - AXIS_XR + 1,
            self.pheight / 2 - 8,
            text=spd_u,
            fill=SPD_COL,
            font=fnt,
            anchor="w",
        )

        # plot trackpoint (X) axis grid
        for n in range(0, maxx, int(maxx / 10)):
            x1, y1 = self._get_point(maxe, maxx, 0, n)
            x2, y2 = self._get_point(maxe, maxx, maxe, n)
            self._canvas_profile.create_line(x1, y1 - 1, x1, y2, fill="grey")
            for xtick in (
                (tim1, 0, "w"),
                (timm, maxx / 2, "center"),
                (tim2, maxx, "e"),
            ):
                x, y = self._get_point(maxe, maxx, 0, xtick[1])
                self._canvas_profile.create_text(
                    x,
                    y + 8,
                    text=f"{datetime.fromtimestamp(xtick[0])}",
                    fill="grey",
                    font=fnt,
                    anchor=xtick[2],
                )

    def _format_metadata(self, metadata: dict) -> str:
        """
        Format metadata as string.
        """

        dst_u, dst_c, ele_u, ele_c, spd_u, spd_c = self._get_units()

        elapsed = self._metadata["elapsed"] / 3600  # h
        dist = self._metadata["distance"]  # km
        minele = self._metadata["min_elevation"]  # m
        maxele = self._metadata["max_elevation"]  # m
        maxspd = self._metadata["max_speed"]  # km/h

        if maxele == 0 and minele == 1e10:
            ele = "N/A"
        else:
            ele = (
                f"({ele_u}) min: {minele*ele_c:,.2f} max: {maxele*ele_c:,.2f} "
                + f"diff: {(maxele-minele)*ele_c:,.2f}; "
            )
        metadata = []
        metadata.append(
            f"Points: {self._metadata['points']:,}; Dist ({dst_u}): {dist*dst_c:,.2f}; "
            + f"Elapsed (hours): {elapsed:,.2f}; "
            + f"Speed ({spd_u}) avg: {(dist/elapsed)*spd_c:,.2f} "
            + f"max: {maxspd*spd_c:,.2f};"
        )
        metadata.append(f"Elevation {ele}")
        for i in range(MD_LINES):
            self._info[i].set(metadata[i])

    def _get_units(self) -> tuple:
        """
        Get speed and elevation units and conversions.
        Default is metric.

        :return: tuple of (dst_u, dst_c, ele_u, ele_C, spd_u, spd_c)
        :rtype: tuple
        """

        settings = self.__app.frm_settings.config
        units = settings["units"]

        if units == UI:
            dst_u = "miles"
            dst_c = KM2MIL
            ele_u = "ft"
            ele_c = M2FT
            spd_u = "mph"
            spd_c = KPH2MPH
        elif units == UIK:
            dst_u = "naut miles"
            dst_c = KM2NMIL
            ele_u = "ft"
            ele_c = M2FT
            spd_u = "knt"
            spd_c = KPH2KNT
        elif units == UMK:
            dst_u = "km"
            dst_c = 1
            ele_u = "m"
            ele_c = 1
            spd_u = "kph"
            spd_c = 1
        else:  # UMM
            dst_u = "m"
            dst_c = KM2M
            ele_u = "m"
            ele_c = 1
            spd_u = "m/s"
            spd_c = KPH2MPS

        return (dst_u, dst_c, ele_u, ele_c, spd_u, spd_c)

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
