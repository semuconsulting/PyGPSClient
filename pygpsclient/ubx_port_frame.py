"""
UBX Configuration widget for CFG-PRT commands

Created on 22 Dec 2020

@author: semuadmin
"""
# pylint: disable=invalid-name, too-many-instance-attributes, too-many-ancestors

from tkinter import (
    Frame,
    Checkbutton,
    Spinbox,
    Button,
    Label,
    StringVar,
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
    PORTIDS,
    BAUDRATES,
    READONLY,
    UBX_CFGPRT,
)
from .strings import LBLCFGPRT


class UBX_PORT_Frame(Frame):
    """
    UBX Port and Protocol configuration command panel.
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
        self._baudrate = IntVar()
        self._portid = StringVar()
        self._inprot = b"\x00\x00"
        self._outprot = b"\x00\x00"
        self._inprot_nmea = IntVar()
        self._inprot_ubx = IntVar()
        self._inprot_rtcm2 = IntVar()
        self._inprot_rtcm3 = IntVar()
        self._outprot_nmea = IntVar()
        self._outprot_ubx = IntVar()
        self._outprot_rtcm3 = IntVar()

        self._body()
        self._do_layout()

    def _body(self):
        """
        Set up frame and widgets.
        """

        self._lbl_cfg_port = Label(self, text=LBLCFGPRT, anchor="w")
        self._lbl_ubx_portid = Label(self, text="Port ID")
        self._spn_ubx_portid = Spinbox(
            self,
            values=PORTIDS,
            width=8,
            state=READONLY,
            readonlybackground=ENTCOL,
            wrap=True,
            textvariable=self._portid,
            command=lambda: self._on_select_portid(),  # pylint: disable=unnecessary-lambda
        )
        self._lbl_ubx_baudrate = Label(self, text="Baud")
        self._spn_ubx_baudrate = Spinbox(
            self,
            values=(BAUDRATES),
            width=6,
            state=READONLY,
            readonlybackground=ENTCOL,
            wrap=True,
            textvariable=self._baudrate,
        )
        self._lbl_inprot = Label(self, text="Input")
        self._chk_inprot_nmea = Checkbutton(
            self, text="NMEA", variable=self._inprot_nmea
        )
        self._chk_inprot_ubx = Checkbutton(self, text="UBX", variable=self._inprot_ubx)
        self._chk_inprot_rtcm2 = Checkbutton(
            self, text="RTCM2", variable=self._inprot_rtcm2
        )
        self._chk_inprot_rtcm3 = Checkbutton(
            self, text="RTCM3", variable=self._inprot_rtcm3
        )
        self._lbl_outprot = Label(self, text="Output")
        self._chk_outprot_nmea = Checkbutton(
            self, text="NMEA", variable=self._outprot_nmea
        )
        self._chk_outprot_ubx = Checkbutton(
            self, text="UBX", variable=self._outprot_ubx
        )
        self._chk_outprot_rtcm3 = Checkbutton(
            self, text="RTCM3", variable=self._outprot_rtcm3
        )
        self._lbl_send_command = Label(self, image=self._img_pending)
        self._btn_send_command = Button(
            self,
            image=self._img_send,
            width=50,
            command=self._on_send_port,
            font=self.__app.font_md,
        )

    def _do_layout(self):
        """
        Layout widgets.
        """

        self._lbl_cfg_port.grid(column=0, row=0, columnspan=6, padx=3, sticky=(W, E))
        self._lbl_ubx_portid.grid(
            column=0, row=1, columnspan=1, rowspan=2, padx=3, sticky=(W)
        )
        self._spn_ubx_portid.grid(column=1, row=1, columnspan=1, rowspan=2, sticky=(W))
        self._lbl_ubx_baudrate.grid(
            column=2, row=1, columnspan=1, rowspan=2, padx=3, sticky=(W)
        )
        self._spn_ubx_baudrate.grid(
            column=3, row=1, columnspan=2, rowspan=2, sticky=(W)
        )
        self._lbl_inprot.grid(column=0, row=3, padx=3, sticky=(W))
        self._chk_inprot_nmea.grid(column=1, row=3, sticky=(W))
        self._chk_inprot_ubx.grid(column=2, row=3, sticky=(W))
        self._chk_inprot_rtcm2.grid(column=3, row=3, sticky=(W))
        self._chk_inprot_rtcm3.grid(column=4, row=3, sticky=(W))
        self._lbl_outprot.grid(column=0, row=4, padx=3, sticky=(W))
        self._chk_outprot_nmea.grid(column=1, row=4, sticky=(W))
        self._chk_outprot_ubx.grid(column=2, row=4, sticky=(W))
        self._chk_outprot_rtcm3.grid(column=3, row=4, sticky=(W))
        self._btn_send_command.grid(
            column=4, row=1, rowspan=2, ipadx=3, ipady=3, sticky=(E)
        )
        self._lbl_send_command.grid(
            column=5, row=1, rowspan=2, ipadx=3, ipady=3, sticky=(E)
        )

        (cols, rows) = self.grid_size()
        for i in range(cols):
            self.grid_columnconfigure(i, weight=1)
        for i in range(rows):
            self.grid_rowconfigure(i, weight=1)
        self.option_add("*Font", self.__app.font_sm)

    def reset(self):
        """
        Reset panel to initial settings
        """

        self._do_poll_prt()

    def update_status(self, cfgtype, **kwargs):
        """
        Update pending confirmation status.
        """

        if cfgtype == "CFG-PRT":
            self._baudrate.set(str(kwargs.get("baudrate", 0)))
            self._inprot = kwargs.get("inprot", b"\x00\x00")
            self._outprot = kwargs.get("outprot", b"\x00\x00")
            inprot = UBXMessage.bytes2val(self._inprot, "U002")
            self._inprot_ubx.set(inprot >> 0 & 1)
            self._inprot_nmea.set(inprot >> 1 & 1)
            self._inprot_rtcm2.set(inprot >> 2 & 1)
            self._inprot_rtcm3.set(inprot >> 5 & 1)
            outprot = UBXMessage.bytes2val(self._outprot, "U002")
            self._outprot_ubx.set(outprot >> 0 & 1)
            self._outprot_nmea.set(outprot >> 1 & 1)
            self._outprot_rtcm3.set(outprot >> 5 & 1)
            self._lbl_send_command.config(image=self._img_confirmed)
            self.__container.set_status("CFG-PRT GET message received", "green")
        elif cfgtype == "ACK-NAK":
            self.__container.set_status("CFG-PRT POLL message rejected", "red")
            self._lbl_send_command.config(image=self._img_warn)

    def _on_select_portid(self):
        """
        Handle portid selection.
        """

        self._do_poll_prt()

    def _on_send_port(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Handle Send port config button press.
        """

        port = int(self._portid.get()[0:1])
        portID = UBXMessage.val2bytes(port, "U001")
        reserved0 = b"\x00"
        reserved4 = b"\x00\00"
        reserved5 = b"\x00\00"
        txReady = b"\x00\x00"
        if port == 0:  # I2C
            mode = b"\x84\x00\x00\x00"
        elif port == 1:  # UART1
            mode = b"\xc0\x08\x00\x00"
        elif port == 2:  # UART2
            mode = b"\xc0\x08\x00\x00"
        else:
            mode = b"\x00\x00\x00\x00"
        baudRate = UBXMessage.val2bytes(self._baudrate.get(), "U004")
        inprot = (
            self._inprot_ubx.get()
            + (self._inprot_nmea.get() << 1)
            + (self._inprot_rtcm2.get() << 2)
            + (self._inprot_rtcm3.get() << 5)
        )
        inProtoMask = UBXMessage.val2bytes(inprot, "U002")
        outprot = (
            self._outprot_ubx.get()
            + (self._outprot_nmea.get() << 1)
            + (self._outprot_rtcm3.get() << 5)
        )
        outProtoMask = UBXMessage.val2bytes(outprot, "U002")
        payload = (
            portID
            + reserved0
            + txReady
            + mode
            + baudRate
            + inProtoMask
            + outProtoMask
            + reserved4
            + reserved5
        )
        msg = UBXMessage("CFG", "CFG-PRT", SET, payload=payload)
        self.__app.serial_handler.serial_write(msg.serialize())
        self._lbl_send_command.config(image=self._img_pending)
        self.__container.set_status("CFG-PRT SET message sent", "blue")
        self.__container.set_pending(UBX_CFGPRT, ("ACK-ACK", "ACK-NAK"))

        self._do_poll_prt()

    def _do_poll_prt(self):
        """
        Poll PRT message configuration.
        """

        portID = int(self._portid.get()[0:1])
        msg = UBXMessage("CFG", "CFG-PRT", POLL, portID=portID)
        self.__app.serial_handler.serial_write(msg.serialize())
        self._lbl_send_command.config(image=self._img_pending)
        self.__container.set_status("CFG-PRT POLL message sent", "blue")
        self.__container.set_pending(UBX_CFGPRT, ("CFG-PRT", "ACK-NAK"))
