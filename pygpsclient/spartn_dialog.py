"""
SPARTN configuration dialog

This is the pop-up dialog containing the various
SPARTN configuration functions.

Created on 26 Jan 2023

:author: semuadmin
:copyright: SEMU Consulting © 2023
:license: BSD 3-Clause
"""
# pylint: disable=invalid-name, too-many-locals, too-many-instance-attributes

from datetime import datetime, timedelta
from tkinter import (
    ttk,
    Toplevel,
    Frame,
    Button,
    Checkbutton,
    Radiobutton,
    Label,
    Entry,
    StringVar,
    IntVar,
    N,
    S,
    E,
    W,
    NORMAL,
)
from PIL import ImageTk, Image
from pyubx2 import UBXMessage, val2bytes, SET, POLL, U1, U2, U4, TXN_NONE, SET_LAYER_RAM
from pygpsclient.globals import (
    ICON_EXIT,
    ICON_SEND,
    ICON_CONFIRMED,
    ICON_PENDING,
    ICON_WARNING,
    ENTCOL,
    POPUP_TRANSIENT,
    CONNECTED,
)
from pygpsclient.strings import (
    DLGSPARTNCONFIG,
    LBLSPTNCURR,
    LBLSPTNNEXT,
    LBLSPTNKEY,
    LBLSPTNDAT,
    LBLSPTNUPLOAD,
    LBLSPTNFP,
    LBLSPTNNMEA,
    NOTCONN,
    NULLSEND,
    CONFIGOK,
    CONFIGBAD,
)
from pygpsclient.helpers import (
    valid_entry,
    get_gpswnotow,
    VALHEX,
    VALDMY,
    VALLEN,
)

SPARTN_KEYLEN = 16
RESERVED0 = b"\x00\x00"
RESERVED1 = b"\x00"
RXMMSG = "RXM-SPARTN-KEY"
CFGMSG = "CFG-VALSET"
INPORTS = ("I2C", "UART1", "UART2", "USB", "SPI")


class SPARTNConfigDialog(Toplevel):
    """,
    SPARTNConfigDialog class.
    """

    def __init__(self, app, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Constructor.

        :param Frame app: reference to main tkinter application
        :param args: optional args to pass to parent class (not currently used)
        :param kwargs: optional kwargs to pass to parent class (not currently used)
        """

        self.__app = app  # Reference to main application class
        self.__master = self.__app.get_master()  # Reference to root class (Tk)
        Toplevel.__init__(self, app)
        if POPUP_TRANSIENT:
            self.transient(self.__app)
        self.resizable(False, False)
        self.title(DLGSPARTNCONFIG)  # pylint: disable=E1102
        self.protocol("WM_DELETE_WINDOW", self.on_exit)
        self._img_pending = ImageTk.PhotoImage(Image.open(ICON_PENDING))
        self._img_confirmed = ImageTk.PhotoImage(Image.open(ICON_CONFIRMED))
        self._img_warn = ImageTk.PhotoImage(Image.open(ICON_WARNING))
        self._img_exit = ImageTk.PhotoImage(Image.open(ICON_EXIT))
        self._img_send = ImageTk.PhotoImage(Image.open(ICON_SEND))
        self._status = StringVar()
        self._spartn_source = IntVar()
        self._status_cfgmsg = StringVar()
        self._spartn_key1 = StringVar()
        self._spartn_valdate1 = StringVar()
        self._spartn_key2 = StringVar()
        self._spartn_valdate2 = StringVar()
        self._upload_keys = IntVar()
        self._send_f9p_config = IntVar()
        self._disable_nmea = IntVar()
        self._ports = INPORTS

        self._body()
        self._do_layout()
        self._reset()

    def _body(self):
        """
        Set up frame and widgets.
        """
        # pylint: disable=unnecessary-lambda

        self._frm_container = Frame(self, borderwidth=2, relief="groove")
        self._frm_status = Frame(self._frm_container, borderwidth=2, relief="groove")
        self._lbl_status = Label(
            self._frm_status, textvariable=self._status, anchor="w"
        )
        self._btn_exit = Button(
            self._frm_status,
            image=self._img_exit,
            width=55,
            fg="red",
            command=self.on_exit,
            font=self.__app.font_md,
        )

        # SPARTN configuration options
        self._lbl_curr = Label(self._frm_container, text=LBLSPTNCURR)
        self._lbl_key1 = Label(self._frm_container, text=LBLSPTNKEY)
        self._ent_key1 = Entry(
            self._frm_container,
            textvariable=self._spartn_key1,
            bg=ENTCOL,
            state=NORMAL,
            relief="sunken",
            width=32,
        )
        self._lbl_valdate1 = Label(self._frm_container, text=LBLSPTNDAT)
        self._ent_valdate1 = Entry(
            self._frm_container,
            textvariable=self._spartn_valdate1,
            bg=ENTCOL,
            state=NORMAL,
            relief="sunken",
            width=8,
        )
        self._lbl_next = Label(self._frm_container, text=LBLSPTNNEXT)
        self._lbl_key2 = Label(self._frm_container, text=LBLSPTNKEY)
        self._ent_key2 = Entry(
            self._frm_container,
            textvariable=self._spartn_key2,
            bg=ENTCOL,
            state=NORMAL,
            relief="sunken",
            width=32,
        )
        self._lbl_valdate2 = Label(self._frm_container, text=LBLSPTNDAT)
        self._ent_valdate2 = Entry(
            self._frm_container,
            textvariable=self._spartn_valdate2,
            bg=ENTCOL,
            state=NORMAL,
            relief="sunken",
            width=8,
        )
        self._rad_source1 = Radiobutton(
            self._frm_container, text="L-Band", variable=self._spartn_source, value=1
        )
        self._rad_source0 = Radiobutton(
            self._frm_container, text="IP", variable=self._spartn_source, value=0
        )
        self._chk_upload_keys = Checkbutton(
            self._frm_container,
            text=LBLSPTNUPLOAD,
            variable=self._upload_keys,
        )
        self._chk_send_config = Checkbutton(
            self._frm_container,
            text=LBLSPTNFP,
            variable=self._send_f9p_config,
        )
        self._chk_disable_nmea = Checkbutton(
            self._frm_container, text=LBLSPTNNMEA, variable=self._disable_nmea
        )
        self._lbl_send_command = Label(self._frm_container, image=None)
        self._btn_send_command = Button(
            self._frm_container,
            image=self._img_send,
            width=50,
            fg="green",
            command=self._on_send_config,
            font=self.__app.font_md,
        )

    def _do_layout(self):
        """
        Position widgets in frame.
        """

        # top of grid
        col = 0
        row = 0
        self._frm_container.grid(
            column=col,
            row=row,
            columnspan=3,
            rowspan=6,
            padx=3,
            pady=3,
            ipadx=5,
            ipady=5,
            sticky=(N, S, W, E),
        )

        # body of grid
        self._lbl_curr.grid(column=0, row=0, columnspan=3, padx=3, pady=2, sticky=W)
        self._lbl_key1.grid(column=0, row=1, padx=3, pady=2, sticky=W)
        self._ent_key1.grid(column=1, row=1, columnspan=2, padx=3, pady=2, sticky=W)
        self._lbl_valdate1.grid(column=0, row=2, padx=3, pady=2, sticky=W)
        self._ent_valdate1.grid(column=1, row=2, columnspan=2, padx=3, pady=2, sticky=W)
        ttk.Separator(self._frm_container).grid(
            column=0, row=3, columnspan=3, padx=2, pady=3, sticky=(W, E)
        )
        self._lbl_next.grid(column=0, row=4, columnspan=3, padx=3, pady=2, sticky=W)
        self._lbl_key2.grid(column=0, row=5, padx=3, pady=2, sticky=W)
        self._ent_key2.grid(column=1, row=5, columnspan=2, padx=2, pady=2, sticky=W)
        self._lbl_valdate2.grid(column=0, row=6, padx=3, pady=2, sticky=W)
        self._ent_valdate2.grid(column=1, row=6, columnspan=2, padx=3, pady=2, sticky=W)
        ttk.Separator(self._frm_container).grid(
            column=0, row=7, columnspan=3, padx=2, pady=3, sticky=(W, E)
        )
        self._rad_source1.grid(column=0, row=8, padx=3, pady=2, sticky=W)
        self._rad_source0.grid(column=1, row=8, padx=3, pady=2, sticky=W)
        self._chk_upload_keys.grid(
            column=0, row=9, columnspan=2, padx=3, pady=2, sticky=W
        )
        self._chk_send_config.grid(
            column=0, row=10, columnspan=2, padx=3, pady=2, sticky=W
        )
        self._chk_disable_nmea.grid(
            column=0, columnspan=2, row=11, padx=3, pady=2, sticky=W
        )
        self._btn_send_command.grid(
            column=1, row=8, rowspan=4, padx=3, pady=2, sticky=(E)
        )
        self._lbl_send_command.grid(
            column=2, row=8, rowspan=4, padx=3, pady=2, sticky=W
        )

        # bottom of grid
        row = 12
        col = 0
        (colsp, rowsp) = self._frm_container.grid_size()
        self._frm_status.grid(column=col, row=row, columnspan=colsp, sticky=(W, E))
        self._lbl_status.grid(
            column=0, row=0, columnspan=colsp - 1, ipadx=3, ipady=3, sticky=(W, E)
        )
        self._btn_exit.grid(column=colsp - 1, row=0, ipadx=3, ipady=3, sticky=(E))

        for frm in (self._frm_container, self._frm_status):
            for i in range(colsp):
                frm.grid_columnconfigure(i, weight=1)
            for i in range(rowsp):
                frm.grid_rowconfigure(i, weight=1)

        self._frm_container.option_add("*Font", self.__app.font_sm)
        self._frm_status.option_add("*Font", self.__app.font_sm)

    def _reset(self):
        """
        Reset configuration widgets.
        """

        curr = datetime.now()
        self._set_date(self._spartn_valdate1, curr)
        self._set_date(self._spartn_valdate2, curr + timedelta(weeks=4))
        self._spartn_source.set(1)
        self._upload_keys.set(1)
        self._send_f9p_config.set(1)
        self._disable_nmea.set(0)
        self.set_status("", "blue")

    def set_status(self, message: str, color: str = "blue"):
        """
        Set status message.

        :param str message: message to be displayed
        :param str color: rgb color of text (blue)
        """

        message = (message[:50] + "..") if len(message) > 50 else message
        self._lbl_status.config(fg=color)
        self._status.set(" " + message)

    def on_exit(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Handle Exit button press.
        """

        # self.__master.update_idletasks()
        self.__app.stop_spartnconfig_thread()
        self.destroy()

    def _valid_settings(self) -> bool:
        """
        Validate settings.

        :return: valid True/False
        :rtype: bool
        """

        valid = True
        # key must be valid hexadecimal and 16 bytes (32 chars) in length
        valid = (
            valid
            & valid_entry(self._ent_key1, VALHEX)
            & valid_entry(self._ent_key1, VALLEN, SPARTN_KEYLEN * 2, SPARTN_KEYLEN * 2)
        )
        # from date must be valid date in format YYYYMMDD
        valid = valid & valid_entry(self._ent_valdate1, VALDMY)
        valid = (
            valid
            & valid_entry(self._ent_key2, VALHEX)
            & valid_entry(self._ent_key2, VALLEN, SPARTN_KEYLEN * 2, SPARTN_KEYLEN * 2)
        )
        valid = valid & valid_entry(self._ent_valdate2, VALDMY)

        if not valid:
            self.set_status("ERROR - invalid settings", "red")

        return valid

    def _format_rxmspartn(self) -> UBXMessage:
        """
        Format UBX RXM-SPARTN-KEY message.
        """

        version = val2bytes(1, U1)
        numKeys = val2bytes(2, U1)
        key1 = bytes.fromhex(self._spartn_key1.get())
        keylen1 = val2bytes(len(key1), U1)
        wno1, tow1 = get_gpswnotow(self._get_date(self._spartn_valdate1))
        wno1b = val2bytes(wno1, U2)
        tow1b = val2bytes(tow1, U4)
        key2 = bytes.fromhex(self._spartn_key1.get())
        keylen2 = val2bytes(len(key2), U1)
        wno2, tow2 = get_gpswnotow(self._get_date(self._spartn_valdate2))
        wno2b = val2bytes(wno2, U2)
        tow2b = val2bytes(tow2, U4)

        payload = (
            version
            + numKeys
            + RESERVED0
            + RESERVED1
            + keylen1
            + wno1b
            + tow1b
            + RESERVED1
            + keylen2
            + wno2b
            + tow2b
            + key1
            + key2
        )
        msg = UBXMessage("RXM", RXMMSG, SET, payload=payload)
        return msg

    def _format_cfgvalset(self) -> UBXMessage:
        """
        Format UBX CFG-VALSET message to configure receiver.
        """

        # select SPARTN source (L-band or IP)
        cfgdata = [
            ("CFG_SPARTN_USE_SOURCE", self._spartn_source.get()),
        ]
        # enable SPARTN and UBX on selected ports
        for port in self._ports:
            cfgdata.append((f"CFG_{port}INPROT_UBX", 1))
            cfgdata.append((f"CFG_{port}INPROT_RTCM3X", 1))
            cfgdata.append((f"CFG_{port}INPROT_SPARTN", 1))
            cfgdata.append((f"CFG_MSGOUT_UBX_RXM_COR_{port}", 1))

            # if NMEA disabled, remove it from out ports and enable
            # a couple of UBX NAV messages instead
            if self._disable_nmea.get():
                cfgdata.append((f"CFG_{port}OUTPROT_NMEA", 0))
                cfgdata.append((f"CFG_MSGOUT_UBX_NAV_PVT_{port}", 1))
                cfgdata.append((f"CFG_MSGOUT_UBX_NAV_SAT_{port}", 4))
            else:
                cfgdata.append((f"CFG_{port}OUTPROT_NMEA", 1))
                cfgdata.append((f"CFG_MSGOUT_UBX_NAV_PVT_{port}", 0))
                cfgdata.append((f"CFG_MSGOUT_UBX_NAV_SAT_{port}", 0))

        msg = UBXMessage.config_set(SET_LAYER_RAM, TXN_NONE, cfgdata)
        return msg

    def _on_send_config(self):
        """
        Send config to receiver.
        """

        if not self._valid_settings():
            return

        if self.__app.conn_status != CONNECTED:
            self.set_status(NOTCONN, "red")
            # return

        if self._send_f9p_config.get():
            msgc = "config"
            msg = self._format_cfgvalset()
            self._send_command(msg)
        else:
            msgc = ""
        if self._upload_keys.get():
            msgk = "keys"
            msg = self._format_rxmspartn()
            self._send_command(msg)
            # poll RXM-SPARTN-KEY to check keys have loaded
            msg = UBXMessage("RXM", RXMMSG, POLL)
            self._send_command(msg)
        else:
            msgk = ""
        if msgk == "" and msgc == "":
            self.set_status(NULLSEND, "red")
            return
        if msgk != "" and msgc != "":
            msga = " and "
        else:
            msga = ""
        self.set_status(f"{(msgk + msga + msgc).capitalize()} uploaded", "green")
        self._lbl_send_command.config(image=self._img_pending)

    def _send_command(self, msg: UBXMessage):
        """
        Send command to receiver.
        """

        self.__app.stream_handler.serial_write(msg.serialize())

    def update_status(self, msg: UBXMessage):
        """
        Update pending confirmation status.

        :param UBXMessage msg: UBX config message
        """

        if msg.identity == RXMMSG:
            if msg.numKeys == 2:  # check both keys have been uploaded
                self._lbl_send_command.config(image=self._img_confirmed)
                self.set_status(CONFIGOK.format(RXMMSG), "green")
            else:
                self._lbl_send_command.config(image=self._img_warn)
                self.set_status(CONFIGBAD.format(RXMMSG), "red")
        elif msg.identity == "ACK-ACK":
            self._lbl_send_command.config(image=self._img_confirmed)
            self.set_status(CONFIGOK.format(CFGMSG), "green")
        elif msg.identity == "ACK-NAK":
            self._lbl_send_command.config(image=self._img_warn)
            self.set_status(CONFIGBAD.format(CFGMSG), "red")

    def _set_date(self, val: StringVar, dat: datetime):
        """
        Set date string in entry field.
        """

        val.set(dat.strftime("%Y%m%d"))

    def _get_date(self, val: StringVar) -> datetime:
        """
        Get datetime from entry field.
        """

        dat = val.get()
        return datetime(int(dat[0:4]), int(dat[4:6]), int(dat[6:8]))
