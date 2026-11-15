"""
attitude_frame.py

Attitude (3D orientation) frame class for PyGPSClient Application.

This show orientiation (Pitch, Roll, Yaw) and calibration status of
a variety of sources.

Created 23 March 2023

:author: semuadmin (Steve Smith)
:copyright: 2020 semuadmin
:license: BSD 3-Clause
"""

from tkinter import (
    EW,
    NSEW,
    NW,
    Canvas,
    Frame,
    IntVar,
    Label,
    Spinbox,
    StringVar,
    TclError,
    Tk,
    W,
)

from pynmeagps import FMI_STATUS
from pyubx2 import ESFALG_STATUS

from pygpsclient.custom_classes import TAG_WAIT
from pygpsclient.globals import (
    BGCOL,
    ERRCOL,
    FGCOL,
    GRIDMAJCOL,
    INFOCOL,
    PNTCOL,
    READONLY,
    TRACEMODE_WRITE,
)
from pygpsclient.helpers import rgb2str, scale_font
from pygpsclient.widget_frame import WidgetFrame

OFFSETX = 5
OFFSETY = 10
ROLLCOL = rgb2str(123, 163, 56)
PITCHCOL = rgb2str(227, 73, 87)
YAWCOL = rgb2str(72, 130, 220)
CONTRASTCOL = "black"
DATA = "dat"
ESFALG = "ESF-ALG"
GPFMI = "GPFMI"
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


class AttitudeFrame(WidgetFrame):
    """
    Attitude (3D orientation) frame class.
    """

    def __init__(self, app: Tk, parent: Frame, *args, **kwargs):
        """
        Constructor.

        :param Tk app: reference to main tkinter application
        :param Frame parent: reference to parent frame
        :param args: Optional args to pass to Frame parent class
        :param kwargs: Optional kwargs to pass to Frame parent class
        """

        self.__app = app
        self._range = IntVar()
        self._option = StringVar()
        self._range.set(RANGES[0])

        super().__init__(app, parent, *args, **kwargs)

    def _body(self):
        """Set up frame and widgets."""

        self._canvas = Canvas(self, width=self.width, height=self.height, bg=BGCOL)
        self._lbl_range = Label(self, text="Range", fg=FGCOL, bg=BGCOL, anchor=W)
        self._spn_range = Spinbox(
            self,
            values=RANGES,
            width=8,
            wrap=True,
            fg=PNTCOL,
            bg=BGCOL,
            readonlybackground=BGCOL,
            buttonbackground=BGCOL,
            textvariable=self._range,
            state=READONLY,
        )
        self._lbl_option = Label(self, text="Option", fg=FGCOL, bg=BGCOL, anchor=W)
        self._spn_option = Spinbox(
            self,
            values=OPTIONS,
            width=8,
            wrap=True,
            fg=PNTCOL,
            bg=BGCOL,
            readonlybackground=BGCOL,
            buttonbackground=BGCOL,
            textvariable=self._option,
            state=READONLY,
        )

    def _do_layout(self):
        """
        Arrange frame and widgets in grid.
        """

        self._canvas.grid(column=0, row=0, columnspan=4, sticky=NSEW)
        self._lbl_range.grid(column=0, row=1, sticky=EW)
        self._spn_range.grid(column=1, row=1, sticky=EW)
        self._lbl_option.grid(column=2, row=1, sticky=EW)
        self._spn_option.grid(column=3, row=1, sticky=EW)

        for i in range(4):
            self.grid_columnconfigure(i, weight=1, uniform="ent")
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=0)

    def reset(self):
        """
        Reset settings to saved configuration.
        """

        cfg = self.__app.configuration.get("imusettings_d")
        self._range.set(cfg.get("range_n"))
        self._option.set(cfg.get("option_s"))

    def _attach_events(self):
        """
        Bind events to frame.
        """

        self._canvas.bind("<Double-Button-1>", self._on_clear)
        for setting in (self._range, self._option):
            setting.trace_add(TRACEMODE_WRITE, self._on_update_config)

    def _on_update_config(self, var, index, mode):  # pylint: disable=unused-argument
        """
        Update in-memory configuration if setting is changed.
        """

        try:
            self.update()
            ims = {}
            ims["range_n"] = int(self._range.get())
            ims["option_s"] = self._option.get()
            self.__app.configuration.set("imusettings_d", ims)
            self._flag_range(False)
        except (ValueError, TclError):
            pass

    def init_frame(self):
        """
        Initialize scatter plot.
        """

        width, _ = self.get_size()
        self._flag_range(False)
        self._canvas.delete("all")
        self._canvas.create_line(
            (width - OFFSETX * 2) / 2,
            OFFSETY,
            (width - OFFSETX * 2) / 2,
            self._fonth * 5 + OFFSETY + 6,
            fill=GRIDMAJCOL,
            width=2,
        )
        self._canvas.create_text(
            OFFSETX,
            OFFSETY,
            text="Roll X:",
            fill=FGCOL,
            font=self._font,
            anchor=NW,
        )
        self._canvas.create_text(
            OFFSETX,
            self._fonth * 2 + OFFSETY,
            text="Pitch Y:",
            fill=FGCOL,
            font=self._font,
            anchor=NW,
        )
        self._canvas.create_text(
            OFFSETX,
            self._fonth * 4 + OFFSETY,
            text="Yaw Z:",
            fill=FGCOL,
            font=self._font,
            anchor=NW,
        )
        self._canvas.create_text(
            OFFSETX,
            self._fonth * 6 + OFFSETY,
            text="Source:",
            fill=FGCOL,
            font=self._font,
            anchor=NW,
        )
        self._canvas.create_text(
            OFFSETX,
            self._fonth * 7 + OFFSETY,
            text="Status:",
            fill=FGCOL,
            font=self._font,
            anchor=NW,
        )

    def update_frame(self):
        """
        Collect attitude data and update the plot.
        """
        self._canvas.delete(DATA)
        width, _ = self.get_size()
        owidth = width - OFFSETX * 2
        wid = int(self._fonth / 2)
        wid2 = int(wid / 2)

        try:
            scale = self._range.get()
            data = self.__app.gnss_status.imu_data
            if data != {}:
                self._waiting = False
                self._canvas.delete(TAG_WAIT)
            rng = self._range.get()
            roll = float(data["roll"])
            pitch = float(data["pitch"])
            yaw = float(data["yaw"])
            source = data["source"]
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

            self._canvas.create_text(
                OFFSETX,
                OFFSETY,
                text=f"\t{roll}",
                fill=ROLLCOL,
                font=self._font,
                anchor=NW,
                tag=DATA,
            )
            self._canvas.create_line(
                owidth / 2,
                self._fonth + OFFSETY + wid2,
                owidth / 2 + rollbar,
                self._fonth + OFFSETY + wid2,
                fill=ROLLCOL,
                width=wid,
                tag=DATA,
            )
            self._canvas.create_text(
                OFFSETX,
                self._fonth * 2 + OFFSETY,
                text=f"\t{pitch}",
                fill=PITCHCOL,
                font=self._font,
                anchor=NW,
                tag=DATA,
            )
            self._canvas.create_line(
                owidth / 2,
                self._fonth * 3 + OFFSETY + wid2,
                owidth / 2 + pitchbar,
                self._fonth * 3 + OFFSETY + wid2,
                fill=PITCHCOL,
                width=wid,
                tag=DATA,
            )
            self._canvas.create_text(
                OFFSETX,
                self._fonth * 4 + OFFSETY,
                text=f"\t{yaw}",
                fill=YAWCOL,
                font=self._font,
                anchor=NW,
                tag=DATA,
            )
            self._canvas.create_line(
                owidth / 2,
                self._fonth * 5 + OFFSETY + wid2,
                owidth / 2 + yawbar,
                self._fonth * 5 + OFFSETY + wid2,
                fill=YAWCOL,
                width=wid,
                tag=DATA,
            )
            self._canvas.create_text(
                OFFSETX,
                self._fonth * 6 + OFFSETY,
                text=f"\t{source}",
                fill=INFOCOL,
                font=self._font,
                anchor=NW,
                tag=DATA,
            )
            self._canvas.create_text(
                OFFSETX,
                self._fonth * 7 + OFFSETY,
                text=f"{status}",
                fill=INFOCOL,
                font=self._font,
                anchor=NW,
                tag=DATA,
            )

        except (KeyError, ValueError):
            self._canvas.delete(DATA)

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

    def _on_resize(self, event):  # pylint: disable=unused-argument
        """
        Resize frame.

        :param Event event: resize event
        """

        self.width, self.height = super().get_size()
        self._font, self._fonth = scale_font(self.width, 12, 25, 30)
        self.init_frame()
        self.update_frame()
        self._on_waiting()
