"""
Spectrum Analysis frame class for PyGPSClient application.

This handles a frame containing a spectrum analysis chart from
a MON-SPAN message.

Created on 23 Dec 2022

:author: semuadmin
:copyright: SEMU Consulting © 2022
:license: BSD 3-Clause
"""

from math import ceil
from tkinter import BOTH, YES, Canvas, Frame, font

from pyubx2 import UBXMessage

from pygpsclient.globals import BGCOL, FGCOL, GNSS_LIST, SPECTRUMVIEW, WIDGETU2
from pygpsclient.helpers import setubxrate
from pygpsclient.strings import DLGENABLEMONSPAN, DLGNOMONSPAN, DLGWAITMONSPAN

# Graph dimensions
RESFONT = 24  # font size relative to widget size
MINFONT = 7  # minimum font size
OL_WID = 1
MIN_DB = 20
MAX_DB = 180
MIN_HZ = 1130000000
MAX_HZ = 1650000000
TICK_DB = 20  # 20 dB divisions
TICK_GHZ = 40000000  # 40 MHz divisions
TICK_COL = "grey"
RF_BANDS = {
    "B1": 1575420000,
    "B3": 1268520000,
    "B2": 1202025000,
    "B2a": 1176450000,
    "SAR": 1544500000,
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
ACTIVE = ""


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
        self._body()
        self._set_fontsize()
        self._attach_events()

    def _body(self):
        """
        Set up frame and widgets.
        """

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.can_spectrumview = Canvas(
            self, width=self.width, height=self.height, bg=BGCOL
        )
        self.can_spectrumview.pack(fill=BOTH, expand=YES)

    def _attach_events(self):
        """
        Bind events to frame.
        """

        self.bind("<Configure>", self._on_resize)
        self.can_spectrumview.bind("<Button-1>", self._on_click)
        self.can_spectrumview.bind("<Double-Button-1>", self._toggle_rf)

    def init_graph(self):
        """
        Initialise spectrum chart.
        """

        self.can_spectrumview.delete("all")

        # plot y (dB) axis grid
        i = 0
        for db in range(self._mindb, self._maxdb, TICK_DB):
            x1, y1 = self._get_point(self._minhz, db)
            x2, y2 = self._get_point(self._maxhz, db)
            self.can_spectrumview.create_line(
                x1, y1, x2 + 1, y1, fill=TICK_COL if i else FGCOL
            )
            self.can_spectrumview.create_text(
                x1,
                y1,
                text=f"{db}",
                angle=90,
                fill=FGCOL,
                font=self._font,
                anchor="s",
            )
            i += 1

        # plot x (Hz) axis grid
        i = 0
        for hz in range(self._minhz, self._maxhz, TICK_GHZ):
            x1, y1 = self._get_point(hz, self._mindb)
            x2, y2 = self._get_point(hz, self._maxdb)
            self.can_spectrumview.create_line(
                x1, y1 - 1, x1, y2, fill=TICK_COL if i else FGCOL
            )
            self.can_spectrumview.create_text(
                x1,
                y1,
                text=f"{hz / 1e9:.2f}",  # GHz
                fill=FGCOL,
                font=self._font,
                anchor="n",
            )
            i += 1

        x, y = self._get_point(self._maxhz, self._mindb)
        self.can_spectrumview.create_text(
            x,
            y,
            text="GHz",
            fill=FGCOL,
            font=self._font,
            anchor="se",
        )
        x, y = self._get_point(self._minhz + self._fonth, self._maxdb - 5)
        self.can_spectrumview.create_text(
            x,
            y,
            text="dB",
            fill=FGCOL,
            angle=90,
            font=self._font,
            anchor="ne",
        )

        # display 'enable MON-SPAN' warning
        self.can_spectrumview.create_text(
            self.width / 2,
            self.height / 2,
            text=self._monspan_status,
            fill="orange",
        )

    def reset(self):
        """
        Reset spectrumview frame.
        """

        self.__app.gnss_status.spectrum_data = []
        self._chartpos = None
        self.can_spectrumview.delete("all")
        self.update_frame()
        self.enable_MONSPAN(self.winfo_ismapped())

    def enable_MONSPAN(self, status: bool):
        """
        Enable/disable UBX MON-SPAN message.

        :param bool status: 0 = off, 1 = on
        """

        setubxrate(self.__app, 0x0A, 0x31, status)
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
                anchor="s",
            )
            self._pending_confs.pop("ACK-NAK")
            self._monspan_status = DLGNOMONSPAN
            self.init_graph()

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

        specxy, self._minhz, self._maxhz, self._mindb, self._maxdb = self._get_limits(
            rfblocks
        )
        self.init_graph()

        # plot frequency band markers
        if self._showrf:
            for nam, frq in RF_BANDS.items():
                if self._minhz < frq < self._maxhz:
                    x1, y1 = self._get_point(frq, self._maxdb)
                    x2, y2 = self._get_point(frq, self._mindb)
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
                            x1, y1, x1, y2, fill=col, dash=(5, 2), width=OL_WID
                        )
                    self.can_spectrumview.create_text(
                        x2 + 2,
                        y2 - yoff - 1,
                        text=nam,
                        fill=col,
                        anchor="nw",
                        font=self._font,
                    )

        # for each RF block in MON-SPAN message
        for i, rfblock in enumerate(specxy):
            col = RF_LIST[i % len(RF_LIST)]

            # draw legend for this RF block
            x1, y1 = self._get_point(self._minhz + ((i + 0.3) * 1e8), self._maxdb - 15)
            x2, y2 = self._get_point(self._minhz + ((i + 0.7) * 1e8), self._maxdb - 15)
            self.can_spectrumview.create_line(
                x1,
                y1,
                x2,
                y1,
                fill=col,
                width=OL_WID,
            )
            self.can_spectrumview.create_text(
                (x1 + x2) / 2,
                y1,
                text=f"RF {i + 1}",
                fill=FGCOL,
                font=self._font,
                anchor="s",
            )

            # plot spectrum for this RF block
            x2 = 5
            y2 = self.height - 5
            for n, (hz, db) in enumerate(rfblock):
                x1, y1 = x2, y2
                x2, y2 = self._get_point(hz, db)
                if n:
                    self.can_spectrumview.create_line(
                        x1, y1, x2, y2, fill=col, width=OL_WID
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
            )

        # self.can_spectrumview.update_idletasks()

    def _get_point(self, hz: float, db: float) -> tuple:
        """
        Convert (hz,db) values to canvas pixel coordinates (x,y).

        :param hz float: hz (x) value
        :param db float: db (y) value
        :return: (x, y) coordinates
        :rtype: tuple
        """

        offset = self._fonth + 4
        val_db = db - self._mindb
        range_db = self._maxdb - self._mindb
        range_x = self.width - offset * 2
        val_hz = hz - self._minhz
        range_hz = self._maxhz - self._minhz
        range_y = self.height - self._fonth

        x = offset + (val_hz * range_x / range_hz)
        y = self.height - offset - (val_db * range_y / range_db)
        return (int(x), int(y))

    def _get_hzdb(self, x: int, y: int) -> tuple:
        """
        Get frequency & level corresponding to cursor x,y position.

        :param x int: cursor x position
        :param y int: cursor y position
        :return: (Ghz, dB) values
        :rtype: tuple
        """

        offset = self._fonth + 4
        val_x = x - offset
        range_x = self.width - offset * 2
        range_db = self._maxdb - self._mindb
        val_y = y - self.height + offset
        range_y = self._fonth - self.height
        range_hz = self._maxhz - self._minhz

        hz = self._minhz + (val_x * range_hz / range_x)
        db = self._mindb + (val_y * range_db / range_y)
        return (hz / 1e9, db)

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
        mindb = 0
        maxdb = 0
        specxy = []

        # for each RF block in MON-SPAN message
        for i, rfblock in enumerate(rfblocks):
            (spec, spn, res, ctr, _) = rfblock
            minhz = int(min(minhz, ctr - res * (spn / res) / 2))
            maxhz = int(max(maxhz, ctr + res * (spn / res) / 2))
            spanhz = []
            for i, db in enumerate(spec):
                # db -= pga  # compensate for programmable gain
                mindb = min(mindb, db)
                maxdb = max(maxdb, db)
                hz = int(minhz + (res * i))
                spanhz.append((hz, db))
            specxy.append(spanhz)

        return (
            specxy,
            int(minhz - TICK_GHZ / 2),
            maxhz,
            MIN_DB,
            (ceil((maxdb + 10) / 10) * 10) + TICK_DB,
        )

    def _on_resize(self, event):  # pylint: disable=unused-argument
        """
        Resize frame.

        :param event event: resize event
        """

        self.width, self.height = self.get_size()
        self._chartpos = None

    def _on_click(self, event):
        """
        Save flagged chart position.
        """

        hz, db = self._get_hzdb(event.x, event.y)
        self._chartpos = (event.x, event.y, hz, db)

    def _toggle_rf(self, event):  # pylint: disable=unused-argument
        """
        Toggle RF band markers on/off.
        """

        self._showrf = not self._showrf
        self._chartpos = None

    def get_size(self):
        """
        Get current canvas size.

        :return: window size (width, height)
        :rtype: tuple
        """

        self.update_idletasks()  # Make sure we know about any resizing
        width = self.can_spectrumview.winfo_width()
        height = self.can_spectrumview.winfo_height()
        self._set_fontsize()
        return (width, height)

    def _set_fontsize(self):
        """
        Set font size and line spacing
        """

        dim = min(self.width, self.height)
        self._font = font.Font(size=max(int(dim * RESFONT / 1000), MINFONT))
        self._fonth = self._font.metrics("linespace")
