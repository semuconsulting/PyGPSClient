"""
UBX Configuration frame for CFG-PRT commands

Created on 22 Dec 2020

:author: semuadmin
:copyright: SEMU Consulting © 2020
:license: BSD 3-Clause
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
    BPSRATES,
    READONLY,
    UBX_CFGPRT,
    CONNECTED,
)
from .strings import LBLCFGPRT


class UBX_PORT_Frame(Frame):
    """
    UBX Port and Protocol configuration command panel.
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
        self._bpsrate = IntVar()
        self._portid = StringVar()
        self._inprot = (1, 1, 0, 1)
        self._outprot = (1, 1, 0)
        self._inprot_nmea = IntVar()
        self._inprot_ubx = IntVar()
        self._inprot_rtcm2 = IntVar()
        self._inprot_rtcm3 = IntVar()
        self._outprot_nmea = IntVar()
        self._outprot_ubx = IntVar()
        self._outprot_rtcm3 = IntVar()

        self._body()
        self._do_layout()
        self._attach_events()

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
        self._lbl_ubx_bpsrate = Label(self, text="Rate bps")
        self._spn_ubx_bpsrate = Spinbox(
            self,
            values=(BPSRATES),
            width=6,
            state=READONLY,
            readonlybackground=ENTCOL,
            wrap=True,
            textvariable=self._bpsrate,
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
        self._lbl_ubx_bpsrate.grid(
            column=2, row=1, columnspan=1, rowspan=2, padx=3, sticky=(W)
        )
        self._spn_ubx_bpsrate.grid(column=3, row=1, columnspan=2, rowspan=2, sticky=(W))
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

    def _attach_events(self):
        """
        Bind events to widget.
        """

        # click mouse button to refresh information
        self.bind("<Button>", self._do_poll_prt)

    def reset(self):
        """
        Reset panel to initial settings
        """

        if self.__app.conn_status == CONNECTED:
            self._do_poll_prt()

    def update_status(self, msg: UBXMessage):
        """
        Update pending confirmation status.

        :param UBXMessage msg: UBX config message
        """

        if msg.identity == "CFG-PRT":
            self._bpsrate.set(msg.baudRate)
            self._inprot_ubx.set(msg.inUBX)
            self._inprot_nmea.set(msg.inNMEA)
            self._inprot_rtcm2.set(msg.inRTCM)
            self._inprot_rtcm3.set(msg.inRTCM3)
            self._outprot_ubx.set(msg.outUBX)
            self._outprot_nmea.set(msg.outNMEA)
            self._outprot_rtcm3.set(msg.outRTCM3)
            self._lbl_send_command.config(image=self._img_confirmed)
            self.__container.set_status("CFG-PRT GET message received", "green")

        elif msg.identity == "ACK-NAK":
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

        portID = int(self._portid.get()[0:1])
        baudRate = int(self._bpsrate.get())
        inUBX = self._inprot_ubx.get()
        inNMEA = self._inprot_nmea.get()
        inRTCM = self._inprot_rtcm2.get()
        inRTCM3 = self._inprot_rtcm3.get()
        outUBX = self._outprot_ubx.get()
        outNMEA = self._outprot_nmea.get()
        outRTCM3 = self._outprot_rtcm3.get()
        msg = UBXMessage(
            "CFG",
            "CFG-PRT",
            SET,
            portID=portID,
            charLen=3,  # 8 data bits
            parity=4,  # none
            nStopBits=0,  # 1 stop bit
            baudRate=baudRate,
            inUBX=inUBX,
            inNMEA=inNMEA,
            inRTCM=inRTCM,
            inRTCM3=inRTCM3,
            outUBX=outUBX,
            outNMEA=outNMEA,
            outRTCM3=outRTCM3,
        )
        self.__app.stream_handler.serial_write(msg.serialize())
        self._lbl_send_command.config(image=self._img_pending)
        self.__container.set_status("CFG-PRT SET message sent", "blue")
        self.__container.set_pending(UBX_CFGPRT, ("ACK-ACK", "ACK-NAK"))

        self._do_poll_prt()

    def _do_poll_prt(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Poll PRT message configuration.
        """

        portID = int(self._portid.get()[0:1])
        msg = UBXMessage("CFG", "CFG-PRT", POLL, portID=portID)
        self.__app.stream_handler.serial_write(msg.serialize())
        self._lbl_send_command.config(image=self._img_pending)
        self.__container.set_status("CFG-PRT POLL message sent", "blue")
        for msgid in ("CFG-PRT", "ACK-NAK"):
            self.__container.set_pending(msgid, UBX_CFGPRT)
