"""
UBX Configuration widget for CFG-RATE commands

Created on 19 Feb 2020

@author: semuadmin
"""
# pylint: disable=invalid-name, too-many-instance-attributes, too-many-ancestors

from tkinter import (
    Frame,
    Spinbox,
    Button,
    Label,
    IntVar,
    E,
    W,
)
from PIL import ImageTk, Image
from pyubx2 import (
    UBXMessage,
    POLL,
    SET,
)
from .globals import (
    ENTCOL,
    ICON_SEND,
    ICON_WARNING,
    ICON_PENDING,
    ICON_CONFIRMED,
    READONLY,
    UBX_CFGRATE,
)
from .strings import LBLCFGRATE

TIMEREFS = {
    "UTC": 0,
    "GPS": 1,
    "GLO": 2,
    "BEI": 3,
    "GAL": 4,
}


class UBX_RATE_Frame(Frame):
    """
    UBX Navigation Solution Rate configuration command panel.
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
        self._measint = IntVar()
        self._navrate = IntVar()
        self._timeref = IntVar()

        self._body()
        self._do_layout()
        self._attach_events()

    def _body(self):
        """
        Set up frame and widgets.
        """

        self._lbl_cfg_rate = Label(self, text=LBLCFGRATE, anchor="w")
        self._lbl_ubx_measint = Label(self, text="Solution Interval (ms)")
        self._spn_ubx_measint = Spinbox(
            self,
            values=(50, 100, 200, 500, 1000, 2000, 5000, 10000),
            width=6,
            state=READONLY,
            readonlybackground=ENTCOL,
            wrap=True,
            textvariable=self._measint,
        )
        self._lbl_ubx_navrate = Label(self, text="Measurement Ratio")
        self._spn_ubx_navrate = Spinbox(
            self,
            from_=1,
            to=127,
            width=4,
            state=READONLY,
            readonlybackground=ENTCOL,
            wrap=True,
            textvariable=self._navrate,
        )
        self._lbl_ubx_timeref = Label(self, text="Time Reference")
        self._spn_ubx_timeref = Spinbox(
            self,
            values=(0, 1, 2, 3, 4),
            width=4,
            state=READONLY,
            readonlybackground=ENTCOL,
            wrap=True,
            textvariable=self._timeref,
        )
        self._lbl_send_command = Label(self, image=self._img_pending)
        self._btn_send_command = Button(
            self,
            image=self._img_send,
            width=50,
            command=self._on_send_rate,
            font=self.__app.font_md,
        )

    def _do_layout(self):
        """
        Layout widgets.
        """

        self._lbl_cfg_rate.grid(column=0, row=0, columnspan=6, padx=3, sticky=(W, E))
        self._lbl_ubx_measint.grid(
            column=0, row=1, columnspan=2, rowspan=1, padx=3, pady=3, sticky=(W)
        )
        self._spn_ubx_measint.grid(column=2, row=1, columnspan=1, rowspan=1, sticky=(W))
        self._lbl_ubx_navrate.grid(
            column=0, row=2, columnspan=2, rowspan=1, padx=3, pady=3, sticky=(W)
        )
        self._spn_ubx_navrate.grid(column=2, row=2, columnspan=2, rowspan=1, sticky=(W))
        self._lbl_ubx_timeref.grid(
            column=0, row=3, columnspan=2, rowspan=1, padx=3, pady=3, sticky=(W)
        )
        self._spn_ubx_timeref.grid(column=2, row=3, columnspan=2, rowspan=1, sticky=(W))
        self._btn_send_command.grid(
            column=4, row=1, rowspan=3, ipadx=3, ipady=3, sticky=(E)
        )
        self._lbl_send_command.grid(
            column=5, row=1, rowspan=3, ipadx=3, ipady=3, sticky=(E)
        )

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
        self.bind("<Button>", self._do_poll_rate)

    def reset(self):
        """
        Reset panel to initial settings
        """

        self._do_poll_rate()

    def update_status(self, cfgtype, **kwargs):
        """
        Update pending confirmation status.
        """

        if cfgtype == "CFG-RATE":
            self._measint.set(kwargs.get("measrate", 1000))
            self._navrate.set(kwargs.get("navrate", 1))
            self._timeref.set(kwargs.get("timeref", 0))
            self._lbl_send_command.config(image=self._img_confirmed)
            self.__container.set_status("CFG-RATE GET message received", "green")
        elif cfgtype == "ACK-NAK":
            self.__container.set_status("CFG-RATE POLL message rejected", "red")
            self._lbl_send_command.config(image=self._img_warn)

    def _on_send_rate(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Handle Send rate config button press.
        """

        msg = UBXMessage(
            "CFG",
            "CFG-RATE",
            SET,
            measRate=self._measint.get(),
            navRate=self._navrate.get(),
            timeRef=self._timeref.get(),
        )
        self.__app.serial_handler.serial_write(msg.serialize())
        self._lbl_send_command.config(image=self._img_pending)
        self.__container.set_status("CFG-RATE SET message sent", "blue")
        self.__container.set_pending(UBX_CFGRATE, ("ACK-ACK", "ACK-NAK"))

        self._do_poll_rate()

    def _do_poll_rate(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Poll RATE message configuration.
        """

        msg = UBXMessage("CFG", "CFG-RATE", POLL)
        self.__app.serial_handler.serial_write(msg.serialize())
        self._lbl_send_command.config(image=self._img_pending)
        self.__container.set_status("CFG-RATE POLL message sent", "blue")
        self.__container.set_pending(UBX_CFGRATE, ("CFG-RATE", "ACK-NAK"))
