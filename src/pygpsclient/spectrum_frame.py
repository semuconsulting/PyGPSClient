"""
spectrum_frame.py

Spectrum Analysis frame class for PyGPSClient application.

This handles a frame containing a spectrum analysis chart from
a MON-SPAN message.

Created on 23 Dec 2022

:author: semuadmin
:copyright: 2020 SEMU Consulting
:license: BSD 3-Clause
"""

import logging
from tkinter import ALL, NW, Canvas, Checkbutton, E, Frame, IntVar, N, S, W

from pyubx2 import UBXMessage

from pygpsclient.globals import (
    BGCOL,
    FGCOL,
    GNSS_LIST,
    GRIDCOL,
    PNTCOL,
    SPECTRUMVIEW,
    WIDGETU2,
    AreaXY,
)
from pygpsclient.helpers import data2xy, fontheight, scale_font, setubxrate, xy2data
from pygpsclient.strings import DLGENABLEMONSPAN, DLGNOMONSPAN, DLGWAITMONSPAN

# Graph dimensions
RESFONT = 24  # font size relative to widget size
MINFONT = 7  # minimum font size
OL_WID = 1
MIN_DB = 0
MAX_DB = 200
MIN_HZ = 1130000000
MAX_HZ = 1650000000
TICK_DB = 20  # 20 dB divisions
TICK_GHZ = 40000000  # 40 MHz divisions
RF_BANDS = {
    "B1": 1575420000,
    "B3": 1268520000,
    "B2": 1202025000,
    "B2a": 1176450000,
    "E6": 1278750000,
    "E5b": 1202025000,
    "E5a": 1176450000,
    "E1": 1575420000,
    "G3": 1202025000,
    "G2": 1248060000,
    "G1": 1600995000,
    "L5": 1176450000,
    "L2": 1227600000,
    "L1": 1575420000,
}
RF_LIST = {
    0: "aquamarine2",
    1: "orange",
    2: "deepskyblue",
    3: "sandybrown",
    4: "dodgerblue",
    5: "darkorange",
}
RF_LIST_SNAPSHOT = {
    0: "gray75",
    1: "gray60",
    2: "gray65",
    3: "gray50",
    4: "gray55",
    5: "gray40",
}
ACTIVE = ""
MODEINIT = "init"
MODELIVE = "live"
MODESNAP = "snap"


class SpectrumviewFrame(Frame):
    """
    Spectrumview frame class.
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
        self.logger = logging.getLogger(__name__)

        Frame.__init__(self, self.__master, *args, **kwargs)

        def_w, def_h = WIDGETU2
        self.width = kwargs.get("width", def_w)
        self.height = kwargs.get("height", def_h)
        self._mindb = MIN_DB
        self._maxdb = MAX_DB
        self._minhz = MIN_HZ
        self._maxhz = MAX_HZ
        self._monspan_status = DLGENABLEMONSPAN
        self._pending_confs = {}
        self._showrf = True
        self._chartpos = None
        self._spectrum_snapshot = []
        self._pgaoffset = IntVar()
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
        self.grid_rowconfigure(1, weight=0)
        self.can_spectrumview = Canvas(
            self, width=self.width, height=self.height, bg=BGCOL
        )
        self.chk_pgaoffset = Checkbutton(
            self,
            text="PGA Offset",
            fg=PNTCOL,
            bg=BGCOL,
            variable=self._pgaoffset,
            anchor=W,
        )
        # self.can_spectrumview.pack(fill=BOTH, expand=YES)
        self.can_spectrumview.grid(column=0, row=0, columnspan=3, sticky=(N, S, E, W))
        self.chk_pgaoffset.grid(column=0, row=1, sticky=(W, E))

    def _attach_events(self):
        """
        Bind events to frame.
        """

        self.bind("<Configure>", self._on_resize)
        self.can_spectrumview.bind("<Button-1>", self._on_click)
        self.can_spectrumview.bind("<Double-Button-1>", self._on_toggle_rf)
        self.can_spectrumview.bind("<Button-2>", self._on_snapshot)
        self.can_spectrumview.bind("<Double-Button-2>", self._on_clear_snapshot)

    def init_frame(self):
        """
        Initialise spectrum chart.
        """

        offset = self._fonth + 4
        w = self.width - offset * 2
        h = self.height - offset
        bounds = AreaXY(self._minhz, self._mindb, self._maxhz, self._maxdb)
        self.can_spectrumview.delete(ALL)

        # plot y (dB) axis grid
        i = 0
        for db in range(self._mindb, self._maxdb, TICK_DB):
            x1, y1 = data2xy(w, h, bounds, self._minhz, db, offset)
            x2, y2 = data2xy(w, h, bounds, self._maxhz, db, offset)
            self.can_spectrumview.create_line(
                x1,
                y1,
                x2 + 1,
                y1,
                fill=GRIDCOL if i else FGCOL,
                tags=MODEINIT,
            )
            self.can_spectrumview.create_text(
                x1,
                y1,
                text=f"{db}",
                angle=90,
                fill=FGCOL,
                font=self._font,
                anchor=S,
                tags=MODEINIT,
            )
            i += 1

        # plot x (Hz) axis grid
        i = 0
        for hz in range(self._minhz, self._maxhz, TICK_GHZ):
            x1, y1 = data2xy(w, h, bounds, hz, self._mindb, offset)
            x2, y2 = data2xy(w, h, bounds, hz, self._maxdb, offset)
            self.can_spectrumview.create_line(
                x1,
                y1 - 1,
                x1,
                y2,
                fill=GRIDCOL if i else FGCOL,
                tags=MODEINIT,
            )
            self.can_spectrumview.create_text(
                x1,
                y1,
                text=f"{hz / 1e9:.2f}",  # GHz
                fill=FGCOL,
                font=self._font,
                anchor=N,
                tags=MODEINIT,
            )
            i += 1

        x, y = data2xy(w, h, bounds, self._maxhz, self._mindb, offset)
        self.can_spectrumview.create_text(
            x,
            y,
            text="GHz",
            fill=FGCOL,
            font=self._font,
            anchor="se",
            tags=MODEINIT,
        )
        x, y = data2xy(w, h, bounds, self._minhz + self._fonth, self._maxdb - 5, offset)
        self.can_spectrumview.create_text(
            x,
            y,
            text="dB",
            fill=FGCOL,
            angle=90,
            font=self._font,
            anchor="ne",
            tags=MODEINIT,
        )

        # display 'enable MON-SPAN' warning
        self.can_spectrumview.create_text(
            self.width / 2,
            self.height / 2,
            text=self._monspan_status,
            fill="orange",
            tags=MODEINIT,
        )

    def reset(self):
        """
        Reset spectrumview frame.
        """

        self.__app.gnss_status.spectrum_data = []
        self._chartpos = None
        self._pgaoffset.set(0)
        self.can_spectrumview.delete(ALL)
        self.update_frame()

    def enable_messages(self, status: bool):
        """
        Enable/disable UBX MON-SPAN message.

        :param bool status: 0 = off, 1 = on
        """

        setubxrate(self.__app, "MON-SPAN", status)
        for msgid in ("ACK-ACK", "ACK-NAK"):
            self._set_pending(msgid, SPECTRUMVIEW)
        self._monspan_status = DLGWAITMONSPAN

    def _set_pending(self, msgid: int, ubxfrm: int):
        """
        Set pending confirmation flag for Spectrumview frame to
        signify that it's waiting for a confirmation message.

        :param int msgid: UBX message identity
        :param int ubxfrm: integer representing UBX configuration frame (0-6)
        """

        self._pending_confs[msgid] = ubxfrm

    def update_pending(self, msg: UBXMessage):
        """
        Receives polled confirmation message from the ubx_handler and
        updates spectrumview canvas.

        :param UBXMessage msg: UBX config message
        """

        pending = self._pending_confs.get(msg.identity, False)

        if pending and msg.identity == "ACK-NAK":
            self.reset()
            w, h = self.width, self.height
            self.can_spectrumview.create_text(
                w / 2,
                h / 2,
                text=DLGNOMONSPAN,
                fill="orange",
                anchor=S,
            )
            self._pending_confs.pop("ACK-NAK")
            self._monspan_status = DLGNOMONSPAN
            self.init_frame()

        if self._pending_confs.get("ACK-ACK", False):
            self._pending_confs.pop("ACK-ACK")

    def update_frame(self):
        """
        Plot MON-SPAN spectrum analysis.

        spectrum_data is list of tuples (spec, spn, res, ctr, pga),
        one item per RF block.
        """

        rfblocks = self.__app.gnss_status.spectrum_data
        if len(rfblocks) == 0:
            return
        self._monspan_status = ACTIVE
        self._update_plot(rfblocks)

        if self._spectrum_snapshot != []:
            self._update_plot(self._spectrum_snapshot, MODESNAP, RF_LIST_SNAPSHOT)

    def _update_plot(self, rfblocks: list, mode: str = MODELIVE, colors: dict = None):
        """
        Update spectrum plot with live or snapshot rf block data.

        :param list rfblocks: array of spectrum rf blocks
        :param dict colors: dictionary of color for each rf block
        :param str mode: plot mode ("live" or "snap"shot)
        """

        offset = self._fonth + 4
        w = self.width - offset * 2
        h = self.height - offset

        if colors is None:
            colors = RF_LIST

        self._mindb = MIN_DB
        self._maxdb = MAX_DB
        if self._pgaoffset.get():
            self._maxdb += 40

        specxy, self._minhz, self._maxhz = self._get_limits(rfblocks)
        bounds = AreaXY(self._minhz, self._mindb, self._maxhz, self._maxdb)
        if mode == MODESNAP:
            self.can_spectrumview.delete(MODESNAP)
        else:
            self.init_frame()
            # plot frequency band markers
            if self._showrf:
                self._plot_rf_markers(w, h, bounds, offset, mode)

        # for each RF block in MON-SPAN message
        for i, rfblock in enumerate(specxy):
            col = colors[i % len(colors)]

            # draw legend for this RF block
            x1, y1 = (50 * (i + 1) + (i * self._fonth), self._fonth * 2)
            x2, y2 = (50 + 50 * (i + 1) + (i * self._fonth), self._fonth * 2)
            if mode == MODESNAP:
                y1 += self._fonth
                y2 += self._fonth
            else:
                self.can_spectrumview.create_text(
                    (x1 + x2) / 2,
                    y1,
                    text=f"RF {i + 1}",
                    fill=FGCOL,
                    font=self._font,
                    anchor=S,
                    tags=mode,
                )
            self.can_spectrumview.create_line(
                x1,
                y1,
                x2,
                y1,
                fill=col,
                width=OL_WID,
                tags=mode,
            )

            # plot spectrum for this RF block
            x2 = 5
            y2 = self.height - 5
            for n, (hz, db) in enumerate(rfblock):
                x1, y1 = x2, y2
                x2, y2 = data2xy(w, h, bounds, hz, db, offset)
                if n:
                    self.can_spectrumview.create_line(
                        x1,
                        y1,
                        x2,
                        y2,
                        fill=col,
                        width=OL_WID,
                        tags=mode,
                    )

        # display any flagged chart position
        if self._chartpos is not None:
            x, y, hz, db = self._chartpos
            self.can_spectrumview.create_text(
                x,
                y,
                text=f"{hz:.3f} GHz\n{db:.1f} dB",
                fill=FGCOL,
                font=self._font,
                anchor="center",
                tags=mode,
            )

    def _plot_rf_markers(self, w: int, h: int, bounds: AreaXY, offset: int, mode: int):
        """
        Plot RF band markers

        :param int w: plots width
        :param int h: plot height
        :param AreaXY bounds: data bounds
        :param offset: _description_
        """
        # pylint: disable=too-many-arguments, too-many-positional-arguments

        for nam, frq in RF_BANDS.items():
            if self._minhz < frq < self._maxhz:
                x1, y1 = data2xy(w, h, bounds, frq, self._maxdb, offset)
                x2, y2 = data2xy(w, h, bounds, frq, self._mindb, offset)
                yoff, col = {
                    "L": (self._fonth, GNSS_LIST[0][1]),  # GPS
                    "G": (self._fonth * 2, GNSS_LIST[6][1]),  # GLONASS
                    "E": (self._fonth * 3, GNSS_LIST[2][1]),  # Galileo
                    "S": (self._fonth * 3, GNSS_LIST[2][1]),  # Galileo SAR
                    "B": (self._fonth * 4, GNSS_LIST[3][1]),  # Beidou
                }[nam[0:1]]
                if nam not in (
                    "E1",
                    "E5a",
                    "E5b",
                    "B2a",
                    "B2",
                    "B1",
                ):  # same freq as other bands
                    self.can_spectrumview.create_line(
                        x1,
                        y1,
                        x1,
                        y2,
                        fill=col,
                        dash=(5, 2),
                        width=OL_WID,
                        tags=mode,
                    )
                self.can_spectrumview.create_text(
                    x2 + 2,
                    y2 - yoff - 1,
                    text=nam,
                    fill=col,
                    anchor=NW,
                    font=self._font,
                    tags=mode,
                )

    def _get_limits(self, rfblocks: list) -> tuple:
        """
        Get axis limits for all RF blocks and convert
        spectrum arrays to (x,y) arrays.
        Frequencies expressed as GHz.

        :param list rfblocks: RF Blocks
        :return: tuple of points and axis limits
        :rtype: tuple
        """

        minhz = 999 * 1e9
        maxhz = 0
        specxy = []

        # for each RF block in MON-SPAN message
        for i, rfblock in enumerate(rfblocks):
            (spec, spn, res, ctr, pga) = rfblock
            minhz = int(min(minhz, ctr - res * (spn / res) / 2))
            maxhz = int(max(maxhz, ctr + res * (spn / res) / 2))
            spanhz = []
            for i, db in enumerate(spec):
                if self._pgaoffset.get():
                    db += pga  # compensate for programmable gain
                hz = int(ctr - (spn / 2) + (res * i))
                spanhz.append((hz, db))
            specxy.append(spanhz)

        return (
            specxy,
            int(minhz - TICK_GHZ / 2),
            int(maxhz + TICK_GHZ / 2),
        )

    def _on_click(self, event):
        """
        Save flagged chart position.
        """

        offset = self._fonth + 4
        w = self.width - offset * 2
        h = self.height - offset
        bounds = AreaXY(self._minhz, self._mindb, self._maxhz, self._maxdb)
        hz, db = xy2data(w, h, bounds, event.x - offset, event.y)
        self._chartpos = (event.x, event.y, hz / 1e9, db)

    def _on_toggle_rf(self, event):  # pylint: disable=unused-argument
        """
        Toggle RF band markers on/off.
        """

        self._showrf = not self._showrf
        self._chartpos = None

    def _on_snapshot(self, event):  # pylint: disable=unused-argument
        """
        Capture snapshot of current spectrum.
        """

        self._spectrum_snapshot = self.__app.gnss_status.spectrum_data

    def _on_clear_snapshot(self, event):  # pylint: disable=unused-argument
        """
        Clear snapshot of current spectrum.
        """

        self._spectrum_snapshot = []
        self.can_spectrumview.delete("snap")

    def _on_resize(self, event):  # pylint: disable=unused-argument
        """
        Resize frame.

        :param event event: resize event
        """

        self.width, self.height = self.get_size()
        self._font, self._fonth = scale_font(self.width, 8, 25, 20)
        self._chartpos = None

    def get_size(self):
        """
        Get current canvas size.

        :return: window size (width, height)
        :rtype: tuple
        """

        self.update_idletasks()  # Make sure we know about any resizing
        return self.can_spectrumview.winfo_width(), self.can_spectrumview.winfo_height()
