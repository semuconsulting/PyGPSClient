"""
System Monitor frame for PyGPSClient application.

This present current u-blox receiver status based
on MON-SYS polls

Created on 30 Apr 2023

:author: semuadmin
:copyright: SEMU Consulting © 2022
:license: BSD 3-Clause
"""

from tkinter import BOTH, YES, Canvas, Frame, font

from pyubx2 import SET, UBXMessage

from pygpsclient.globals import BGCOL, SYSMONVIEW, WIDGETU2
from pygpsclient.strings import DLGNOMONSYS, DLGWAITMONSYS, MONSYSERROR

# Graph dimensions
RESFONT = 40  # font size relative to widget size
MINFONT = 8  # minimum font size
MAXTEMP = 100  # °C
TOPLIM = 80
MIDLIM = 50
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
        self._monsys_enabled = False
        self._pending_confs = {}
        self._maxtemp = 0
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

        # display 'enable MON-SYS' warning
        if not self._monsys_enabled:
            self.can_sysmon.create_text(
                self.width / 2,
                self.height / 2,
                text=MONSYSERROR,
                fill="orange",
            )

    def _on_clear(self, event):  # pylint: disable=unused-argument
        """
        Clear plot.

        :param Event event: clear event
        """

        self._maxtemp = 0
        self.init_chart()

    def enable_MONSYS(self, status: bool):
        """
        Enable/disable UBX MON-SYS (b'\x0a\x39') message.

        NB: CPU Load value only valid if rate = 1

        :param bool status: 0 = off, 1 = on
        """

        msg = UBXMessage(
            "CFG",
            "CFG-MSG",
            SET,
            msgClass=0x0A,
            msgID=0x39,
            rateUART1=status,
            rateUART2=status,
            rateUSB=status,
        )
        self.__app.gnss_outqueue.put(msg.serialize())
        for msgid in ("ACK-ACK", "ACK-NAK"):
            self._set_pending(msgid, SYSMONVIEW)
        w, h = self.width, self.height
        self.can_sysmon.create_text(
            w / 2,
            h / 2,
            text=DLGWAITMONSYS,
            fill="orange",
            anchor="s",
        )

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
            # self._on_clear()
            w, h = self.width, self.height
            self.can_sysmon.create_text(
                w / 2,
                h / 2,
                text=DLGNOMONSYS,
                fill="orange",
                anchor="s",
            )
            self._pending_confs.pop("ACK-NAK")
            self._monsys_enabled = False

        if self._pending_confs.get("ACK-ACK", False):
            self._pending_confs.pop("ACK-ACK")

    def update_frame(self):
        """
        Plot MON-SPAN spectrum analysis.

        spectrum_data is list of tuples (spec, spn, res, ctr, pga),
        one item per RF block.
        """

        self._monsys_enabled = True
        self.init_chart()
        xoffset = 10
        y = 10
        scale = (self.width - (2 * xoffset)) / 100

        try:
            sysdata = self.__app.gnss_status.sysmon_data
            bootType = BOOTTYPES.get(sysdata["bootType"], "N/A")
            cpuLoad = sysdata["cpuLoad"]
            cpuLoadMax = sysdata["cpuLoadMax"]
            memUsage = sysdata["memUsage"]
            memUsageMax = sysdata["memUsageMax"]
            ioUsage = sysdata["ioUsage"]
            ioUsageMax = sysdata["ioUsageMax"]
            runTime = sysdata["runTime"]
            if runTime > 60:
                runTimeU = runTime / 60
                unt = "mins"
                fmt = ",.2f"
            elif runTime > 3600:
                runTimeU = runTime / 3600
                unt = "hours"
                fmt = ",.2f"
            else:
                runTimeU = runTime
                unt = "secs"
                fmt = ",.0f"

            noticeCount = sysdata["noticeCount"]
            warnCount = sysdata["warnCount"]
            errorCount = sysdata["errorCount"]
            tempValue = sysdata["tempValue"]
            tempValueP = tempValue * 100 / MAXTEMP
            self._maxtemp = max(tempValue, self._maxtemp) * 100 / MAXTEMP
        except KeyError:
            return

        y = self._draw_line(xoffset, y, scale, cpuLoadMax, cpuLoad, "CPU", "%")
        y = self._draw_line(xoffset, y, scale, memUsageMax, memUsage, "Memory", "%")
        y = self._draw_line(xoffset, y, scale, ioUsageMax, ioUsage, "I/O", "%")
        y = self._draw_line(xoffset, y, scale, self._maxtemp, tempValueP, "Temp", "°C")
        y += self._fonth
        self.can_sysmon.create_text(
            xoffset,
            y,
            text=f"Boot Type: {bootType}, Runtime: {runTimeU:{fmt}} {unt}",
            fill="white",
            anchor="w",
            font=self._font,
        )
        y += 2 * self._fonth
        self.can_sysmon.create_text(
            xoffset,
            y,
            text=f"Notices: {noticeCount}, Warnings: {warnCount}, Errors: {errorCount}",
            fill="white",
            anchor="w",
            font=self._font,
        )

    def _draw_line(
        self, x: int, y: int, scale: float, maxval: int, val: int, lbl: str, unit: str
    ) -> int:
        """
        Draw line on chart.
        """

        y += self._fonth
        if val > 100:
            val = 100
            lbl += "!"
        txtcol = "white"
        dash = (5, 2)
        thick = self._fonth - 2
        self.can_sysmon.create_text(
            x,
            y,
            text=f"{lbl}: {val} {unit}",
            fill=txtcol,
            anchor="w",
            font=self._font,
        )
        y += self._fonth
        self.can_sysmon.create_line(
            x,
            y,
            x + maxval * scale,
            y,
            fill=self._set_col(maxval),
            dash=dash,
            width=thick,
        )
        self.can_sysmon.create_line(
            x,
            y,
            x + val * scale,
            y,
            fill=self._set_col(val),
            width=thick,
        )
        y += self._fonth
        return y

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
        Set font size and line spacing
        """

        dim = min(self.width, self.height)
        self._font = font.Font(size=max(int(dim * RESFONT / 1000), MINFONT))
        self._fonth = self._font.metrics("linespace")

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
