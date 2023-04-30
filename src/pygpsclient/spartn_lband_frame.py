"""
SPARTN L-Band Correction receiver configuration dialog

Created on 26 Jan 2023

:author: semuadmin
:copyright: SEMU Consulting © 2023
:license: BSD 3-Clause
"""

from tkinter import (
    DISABLED,
    NORMAL,
    Button,
    Checkbutton,
    E,
    Entry,
    Frame,
    IntVar,
    Label,
    N,
    S,
    Spinbox,
    StringVar,
    W,
    ttk,
)

from PIL import Image, ImageTk
from pyubx2 import POLL_LAYER_RAM, SET, SET_LAYER_RAM, TXN_NONE, UBXMessage

from pygpsclient.globals import (
    BPSRATES,
    CONNECTED_SPARTNIP,
    CONNECTED_SPARTNLB,
    DISCONNECTED,
    ICON_BLANK,
    ICON_CONFIRMED,
    ICON_DISCONN,
    ICON_EXIT,
    ICON_PENDING,
    ICON_SEND,
    ICON_SERIAL,
    ICON_SOCKET,
    ICON_WARNING,
    KNOWNGPS,
    MSGMODES,
    NOPORTS,
    READONLY,
    SPARTN_EOF_EVENT,
    SPARTN_EVENT,
    SPARTN_LBAND,
    TIMEOUTS,
)
from pygpsclient.helpers import VALINT, valid_entry
from pygpsclient.serialconfig_frame import SerialConfigFrame
from pygpsclient.strings import CONFIGBAD, CONFIGOK, DLGSPARTNWARN, LBLSPARTNLB

U2MAX = 2e16 - 1
U8MAX = 2e64 - 1
BAUDRATE = 38400
SPARTN_KEYLEN = 16
RESERVED0 = b"\x00\x00"
RESERVED1 = b"\x00"
CFGSET = "CFG-VALGET/SET"
CFGPOLL = "CFG-VALGET"
INPORTS = ("I2C", "UART1", "UART2", "USB", "SPI")
PASSTHRU = "Passthrough"
PMP_DATARATES = {
    "B600": 600,
    "B1200": 1200,
    "B2400": 2400,
    "B4800": 4800,
}
SPARTN_DEFAULT = {
    "freq": 1539812500,
    "schwin": 2200,
    "usesid": 1,
    "sid": 50821,
    "drat": PMP_DATARATES["B2400"],
    "descrm": 1,
    "prescrm": 1,
    "descrminit": 23560,
    "unqword": 16238547128276412563,
}


class SPARTNLBANDDialog(Frame):
    """,
    SPARTNConfigDialog class.
    """

    def __init__(
        self, app, container, *args, **kwargs
    ):  # pylint: disable=unused-argument
        """
        Constructor.

        :param Frame app: reference to main tkinter application
        :param Frame container: reference to container frame
        :param args: optional args to pass to parent class (not currently used)
        :param kwargs: optional kwargs to pass to parent class (not currently used)
        """

        self.__app = app  # Reference to main application class
        self.__master = self.__app.appmaster  # Reference to root class (Tk)
        self.__container = container  # container frame

        Frame.__init__(self, self.__container.container, *args, **kwargs)

        self._img_blank = ImageTk.PhotoImage(Image.open(ICON_BLANK))
        self._img_pending = ImageTk.PhotoImage(Image.open(ICON_PENDING))
        self._img_confirmed = ImageTk.PhotoImage(Image.open(ICON_CONFIRMED))
        self._img_warn = ImageTk.PhotoImage(Image.open(ICON_WARNING))
        self._img_exit = ImageTk.PhotoImage(Image.open(ICON_EXIT))
        self._img_send = ImageTk.PhotoImage(Image.open(ICON_SEND))
        self._img_serial = ImageTk.PhotoImage(Image.open(ICON_SERIAL))
        self._img_socket = ImageTk.PhotoImage(Image.open(ICON_SOCKET))
        self._img_disconn = ImageTk.PhotoImage(Image.open(ICON_DISCONN))
        self._status = StringVar()
        self._spartn_freq = StringVar()
        self._spartn_schwin = StringVar()
        self._spartn_usesid = IntVar()
        self._spartn_sid = StringVar()
        self._spartn_drat = StringVar()
        self._spartn_descrm = IntVar()
        self._spartn_prescrm = IntVar()
        self._spartn_descrminit = StringVar()
        self._spartn_unqword = StringVar()
        self._spartn_outport = StringVar()
        self._enabledbg = IntVar()
        self._saveconfig = IntVar()
        self._ports = INPORTS
        self._settings = {}
        self._connected = DISCONNECTED

        self._body()
        self._do_layout()
        self._reset()

    def _body(self):
        """
        Set up frame and widgets.
        """
        # pylint: disable=unnecessary-lambda
        self._lbl_corrlband = Label(self, text=LBLSPARTNLB)
        # Correction receiver serial port configuration panel
        userport = self.__app.app_config.get("spartnport", "")
        self._frm_spartn_serial = SerialConfigFrame(
            self,
            preselect=KNOWNGPS,
            timeouts=TIMEOUTS,
            bpsrates=BPSRATES,
            msgmodes=list(MSGMODES.keys()),
            userport=userport,  # user-defined serial port
        )
        self._lbl_freq = Label(self, text="L-Band Frequency (Hz)")
        self._ent_freq = Entry(
            self,
            textvariable=self._spartn_freq,
            state=NORMAL,
            relief="sunken",
            width=10,
        )
        self._chk_enabledbg = Checkbutton(
            self,
            text="Enable Debug?",
            variable=self._enabledbg,
        )
        self._lbl_schwin = Label(self, text="Search window")
        self._ent_schwin = Entry(
            self,
            textvariable=self._spartn_schwin,
            state=NORMAL,
            relief="sunken",
            width=10,
        )
        self._chk_saveconfig = Checkbutton(
            self,
            text="Save Config?",
            variable=self._saveconfig,
        )
        self._chk_usesid = Checkbutton(
            self,
            text="Use Service ID?",
            variable=self._spartn_usesid,
        )
        self._lbl_sid = Label(self, text="Service ID")
        self._ent_sid = Entry(
            self,
            textvariable=self._spartn_sid,
            state=NORMAL,
            relief="sunken",
            width=10,
        )
        self._lbl_drat = Label(self, text="Data Rate")
        self._spn_drat = Spinbox(
            self,
            values=list(PMP_DATARATES.values()),
            textvariable=self._spartn_drat,
            state=READONLY,
            width=5,
            wrap=True,
        )
        self._chk_descrm = Checkbutton(
            self,
            text="Use Descrambler?",
            variable=self._spartn_descrm,
        )
        self._chk_prescram = Checkbutton(
            self,
            text="Use Prescrambling?",
            variable=self._spartn_prescrm,
        )
        self._lbl_descraminit = Label(self, text="Descrambler Init")
        self._ent_descraminit = Entry(
            self,
            textvariable=self._spartn_descrminit,
            state=NORMAL,
            relief="sunken",
            width=10,
        )
        self._lbl_unqword = Label(self, text="Unique Word")
        self._ent_unqword = Entry(
            self,
            textvariable=self._spartn_unqword,
            state=NORMAL,
            relief="sunken",
            width=20,
        )
        self._lbl_outport = Label(self, text="Output Port")
        self._spn_outport = Spinbox(
            self,
            values=INPORTS + (PASSTHRU,),
            textvariable=self._spartn_outport,
            state=READONLY,
            width=10,
            wrap=True,
        )
        self._btn_connect = Button(
            self,
            width=45,
            image=self._img_serial,
            command=lambda: self.on_connect(),
        )
        self._btn_disconnect = Button(
            self,
            width=45,
            image=self._img_disconn,
            command=lambda: self.on_disconnect(),
            state=DISABLED,
        )
        self._lbl_send = Label(self, image=self._img_blank)
        self._btn_send = Button(
            self,
            image=self._img_send,
            width=45,
            command=self._on_send_config,
        )

    def _do_layout(self):
        """
        Position widgets in frame.
        """

        self._lbl_corrlband.grid(
            column=0, row=0, columnspan=4, padx=3, pady=2, sticky=W
        )
        self._frm_spartn_serial.grid(
            column=0, row=1, columnspan=4, padx=3, pady=2, sticky=(N, S, W, E)
        )
        ttk.Separator(self).grid(
            column=0, row=2, columnspan=4, padx=2, pady=3, sticky=(W, E)
        )
        self._lbl_freq.grid(column=0, row=3, sticky=W)
        self._ent_freq.grid(column=1, row=3, sticky=W)
        self._chk_enabledbg.grid(column=2, row=3, columnspan=2, sticky=W)
        self._lbl_schwin.grid(column=0, row=4, sticky=W)
        self._ent_schwin.grid(column=1, row=4, sticky=W)
        self._chk_saveconfig.grid(column=2, row=4, sticky=W)
        self._chk_usesid.grid(column=0, row=5, sticky=W)
        self._chk_descrm.grid(column=1, row=5, sticky=W)
        self._chk_prescram.grid(column=2, row=5, columnspan=2, sticky=W)
        self._lbl_sid.grid(column=0, row=6, sticky=W)
        self._ent_sid.grid(column=1, row=6, columnspan=3, sticky=W)
        self._lbl_drat.grid(column=0, row=7, sticky=W)
        self._spn_drat.grid(column=1, row=7, columnspan=3, sticky=W)
        self._lbl_descraminit.grid(column=0, row=8, sticky=W)
        self._ent_descraminit.grid(column=1, row=8, columnspan=3, sticky=W)
        self._lbl_unqword.grid(column=0, row=9, sticky=W)
        self._ent_unqword.grid(column=1, row=9, columnspan=3, sticky=W)
        self._lbl_outport.grid(column=0, row=10, sticky=W)
        self._spn_outport.grid(column=1, row=10, columnspan=3, sticky=W)
        ttk.Separator(self).grid(
            column=0, row=11, columnspan=4, padx=2, pady=3, sticky=(W, E)
        )
        self._btn_connect.grid(column=0, row=12, padx=3, pady=2, sticky=W)
        self._btn_disconnect.grid(column=1, row=12, padx=3, pady=2, sticky=W)
        self._btn_send.grid(column=2, row=12, padx=3, pady=2, sticky=W)
        self._lbl_send.grid(column=3, row=12, padx=3, pady=2, sticky=W)

    def _reset(self):
        """
        Reset configuration widgets.
        """

        self._enabledbg.set(0)
        self._saveconfig.set(0)
        self._spartn_drat.set(PMP_DATARATES["B2400"])
        self._spartn_freq.set(SPARTN_DEFAULT["freq"])
        self._spartn_schwin.set(SPARTN_DEFAULT["schwin"])
        self._spartn_usesid.set(SPARTN_DEFAULT["usesid"])
        self._spartn_sid.set(SPARTN_DEFAULT["sid"])
        self._spartn_descrm.set(SPARTN_DEFAULT["descrm"])
        self._spartn_prescrm.set(SPARTN_DEFAULT["prescrm"])
        self._spartn_descrminit.set(SPARTN_DEFAULT["descrminit"])
        self._spartn_unqword.set(SPARTN_DEFAULT["unqword"])
        self._spartn_outport.set(PASSTHRU)
        self.__container.set_status("")
        if self.__app.rtk_conn_status == CONNECTED_SPARTNLB:
            self.set_controls(CONNECTED_SPARTNLB)
        else:
            self.set_controls(DISCONNECTED)

    def set_controls(self, status: int):
        """
        Enable or disable widgets depending on connection status.

        :param int status: connection status (0 = disconnected, 1 = connected)
        """

        stat = DISABLED if status == CONNECTED_SPARTNLB else NORMAL
        for wdg in (self._btn_connect,):
            wdg.config(state=stat)
        stat = NORMAL if status == CONNECTED_SPARTNLB else DISABLED
        for wdg in (
            self._ent_freq,
            self._ent_schwin,
            self._ent_sid,
            self._ent_unqword,
            self._ent_descraminit,
            self._chk_enabledbg,
            self._chk_saveconfig,
            self._chk_descrm,
            self._chk_prescram,
            self._chk_usesid,
            self._btn_disconnect,
            self._btn_send,
        ):
            wdg.config(state=stat)
        stat = READONLY if status == CONNECTED_SPARTNLB else DISABLED
        for wdg in (
            self._spn_drat,
            self._spn_outport,
        ):
            wdg.config(state=stat)

    def _valid_settings(self) -> bool:
        """
        Validate settings.

        :return: valid True/False
        :rtype: bool
        """

        valid = True
        valid = valid & valid_entry(
            self._ent_freq, VALINT, 1e9, 2e9
        )  # L-band 1GHz - 2GHz
        valid = valid & valid_entry(self._ent_schwin, VALINT, 0, U2MAX)  # U2
        valid = valid & valid_entry(self._ent_sid, VALINT, 0, U2MAX)  # U2
        valid = valid & valid_entry(self._ent_descraminit, VALINT, 0, U2MAX)  # U2
        valid = valid & valid_entry(self._ent_unqword, VALINT, 0, U8MAX)  # U8

        if not valid:
            self.__container.set_status("ERROR - invalid settings", "red")

        return valid

    def on_connect(self):
        """
        Connect to Correction receiver.
        """

        if self.__app.rtk_conn_status == CONNECTED_SPARTNIP:
            self.__container.set_status(
                DLGSPARTNWARN.format("IP", "L-Band"),
                "red",
            )
            return

        if self.serial_settings.status == NOPORTS:
            return

        # start serial stream thread
        self.__app.rtk_conn_status = CONNECTED_SPARTNLB
        self.__app.spartn_stream_handler.start_read_thread(self._get_settings())
        self.__container.set_status(
            f"Connected to {self.serial_settings.port}:{self.serial_settings.port_desc} "
            + f"@ {self.serial_settings.bpsrate}",
            "green",
        )
        self.set_controls(CONNECTED_SPARTNLB)

        self._poll_config()

    def on_disconnect(self, msg: str = ""):
        """
        Disconnect from L-Band Correction receiver.

        :param str msg: optional disconnection message
        """

        msg += "Disconnected"
        if self.__app.rtk_conn_status == CONNECTED_SPARTNLB:
            if self.__app.spartn_stream_handler is not None:
                self.__app.spartn_stream_handler.stop_read_thread()
                self.__app.rtk_conn_status = DISCONNECTED
                self.__container.set_status(
                    msg,
                    "red",
                )
            self.set_controls(DISCONNECTED)

    def _get_settings(self) -> dict:
        """
        Get settings dict.

        :return: dictionary of settings for stream handler
        :rtype: dict
        """

        return {
            "owner": self,
            "read_event": SPARTN_EVENT,
            "eof_event": SPARTN_EOF_EVENT,
            "inqueue": self.__app.spartn_inqueue,
            "outqueue": self.__app.spartn_outqueue,
            "socket_inqueue": self.__app.socket_inqueue,
            "socket_outqueue": self.__app.socket_outqueue,
            "serial_settings": self.serial_settings,
            "in_filepath": "",
        }

    def _format_cfgpoll(self) -> UBXMessage:
        """
        Format UBX CFG-VALGET message to poll Correction receiver
        configuration.
        """

        outport = self._spartn_outport.get()
        if outport == PASSTHRU:
            outport = "USB"

        cfgdata = [
            "CFG_PMP_CENTER_FREQUENCY",
            "CFG_PMP_SEARCH_WINDOW",
            "CFG_PMP_USE_SERVICE_ID",
            "CFG_PMP_SERVICE_ID",
            "CFG_PMP_DATA_RATE",
            "CFG_PMP_USE_DESCRAMBLER",
            "CFG_PMP_DESCRAMBLER_INIT",
            "CFG_PMP_USE_PRESCRAMBLING",
            "CFG_PMP_UNIQUE_WORD",
        ]
        for port in INPORTS:
            cfgdata.append(f"CFG_MSGOUT_UBX_RXM_PMP_{port}")
            cfgdata.append(f"CFG_{port}OUTPROT_UBX")
            if port in ("UART1", "UART2"):
                cfgdata.append(f"CFG_{port}_BAUDRATE")

        msg = UBXMessage.config_poll(POLL_LAYER_RAM, 0, cfgdata)
        return msg

    def _format_cfgcorr(self) -> UBXMessage:
        """
        Format UBX CFG-VALSET message to configure Correction receiver.
        Sets RCM-PMP and selection output port configuration.
        """

        outport = self._spartn_outport.get()
        if outport == PASSTHRU:
            outport = "USB"

        cfgdata = [
            ("CFG_PMP_CENTER_FREQUENCY", int(self._spartn_freq.get())),
            ("CFG_PMP_SEARCH_WINDOW", int(self._spartn_schwin.get())),
            ("CFG_PMP_USE_SERVICE_ID", int(self._spartn_usesid.get())),
            ("CFG_PMP_SERVICE_ID", int(self._spartn_sid.get())),
            ("CFG_PMP_DATA_RATE", int(self._spartn_drat.get())),
            ("CFG_PMP_USE_DESCRAMBLER", int(self._spartn_descrm.get())),
            ("CFG_PMP_DESCRAMBLER_INIT", int(self._spartn_descrminit.get())),
            ("CFG_PMP_USE_PRESCRAMBLING", int(self._spartn_prescrm.get())),
            ("CFG_PMP_UNIQUE_WORD", int(self._spartn_unqword.get())),
        ]
        for port in INPORTS:
            cfgdata.append((f"CFG_MSGOUT_UBX_RXM_PMP_{port}", 1))
            cfgdata.append((f"CFG_{port}OUTPROT_UBX", 1))
            if self._enabledbg.get():
                cfgdata.append((f"CFG_INFMSG_UBX_{port}", b"\x1f"))
            else:
                cfgdata.append((f"CFG_INFMSG_UBX_{port}", b"\x07"))
        if outport in ("UART1", "UART2"):
            cfgdata.append(f"CFG_{outport}_BAUDRATE", int(self.serial_settings.bpsrate))

        msg = UBXMessage.config_set(SET_LAYER_RAM, TXN_NONE, cfgdata)
        return msg

    def _format_cfgcfg(self) -> UBXMessage:
        """
        Format UBX CFG-CFG command to persist configuration
        to correction receiver's BBR / Flash / EEPROM memory.
        """

        msg = UBXMessage(
            "CFG",
            "CFG-CFG",
            SET,
            # clearMask=b"\x01\x00\x00\x00",
            saveMask=b"\x1f\x1f\x00\x00",
            # loadMask=b"\x01\x00\x00\x00",
            devBBR=1,
            devFlash=1,
            devEEPROM=1,
        )
        return msg

    def _on_send_config(self):
        """
        Send config to L-Band Correction receiver (e.g. D9S).
        """

        if not self._valid_settings():
            return

        msg = self._format_cfgcorr()
        self._send_command(msg)
        self.__container.set_status(f"{CFGSET} command sent", "green")
        self._lbl_send.config(image=self._img_pending)

        # save config to persistent memory
        if self._saveconfig.get():
            msg = self._format_cfgcfg()
            self._send_command(msg)

        self._poll_config()

    def _poll_config(self):
        """
        Poll receiver for current configuration.
        """

        msg = self._format_cfgpoll()
        self._send_command(msg)

        for msgid in (CFGPOLL, "ACK-ACK", "ACK-NAK"):
            self.__container.set_pending(msgid, SPARTN_LBAND)

    def _send_command(self, msg: UBXMessage):
        """
        Send command to L-Band Correction receiver.
        """

        self.__app.spartn_outqueue.put(msg.serialize())

    def update_status(self, msg: UBXMessage):
        """
        Update pending confirmation status.
        :param UBXMessage msg: UBX config message
        """

        if msg.identity == CFGPOLL:
            if hasattr(msg, "CFG_PMP_CENTER_FREQUENCY"):
                self._spartn_freq.set(msg.CFG_PMP_CENTER_FREQUENCY)
            if hasattr(msg, "CFG_PMP_SEARCH_WINDOW"):
                self._spartn_schwin.set(msg.CFG_PMP_SEARCH_WINDOW)
            if hasattr(msg, "CFG_PMP_USE_SERVICE_ID"):
                self._spartn_usesid.set(msg.CFG_PMP_USE_SERVICE_ID)
            if hasattr(msg, "CFG_PMP_SERVICE_ID"):
                self._spartn_sid.set(msg.CFG_PMP_SERVICE_ID)
            if hasattr(msg, "CFG_PMP_DATA_RATE"):
                self._spartn_drat.set(msg.CFG_PMP_DATA_RATE)
            if hasattr(msg, "CFG_PMP_USE_DESCRAMBLER"):
                self._spartn_descrm.set(msg.CFG_PMP_USE_DESCRAMBLER)
            if hasattr(msg, "CFG_PMP_DESCRAMBLER_INIT"):
                self._spartn_descrminit.set(msg.CFG_PMP_DESCRAMBLER_INIT)
            if hasattr(msg, "CFG_PMP_USE_PRESCRAMBLING"):
                self._spartn_prescrm.set(msg.CFG_PMP_USE_PRESCRAMBLING)
            if hasattr(msg, "CFG_PMP_UNIQUE_WORD"):
                self._spartn_unqword.set(msg.CFG_PMP_UNIQUE_WORD)
            self.__container.set_status(f"{CFGPOLL} received", "green")
            self._lbl_send.config(image=self._img_confirmed)
        elif msg.identity == "ACK-ACK":
            self._lbl_send.config(image=self._img_confirmed)
            self.__container.set_status(CONFIGOK.format(CFGSET), "green")
        elif msg.identity == "ACK-NAK":
            self._lbl_send.config(image=self._img_warn)
            self.__container.set_status(CONFIGBAD.format(CFGSET), "red")
        self.update_idletasks()

    # ============================================
    # FOLLOWING METHODS REQUIRED BY STREAM_HANDLER
    # ============================================

    @property
    def conn_status(self) -> int:
        """
        Getter for connection status
        (0 = disconnected, 1 = serial, 2 = socket, 4 = file).
        """

        return self.__app.rtk_conn_status

    @conn_status.setter
    def conn_status(self, status: int):
        """
        Setter for connection status.

        :param int status: 0 = disconnected, 1 = serial, 2 = socket, 4 = file.
        """

        self.__app.rtk_conn_status = status

    def set_status(self, msg: str, color: str = ""):
        """
        Set status message.

        :param str message: message to be displayed
        :param str color: rgb color of text (blue)
        """

        if color == "":
            self.__container.set_status(msg)
        else:
            self.__container.set_status(msg, color)

    def set_connection(self, msg: str, color: str = ""):
        """
        Set status message.

        :param str message: message to be displayed
        :param str color: rgb color of text (blue)
        """

        if color == "":
            self.__container.set_status(msg)
        else:
            self.__container.set_status(msg, color)

    @property
    def serial_settings(self) -> Frame:
        """
        Getter for common serial configuration panel

        :return: reference to serial form
        :rtype: Frame
        """

        return self._frm_spartn_serial
