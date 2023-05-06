"""
System Monitor frame for PyGPSClient application.

Shows cpu, memory, i/o status, core temperature and warning/error counts
for u-blox devices which support the MON-SYS and/or MON-COMMS UBX message
types.

Created on 30 Apr 2023

:author: semuadmin
:copyright: SEMU Consulting © 2022
:license: BSD 3-Clause
"""

from tkinter import Canvas, Checkbutton, E, Frame, IntVar, N, S, W

from pyubx2 import UBXMessage

from pygpsclient.globals import BGCOL, FGCOL, SYSMONVIEW, WIDGETU2
from pygpsclient.helpers import bytes2unit, hsv2rgb, secs2unit, setubxrate, sizefont
from pygpsclient.strings import DLGENABLEMONSYS, DLGNOMONSYS, DLGWAITMONSYS, NA

MINFONT = 6  # minimum font size
MAXTEMP = 100  # °C
XOFFSET = 10
SPACING = 5
DASH = (5, 2)
BOOTTYPES = {
    0: "Unknown",
    1: "Cold Start",
    2: "Watchdog",
    3: "Hardware reset",
    4: "Hardware backup",
    5: "Software backup",
    6: "Software reset",
    7: "VIO fail",
    8: "VDD_X fail",
    9: "VDD_RF fail",
    10: "V_CORE_HIGH fail",
}
PORTIDS = {
    0x0000: "I2C",  # 0 I2C
    0x0100: "UART1",  # 256 UART1
    0x0101: "INT1",  # 257 inter-cpu connect
    0x0200: "INT2",  # 512 inter-cpu connect
    0x0201: "UART2",  # 513 UART2
    0x0300: "USB",  # 768 USB
    0x0400: "SPI",  # 1024 SPI
}
ACTIVE = ""
MAXLINES = 23
MINFONT = 4
MAXWAIT = 10


class SysmonFrame(Frame):
    """
    SysmonFrame class.
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
        self._monsys_status = DLGENABLEMONSYS
        self._pending_confs = {}
        self._maxtemp = 0
        self._waits = 0
        self._mode = IntVar()
        self._body()
        self._attach_events()
        self._set_fontsize()

    def _body(self):
        """
        Set up frame and widgets.
        """

        self._can_sysmon = Canvas(self, width=self.width, height=self.height, bg=BGCOL)
        self._frm_status = Frame(self, bg=BGCOL)
        self._chk_mode = Checkbutton(
            self._frm_status,
            text="Actual I/O",
            variable=self._mode,
            fg=FGCOL,
            bg=BGCOL,
        )
        self._can_sysmon.grid(column=0, row=0, padx=0, pady=0, sticky=(N, S, W, E))
        self._frm_status.grid(column=0, row=1, padx=2, pady=2, sticky=(W, E))
        self._chk_mode.grid(column=0, row=0, padx=0, pady=0, sticky=W)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

    def _attach_events(self):
        """
        Bind events to frame.
        """

        self.bind("<Configure>", self._on_resize)
        self._can_sysmon.bind("<Double-Button-1>", self._on_clear)
        self._mode.trace_add("write", self._on_mode)

    def init_chart(self):
        """
        Initialise sysmon chart.
        """

        self._can_sysmon.delete("all")
        self._can_sysmon.create_text(
            self.width / 2,
            self.height / 2,
            text=self._monsys_status,
            fill="orange",
        )

    def _on_clear(self, event):  # pylint: disable=unused-argument
        """
        Clear chart data and reinitialise canvas.

        :param Event event: clear event
        """

        self.__app.gnss_status.sysmon_data = {}
        self.__app.gnss_status.comms_data = {}
        self._maxtemp = 0
        self._monsys_status = DLGWAITMONSYS
        self.init_chart()

    def _on_mode(self, *args):  # pylint: disable=unused-argument
        """
        Update I/O display mode - actual or pending i/o.

        :param Event event: clear event
        """

        txt = "Pending I/O" if self._mode.get() else "Actual I/O"
        self._chk_mode.config(text=txt)

    def enable_MONSYS(self, status: int):
        """
        Enable/disable UBX MON-SYS & MON-COMMS messages on
        default port(s).

        NB: CPU Load value only valid if rate = 1

        :param int status: 0 = off, 1 = on
        """

        for mid in (0x39, 0x36):
            setubxrate(self.__app, 0x0A, mid, status)
        for msgid in ("ACK-ACK", "ACK-NAK"):
            self._set_pending(msgid, SYSMONVIEW)
        self._monsys_status = DLGWAITMONSYS
        self.init_chart()

    def _set_pending(self, msgid: int, ubxfrm: int):
        """
        Set pending confirmation flag for sysmon widget to
        signify that it's waiting for a confirmation message.

        :param int msgid: UBX message identity
        :param int ubxfrm: integer representing UBX configuration frame (0-13)
        """

        self._pending_confs[msgid] = ubxfrm

    def update_pending(self, msg: UBXMessage):
        """
        Receives polled confirmation message from the ubx_handler and
        updates sysmon status.

        :param UBXMessage msg: UBX config message
        """

        pending = self._pending_confs.get(msg.identity, False)
        if pending and msg.identity == "ACK-NAK":
            self._pending_confs.pop("ACK-NAK")
            self._monsys_status = DLGNOMONSYS

        if self._pending_confs.get("ACK-ACK", False):
            self._pending_confs.pop("ACK-ACK")

    def update_frame(self):
        """
        Plot MON-SPAN spectrum analysis.

        If no updates received after a given number of trys,
        assume receiver doesn't support MON-SYS or MON-COMMS.

        sysmon_data is a list of sys monitor parms.
        comms-data is a tuple of tx and rx values
        """

        sysdata = self.__app.gnss_status.sysmon_data
        commsdata = self.__app.gnss_status.comms_data

        if len(sysdata) + len(commsdata) == 0:
            self._waits += 1
            if self._waits >= MAXWAIT:
                self._monsys_status = DLGNOMONSYS
                self.init_chart()
            return

        self._monsys_status = ACTIVE
        self._waits = 0
        try:
            bootType = BOOTTYPES[sysdata.get("bootType", 0)]
            cpuLoad = sysdata.get("cpuLoad", NA)
            cpuLoadMax = sysdata.get("cpuLoadMax", NA)
            memUsage = sysdata.get("memUsage", NA)
            memUsageMax = sysdata.get("memUsageMax", NA)
            ioUsage = sysdata.get("ioUsage", NA)
            ioUsageMax = sysdata.get("ioUsageMax", NA)
            runTime = sysdata.get("runTime", NA)
            noticeCount = sysdata.get("noticeCount", NA)
            warnCount = sysdata.get("warnCount", NA)
            errorCount = sysdata.get("errorCount", NA)
            tempValue = sysdata.get("tempValue", NA)
            if isinstance(tempValue, int):
                tempValueP = tempValue * 100 / MAXTEMP
                self._maxtemp = max(tempValue, self._maxtemp) * 100 / MAXTEMP
            else:
                tempValueP = NA

            self.init_chart()
            y = self._fonth
            y = self._chart_parm(XOFFSET, y, cpuLoadMax, cpuLoad, "CPU", "%")
            y = self._chart_parm(XOFFSET, y, memUsageMax, memUsage, "Memory", "%")
            y = self._chart_parm(XOFFSET, y, ioUsageMax, ioUsage, "I/O", "%")
            for port, pdata in sorted(commsdata.items()):
                y = self._chart_io(XOFFSET, y, port, pdata)
            y += SPACING
            y = self._chart_parm(XOFFSET, y, self._maxtemp, tempValueP, "Temp", "°C")

            rtm, rtmu = secs2unit(runTime)
            rtf = "" if rtmu == "secs" else ",.02f"
            txt = (
                f"Boot Type: {bootType}\n"
                + f"Runtime: {rtm:{rtf}} {rtmu}\n"
                + f"Notices: {noticeCount}, Warnings: {warnCount}, Errors: {errorCount}"
            )
            self._can_sysmon.create_text(
                XOFFSET,
                y,
                text=txt,
                fill=FGCOL,
                anchor="nw",
                font=self._font,
            )
        except KeyError:  # invalid sysmon-data or comms-data
            self._monsys_status = DLGNOMONSYS
            self.init_chart()

    def _chart_parm(
        self,
        xoffset: int,
        y: int,
        maxval: int,
        val: int,
        lbl: str,
        unit: str,
    ) -> int:
        """
        Draw caption and current/max bar charts on canvas.
        """

        scale = (self.width - (3 * xoffset)) / 100
        x = xoffset
        self._can_sysmon.create_text(
            x,
            y,
            text=f"{lbl}: {val} {unit}",
            fill=FGCOL,
            anchor="w",
            font=self._font,
        )
        y += self._fonth
        if isinstance(maxval, (int, float)):
            self._can_sysmon.create_line(
                x,
                y,
                x + maxval * scale,
                y,
                fill=self._set_col(maxval),
                dash=DASH,
                width=self._fonth,
            )
        if isinstance(val, (int, float)):
            self._can_sysmon.create_line(
                x,
                y,
                x + val * scale,
                y,
                fill=self._set_col(val),
                width=self._fonth,
            )
            y += self._fonth + SPACING
        return y

    def _chart_io(self, xoffset: int, y: int, port: int, pdata: tuple):
        """
        Draw port I/O captions and tx/rx current/max bar charts on canvas.

        I/O byte counts will display actual or pending, depending
        on mode setting.

        :param int xoffset: x axis offset
        :param int y: y axis
        :param int port: port id
        :param tuple pdata: port data tx & rx
        :param int mode: 0 = total bytes, 1 = pending bytes
        """

        mod = self._mode.get()
        cap = self._font.measure("UART2 → 888.88 GB ← 888.88 GB: ⇄")
        scale = (self.width - cap - (3 * xoffset)) / 100
        x = xoffset
        txb, txbu = bytes2unit(pdata[3 if mod else 2])  # total or pending
        txf = "d" if txbu == "" else ".02f"
        rxb, rxbu = bytes2unit(pdata[7 if mod else 6])
        rxf = "d" if rxbu == "" else ".02f"
        txt = f"{PORTIDS.get(port, NA)} → {txb:{txf}} {txbu} ← {rxb:{rxf}} {rxbu}:"
        self._can_sysmon.create_text(  # port
            x,
            y,
            text=txt,
            fill=FGCOL,
            anchor="w",
            font=self._font,
        )
        self._can_sysmon.create_text(  # port
            x + cap - 1,
            y,
            text="⇄",
            fill=FGCOL,
            anchor="e",
            font=self._font,
        )
        p = -1
        for i in range(0, 8, 4):  # RX & TX
            self._can_sysmon.create_line(  # max
                x + cap,
                y + p,
                x + cap + pdata[i + 1] * scale,
                y + p,
                fill=self._set_col(pdata[i + 1]),
                dash=DASH,
                width=2,
            )
            self._can_sysmon.create_line(  # val
                x + cap,
                y + p,
                x + cap + pdata[i] * scale,
                y + p,
                fill=self._set_col(pdata[i]),
                width=2,
            )
            p += 4
        y += self._fonth
        return y

    def _set_col(self, val: float) -> str:
        """
        Set bar chart line color
        (green low, red high).

        :param val: value as %
        :return: color string
        :rtype: str
        """

        return hsv2rgb((100 - min(100, val)) / 300, 0.8, 0.8)

    def _on_resize(self, event):  # pylint: disable=unused-argument
        """
        Resize frame.

        :param event event: resize event
        """

        self.width, self.height = self.get_size()

    def get_size(self):
        """
        Get current canvas size.

        :return: window size (width, height)
        :rtype: tuple
        """

        self.update_idletasks()  # Make sure we know about any resizing
        width = self._can_sysmon.winfo_width()
        height = self._can_sysmon.winfo_height()
        self._set_fontsize()
        return (width, height)

    def _set_fontsize(self):
        """
        Set font size to accommodate specified number of lines on canvas.
        """

        self._font, self._fonth = sizefont(self.height, MAXLINES, MINFONT)
