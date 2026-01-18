"""
signalsview_frame.py

Signals view frame class for PyGPSClient application.

This handles a frame containing a graph of current signal C/No level,
correction source and other signal-related flags.

Created on 24 Dec 2025

:author: semuadmin (Steve Smith)
:copyright: 2020 semuadmin
:license: BSD 3-Clause
"""

# pylint: disable=no-member, unused-variable, duplicate-code

from tkinter import ALL, NSEW, NW, SE, Frame, N, S, font

from pyubx2 import CORRSOURCE, SIGID, UBXMessage

from pygpsclient.canvas_subclasses import (
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
    GRIDMAJCOL,
    MAX_SNR,
    PNTCOL,
    SIGNALSVIEW,
    WIDGETU3,
)
from pygpsclient.helpers import col2contrast, fitfont, setubxrate
from pygpsclient.strings import DLGENABLENAVSIG, DLGNONAVSIG, DLGWAITNAVSIG

OL_WID = 1
FONTSCALELG = 40
MAXWAIT = 10
ACTIVE = ""
XLBLANGLE = 60
XLBLFMT = "000 WWW_W/W"
# Correction source legend
CSLEG = ", ".join(
    f"{key} {val}" for key, val in CORRSOURCE.items() if key != 0
).replace(", 7", ",\n7")
CL = "A" * len(CSLEG.split("\n", 1)[0])


def unused_sigs(data: dict) -> int:
    """
    Get number of 'unused' sigs in gnss_data.sig_data.

    :param dict data: sig_data
    :return: number of sigs where cno = 0
    :rtype: int
    """

    return sum(1 for (_, _, _, cno, _, _, _, _) in data.values() if cno == 0)


class SignalsviewFrame(Frame):
    """
    Signalsview frame class.
    """

    def __init__(self, app: Frame, parent: Frame, *args, **kwargs):
        """
        Constructor.

        :param Frame app: reference to main tkinter application
        :param Frame parent: reference to parent frame
        :param args: optional args to pass to Frame parent class
        :param kwargs: optional kwargs to pass to Frame parent class
        """

        self.__app = app  # Reference to main application class
        self.__master = self.__app.appmaster  # Reference to root class (Tk)

        super().__init__(parent, *args, **kwargs)

        def_w, def_h = WIDGETU3
        self.width = kwargs.get("width", def_w)
        self.height = kwargs.get("height", def_h)
        self._redraw = True
        self._navsig_status = DLGENABLENAVSIG
        self._pending_confs = {}
        self._waits = 0
        self._body()
        self._attach_events()

    def _body(self):
        """
        Set up frame and widgets.
        """

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._canvas = CanvasGraph(
            self.__app, self, width=self.width, height=self.height, bg=BGCOL
        )
        self._canvas.grid(column=0, row=0, sticky=NSEW)

    def _attach_events(self):
        """
        Bind events to frame.
        """

        self.bind("<Configure>", self._on_resize)
        self._canvas.bind("<Double-Button-1>", self._on_legend)
        self._canvas.bind("<Double-Button-2>", self._on_cno0)
        self._canvas.bind("<Double-Button-3>", self._on_cno0)

    def _on_legend(self, event):  # pylint: disable=unused-argument
        """
        On double-click - toggle legend on/off.

        :param event: event
        """

        self.__app.configuration.set(
            "legend_b", not self.__app.configuration.get("legend_b")
        )
        self._redraw = True

    def _on_cno0(self, event):  # pylint: disable=unused-argument
        """
        On double-right-click - include signals where C/No = 0.

        :param event: event
        """

        self.__app.configuration.set(
            "unusedsat_b", not self.__app.configuration.get("unusedsat_b")
        )
        self._redraw = True

    def enable_messages(self, status: bool):
        """
        Enable/disable UBX NAV-SIG message.

        :param bool status: 0 = off, 1 = on
        """

        setubxrate(self.__app, "NAV-SIG", status)
        for msgid in ("ACK-ACK", "ACK-NAK"):
            self._set_pending(msgid, SIGNALSVIEW)
        self._navsig_status = DLGWAITNAVSIG

    def _set_pending(self, msgid: int, ubxfrm: int):
        """
        Set pending confirmation flag for Signalsview frame to
        signify that it's waiting for a confirmation message.

        :param int msgid: UBX message identity
        :param int ubxfrm: integer representing UBX configuration frame
        """

        self._pending_confs[msgid] = ubxfrm

    def update_pending(self, msg: UBXMessage):
        """
        Receives polled confirmation message from the ubx_handler and
        updates signalsview canvas.

        :param UBXMessage msg: UBX config message
        """

        pending = self._pending_confs.get(msg.identity, False)

        if pending and msg.identity == "ACK-NAK":
            self.reset()
            w, h = self.width, self.height
            self._canvas.create_text(
                w / 2,
                h / 2,
                text=DLGNONAVSIG,
                fill=PNTCOL,
                anchor=S,
                tags=TAG_DATA,
            )
            self._pending_confs.pop("ACK-NAK")
            self._navsig_status = DLGNONAVSIG

        if self._pending_confs.get("ACK-ACK", False):
            self._pending_confs.pop("ACK-ACK")

    def reset(self):
        """
        Reset spectrumview frame.
        """

        self.__app.gnss_status.sig_data = []
        self._canvas.delete(ALL)
        self.update_frame()

    def init_frame(self):
        """
        Initialise graph view
        """

        # only redraw the tags that have changed
        tags = (TAG_GRID, TAG_XLABEL, TAG_YLABEL) if self._redraw else ()
        self._canvas.create_graph(
            xdatamax=10,
            ydatamax=(MAX_SNR,),
            xtickmaj=10,
            ytickmaj=int(MAX_SNR / 10),
            ylegend=("C/No dBHz",),
            ycol=(FGCOL,),
            ylabels=True,
            xlabelsfrm=XLBLFMT,
            xangle=XLBLANGLE,
            fontscale=FONTSCALELG,
            tags=tags,
        )
        self._redraw = False

        # display 'enable NAV-SIG' warning
        self._canvas.create_text(
            self.width / 2,
            self.height / 2,
            text=self._navsig_status,
            fill=PNTCOL,
            tags=TAG_DATA,
        )

    def _draw_legend(self):
        """
        Draw GNSS color code and correction source legends
        """

        w = self.width / 12 / 2
        h = self.height / 18

        # gnssid color code legend
        lgfont = font.Font(size=int(min(self.width / 2, self.height) / FONTSCALELG))
        for i, (_, (gnssName, gnssCol)) in enumerate(GNSS_LIST.items()):
            x = (self._canvas.xoffl * 2) + w * i
            self._canvas.create_rectangle(
                x,
                self._canvas.yofft,
                x + w - 5,
                self._canvas.yofft + h,
                outline=GRIDMAJCOL,
                fill=gnssCol,
                width=OL_WID,
                tags=TAG_XLABEL,
            )
            self._canvas.create_text(
                (x + x + w - 5) / 2,
                self._canvas.yofft + h / 2,
                text=gnssName,
                fill=col2contrast(gnssCol),
                font=lgfont,
                tags=TAG_XLABEL,
            )

        # correction source legend
        xfnt, _, _ = fitfont(CL, self.width / 2 - self._canvas.xoffl, h / 2, maxsiz=12)
        self._canvas.create_text(
            self.width / 2,
            self._canvas.yofft + 1,
            text=f"Correction Source:\n{CSLEG}",
            fill=FGCOL,
            font=xfnt,
            anchor=NW,
            tags=TAG_DATA,
        )

    def update_frame(self):
        """
        Plot signal signal-to-noise ratio (C/No).
        Automatically adjust y axis according to number of satellites in view.
        """

        data = self.__app.gnss_status.sig_data
        if len(data) == 0:
            if self._waits >= MAXWAIT:
                self._navsig_status = DLGNONAVSIG
            else:
                self._waits += 1
        else:
            self._waits = 0
            self._navsig_status = ACTIVE
        show_unused = self.__app.configuration.get("unusedsat_b")
        siv = len(data)
        siv = siv if show_unused else siv - unused_sigs(data)
        if siv <= 0:
            return

        w, h = self.width, self.height
        self.init_frame()

        offset = self._canvas.xoffl
        colwidth = (w - self._canvas.xoffl - self._canvas.xoffr + 1) / siv
        xfnt, _, _ = fitfont(
            XLBLFMT,
            colwidth * 1.66,
            self._canvas.yoffb,
            XLBLANGLE,
        )
        for val in sorted(data.values()):  # sort by ascending gnssid, svid, sigid
            gnssId, prn, sigid, cno, corrsource, quality, flags, _ = val
            if cno == 0 and not show_unused:
                continue
            sig = SIGID.get((gnssId, sigid), sigid)
            snr_y = int(cno) * (h - self._canvas.yoffb - 1) / MAX_SNR
            _, ol_col = GNSS_LIST[gnssId]
            prn = f"{int(prn):02}"
            self._canvas.create_rectangle(
                offset,
                h - self._canvas.yoffb - 1,
                offset + colwidth - OL_WID,
                h - self._canvas.yoffb - snr_y - 1,
                outline=GRIDMAJCOL,
                fill=ol_col,
                width=OL_WID,
                tags=TAG_DATA,
            )
            # xlabel prn - sigid
            self._canvas.create_text(
                offset + colwidth,
                h - self._canvas.yoffb + 3,
                text=f"{prn} {sig}",
                fill=FGCOL,
                font=xfnt,
                angle=XLBLANGLE,
                anchor=SE,
                tags=TAG_DATA,
            )
            # xcaption corrsource if > 0
            if corrsource:
                self._canvas.create_text(
                    offset + colwidth / 2,
                    h - self._canvas.yoffb - snr_y + 2,
                    text=corrsource,
                    fill=col2contrast(ol_col),
                    font=xfnt,
                    anchor=N,
                    tags=TAG_DATA,
                )
            offset += colwidth

        if self.__app.configuration.get("legend_b"):
            self._draw_legend()
        self.update_idletasks()

    def _on_resize(self, event):  # pylint: disable=unused-argument
        """
        Resize frame

        :param event event: resize event
        """

        self.width, self.height = self.get_size()
        self._redraw = True

    def get_size(self):
        """
        Get current canvas size.

        :return: window size (width, height)
        :rtype: tuple
        """

        self.update_idletasks()  # Make sure we know about any resizing
        return self._canvas.winfo_width(), self._canvas.winfo_height()
