"""
chart_frame.py

Chart frame class for PyGPSClient application.

This emulates a multi-channel plotter, allowing the user to plot
multiple named numeric data attributes from any parsed GNSS source over
time. X-axis and Y-axis scale and ranges are all configurable.

Created on 24 Nov 2024

:author: semuadmin (Steve Smith)
:copyright: 2020 semuadmin
:license: BSD 3-Clause
"""

from random import choice
from time import time
from tkinter import (
    EW,
    NORMAL,
    NSEW,
    Entry,
    Frame,
    Label,
    Spinbox,
    StringVar,
    TclError,
    font,
)

from pygpsclient.canvas_subclasses import (
    TAG_DATA,
    TAG_GRID,
    TAG_XLABEL,
    TAG_YLABEL,
    CanvasGraph,
)
from pygpsclient.globals import (
    BGCOL,
    ERRCOL,
    FGCOL,
    PLOTCOLS,
    READONLY,
    TRACEMODE_WRITE,
    VALFLOAT,
    VALNONSPACE,
    WIDGETU6,
)
from pygpsclient.helpers import time2str

OL_WID = 1
LBLCOL = "white"
CONTRASTCOL = "black"
# total capacity depends on available free memory...
TIMRANGE = [int(i * 10**n) for n in (1, 2, 3, 4) for i in (1, 2.4, 3.6, 4.8, 6)]
DPTRANGE = [int(i * 10**n) for n in (3, 4, 5, 6) for i in (1, 2, 5)]
CHARTMINY = 0
CHARTMAXY = 100
CHARTSCALE = 1
FONTSCALE = 20
MINY = "MinY {}"
MAXY = "MaxY {}"


def gen_yrange() -> tuple:
    """
    Generate scale and max/min Y ranges for spinboxes.

    :return: Y range
    :rtype: tuple
    """

    srange = ()
    for i in range(0, 8):
        for n in (1, 2, 5):
            srange += (n * 10**i,)
    for i in range(8, 0, -1):
        for n in (5, 2, 1):
            v = n * 10**-i
            if v == 4.9999999999999996e-06:  # fix Python rounding quirk!
                v = 5e-06
            srange += (v,)

    yrange = ("0",)
    for i in range(0, 8):
        for n in (1, 2, 5):
            yrange += (n * 10**i,)
    for i in range(8, -1, -1):
        for n in (5, 2, 1):
            yrange += (-n * 10**i,)

    return srange, yrange


class ChartviewFrame(Frame):
    """
    CHartview frame class.
    """

    def __init__(self, app, parent, *args, **kwargs):
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

        self.chartsettings = self.__app.configuration.get("chartsettings_d")
        def_w, def_h = WIDGETU6
        self.width = kwargs.get("width", def_w)
        self.height = kwargs.get("height", def_h)
        self.configure(bg=BGCOL)
        self._xoff = 20  # chart X offset for labels
        self._yoff = 20  # chart Y offset for labels
        self._chart_data = {}
        self._num_chans = self.chartsettings.get(
            "numchn_n", self.chartsettings.get("numchn", 4)
        )  # cater for typo in earlier chartsettings
        if self._num_chans % 2:  # no channels must be even
            self._num_chans += 1
        self._plotcols = PLOTCOLS
        self._font = self.__app.font_sm
        # generate random plot colours for channels > 4
        if self._num_chans > 4:
            self._plotcols += tuple(
                "#" + "".join([choice("9ABCDEF") for j in range(6)])
                for i in range(self._num_chans - 4)
            )
        self._data_id = [None] * self._num_chans
        self._data_name = [None] * self._num_chans
        self._data_scale = [None] * self._num_chans
        self._data_miny = [None] * self._num_chans
        self._data_maxy = [None] * self._num_chans
        self._mintim = 0
        self._maxtim = 0
        self._redraw = True
        self._timrange = StringVar()
        self._maxpoints = StringVar()
        for chn in range(self._num_chans):
            self._data_id[chn] = StringVar()
            self._data_name[chn] = StringVar()
            self._data_scale[chn] = StringVar()
            self._data_miny[chn] = StringVar()
            self._data_maxy[chn] = StringVar()
        self._body()
        self._do_layout()
        self.reset()
        self._attach_events()

    def _body(self):
        """
        Set up frame and widgets.
        """

        srange, yrange = gen_yrange()
        # set column and row expand behaviour
        for i in range(6):
            self.grid_columnconfigure(i, weight=1, uniform="ent")
        self.grid_rowconfigure(0, weight=1)
        for i in range(1, 2 + self._num_chans):
            self.grid_rowconfigure(i, weight=0)
        self._canvas = CanvasGraph(
            self.__app, self, width=self.width, height=self.height, bg=BGCOL
        )
        self._lbl_id = Label(
            self,
            text="Identity",
            fg=LBLCOL,
            bg=BGCOL,
        )
        self._lbl_name = Label(
            self,
            text="Name",
            fg=LBLCOL,
            bg=BGCOL,
        )
        self._lbl_scale = Label(
            self,
            text="Scale",
            fg=LBLCOL,
            bg=BGCOL,
        )
        self._lbl_miny = Label(
            self,
            text=MINY.format(""),
            fg=LBLCOL,
            bg=BGCOL,
        )
        self._lbl_maxy = Label(
            self,
            text=MAXY.format(""),
            fg=LBLCOL,
            bg=BGCOL,
        )
        self._lbl_timrange = Label(
            self,
            text="Time Range s",
            fg=LBLCOL,
            bg=BGCOL,
        )
        self._lbl_maxpoints = Label(
            self,
            text="Max Points",
            fg=LBLCOL,
            bg=BGCOL,
        )
        self._ent_id = [None] * self._num_chans
        self._ent_name = [None] * self._num_chans
        self._spn_scale = [None] * self._num_chans
        self._spn_miny = [None] * self._num_chans
        self._spn_maxy = [None] * self._num_chans
        for chn in range(self._num_chans):
            self._ent_id[chn] = Entry(
                self,
                textvariable=self._data_id[chn],
                state=NORMAL,
                relief="sunken",
                width=10,
                fg=self._plotcols[chn],
                bg=BGCOL,
            )
            self._ent_name[chn] = Entry(
                self,
                textvariable=self._data_name[chn],
                state=NORMAL,
                relief="sunken",
                width=10,
                fg=self._plotcols[chn],
                bg=BGCOL,
            )
            self._spn_scale[chn] = Spinbox(
                self,
                values=srange,
                wrap=True,
                textvariable=self._data_scale[chn],
                state=NORMAL,
                width=10,
                fg=self._plotcols[chn],
                bg=BGCOL,
                buttonbackground=BGCOL,
            )
            self._spn_miny[chn] = Spinbox(
                self,
                values=yrange,
                wrap=True,
                textvariable=self._data_miny[chn],
                state=NORMAL,
                width=10,
                fg=self._plotcols[chn],
                bg=BGCOL,
                buttonbackground=BGCOL,
            )
            self._spn_maxy[chn] = Spinbox(
                self,
                values=yrange,
                wrap=True,
                textvariable=self._data_maxy[chn],
                state=NORMAL,
                width=10,
                fg=self._plotcols[chn],
                bg=BGCOL,
                buttonbackground=BGCOL,
            )

        self._spn_timrange = Spinbox(
            self,
            values=TIMRANGE,
            wrap=True,
            textvariable=self._timrange,
            state=READONLY,
            width=8,
            fg=LBLCOL,
            readonlybackground=BGCOL,
            buttonbackground=BGCOL,
        )
        self._spn_maxpoints = Spinbox(
            self,
            values=DPTRANGE,
            wrap=True,
            textvariable=self._maxpoints,
            state=READONLY,
            width=8,
            fg=LBLCOL,
            readonlybackground=BGCOL,
            buttonbackground=BGCOL,
        )

    def _do_layout(self):
        """
        Position widgets in frame.
        """

        self._canvas.grid(column=0, row=0, columnspan=6, sticky=NSEW)
        self._lbl_id.grid(column=0, row=1, sticky=EW)
        self._lbl_name.grid(column=1, row=1, sticky=EW)
        self._lbl_scale.grid(column=2, row=1, sticky=EW)
        self._lbl_miny.grid(column=3, row=1, sticky=EW)
        self._lbl_maxy.grid(column=4, row=1, sticky=EW)
        for chn in range(self._num_chans):
            self._ent_id[chn].grid(column=0, row=2 + chn, sticky=EW)
            self._ent_name[chn].grid(column=1, row=2 + chn, sticky=EW)
            self._spn_scale[chn].grid(column=2, row=2 + chn, sticky=EW)
            self._spn_miny[chn].grid(column=3, row=2 + chn, sticky=EW)
            self._spn_maxy[chn].grid(column=4, row=2 + chn, sticky=EW)
        self._lbl_timrange.grid(column=5, row=1, sticky=EW)
        self._spn_timrange.grid(column=5, row=2, sticky=EW)
        self._lbl_maxpoints.grid(column=5, row=3, sticky=EW)
        self._spn_maxpoints.grid(column=5, row=4, sticky=EW)

    def _attach_events(self):
        """
        Bind events to frame.
        """

        self.bind("<Configure>", self._on_resize)
        self._canvas.bind("<Double-Button-1>", self._on_clear)
        self._canvas.bind("<Double-Button-2>", self._on_clipboard)
        self._canvas.bind("<Double-Button-3>", self._on_clipboard)
        self._timrange.trace_add(TRACEMODE_WRITE, self._on_update_config)
        self._maxpoints.trace_add(TRACEMODE_WRITE, self._on_update_config)
        for chn in range(self._num_chans):
            self._data_id[chn].trace_add(TRACEMODE_WRITE, self._on_update_config)
            self._data_name[chn].trace_add(TRACEMODE_WRITE, self._on_update_config)
            self._data_scale[chn].trace_add(TRACEMODE_WRITE, self._on_update_config)
            self._data_miny[chn].trace_add(TRACEMODE_WRITE, self._on_update_config)
            self._data_maxy[chn].trace_add(TRACEMODE_WRITE, self._on_update_config)

    def _on_update_config(self, var, index, mode):  # pylint: disable=unused-argument
        """
        Update in-memory configuration if setting is changed.
        """

        try:
            cst = {}
            cst["numchn_n"] = int(self._num_chans)
            cst["timrng_n"] = int(self._timrange.get())
            cst["maxpoints_n"] = int(self._maxpoints.get())
            for chn in range(self._num_chans):
                cst[chn] = {}
                cst[chn]["id_s"] = self._data_id[chn].get()
                cst[chn]["name_s"] = self._data_name[chn].get()
                cst[chn]["scale_f"] = float(self._data_scale[chn].get())
                cst[chn]["miny_f"] = float(self._data_miny[chn].get())
                cst[chn]["maxy_f"] = float(self._data_maxy[chn].get())
            self.__app.configuration.set("chartsettings_d", cst)
        except (ValueError, TclError):
            pass
        self._redraw = True

    def reset(self):
        """
        Reset chart frame.
        """

        self._timrange.set(self.chartsettings.get("timrng_n", TIMRANGE[3]))  # 60s
        self._maxpoints.set(self.chartsettings.get("maxpoints_n", DPTRANGE[2]))  # 5000
        for chn in range(self._num_chans):
            cst = self.chartsettings.get(str(chn), {})
            self._data_id[chn].set(cst.get("id_s", ""))
            self._data_name[chn].set(cst.get("name_s", ""))
            self._data_scale[chn].set(cst.get("scale_f", 1))
            self._data_miny[chn].set(cst.get("miny_f", CHARTMINY))
            self._data_maxy[chn].set(cst.get("maxy_f", CHARTMAXY))

        self._on_clear(None)

    def _on_clear(self, event):  # pylint: disable=unused-argument
        """
        Clear data.
        """

        self._chart_data = {}
        self._redraw = True
        self.update_frame()

    def _valid_settings(self) -> bool:
        """
        Validate settings.

        :return: True/False
        :rtype: bool
        """

        valid = True
        for chn in range(self._num_chans):
            valid &= self._ent_id[chn].validate(VALNONSPACE)
            valid &= self._ent_name[chn].validate(VALNONSPACE)
            valid &= self._spn_scale[chn].validate(VALFLOAT)
            valid &= self._spn_miny[chn].validate(VALFLOAT)
            valid &= self._spn_maxy[chn].validate(VALFLOAT)
        return valid

    def update_data(self, parsed_data: object):
        """
        Update chart data from parsed message.

        :param object parsed_data: parsed message
        """

        try:
            maxpoints = int(self._maxpoints.get())
        except ValueError:
            maxpoints = DPTRANGE[2]  # 5000

        now = round(time(), 0)  # time to nearest second
        if now not in self._chart_data:
            self._chart_data[now] = {}
        for chn in range(self._num_chans):
            mid = self._data_id[chn].get()
            name = self._data_name[chn].get()
            if name == "":
                continue
            if mid != "":
                if hasattr(parsed_data, "identity"):
                    if parsed_data.identity != mid:
                        continue

            # wildcards *+-, sum, max or min of group of values
            if name == "processtime":
                val = self.__app.processtime / 1000  # microseconds
            elif name[-1] in ("*", "+", "-"):
                vals = []
                for attr in parsed_data.__dict__:
                    if name[:-1] in attr and name[0] != "_":
                        try:
                            vals.append(float(getattr(parsed_data, attr)))
                        except ValueError:
                            continue
                if vals:  # != []
                    if name[-1] == "+":
                        val = max(vals)
                    elif name[-1] == "-":
                        val = min(vals)
                    else:
                        val = sum(vals) / (len(vals) * 1.0)
                else:
                    val = None
            else:
                if hasattr(parsed_data, name):
                    try:
                        val = float(getattr(parsed_data, name))
                    except ValueError:
                        val = None
                else:
                    continue

            self._chart_data[now][chn] = val

            # update X axis (time) range
            self._mintim = min(now, self._mintim)
            self._maxtim = max(now, self._maxtim)

            # flag if scaled value is out of range
            self.flag_outofrange(chn, val)

        # limit number of data points
        while len(self._chart_data) > maxpoints:
            self._chart_data.pop(min(self._chart_data))

    def flag_outofrange(self, chn: int, val: float):
        """
        Flag if scaled value is over or under range.

        :param int chn: channel number
        :param float val: value
        """

        if val is None:
            return

        try:
            minval = float(self._data_miny[chn].get())
            maxval = float(self._data_maxy[chn].get())
            scale = float(self._data_scale[chn].get())
            ucol = ocol = BGCOL
            ufcol = ofcol = self._plotcols[chn]
            if val / scale < minval:
                ucol = ERRCOL
                ufcol = CONTRASTCOL
            elif val / scale > maxval:
                ocol = ERRCOL
                ofcol = CONTRASTCOL
            self._spn_miny[chn].configure(bg=ucol, fg=ufcol)
            self._spn_maxy[chn].configure(bg=ocol, fg=ofcol)
        except (TypeError, ValueError):
            pass

    def update_frame(self):
        """
        Plot selected chart data.
        """

        self._update_plot(self._chart_data)

    def init_frame(self):
        """
        Initialise spectrum chart.
        """

        # pylint: disable=consider-using-generator

        # need tuples here to pass validation in create_graph()
        yminval = tuple(
            [float(self._data_miny[chn].get()) for chn in range(self._num_chans)]
        )
        ymaxval = tuple(
            [float(self._data_maxy[chn].get()) for chn in range(self._num_chans)]
        )
        yleg = tuple(["" for chn in range(self._num_chans)])
        dp = tuple([0 for chn in range(self._num_chans)])
        ycol = self._plotcols

        # Initialise graph
        # only redraw the tags that have changed
        tags = (TAG_GRID, TAG_XLABEL, TAG_YLABEL) if self._redraw else (TAG_XLABEL,)
        self._maxtim = time()
        self._mintim = self._maxtim - int(self._timrange.get())
        self._canvas.create_graph(
            xdatamax=self._maxtim,
            xdatamin=self._mintim,
            ydatamax=ymaxval,
            ydatamin=yminval,
            xtickmaj=5,
            xtickmin=20,
            ytickmaj=5,
            ytickmin=20,
            xdp=0,
            ydp=dp,
            xlegend="time",
            xtimeformat="%H:%M:%S",
            xcol=FGCOL,
            ylegend=yleg,
            ycol=ycol,
            xlabels=True,
            ylabels=True,
            fontscale=FONTSCALE,
            tags=tags,
        )
        self._redraw = False

    def _update_plot(self, data: dict):
        """
        Update chart plot with data.

        :param dict data: list of chart data
        :param int xrange: number of points
        """

        # pylint: disable=no-member

        if not self._valid_settings():
            return

        self.init_frame()

        self._spn_timrange.configure(fg=LBLCOL, readonlybackground=BGCOL)

        # plot each channel's data points
        for chn in range(self._num_chans):
            tm2 = self._mintim
            vl2 = 0
            for n, (tim, channels) in enumerate(data.items()):

                try:
                    val = channels[chn]
                except KeyError:
                    val = None

                if val is None:
                    continue

                scale = float(self._data_scale[chn].get())
                if scale != 1:
                    val /= scale  # scale data

                tm1, vl1 = tm2, vl2
                tm2, vl2 = tim, val
                if n and tm1 > self._mintim:
                    self._canvas.create_gline(
                        tm1,
                        vl1,
                        tm2,
                        vl2,
                        fill=self._canvas.ycol[chn],
                        width=OL_WID,
                        chn=chn,
                        tags=(TAG_DATA,),
                    )
                self.update_idletasks()

    def _on_clipboard(self, event):  # pylint: disable=unused-argument
        """
        Copy chart data to clipboard in CSV format.

        :param event event: double click event
        """

        csv = (
            f"PyGPSClient Chart Data,{time2str(time(),'%Y-%m-%d-%H:%M:%S')},"
            f"Channels,{self._num_chans}\n"
        )
        hdr = True
        for tim, data in self._chart_data.items():
            if hdr:
                csv += "Timestamp"
                for chn in range(self._num_chans):
                    csv += f",{self._ent_id[chn].get()}.{self._ent_name[chn].get()}"
                csv += "\n"
                hdr = False
            csv += f"{time2str(tim,'%Y-%m-%d-%H:%M:%S')}"
            for chn in range(self._num_chans):
                try:
                    csv += f",{data[chn]}"
                except KeyError:
                    csv += ","
            csv += "\n"
        self.__master.clipboard_clear()
        self.__master.clipboard_append(csv)
        self.__master.update()

    def _on_resize(self, event):  # pylint: disable=unused-argument
        """
        Resize frame.

        :param event event: resize event
        """

        self.width, self.height = self.get_size()
        self._font = font.Font(size=int(min(self.width, self.height) / FONTSCALE))
        self._redraw = True

    def get_size(self):
        """
        Get current canvas size.

        :return: window size (width, height)
        :rtype: tuple
        """

        self.update_idletasks()  # Make sure we know about any resizing
        return self._canvas.winfo_width(), self._canvas.winfo_height()
