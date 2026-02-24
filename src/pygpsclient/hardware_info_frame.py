"""
hardware_info_frame.py

Hardware Information Dialog for NMEA and UBX Configuration panels.

Created on 22 Dec 2020

:author: semuadmin (Steve Smith)
:copyright: 2020 semuadmin
:license: BSD 3-Clause
"""

from tkinter import Frame, Label, W

from PIL import Image, ImageTk

from pygpsclient.globals import (
    ICON_CONFIRMED,
    ICON_PENDING,
    ICON_SEND,
    ICON_WARNING,
    INFOCOL,
    OKCOL,
)
from pygpsclient.strings import HWREPOLL, HWRESET, NA


class Hardware_Info_Frame(Frame):
    """
    Hardware & firmware information panel.
    """

    def __init__(self, app: Frame, parent: Frame, *args, **kwargs):
        """
        Constructor.

        :param Frame app: reference to main tkinter application
        :param Frame parent: reference to parent frame (config-dialog)
        :param args: optional args to pass to Frame parent class
        :param kwargs: optional kwargs to pass to Frame parent class
        """

        self.__app = app  # Reference to main application class
        self.__container = parent
        self._protocol = kwargs.pop("protocol", "UBX")

        super().__init__(parent.container, *args, **kwargs)

        self._img_send = ImageTk.PhotoImage(Image.open(ICON_SEND))
        self._img_pending = ImageTk.PhotoImage(Image.open(ICON_PENDING))
        self._img_confirmed = ImageTk.PhotoImage(Image.open(ICON_CONFIRMED))
        self._img_warn = ImageTk.PhotoImage(Image.open(ICON_WARNING))

        self._body()
        self._do_layout()
        self.reset()
        self._attach_events()

    def _body(self):
        """
        Set up frame and widgets.
        """

        self._lbl_hwverl = Label(self, text="Hardware")
        self._lbl_hwver = Label(self)
        self._lbl_swverl = Label(self, text="Software")
        self._lbl_swver = Label(self)
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

        self._lbl_hwverl.grid(column=0, row=0, padx=2, sticky=W)
        self._lbl_hwver.grid(column=1, row=0, columnspan=2, padx=2, sticky=W)
        self._lbl_swverl.grid(column=3, row=0, padx=2, sticky=W)
        self._lbl_swver.grid(column=4, row=0, columnspan=2, padx=2, sticky=W)
        self._lbl_fwverl.grid(column=0, row=1, padx=2, sticky=W)
        self._lbl_fwver.grid(column=1, row=1, columnspan=2, padx=2, sticky=W)
        self._lbl_romverl.grid(column=3, row=1, padx=2, sticky=W)
        self._lbl_romver.grid(column=4, row=1, columnspan=2, padx=2, sticky=W)
        self._lbl_gnssl.grid(column=0, row=2, columnspan=1, padx=2, sticky=W)
        self._lbl_gnss.grid(column=1, row=2, columnspan=4, padx=2, sticky=W)

        cols, rows = self.grid_size()
        for i in range(cols):
            self.grid_columnconfigure(i, weight=1)
        for i in range(rows):
            self.grid_rowconfigure(i, weight=1)
        # self.option_add("*Font", self.__app.font_sm)

    def _attach_events(self):
        """
        Bind events to widget.

        Single left click to refresh information.
        Double left click to re-poll version data.
        """

        self.bind("<Double-Button-1>", self.repoll)
        self.bind("<Button>", self.reset)

    def repoll(self, event=None):  # pylint: disable=unused-argument):
        """
        Re-poll hardware information.
        """

        self.__app.poll_version(self.__app.protocol_mask)
        self.__container.status_label = (HWREPOLL, INFOCOL)

    def reset(self, event=None):  # pylint: disable=unused-argument):):
        """
        Reset panel to initial settings
        """

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

        self.__container.status_label = (HWRESET, OKCOL)
