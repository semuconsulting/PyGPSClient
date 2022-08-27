"""
UBX Configuration frame for MON-VER and MON-HW messages

Created on 22 Dec 2020

:author: semuadmin
:copyright: SEMU Consulting © 2020
:license: BSD 3-Clause
"""
# pylint: disable=invalid-name

from tkinter import (
    Frame,
    Label,
    StringVar,
    W,
)
from PIL import ImageTk, Image
from pyubx2 import UBXMessage, POLL
from pygpsclient.globals import (
    INFCOL,
    ICON_SEND,
    ICON_WARNING,
    ICON_PENDING,
    ICON_CONFIRMED,
    ANTPOWER,
    ANTSTATUS,
    UBX_MONVER,
    UBX_MONHW,
    CONNECTED,
)


class UBX_INFO_Frame(Frame):
    """
    UBX hardware & firmware information panel.
    """

    def __init__(self, app, container, *args, **kwargs):
        """
        Constructor.

        :param Frame app: reference to main tkinter application
        :param Frame container: reference to container frame (config-dialog)
        :param args: optional args to pass to Frame parent class
        :param kwargs: optional kwargs to pass to Frame parent class
        """

        self.__app = app  # Reference to main application class
        self.__master = self.__app.get_master()  # Reference to root class (Tk)
        self.__container = container

        Frame.__init__(self, self.__container.container, *args, **kwargs)

        self._img_send = ImageTk.PhotoImage(Image.open(ICON_SEND))
        self._img_pending = ImageTk.PhotoImage(Image.open(ICON_PENDING))
        self._img_confirmed = ImageTk.PhotoImage(Image.open(ICON_CONFIRMED))
        self._img_warn = ImageTk.PhotoImage(Image.open(ICON_WARNING))
        self._sw_version = StringVar()
        self._hw_version = StringVar()
        self._fw_version = StringVar()
        self._ant_status = StringVar()
        self._ant_power = StringVar()
        self._protocol = StringVar()
        self._gnss_supported = StringVar()

        self._body()
        self._do_layout()
        self._attach_events()

    def _body(self):
        """
        Set up frame and widgets.
        """

        self._lbl_swverl = Label(self, text="Software")
        self._lbl_swver = Label(self, textvariable=self._sw_version, fg=INFCOL)
        self._lbl_hwverl = Label(self, text="Hardware")
        self._lbl_hwver = Label(self, textvariable=self._hw_version, fg=INFCOL)
        self._lbl_fwverl = Label(self, text="Firmware")
        self._lbl_fwver = Label(self, textvariable=self._fw_version, fg=INFCOL)
        self._lbl_romverl = Label(self, text="Protocol")
        self._lbl_romver = Label(self, textvariable=self._protocol, fg=INFCOL)
        self._lbl_gnssl = Label(self, text="GNSS/AS")
        self._lbl_gnss = Label(self, textvariable=self._gnss_supported, fg=INFCOL)
        self._lbl_ant_statusl = Label(self, text="Ant. Status")
        self._lbl_ant_status = Label(self, textvariable=self._ant_status, fg=INFCOL)
        self._lbl_ant_powerl = Label(self, text="Ant. Power")
        self._lbl_ant_power = Label(self, textvariable=self._ant_power, fg=INFCOL)

    def _do_layout(self):
        """
        Layout widgets.
        """

        self._lbl_swverl.grid(column=0, row=0, padx=2, sticky=(W))
        self._lbl_swver.grid(column=1, row=0, columnspan=2, padx=2, sticky=(W))
        self._lbl_hwverl.grid(column=3, row=0, padx=2, sticky=(W))
        self._lbl_hwver.grid(column=4, row=0, columnspan=2, padx=2, sticky=(W))
        self._lbl_fwverl.grid(column=0, row=1, padx=2, sticky=(W))
        self._lbl_fwver.grid(column=1, row=1, columnspan=2, padx=2, sticky=(W))
        self._lbl_romverl.grid(column=3, row=1, padx=2, sticky=(W))
        self._lbl_romver.grid(column=4, row=1, columnspan=2, padx=2, sticky=(W))
        self._lbl_gnssl.grid(column=0, row=2, columnspan=1, padx=2, sticky=(W))
        self._lbl_gnss.grid(column=1, row=2, columnspan=4, padx=2, sticky=(W))
        self._lbl_ant_statusl.grid(column=0, row=3, columnspan=1, padx=2, sticky=(W))
        self._lbl_ant_status.grid(column=1, row=3, columnspan=2, padx=2, sticky=(W))
        self._lbl_ant_powerl.grid(column=3, row=3, columnspan=1, padx=2, sticky=(W))
        self._lbl_ant_power.grid(column=4, row=3, columnspan=2, padx=2, sticky=(W))

        (cols, rows) = self.grid_size()
        for i in range(cols):
            self.grid_columnconfigure(i, weight=1)
        for i in range(rows):
            self.grid_rowconfigure(i, weight=1)
        self.option_add("*Font", self.__app.font_sm)

    def _attach_events(self):
        """
        Bind events to widget.
        """

        # click mouse button to refresh information
        self.bind("<Button>", self._do_poll_ver)

    def reset(self):
        """
        Reset panel to initial settings
        """

        if self.__app.conn_status == CONNECTED:
            self._do_poll_ver()

    def update_status(self, msg: UBXMessage):
        """
        Update pending confirmation status.

        :param UBXMessage msg: UBX config message
        """

        # MON-VER information (for firmware version)
        if msg.identity == "MON-VER":

            exts = []
            fw_version = b"n/a"
            protocol = b"n/a"
            gnss_supported = b""
            model = b""
            sw_version = getattr(msg, "swVersion", b"n/a")
            sw_version = sw_version.replace(b"\x00", b"")
            sw_version = sw_version.replace(b"ROM CORE", b"ROM")
            sw_version = sw_version.replace(b"EXT CORE", b"Flash")
            hw_version = getattr(msg, "hwVersion", b"n/a")
            hw_version = hw_version.replace(b"\x00", b"")

            for i in range(9):
                idx = f"_{i+1:02d}"
                ext = getattr(msg, "extension" + idx, b"")
                ext = ext.replace(b"\x00", b"")
                exts.append(ext)
                if b"FWVER=" in exts[i]:
                    fw_version = exts[i].replace(b"FWVER=", b"")
                if b"PROTVER=" in exts[i]:
                    protocol = exts[i].replace(b"PROTVER=", b"")
                if b"PROTVER " in exts[i]:
                    protocol = exts[i].replace(b"PROTVER ", b"")
                if b"MOD=" in exts[i]:
                    model = exts[i].replace(b"MOD=", b"")
                    hw_version = model + b" " + hw_version
                for gnss in (b"GPS", b"GLO", b"GAL", b"BDS", b"SBAS", b"IMES", b"QZSS"):
                    if gnss in exts[i]:
                        gnss_supported = gnss_supported + gnss + b" "

            self._sw_version.set(sw_version)
            self._hw_version.set(hw_version)
            self._fw_version.set(fw_version)
            self._protocol.set(protocol)
            self._gnss_supported.set(gnss_supported)

        # MON-HW information (for antenna status)
        if msg.identity == "MON-HW":

            ant_status = getattr(msg, "aStatus", 1)
            ant_power = getattr(msg, "aPower", 2)
            self._ant_status.set(ANTSTATUS[ant_status])
            self._ant_power.set(ANTPOWER[ant_power])

        self.__container.set_status(f"{msg.identity} GET message received", "green")

    def _do_poll_ver(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Poll MON-VER & MON-HW
        """

        for msgtype in ("MON-VER", "MON-HW"):
            msg = UBXMessage(msgtype[0:3], msgtype, POLL)
            self.__app.stream_handler.serial.write(msg.serialize())
            self.__container.set_status(f"{msgtype} POLL message sent", "blue")
        self.__container.set_pending("MON-VER", UBX_MONVER)
        self.__container.set_pending("MON-HW", UBX_MONHW)
