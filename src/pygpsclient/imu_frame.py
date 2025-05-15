"""
imu_frame.py

IMU (Inertial Management Unit) frame class for PyGPSClient Application.

This show orientiation (Pitch, Roll, Yaw) and calibration status of
any UBX or NMEA IMU source.

Created 23 March 2023

:author: semuadmin
:copyright: 2020 SEMU Consulting
:license: BSD 3-Clause
"""

from tkinter import (
    NW,
    Canvas,
    E,
    Frame,
    IntVar,
    Label,
    N,
    S,
    Spinbox,
    StringVar,
    TclError,
    W,
)

from pynmeagps import FMI_STATUS
from pyubx2 import ESFALG_STATUS

from pygpsclient.globals import (
    BGCOL,
    ERRCOL,
    FGCOL,
    GRIDCOL,
    INFOCOL,
    PNTCOL,
    RPTDELAY,
    WIDGETU2,
)
from pygpsclient.helpers import fontheight, rgb2str, scale_font
from pygpsclient.strings import LBLNODATA

OFFSETX = 5
OFFSETY = 10
ROLLCOL = rgb2str(123, 163, 56)
PITCHCOL = rgb2str(227, 73, 87)
YAWCOL = rgb2str(72, 130, 220)
CONTRASTCOL = "black"
DATA = "dat"
ESFALG = "ESF-ALG"
GPFMI = "GPFMI"
SOURCES = (
    ESFALG,
    GPFMI,
    "HNR-ATT",
    "NAV-ATT",
    "NAV-PVAT",
)
RANGES = (
    180,
    90,
    45,
    30,
    15,
    10,
    5,
    2,
    1,
)  # range factors in degrees
OPTIONS = ("N/A",)


class IMUFrame(Frame):
    """
    IMU (Inertial Management Unit) frame class.
    """

    def __init__(self, app, *args, **kwargs):
        """
        Constructor.

        :param Frame app: reference to main tkinter application
        :param args: Optional args to pass to Frame parent class
        :param kwargs: Optional kwargs to pass to Frame parent class
        """
        self.__app = app
        self.__master = self.__app.appmaster

        Frame.__init__(self, self.__master, *args, **kwargs)

        def_w, def_h = WIDGETU2

        self.width = kwargs.get("width", def_w)
        self.height = kwargs.get("height", def_h)
        self._font = self.__app.font_md
        self._fonth = fontheight(self._font)
        self._source = StringVar()
        self._range = IntVar()
        self._option = StringVar()
        self._source.set(SOURCES[0])
        self._range.set(RANGES[0])
        self._body()
        self.reset()
        self._attach_events()

    def _body(self):
        """Set up frame and widgets."""

        for i in range(4):
            self.grid_columnconfigure(i, weight=1, uniform="ent")
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=0)
        self.canvas = Canvas(self, width=self.width, height=self.height, bg=BGCOL)
        self._lbl_source = Label(self, text="Source", fg=FGCOL, bg=BGCOL, anchor=W)
        self._spn_source = Spinbox(
            self,
            values=SOURCES,
            width=15,
            wrap=True,
            repeatdelay=RPTDELAY,
            repeatinterval=RPTDELAY,
            fg=PNTCOL,
            bg=BGCOL,
            textvariable=self._source,
        )
        self._lbl_range = Label(self, text="Range", fg=FGCOL, bg=BGCOL, anchor=W)
        self._spn_range = Spinbox(
            self,
            values=RANGES,
            width=8,
            wrap=True,
            repeatdelay=RPTDELAY,
            repeatinterval=RPTDELAY,
            fg=PNTCOL,
            bg=BGCOL,
            readonlybackground=BGCOL,
            textvariable=self._range,
            state="readonly",
        )
        self._lbl_option = Label(self, text="Option", fg=FGCOL, bg=BGCOL, anchor=W)
        self._spn_option = Spinbox(
            self,
            values=OPTIONS,
            width=8,
            wrap=True,
            repeatdelay=RPTDELAY,
            repeatinterval=RPTDELAY,
            fg=PNTCOL,
            bg=BGCOL,
            readonlybackground=BGCOL,
            textvariable=self._option,
            state="readonly",
        )
        self.canvas.grid(column=0, row=0, columnspan=4, sticky=(N, S, E, W))
        self._lbl_source.grid(column=0, row=1, sticky=(W, E))
        self._spn_source.grid(column=1, row=1, columnspan=3, sticky=(W, E))
        self._lbl_range.grid(column=0, row=2, sticky=(W, E))
        self._spn_range.grid(column=1, row=2, sticky=(W, E))
        self._lbl_option.grid(column=2, row=2, sticky=(W, E))
        self._spn_option.grid(column=3, row=2, sticky=(W, E))

    def reset(self):
        """
        Reset settings to saved configuration.
        """

        cfg = self.__app.configuration.get("imusettings_d")
        self._source.set(cfg.get("source_s"))
        self._range.set(cfg.get("range_n"))
        self._option.set(cfg.get("option_s"))

    def _attach_events(self):
        """
        Bind events to frame.
        """

        self.bind("<Configure>", self._on_resize)
        self.canvas.bind("<Double-Button-1>", self._on_clear)
        for setting in (self._source, self._range, self._option):
            setting.trace_add("write", self._on_update_config)

    def _on_update_config(self, var, index, mode):  # pylint: disable=unused-argument
        """
        Update in-memory configuration if setting is changed.
        """

        try:
            self.update()
            ims = {}
            ims["source_s"] = self._source.get()
            ims["range_n"] = int(self._range.get())
            ims["option_s"] = self._option.get()
            self.__app.configuration.set("imusettings_d", ims)
            self._flag_range(False)
        except (ValueError, TclError):
            pass

    def _init_frame(self):
        """
        Initialize scatter plot.
        """

        width, _ = self.get_size()
        self._flag_range(False)
        self.canvas.delete("all")
        self.canvas.create_line(
            (width - OFFSETX * 2) / 2,
            OFFSETY,
            (width - OFFSETX * 2) / 2,
            self._fonth * 5 + OFFSETY + 6,
            fill=GRIDCOL,
            width=2,
        )
        self.canvas.create_text(
            OFFSETX,
            OFFSETY,
            text="Roll X:",
            fill=FGCOL,
            font=self._font,
            anchor=NW,
        )
        self.canvas.create_text(
            OFFSETX,
            self._fonth * 2 + OFFSETY,
            text="Pitch Y:",
            fill=FGCOL,
            font=self._font,
            anchor=NW,
        )
        self.canvas.create_text(
            OFFSETX,
            self._fonth * 4 + OFFSETY,
            text="Yaw Z:",
            fill=FGCOL,
            font=self._font,
            anchor=NW,
        )
        self.canvas.create_text(
            OFFSETX,
            self._fonth * 6 + OFFSETY,
            text="Status:",
            fill=FGCOL,
            font=self._font,
            anchor=NW,
        )

    def update_frame(self):
        """
        Collect scatterplot data and update the plot.
        """
        self.canvas.delete(DATA)
        width, height = self.get_size()
        owidth = width - OFFSETX * 2
        wid = int(self._fonth / 2)
        wid2 = int(wid / 2)

        try:
            scale = self._range.get()
            source = self._source.get().upper()
            data = self.__app.gnss_status.imu_data
            # only use IMU data matching specified source
            if data["source"].upper() != source:
                raise ValueError("IMU data source does not match")
            rng = self._range.get()
            roll = float(data["roll"])
            pitch = float(data["pitch"])
            yaw = float(data["yaw"])
            status = data["status"]

            if source == GPFMI:  # Feyman IM19 IMU
                st = ""
                for val, (desc, _) in FMI_STATUS.items():
                    if int(status, 16) & val:
                        st += f"\t{desc}\n"
                status = st.upper()
            elif source == ESFALG:  # ZED-F9R ESF IMU
                status = f"\t{(ESFALG_STATUS.get(status, (status,))[0]).upper()}"
                yaw -= 180  # yaw is 0-360
            else:
                status = f"\t{status}"

            rollbar = roll * owidth / rng / 2
            pitchbar = pitch * owidth / rng / 2
            yawbar = yaw * owidth / rng / 2

            # flag if out of range
            if abs(roll) > scale or abs(pitch) > scale or abs(yaw) > scale:
                self._flag_range(True)

            self.canvas.create_text(
                OFFSETX,
                OFFSETY,
                text=f"\t{roll}",
                fill=ROLLCOL,
                font=self._font,
                anchor=NW,
                tag=DATA,
            )
            self.canvas.create_line(
                owidth / 2,
                self._fonth + OFFSETY + wid2,
                owidth / 2 + rollbar,
                self._fonth + OFFSETY + wid2,
                fill=ROLLCOL,
                width=wid,
                tag=DATA,
            )
            self.canvas.create_text(
                OFFSETX,
                self._fonth * 2 + OFFSETY,
                text=f"\t{pitch}",
                fill=PITCHCOL,
                font=self._font,
                anchor=NW,
                tag=DATA,
            )
            self.canvas.create_line(
                owidth / 2,
                self._fonth * 3 + OFFSETY + wid2,
                owidth / 2 + pitchbar,
                self._fonth * 3 + OFFSETY + wid2,
                fill=PITCHCOL,
                width=wid,
                tag=DATA,
            )
            self.canvas.create_text(
                OFFSETX,
                self._fonth * 4 + OFFSETY,
                text=f"\t{yaw}",
                fill=YAWCOL,
                font=self._font,
                anchor=NW,
                tag=DATA,
            )
            self.canvas.create_line(
                owidth / 2,
                self._fonth * 5 + OFFSETY + wid2,
                owidth / 2 + yawbar,
                self._fonth * 5 + OFFSETY + wid2,
                fill=YAWCOL,
                width=wid,
                tag=DATA,
            )
            self.canvas.create_text(
                OFFSETX,
                self._fonth * 6 + OFFSETY,
                text=f"{status}",
                fill=INFOCOL,
                font=self._font,
                anchor=NW,
                tag=DATA,
            )

        except (KeyError, ValueError):
            self.canvas.delete(DATA)
            self.canvas.create_text(
                width / 2, height / 2, text=LBLNODATA, fill=ERRCOL, tag=DATA
            )

    def _flag_range(self, over: bool = False):
        """
        Flag range spinbox if data is overrange.

        :param bool over: overrange flag
        """

        if over:
            self._spn_range.configure(
                fg=CONTRASTCOL, bg=ERRCOL, readonlybackground=ERRCOL
            )
        else:
            self._spn_range.configure(fg=PNTCOL, bg=BGCOL, readonlybackground=BGCOL)

    def _redraw(self):
        """
        Redraw frame.
        """

        self.update_frame()

    def _on_clear(self, event):  # pylint: disable=unused-argument
        """
        Clear frame.

        :param Event event: clear event
        """

        self._init_frame()

    def _on_resize(self, event):  # pylint: disable=unused-argument
        """
        Resize frame.

        :param Event event: resize event
        """

        self.width, self.height = self.get_size()
        self._font, self._fonth = scale_font(self.width, 12, 25, 30)
        self._init_frame()
        self._redraw()

    def get_size(self) -> tuple:
        """
        Get current canvas size.

        :return: window size (width, height)
        :rtype: tuple
        """

        self.update_idletasks()  # Make sure we know about resizing
        return self.canvas.winfo_width(), self.canvas.winfo_height()
