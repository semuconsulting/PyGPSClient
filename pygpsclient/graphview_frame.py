"""
Graphview frame class for PyGPSClient application.

This handles a frame containing a graph of current satellite reception.

Created on 14 Sep 2020

@author: semuadmin
"""
# pylint: disable=invalid-name

from tkinter import Frame, Canvas, font, BOTH, YES

from .globals import snr2col, WIDGETU2, BGCOL, FGCOL, MAX_SNR

# Relative offsets of graph axes
AXIS_XL = 19
AXIS_XR = 10
AXIS_Y = 18


class GraphviewFrame(Frame):
    """
    Frame inheritance class for plotting satellite view.
    """

    def __init__(self, app, *args, **kwargs):
        """
        Constructor.

        :param app: reference to main tkinter application
        """

        self.__app = app  # Reference to main application class
        self.__master = self.__app.get_master()  # Reference to root class (Tk)

        Frame.__init__(self, self.__master, *args, **kwargs)

        def_w, def_h = WIDGETU2
        self.width = kwargs.get("width", def_w)
        self.height = kwargs.get("height", def_h)
        self._bgcol = BGCOL
        self._fgcol = FGCOL
        self._body()

        self.bind("<Configure>", self._on_resize)

    def _body(self):
        """
        Set up frame and widgets.
        """

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.can_graphview = Canvas(
            self, width=self.width, height=self.height, bg=self._bgcol
        )
        self.can_graphview.pack(fill=BOTH, expand=YES)

    def init_graph(self):
        """
        Initialise graph view
        """

        w, h = self.width, self.height
        resize_font = font.Font(size=min(int(h / 25), 10))
        ticks = int(MAX_SNR / 10)
        self.can_graphview.delete("all")
        self.can_graphview.create_line(
            AXIS_XL, 5, AXIS_XL, h - AXIS_Y, fill=self._fgcol
        )
        self.can_graphview.create_line(
            w - AXIS_XR + 2, 5, w - AXIS_XR + 2, h - AXIS_Y, fill=self._fgcol
        )
        for i in range(ticks, 0, -1):
            y = (h - AXIS_Y) * i / ticks
            self.can_graphview.create_line(
                AXIS_XL, y, w - AXIS_XR + 2, y, fill=self._fgcol
            )
            self.can_graphview.create_text(
                10,
                y,
                text=str(MAX_SNR - (i * 10)),
                angle=90,
                fill=self._fgcol,
                font=resize_font,
            )

    def update_graph(self, data, siv=16):
        """
        Plot satellites' signal-to-noise ratio (cno).
        Automatically adjust y axis according to number of satellites in view.

        :param data: array of satellite tuples (svid, elev, azim, cno):
        :param siv: int number of satellites in view
        """

        if siv == 0:
            return

        w, h = self.width, self.height
        self.init_graph()

        offset = AXIS_XL + 1
        colwidth = (w - AXIS_XL - AXIS_XR) / siv
        resize_font = font.Font(size=min(int(colwidth / 2), 10))
        for d in sorted(data):  # sort by ascending prn
            prn, _, _, snr = d
            if snr in ("", "0", 0):
                snr = 1
            else:
                snr = int(snr)
            snr_y = int(snr) * (h - AXIS_Y - 1) / MAX_SNR
            if int(prn) > 96:  # OTHER e.g. GAL
                ol_col = "grey"
            elif 65 <= int(prn) <= 96:  # GLONASS
                ol_col = "brown"
            elif 33 <= int(prn) <= 64:  # SBAS
                ol_col = "blue"
            else:  # original GPS
                ol_col = "black"
            prn = f"{int(prn):02}"
            self.can_graphview.create_rectangle(
                offset,
                h - AXIS_Y - 1,
                offset + colwidth,
                h - AXIS_Y - 1 - snr_y,
                outline=ol_col,
                fill=snr2col(snr),
            )
            self.can_graphview.create_text(
                offset + colwidth / 2,
                h - 10,
                text=prn,
                fill=self._fgcol,
                font=resize_font,
                angle=35,
            )
            offset += colwidth

        self.can_graphview.update()

    def _on_resize(self, event):
        """
        Resize frame
        """

        self.width, self.height = self.get_size()

    def get_size(self):
        """
        Get current canvas size.
        """

        self.update_idletasks()  # Make sure we know about any resizing
        width = self.can_graphview.winfo_width()
        height = self.can_graphview.winfo_height()
        return (width, height)
