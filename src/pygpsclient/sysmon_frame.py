"""
System Monitor frame for PyGPSClient application.

This present current u-blox receiver status based
on MON-SYS polls

Created on 30 Apr 2023

:author: semuadmin
:copyright: SEMU Consulting © 2022
:license: BSD 3-Clause
"""

from tkinter import BOTH, YES, Canvas, Frame

from pyubx2 import SET, UBXMessage

from pygpsclient.globals import BGCOL, SYSMONVIEW, WIDGETU2
from pygpsclient.helpers import sizefont
from pygpsclient.strings import DLGENABLEMONSYS, DLGNOMONSYS, DLGWAITMONSYS, NA

# Graph dimensions
RESFONT = 35  # font size relative to widget size
MINFONT = 6  # minimum font size
MAXTEMP = 100  # °C
TOPLIM = 80
MIDLIM = 50
XOFFSET = 10
SPACING = 5
DASH = (5, 2)
TXTCOL = "white"
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
ACTIVE = ""
MAXLINES = 23
MINFONT = 4
MAXWAIT = 5


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
        self._body()
        self._set_fontsize()
        self._attach_events()

    def _body(self):
        """
        Set up frame and widgets.
        """

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.can_sysmon = Canvas(self, width=self.width, height=self.height, bg=BGCOL)
        self.can_sysmon.pack(fill=BOTH, expand=YES)

    def _attach_events(self):
        """
        Bind events to frame.
        """

        self.bind("<Configure>", self._on_resize)
        self.can_sysmon.bind("<Double-Button-1>", self._on_clear)

    def init_chart(self):
        """
        Initialise sysmon chart.
        """

        self.can_sysmon.delete("all")
        self.can_sysmon.create_text(
            self.width / 2,
            self.height / 2,
            text=self._monsys_status,
            fill="orange",
        )

    def _on_clear(self, event):  # pylint: disable=unused-argument
        """
        Clear plot.

        :param Event event: clear event
        """

        self.__app.gnss_status.sysmon_data = {}
        self.__app.gnss_status.comms_data = {}
        self._maxtemp = 0
        self._monsys_status = DLGWAITMONSYS
        self.init_chart()

    def enable_MONSYS(self, status: bool):
        """
        Enable/disable UBX MON-SYS & MON-COMMS messages.

        NB: CPU Load value only valid if rate = 1

        :param bool status: 0 = off, 1 = on
        """

        for mid in (0x39, 0x36):
            msg = UBXMessage(
                "CFG",
                "CFG-MSG",
                SET,
                msgClass=0x0A,
                msgID=mid,
                rateUART1=status,
                rateUART2=status,
                rateUSB=status,
            )
            self.__app.gnss_outqueue.put(msg.serialize())
        for msgid in ("ACK-ACK", "ACK-NAK"):
            self._set_pending(msgid, SYSMONVIEW)
        self._monsys_status = DLGWAITMONSYS
        self.init_chart()

    def _set_pending(self, msgid: int, ubxfrm: int):
        """
        Set pending confirmation flag for Sysmonview frame to
        signify that it's waiting for a confirmation message.

        :param int msgid: UBX message identity
        :param int ubxfrm: integer representing UBX configuration frame (0-13)
        """

        self._pending_confs[msgid] = ubxfrm

    def update_pending(self, msg: UBXMessage):
        """
        Receives polled confirmation message from the ubx_handler and
        updates sysmon canvas.

        :param UBXMessage msg: UBX config message
        """

        pending = self._pending_confs.get(msg.identity, False)
        if pending and msg.identity == "ACK-NAK":
            self._pending_confs.pop("ACK-NAK")
            self._monsys_status = DLGNOMONSYS
            # self.init_chart()

        if self._pending_confs.get("ACK-ACK", False):
            self._pending_confs.pop("ACK-ACK")

    def update_frame(self):
        """
        Plot MON-SPAN spectrum analysis.

        spectrum_data is list of tuples (spec, spn, res, ctr, pga),
        one item per RF block.
        """

        sysdata = self.__app.gnss_status.sysmon_data
        commsdata = self.__app.gnss_status.comms_data

        # If no updates received after a period, assume
        # receiver doesn't support MON-SYS and/or MON-COMMS
        if len(sysdata) == 0 and len(commsdata) == 0:
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
            y = self._draw_line(XOFFSET, y, cpuLoadMax, cpuLoad, "CPU", "%")
            y = self._draw_line(XOFFSET, y, memUsageMax, memUsage, "Memory", "%")
            y = self._draw_line(XOFFSET, y, ioUsageMax, ioUsage, "I/O", "%")

            for port, pdata in sorted(commsdata.items()):
                y = self._draw_port_io(XOFFSET, y, port, pdata)
            y += SPACING
            y = self._draw_line(XOFFSET, y, self._maxtemp, tempValueP, "Temp", "°C")

            txt = (
                f"Boot Type: {bootType}\n"
                + self._format_runtime(runTime)
                + f"Notices: {noticeCount}, Warnings: {warnCount}, Errors: {errorCount}"
            )
            self.can_sysmon.create_text(
                XOFFSET,
                y,
                text=txt,
                fill=TXTCOL,
                anchor="nw",
                font=self._font,
            )
        except KeyError:
            self._monsys_status = DLGNOMONSYS
            self.init_chart()

    def _draw_line(
        self,
        xoffset: int,
        y: int,
        maxval: int,
        val: int,
        lbl: str,
        unit: str,
    ) -> int:
        """
        Draw line on chart.
        """

        scale = (self.width - (3 * xoffset)) / 100
        x = xoffset
        self.can_sysmon.create_text(
            x,
            y,
            text=f"{lbl}: {val} {unit}",
            fill=TXTCOL,
            anchor="w",
            font=self._font,
        )
        y += self._fonth
        if isinstance(maxval, (int, float)):
            self.can_sysmon.create_line(
                x,
                y,
                x + maxval * scale,
                y,
                fill=self._set_col(maxval),
                dash=DASH,
                width=self._fonth,
            )
        if isinstance(val, (int, float)):
            self.can_sysmon.create_line(
                x,
                y,
                x + val * scale,
                y,
                fill=self._set_col(val),
                width=self._fonth,
            )
            y += self._fonth + SPACING
        return y

    def _draw_port_io(self, xoffset: int, y: int, port: int, pdata: tuple):
        """
        Draw port I/O TX & RX lines on chart

        :param port: _description_
        :param pdata: _description_
        """

        cap = self._font.measure("port 888: ")
        scale = (self.width - cap - (3 * xoffset)) / 100
        x = xoffset
        port = f"port {port:03x}:"
        self.can_sysmon.create_text(  # port
            x,
            y,
            text=port,
            fill=TXTCOL,
            anchor="w",
            font=self._font,
        )
        p = -1
        for i in range(0, 4, 2):  # RX & TX
            self.can_sysmon.create_line(  # max
                x + cap,
                y + p,
                x + cap + pdata[i + 1] * scale,
                y + p,
                fill=self._set_col(pdata[i + 1]),
                dash=DASH,
                width=2,
            )
            self.can_sysmon.create_line(  # val
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
        Set chart line color

        :param val: value as %
        :return: color string
        :rtype: str
        """

        if val > TOPLIM:
            return "orangered"
        if val > MIDLIM:
            return "orange"
        return "yellowgreen"

    def _format_runtime(self, runtime: int) -> str:
        """
        Format runtime in appropriate units.

        :param runtime: runtime in seconds
        :return: runtime in secs, mins, hours or days
        "rtype: str
        """

        if not isinstance(runtime, int):
            return "Runtime: N/A\n"
        if runtime > 86400:
            rnt = runtime / 86400
            rntu = "days"
            rntf = ",.2f"
        elif runtime > 3600:
            rnt = runtime / 3600
            rntu = "hours"
            rntf = ",.2f"
        elif runtime > 60:
            rnt = runtime / 60
            rntu = "mins"
            rntf = ",.2f"
        else:
            rnt = runtime
            rntu = "secs"
            rntf = ",.0f"
        return f"Runtime: {rnt:{rntf}} {rntu}\n"

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
        width = self.can_sysmon.winfo_width()
        height = self.can_sysmon.winfo_height()
        self._set_fontsize()
        return (width, height)

    def _set_fontsize(self):
        """
        Set font size to accommodate specified number of lines on canvas.
        """

        self._font, self._fonth = sizefont(self.height, MAXLINES, MINFONT)
