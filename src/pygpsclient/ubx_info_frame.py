"""
ubx_info_frame.py

UBX Configuration frame for MON-VER and MON-HW messages

Created on 22 Dec 2020

:author: semuadmin
:copyright: 2020 SEMU Consulting
:license: BSD 3-Clause
"""

from tkinter import Frame, Label, W

from PIL import Image, ImageTk
from pyubx2 import UBXMessage

from pygpsclient.globals import (
    CONNECTED,
    CONNECTED_SIMULATOR,
    ICON_CONFIRMED,
    ICON_PENDING,
    ICON_SEND,
    ICON_WARNING,
    UBX_MONVER,
)
from pygpsclient.strings import NA


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
        self.__master = self.__app.appmaster  # Reference to root class (Tk)
        self.__container = container

        Frame.__init__(self, self.__container.container, *args, **kwargs)

        self._img_send = ImageTk.PhotoImage(Image.open(ICON_SEND))
        self._img_pending = ImageTk.PhotoImage(Image.open(ICON_PENDING))
        self._img_confirmed = ImageTk.PhotoImage(Image.open(ICON_CONFIRMED))
        self._img_warn = ImageTk.PhotoImage(Image.open(ICON_WARNING))

        self._body()
        self._do_layout()
        self._attach_events()

    def _body(self):
        """
        Set up frame and widgets.
        """

        self._lbl_swverl = Label(self, text="Software")
        self._lbl_swver = Label(self)
        self._lbl_hwverl = Label(self, text="Hardware")
        self._lbl_hwver = Label(self)
        self._lbl_fwverl = Label(self, text="Firmware")
        self._lbl_fwver = Label(self)
        self._lbl_romverl = Label(self, text="Protocol")
        self._lbl_romver = Label(self)
        self._lbl_gnssl = Label(self, text="GNSS/AS")
        self._lbl_gnss = Label(self)

    def _do_layout(self):
        """
        Layout widgets.
        """

        self._lbl_swverl.grid(column=0, row=0, padx=2, sticky=W)
        self._lbl_swver.grid(column=1, row=0, columnspan=2, padx=2, sticky=W)
        self._lbl_hwverl.grid(column=3, row=0, padx=2, sticky=W)
        self._lbl_hwver.grid(column=4, row=0, columnspan=2, padx=2, sticky=W)
        self._lbl_fwverl.grid(column=0, row=1, padx=2, sticky=W)
        self._lbl_fwver.grid(column=1, row=1, columnspan=2, padx=2, sticky=W)
        self._lbl_romverl.grid(column=3, row=1, padx=2, sticky=W)
        self._lbl_romver.grid(column=4, row=1, columnspan=2, padx=2, sticky=W)
        self._lbl_gnssl.grid(column=0, row=2, columnspan=1, padx=2, sticky=W)
        self._lbl_gnss.grid(column=1, row=2, columnspan=4, padx=2, sticky=W)

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

        if self.__app.conn_status in (CONNECTED, CONNECTED_SIMULATOR):
            self._do_poll_ver()

    def _do_poll_ver(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Poll MON-VER
        """

        self.__app.poll_version()
        self.__container.set_pending("MON-VER", UBX_MONVER)

    def update_status(self, msg: UBXMessage):
        """
        Update pending confirmation status.

        :param UBXMessage msg: UBX config message
        """

        # MON-VER information (for software versions)
        self._lbl_swver.config(
            text=self.__app.gnss_status.version_data.get("swversion", NA)
        )
        self._lbl_hwver.config(
            text=self.__app.gnss_status.version_data.get("hwversion", NA)
        )
        self._lbl_fwver.config(
            text=self.__app.gnss_status.version_data.get("fwversion", NA)
        )
        self._lbl_romver.config(
            text=self.__app.gnss_status.version_data.get("romversion", NA)
        )
        self._lbl_gnss.config(text=self.__app.gnss_status.version_data.get("gnss", NA))

        self.__container.set_status(f"{msg.identity} GET message received", "green")
