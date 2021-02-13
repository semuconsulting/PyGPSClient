"""
UBX Configuration widget for CFG-MSG commands

Created on 22 Dec 2020

Created on 22 Sep 2020

@author: semuadmin
"""
# pylint: disable=invalid-name, too-many-instance-attributes, too-many-ancestors

from tkinter import (
    Frame,
    Listbox,
    Spinbox,
    Scrollbar,
    Button,
    Label,
    IntVar,
    N,
    S,
    E,
    W,
    LEFT,
    VERTICAL,
)
from PIL import ImageTk, Image
from pyubx2 import (
    UBXMessage,
    POLL,
    SET,
    UBX_MSGIDS,
)
from pyubx2.ubxhelpers import key_from_val
from .globals import (
    ENTCOL,
    ICON_SEND,
    ICON_WARNING,
    ICON_PENDING,
    ICON_CONFIRMED,
    READONLY,
    UBX_CFGMSG,
)
from .strings import LBLCFGMSG


class UBX_MSGRATE_Frame(Frame):
    """
    UBX Message Rate configuration command panel.
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
        self._ddc_rate = IntVar()
        self._uart1_rate = IntVar()
        self._usb_rate = IntVar()
        self._spi_rate = IntVar()
        self._cfg_msg_command = None

        self._body()
        self._do_layout()
        self._attach_events()
        self._reset()

    def _body(self):
        """
        Set up frame and widgets.
        """

        MAX_RATE = 0xFF
        self._lbl_cfg_msg = Label(self, text=LBLCFGMSG, anchor="w")
        self._lbx_cfg_msg = Listbox(
            self,
            border=2,
            relief="sunken",
            bg=ENTCOL,
            height=7,
            justify=LEFT,
            exportselection=False,
        )
        self._scr_cfg_msg = Scrollbar(self, orient=VERTICAL)
        self._lbx_cfg_msg.config(yscrollcommand=self._scr_cfg_msg.set)
        self._scr_cfg_msg.config(command=self._lbx_cfg_msg.yview)
        self._lbl_ddc = Label(self, text="I2C")
        self._spn_ddc = Spinbox(
            self,
            width=3,
            from_=0,
            to=MAX_RATE,
            textvariable=self._ddc_rate,
            state=READONLY,
            readonlybackground=ENTCOL,
        )
        self._lbl_uart1 = Label(self, text="UART1")
        self._spn_uart1 = Spinbox(
            self,
            width=3,
            from_=0,
            to=MAX_RATE,
            textvariable=self._uart1_rate,
            state=READONLY,
            readonlybackground=ENTCOL,
        )
        self._lbl_usb = Label(self, text="USB")
        self._spn_usb = Spinbox(
            self,
            width=3,
            from_=0,
            to=MAX_RATE,
            textvariable=self._usb_rate,
            state=READONLY,
            readonlybackground=ENTCOL,
        )
        self._lbl_spi = Label(self, text="SPI")
        self._spn_spi = Spinbox(
            self,
            width=3,
            from_=0,
            to=MAX_RATE,
            textvariable=self._spi_rate,
            state=READONLY,
            readonlybackground=ENTCOL,
        )
        self._lbl_send_command = Label(self)
        self._btn_send_command = Button(
            self,
            image=self._img_send,
            width=50,
            fg="green",
            command=self._on_send_cfg_msg,
            font=self.__app.font_md,
        )

    def _do_layout(self):
        """
        Layout widgets.
        """

        self._lbl_cfg_msg.grid(column=0, row=0, columnspan=6, padx=3, sticky=(W, E))
        self._lbx_cfg_msg.grid(
            column=0, row=1, columnspan=2, rowspan=8, padx=3, pady=3, sticky=(W, E)
        )
        self._scr_cfg_msg.grid(column=1, row=1, rowspan=8, sticky=(N, S, E))
        self._lbl_ddc.grid(column=2, row=1, rowspan=2, padx=0, pady=1, sticky=(E))
        self._spn_ddc.grid(column=3, row=1, rowspan=2, padx=0, pady=0, sticky=(W))
        self._lbl_uart1.grid(column=2, row=3, rowspan=2, padx=0, pady=1, sticky=(E))
        self._spn_uart1.grid(column=3, row=3, rowspan=2, padx=0, pady=0, sticky=(W))
        self._lbl_usb.grid(column=2, row=5, rowspan=2, padx=0, pady=1, sticky=(E))
        self._spn_usb.grid(column=3, row=5, rowspan=2, padx=0, pady=0, sticky=(W))
        self._lbl_spi.grid(column=2, row=7, rowspan=2, padx=0, pady=1, sticky=(E))
        self._spn_spi.grid(column=3, row=7, rowspan=2, padx=0, pady=0, sticky=(W))
        self._btn_send_command.grid(
            column=4, row=1, rowspan=8, ipadx=3, ipady=3, sticky=(E)
        )
        self._lbl_send_command.grid(
            column=5, row=1, rowspan=8, ipadx=3, ipady=3, sticky=(E)
        )

        (cols, rows) = self.grid_size()
        for i in range(cols):
            self.grid_columnconfigure(i, weight=1)
        for i in range(rows):
            self.grid_rowconfigure(i, weight=1)
        self.option_add("*Font", self.__app.font_sm)

    def _attach_events(self):
        """
        Bind listbox selection events.
        """

        self._lbx_cfg_msg.bind("<<ListboxSelect>>", self._on_select_cfg_msg)

    def _reset(self):
        """
        Reset settings to defaults.
        """

        idx = 0
        for _, val in UBX_MSGIDS.items():
            if val[0:3] not in ("ACK", "CFG", "AID", "MGA", "UPD", "FOO"):
                self._lbx_cfg_msg.insert(idx, val)
                idx += 1

    def update_status(self, cfgtype, **kwargs):
        """
        Update pending confirmation status.
        """

        if cfgtype == "CFG-MSG":
            self.__container.set_status("CFG-MSG GET message received", "green")
            self._ddc_rate.set(kwargs.get("ddcrate", 0))
            self._uart1_rate.set(kwargs.get("uart1rate", 0))
            self._usb_rate.set(kwargs.get("usbrate", 0))
            self._spi_rate.set(kwargs.get("spirate", 0))
            self._lbl_send_command.config(image=self._img_confirmed)
        elif cfgtype == "ACK-NAK":
            self.__container.set_status("CFG-MSG POLL message rejected", "red")
            self._lbl_send_command.config(image=self._img_warn)

    def _on_select_cfg_msg(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        CFG-MSG command has been selected.
        """

        idx = self._lbx_cfg_msg.curselection()
        self._cfg_msg_command = self._lbx_cfg_msg.get(idx)

        # poll selected message configuration to get current message rates
        msg = key_from_val(UBX_MSGIDS, self._cfg_msg_command)
        self._do_poll_msg(msg)

    def _on_send_cfg_msg(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        CFG-MSG command send button has been clicked.
        """

        msg = key_from_val(UBX_MSGIDS, self._cfg_msg_command)
        msgClass = int.from_bytes(msg[0:1], "little", signed=False)
        msgID = int.from_bytes(msg[1:2], "little", signed=False)
        rateDDC = int(self._ddc_rate.get())
        rateUART1 = int(self._uart1_rate.get())
        rateUSB = int(self._usb_rate.get())
        rateSPI = int(self._spi_rate.get())
        data = UBXMessage(
            "CFG",
            "CFG-MSG",
            SET,
            msgClass=msgClass,
            msgID=msgID,
            rateDDC=rateDDC,
            rateUART1=rateUART1,
            rateUSB=rateUSB,
            rateSPI=rateSPI,
        )
        self.__app.serial_handler.serial_write(data.serialize())
        self._lbl_send_command.config(image=self._img_pending)
        self.__container.set_status("CFG-MSG SET message sent", "green")
        self.__container.set_pending(UBX_CFGMSG, ("ACK-ACK", "ACK-NAK"))

        self._do_poll_msg(msg)

    def _do_poll_msg(self, msg):
        """
        Poll message rate.
        """

        data = UBXMessage("CFG", "CFG-MSG", POLL, payload=msg)  # poll for a response
        self.__app.serial_handler.serial_write(data.serialize())
        self._lbl_send_command.config(image=self._img_pending)
        self.__container.set_status("CFG-MSG POLL message sent", "blue")
        self.__container.set_pending(UBX_CFGMSG, ("CFG-MSG", "ACK-NAK"))
