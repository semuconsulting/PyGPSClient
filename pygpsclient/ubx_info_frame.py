"""
UBX Configuration widget for MON-VER and MON-HW messages

Created on 22 Dec 2020

@author: semuadmin
"""
# pylint: disable=invalid-name, too-many-instance-attributes, too-many-ancestors

from tkinter import (
    Frame,
    Label,
    StringVar,
    W,
)
from PIL import ImageTk, Image
from pyubx2 import UBXMessage, POLL
from .globals import (
    INFCOL,
    ICON_SEND,
    ICON_WARNING,
    ICON_PENDING,
    ICON_CONFIRMED,
    ANTPOWER,
    ANTSTATUS,
    UBX_MONVER,
    UBX_MONHW,
)


class UBX_INFO_Frame(Frame):
    """
    UBX hardware & firmware information panel.
    """

    def __init__(self, app, container, *args, **kwargs):
        """
        Constructor.

        :param object app: reference to main tkinter application
        :param frame container: container frame
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
        self._lbl_ant_statusl = Label(self, text="Antenna Status")
        self._lbl_ant_status = Label(self, textvariable=self._ant_status, fg=INFCOL)
        self._lbl_ant_powerl = Label(self, text="Antenna Power")
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

        self._do_poll_ver()

    def update_status(self, cfgtype, **kwargs):
        """
        Update pending confirmation status.
        """

        # MON-VER information (for firmware version)
        if cfgtype == "MON-VER":
            self._sw_version.set(kwargs.get("swversion", ""))
            self._hw_version.set(kwargs.get("hwversion", ""))
            self._fw_version.set(kwargs.get("fwversion", ""))
            self._protocol.set(kwargs.get("protocol", ""))
            self._gnss_supported.set(kwargs.get("gnsssupported", ""))

        # MON-HW information (for antenna status)
        if cfgtype == "MON-HW":
            self._ant_status.set(ANTSTATUS[kwargs.get("antstatus", 1)])
            self._ant_power.set(ANTPOWER[kwargs.get("antpower", 2)])

    def _do_poll_ver(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Poll MON-VER & MON-HW
        """

        for msgtype in ("MON-VER", "MON-HW"):
            msg = UBXMessage(msgtype[0:3], msgtype, POLL)
            self.__app.serial_handler.serial.write(msg.serialize())
            self.__container.set_status(f"{msgtype} POLL message sent", "blue")
        self.__container.set_pending(UBX_MONVER, ("MON-VER",))
        self.__container.set_pending(UBX_MONHW, ("MON-HW",))
