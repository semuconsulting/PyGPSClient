"""
spectrum_frame.py

Spectrum Analysis frame class for PyGPSClient application.

This handles a frame containing a spectrum analysis chart from
a MON-SPAN message.

Created on 23 Dec 2022

:author: semuadmin (Steve Smith)
:copyright: 2020 semuadmin
:license: BSD 3-Clause
"""

# pylint: disable=no-member, unused-argument

import logging
from tkinter import ALL, EW, NSEW, NW, Checkbutton, Frame, IntVar, S, W

from pyubx2 import UBXMessage

from pygpsclient.canvas_plot import (
    TAG_DATA,
    TAG_GRID,
    TAG_XLABEL,
    TAG_YLABEL,
    CanvasGraph,
)
from pygpsclient.globals import (
    BGCOL,
    FGCOL,
    GNSS_LIST,
    PLOTCOLS,
    PNTCOL,
    SPECTRUMVIEW,
    WIDGETU2,
)
from pygpsclient.helpers import setubxrate
from pygpsclient.strings import DLGENABLEMONSPAN, DLGNOMONSPAN, DLGWAITMONSPAN

# Graph dimensions
OL_WID = 1
MIN_DB = 0
MAX_DB = 200
MIN_HZ = 1.1e9
MAX_HZ = 1.70e9
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
    0: PLOTCOLS[0],
    1: PLOTCOLS[1],
    2: PLOTCOLS[2],
    3: PLOTCOLS[3],
    4: "#1E90FF",
    5: "#FF8C00",
}
RF_LIST_SNAPSHOT = {
    0: "#BFBFBF",
    1: "#999999",
    2: "#A6A6A6",
    3: "#7F7F7F",
    4: "#8C8C8C",
    5: "#666666",
}
ACTIVE = ""
MODEINIT = "init"
MODELIVE = "live"
MODESNAP = "snap"
MAXWAIT = 10
GHZ = 1e9
FONTSCALE = 35


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
        self._waits = 0
        self._redraw = True
        self._body()
        self._attach_events()

    def _body(self):
        """
        Set up frame and widgets.
        """

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self._canvas = CanvasGraph(
            self.__app, self, width=self.width, height=self.height, bg=BGCOL
        )
        self.chk_pgaoffset = Checkbutton(
            self,
            text="PGA Offset",
            fg=PNTCOL,
            bg=BGCOL,
            variable=self._pgaoffset,
            anchor=W,
        )
        self._canvas.grid(column=0, row=0, columnspan=3, sticky=NSEW)
        self.chk_pgaoffset.grid(column=0, row=1, sticky=EW)

    def _attach_events(self):
        """
        Bind events to frame.
        """

        self.bind("<Configure>", self._on_resize)
        self._canvas.bind("<Button-1>", self._on_click)
        self._canvas.bind("<Double-Button-1>", self._on_toggle_rf)
        self._canvas.bind("<Button-2>", self._on_snapshot)
        self._canvas.bind("<Double-Button-2>", self._on_clear_snapshot)
        self._pgaoffset.trace_add(("write", "unset"), self._on_update_pga)

    def reset(self):
        """
        Reset spectrumview frame.
        """

        self.__app.gnss_status.spectrum_data = []
        self._chartpos = None
        self._pgaoffset.set(0)
        self._canvas.delete(ALL)
        self.update_frame()

    def _on_update_pga(self, var, index, mode):
        """
        Action on updating pga flag.
        """

        if self._pgaoffset.get():
            self._maxdb = MAX_DB + 50
        else:
            self._maxdb = MAX_DB
        self._redraw = True

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
            self._canvas.create_text(
                w / 2,
                h / 2,
                text=DLGNOMONSPAN,
                fill="orange",
                anchor=S,
            )
            self._pending_confs.pop("ACK-NAK")
            self._monspan_status = DLGNOMONSPAN

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
            if self._waits >= MAXWAIT:
                self._monspan_status = DLGNOMONSPAN
            else:
                self._waits += 1
        else:
            self._waits = 0
            self._monspan_status = ACTIVE
        self._update_plot(rfblocks)

        if self._spectrum_snapshot != []:
            self._update_plot(self._spectrum_snapshot, MODESNAP, RF_LIST_SNAPSHOT)

    def init_frame(self):
        """
        Initialise spectrum chart.
        """

        # only redraw the tags that have changed
        tags = (TAG_GRID, TAG_XLABEL, TAG_YLABEL) if self._redraw else ()
        # draw graph axes and labels
        self._canvas.create_graph(
            xdatamax=self._maxhz / GHZ,
            xdatamin=self._minhz / GHZ,
            ydatamax=(self._maxdb,),
            ydatamin=(self._mindb,),
            xtickmaj=10,
            ytickmaj=10,
            xdp=2,
            ydp=(0,),
            xlegend="GHz",
            xcol=FGCOL,
            ylegend=("dB",),
            ycol=(FGCOL,),
            xlabels=True,
            ylabels=True,
            fontscale=FONTSCALE,
            tags=tags,
        )
        self._redraw = False

        # display 'enable MON-SPAN' warning
        self._canvas.create_text(
            self.width / 2,
            self.height / 2,
            text=self._monspan_status,
            fill="orange",
            tags=TAG_DATA,
        )

    def _update_plot(self, rfblocks: list, mode: str = MODELIVE, colors: dict = None):
        """
        Update spectrum plot with live or snapshot rf block data.

        :param list rfblocks: array of spectrum rf blocks
        :param dict colors: dictionary of color for each rf block
        :param str mode: plot mode ("live" or "snap"shot)
        """

        if colors is None:
            colors = RF_LIST

        specxy, self._minhz, self._maxhz = self._get_limits(rfblocks)
        if mode == MODESNAP:
            self._canvas.delete(MODESNAP)
        else:
            self.init_frame()
            # plot frequency bands
            if self._showrf:
                self._plot_rf_bands(mode)

        # for each RF block in MON-SPAN message
        for i, rfblock in enumerate(specxy):
            rf = len(specxy) - i - 1
            col = colors[rf % len(colors)]

            # draw legend for this RF block
            self._plot_rf_legend(col, mode, rf, i)

            # plot spectrum for this RF block
            hz2 = self._minhz / GHZ
            db2 = self._mindb
            for n, (hz, db) in enumerate(rfblock):
                hz1, db1 = hz2, db2
                hz2, db2 = hz / GHZ, db
                if n:
                    self._canvas.create_gline(
                        hz1,
                        db1,
                        hz2,
                        db2,
                        fill=col,
                        width=OL_WID,
                        tags=(mode, TAG_DATA),
                    )
            self.update_idletasks()

        # display any marked db/hz coordinate
        if self._chartpos is not None:
            self._plot_marker(mode)

    def _plot_rf_legend(self, col: str, mode: str, rf: int, index: int):
        """
        Draw RF block legend(s)

        :param str col: color
        :param str mode: plot or snapshot
        :param int rf: RF block
        :param int i: RF block index
        """

        rfw = self.width / 10
        x1 = (
            self.width
            - self._canvas.xoffr
            - rfw * (index + 1)
            - (index * self._canvas.fnth)
        )
        y = self._canvas.yofft * 2
        x2 = x1 + rfw
        if mode == MODESNAP:
            y += self._canvas.fnth
        else:
            self._canvas.create_text(
                (x1 + x2) / 2,
                y,
                text=f"RF {rf + 1}",
                fill=FGCOL,
                font=self._canvas.font,
                anchor=S,
                tags=(mode, TAG_XLABEL),
            )
        self._canvas.create_line(
            x1,
            y,
            x2,
            y,
            fill=col,
            width=OL_WID,
            tags=(mode, TAG_XLABEL),
        )

    def _plot_rf_bands(self, mode: str):
        """
        Plot RF band markers

        :param int mode: plot or snapshot
        """

        for nam, frq in RF_BANDS.items():
            if self._minhz < frq < self._maxhz:
                yoff, col = {
                    "L": (self._canvas.fnth, GNSS_LIST[0][1]),  # GPS
                    "G": (self._canvas.fnth * 2, GNSS_LIST[6][1]),  # GLONASS
                    "E": (self._canvas.fnth * 3, GNSS_LIST[2][1]),  # Galileo
                    "S": (self._canvas.fnth * 3, GNSS_LIST[2][1]),  # Galileo SAR
                    "B": (self._canvas.fnth * 4, GNSS_LIST[3][1]),  # Beidou
                }[nam[0:1]]
                if nam not in (
                    "E1",
                    "E5a",
                    "E5b",
                    "B2a",
                    "B2",
                    "B1",
                ):  # same freq as other bands
                    self._canvas.create_gline(
                        frq / GHZ,
                        self._mindb,
                        frq / GHZ,
                        self._maxdb,
                        fill=col,
                        dash=(5, 2),
                        width=OL_WID,
                        tags=TAG_XLABEL,
                    )
                x, y = self._canvas.d2xy(frq / GHZ, self._mindb)
                self._canvas.create_text(
                    x + 2,
                    y - yoff - 1,
                    text=nam,
                    fill=col,
                    anchor=NW,
                    font=self._canvas.font,
                    tags=TAG_XLABEL,
                )

    def _plot_marker(self, mode):
        """
        Plot saved db/hz coordinate marker.

        :param str mode: plot or snapshot
        """

        hz, db = self._chartpos
        x, y = self._canvas.d2xy(hz, db)
        self._canvas.create_text(
            x,
            y,
            text=f"{hz:.3f} GHz\n{db:.1f} dB",
            fill=FGCOL,
            font=self._canvas.font,
            anchor="center",
            tags=(TAG_XLABEL, mode),
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
            int(min(minhz, MIN_HZ)),
            int(max(maxhz, MAX_HZ)),
        )

    def _on_click(self, event):
        """
        Save flagged chart position.
        """

        self._chartpos = self._canvas.xy2d(event.x, event.y)
        self._redraw = True

    def _on_toggle_rf(self, event):  # pylint: disable=unused-argument
        """
        Toggle RF band markers on/off.
        """

        self._showrf = not self._showrf
        self._chartpos = None
        self._redraw = True

    def _on_snapshot(self, event):  # pylint: disable=unused-argument
        """
        Capture snapshot of current spectrum.
        """

        self._spectrum_snapshot = self.__app.gnss_status.spectrum_data
        self._redraw = True

    def _on_clear_snapshot(self, event):  # pylint: disable=unused-argument
        """
        Clear snapshot of current spectrum.
        """

        self._spectrum_snapshot = []
        self._canvas.delete("snap")
        self._redraw = True

    def _on_resize(self, event):  # pylint: disable=unused-argument
        """
        Resize frame.

        :param event event: resize event
        """

        self.width, self.height = self.get_size()
        self._chartpos = None
        self._redraw = True

    def get_size(self):
        """
        Get current canvas size.

        :return: window size (width, height)
        :rtype: tuple
        """

        self.update_idletasks()  # Make sure we know about any resizing
        return self._canvas.winfo_width(), self._canvas.winfo_height()
