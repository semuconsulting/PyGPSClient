"""
SPARTN configuration dialog

This is the pop-up dialog containing the various
SPARTN configuration functions.

This dialog maintains its own threaded serial
stream handler for incoming and outgoing Correction
receiver (D9S) data (RXM-PMP), and must remain open for
SPARTN passthrough to work.

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
    Spinbox,
    Label,
    Entry,
    StringVar,
    IntVar,
    N,
    S,
    E,
    W,
    NORMAL,
    DISABLED,
)
from queue import Queue
from PIL import ImageTk, Image
from pyubx2 import (
    UBXMessage,
    val2bytes,
    SET,
    POLL,
    U1,
    U2,
    U4,
    TXN_NONE,
    SET_LAYER_RAM,
    POLL_LAYER_RAM,
)
from pygpsclient.globals import (
    ICON_EXIT,
    ICON_SEND,
    ICON_CONFIRMED,
    ICON_PENDING,
    ICON_WARNING,
    ICON_CONN,
    ICON_DISCONN,
    ENTCOL,
    POPUP_TRANSIENT,
    CONNECTED,
    DISCONNECTED,
    NOPORTS,
    SPARTN_EU,
    SPARTN_US,
    SPARTN_FACTORY,
    SPARTN_DEFREG,
    SPARTN_LBAND,
    SPARTN_IP,
    SPARTN_DEFSRC,
    READONLY,
    BPSRATES,
    KNOWNGPS,
    MSGMODES,
    TIMEOUTS,
    SPARTN_EVENT,
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
from pygpsclient.serialconfig_frame import SerialConfigFrame
from pygpsclient.stream_handler import StreamHandler

BAUDRATE = 38400
SPARTN_KEYLEN = 16
RESERVED0 = b"\x00\x00"
RESERVED1 = b"\x00"
RXMMSG = "RXM-SPARTN-KEY"
CFGMSG = "CFG-VALSET"
INPORTS = ("I2C", "UART1", "UART2", "USB", "SPI")
PASSTHRU = "Passthrough"
PMP_DATARATES = {
    "B600": 600,
    "B1200": 1200,
    "B2400": 2400,
    "B4800": 4800,
}
SPARTN_PARMS = {
    SPARTN_FACTORY: {
        "freq": 1539812500,
        "schwin": 2200,
        "usesid": 1,
        "sid": 50821,
        "drat": PMP_DATARATES["B2400"],
        "descrm": 1,
        "prescrm": 1,
        "descrminit": 23560,
        "unqword": 16238547128276412563,
    },
    SPARTN_US: {
        "freq": 1556290000,
        "schwin": 2200,
        "usesid": 1,
        "sid": 50821,
        "drat": PMP_DATARATES["B2400"],
        "descrm": 1,
        "prescrm": 1,
        "descrminit": 26969,
        "unqword": 16238547128276412563,
    },
    # TODO  CHECK THESE DEFAULT VALUES
    SPARTN_EU: {
        "freq": 1545260000,
        "schwin": 2200,
        "usesid": 1,
        "sid": 50821,
        "drat": PMP_DATARATES["B2400"],
        "descrm": 1,
        "prescrm": 1,
        "descrminit": 26969,
        "unqword": 16238547128276412563,
    },
}


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
        self.__master = self.__app.appmaster  # Reference to root class (Tk)
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
        self._img_conn = ImageTk.PhotoImage(Image.open(ICON_CONN))
        self._img_disconn = ImageTk.PhotoImage(Image.open(ICON_DISCONN))
        self.spartn_stream_handler = StreamHandler(self)
        self._status = StringVar()
        self._spartn_source = IntVar()
        self._spartn_region = IntVar()
        self._status_cfgmsg = StringVar()
        self._spartn_key1 = StringVar()
        self._spartn_valdate1 = StringVar()
        self._spartn_key2 = StringVar()
        self._spartn_valdate2 = StringVar()
        self._upload_keys = IntVar()
        self._send_f9p_config = IntVar()
        self._disable_nmea = IntVar()
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
        self._ports = INPORTS

        self._body()
        self._do_layout()
        self._attach_events()
        self._reset()

    def _body(self):
        """
        Set up frame and widgets.
        """
        # pylint: disable=unnecessary-lambda

        self._frm_container = Frame(self)
        self._frm_gnss = Frame(self._frm_container, borderwidth=2, relief="groove")
        self._frm_corr = Frame(self._frm_container, borderwidth=2, relief="groove")
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

        # Correction receiver (D9S) configuration widgets
        self._lbl_corr = Label(
            self._frm_corr, text="CORRECTION RECEIVER CONFIGURATION (D9S)"
        )
        # Correction receiver serial port configuration panel
        self._frm_spartn_serial = SerialConfigFrame(
            self._frm_corr,
            preselect=KNOWNGPS,
            timeouts=TIMEOUTS,
            bpsrates=BPSRATES,
            msgmodes=list(MSGMODES.keys()),
            userport=self.__app.spartn_user_port,  # user-defined serial port
        )
        self._rad_default = Radiobutton(
            self._frm_corr,
            text="Default",
            variable=self._spartn_region,
            value=SPARTN_FACTORY,
        )
        self._rad_us = Radiobutton(
            self._frm_corr, text="USA", variable=self._spartn_region, value=SPARTN_US
        )
        self._rad_eu = Radiobutton(
            self._frm_corr,
            text="Europe",
            variable=self._spartn_region,
            value=SPARTN_EU,
        )
        self._lbl_freq = Label(self._frm_corr, text="L-Band Frequency (Hz)")
        self._ent_freq = Entry(
            self._frm_corr,
            textvariable=self._spartn_freq,
            bg=ENTCOL,
            state=NORMAL,
            relief="sunken",
            width=10,
        )
        self._lbl_schwin = Label(self._frm_corr, text="Search window")
        self._ent_schwin = Entry(
            self._frm_corr,
            textvariable=self._spartn_schwin,
            bg=ENTCOL,
            state=NORMAL,
            relief="sunken",
            width=10,
        )
        self._chk_usesid = Checkbutton(
            self._frm_corr,
            text="Use Service ID?",
            variable=self._spartn_usesid,
        )
        self._lbl_sid = Label(self._frm_corr, text="Service ID")
        self._ent_sid = Entry(
            self._frm_corr,
            textvariable=self._spartn_sid,
            bg=ENTCOL,
            state=NORMAL,
            relief="sunken",
            width=10,
        )
        self._lbl_drat = Label(self._frm_corr, text="Data Rate")
        self._spn_drat = Spinbox(
            self._frm_corr,
            values=list(PMP_DATARATES.values()),
            textvariable=self._spartn_drat,
            readonlybackground=ENTCOL,
            state=READONLY,
            width=5,
            wrap=True,
        )
        self._chk_descrm = Checkbutton(
            self._frm_corr,
            text="Use Descrambler?",
            variable=self._spartn_descrm,
        )
        self._chk_prescram = Checkbutton(
            self._frm_corr,
            text="Use Prescrambling?",
            variable=self._spartn_prescrm,
        )
        self._lbl_descraminit = Label(self._frm_corr, text="Descrambler Init")
        self._ent_descraminit = Entry(
            self._frm_corr,
            textvariable=self._spartn_descrminit,
            bg=ENTCOL,
            state=NORMAL,
            relief="sunken",
            width=10,
        )
        self._lbl_unqword = Label(self._frm_corr, text="Unique Word")
        self._ent_unqword = Entry(
            self._frm_corr,
            textvariable=self._spartn_unqword,
            bg=ENTCOL,
            state=NORMAL,
            relief="sunken",
            width=20,
        )
        self._lbl_outport = Label(self._frm_corr, text="Output Port")
        self._spn_outport = Spinbox(
            self._frm_corr,
            values=INPORTS + (PASSTHRU,),
            textvariable=self._spartn_outport,
            readonlybackground=ENTCOL,
            state=READONLY,
            width=10,
            wrap=True,
        )
        self._btn_d9sconnect = Button(
            self._frm_corr,
            width=45,
            image=self._img_conn,
            command=lambda: self._on_corr_connect(),
        )
        self._btn_d9sdisconnect = Button(
            self._frm_corr,
            width=45,
            image=self._img_disconn,
            command=lambda: self._on_corr_disconnect(),
            state=DISABLED,
        )
        self._lbl_d9ssend = Label(self._frm_corr, image=None)
        self._btn_d9ssend = Button(
            self._frm_corr,
            image=self._img_send,
            width=45,
            command=self._on_send_corr_config,
            font=self.__app.font_md,
        )

        # GNSS Receiver (F9P) configuration widgets
        self._lbl_gnss = Label(self._frm_gnss, text="GNSS RECEIVER CONFIGURATION (F9*)")
        self._lbl_curr = Label(self._frm_gnss, text=LBLSPTNCURR)
        self._lbl_key1 = Label(self._frm_gnss, text=LBLSPTNKEY)
        self._ent_key1 = Entry(
            self._frm_gnss,
            textvariable=self._spartn_key1,
            bg=ENTCOL,
            state=NORMAL,
            relief="sunken",
            width=32,
        )
        self._lbl_valdate1 = Label(self._frm_gnss, text=LBLSPTNDAT)
        self._ent_valdate1 = Entry(
            self._frm_gnss,
            textvariable=self._spartn_valdate1,
            bg=ENTCOL,
            state=NORMAL,
            relief="sunken",
            width=8,
        )
        self._lbl_next = Label(self._frm_gnss, text=LBLSPTNNEXT)
        self._lbl_key2 = Label(self._frm_gnss, text=LBLSPTNKEY)
        self._ent_key2 = Entry(
            self._frm_gnss,
            textvariable=self._spartn_key2,
            bg=ENTCOL,
            state=NORMAL,
            relief="sunken",
            width=32,
        )
        self._lbl_valdate2 = Label(self._frm_gnss, text=LBLSPTNDAT)
        self._ent_valdate2 = Entry(
            self._frm_gnss,
            textvariable=self._spartn_valdate2,
            bg=ENTCOL,
            state=NORMAL,
            relief="sunken",
            width=8,
        )
        self._rad_source1 = Radiobutton(
            self._frm_gnss,
            text="L-Band",
            variable=self._spartn_source,
            value=SPARTN_LBAND,
        )
        self._rad_source0 = Radiobutton(
            self._frm_gnss, text="IP", variable=self._spartn_source, value=SPARTN_IP
        )
        self._chk_upload_keys = Checkbutton(
            self._frm_gnss,
            text=LBLSPTNUPLOAD,
            variable=self._upload_keys,
        )
        self._chk_send_config = Checkbutton(
            self._frm_gnss,
            text=LBLSPTNFP,
            variable=self._send_f9p_config,
        )
        self._chk_disable_nmea = Checkbutton(
            self._frm_gnss, text=LBLSPTNNMEA, variable=self._disable_nmea
        )
        self._lbl_send_command = Label(self._frm_gnss, image=None)
        self._btn_send_command = Button(
            self._frm_gnss,
            image=self._img_send,
            width=45,
            fg="green",
            command=self._on_send_gnss_config,
            font=self.__app.font_md,
        )

    def _do_layout(self):
        """
        Position widgets in frame.
        """

        # top of grid
        self._frm_container.grid(
            column=0, row=0, columnspan=3, padx=3, pady=3, sticky=(N, S, E, W)
        )

        self._do_spartn_layout()
        self._do_gnss_layout()

        # bottom of grid
        self._frm_status.grid(
            column=0,
            row=1,
            columnspan=2,
            ipadx=5,
            ipady=5,
            sticky=(W, E),
        )
        self._lbl_status.grid(column=0, row=0, sticky=W)
        self._btn_exit.grid(column=1, row=0, sticky=E)

        for frm in (self._frm_status,):
            colsp, rowsp = frm.grid_size()
            for i in range(colsp):
                frm.grid_columnconfigure(i, weight=1)
            for i in range(rowsp):
                frm.grid_rowconfigure(i, weight=1)

        self._frm_gnss.option_add("*Font", self.__app.font_sm)
        self._frm_corr.option_add("*Font", self.__app.font_sm)
        self._frm_status.option_add("*Font", self.__app.font_sm)

    def _do_spartn_layout(self):
        """
        Arrange spartn (D9S) configuration widgets in frame.
        """

        self._frm_corr.grid(
            column=0,
            row=0,
            ipadx=5,
            ipady=5,
            sticky=(N, S, W, E),
        )
        self._lbl_corr.grid(column=0, row=0, columnspan=4, padx=3, pady=2, sticky=W)
        self._frm_spartn_serial.grid(
            column=0, row=1, columnspan=4, padx=3, pady=2, sticky=(N, S, W, E)
        )
        ttk.Separator(self._frm_corr).grid(
            column=0, row=2, columnspan=4, padx=2, pady=3, sticky=(W, E)
        )
        self._rad_default.grid(column=0, row=3, sticky=W)
        self._rad_us.grid(column=1, row=3, sticky=W)
        self._rad_eu.grid(column=2, row=3, sticky=W)
        self._lbl_freq.grid(column=0, row=4, sticky=W)
        self._ent_freq.grid(column=1, row=4, columnspan=2, sticky=W)
        self._lbl_schwin.grid(column=0, row=5, sticky=W)
        self._ent_schwin.grid(column=1, row=5, columnspan=2, sticky=W)
        self._chk_usesid.grid(column=0, row=6, sticky=W)
        self._chk_descrm.grid(column=1, row=6, sticky=W)
        self._chk_prescram.grid(column=2, row=6, sticky=W)
        self._lbl_sid.grid(column=0, row=7, sticky=W)
        self._ent_sid.grid(column=1, row=7, columnspan=3, sticky=W)
        self._lbl_drat.grid(column=0, row=8, sticky=W)
        self._spn_drat.grid(column=1, row=8, sticky=W)
        self._lbl_descraminit.grid(column=0, row=9, sticky=W)
        self._ent_descraminit.grid(column=1, row=9, columnspan=3, sticky=W)
        self._lbl_unqword.grid(column=0, row=10, sticky=W)
        self._ent_unqword.grid(column=1, row=10, columnspan=3, sticky=W)
        self._lbl_outport.grid(column=0, row=11, sticky=W)
        self._spn_outport.grid(column=1, row=11, columnspan=3, sticky=W)
        ttk.Separator(self._frm_corr).grid(
            column=0, row=12, columnspan=4, padx=2, pady=3, sticky=(W, E)
        )
        self._btn_d9sconnect.grid(column=0, row=13, padx=3, pady=2, sticky=W)
        self._btn_d9sdisconnect.grid(column=1, row=13, padx=3, pady=2, sticky=W)
        self._btn_d9ssend.grid(column=2, row=13, padx=3, pady=2, sticky=W)
        self._lbl_d9ssend.grid(column=3, row=13, padx=3, pady=2, sticky=W)

    def _do_gnss_layout(self):
        """
        Arrange gnss (F9P) configuration widgets in frame.
        """

        self._frm_gnss.grid(
            column=1,
            row=0,
            ipadx=5,
            ipady=5,
            sticky=(N, S, W, E),
        )
        self._lbl_gnss.grid(column=0, row=0, columnspan=4, padx=3, pady=2, sticky=W)
        self._lbl_curr.grid(column=0, row=1, columnspan=4, padx=3, pady=2, sticky=W)
        self._lbl_key1.grid(column=0, row=2, padx=3, pady=2, sticky=W)
        self._ent_key1.grid(column=1, row=2, columnspan=3, padx=3, pady=2, sticky=W)
        self._lbl_valdate1.grid(column=0, row=3, padx=3, pady=2, sticky=W)
        self._ent_valdate1.grid(column=1, row=3, columnspan=3, padx=3, pady=2, sticky=W)
        ttk.Separator(self._frm_gnss).grid(
            column=0, row=4, columnspan=4, padx=2, pady=3, sticky=(W, E)
        )
        self._lbl_next.grid(column=0, row=5, columnspan=3, padx=3, pady=2, sticky=W)
        self._lbl_key2.grid(column=0, row=6, padx=3, pady=2, sticky=W)
        self._ent_key2.grid(column=1, row=6, columnspan=3, padx=2, pady=2, sticky=W)
        self._lbl_valdate2.grid(column=0, row=7, padx=3, pady=2, sticky=W)
        self._ent_valdate2.grid(column=1, row=7, columnspan=3, padx=3, pady=2, sticky=W)
        ttk.Separator(self._frm_gnss).grid(
            column=0, row=8, columnspan=4, padx=2, pady=3, sticky=(W, E)
        )
        self._rad_source1.grid(column=0, row=9, padx=3, pady=2, sticky=W)
        self._rad_source0.grid(column=1, row=9, padx=3, pady=2, sticky=W)
        self._chk_upload_keys.grid(column=0, row=10, padx=3, pady=2, sticky=W)
        self._chk_send_config.grid(column=1, row=10, padx=3, pady=2, sticky=W)
        self._chk_disable_nmea.grid(column=2, row=10, padx=3, pady=2, sticky=W)
        ttk.Separator(self._frm_gnss).grid(
            column=0, row=11, columnspan=4, padx=2, pady=3, sticky=(W, E)
        )
        self._btn_send_command.grid(column=2, row=12, padx=3, pady=2, sticky=W)
        self._lbl_send_command.grid(column=3, row=12, padx=3, pady=2, sticky=W)

    def _attach_events(self):
        """
        Bind events to widgets.
        """

        self._spartn_region.trace_add("write", self._on_select_region)

    def _on_select_region(self, var, index, mode):  # pylint: disable=unused-argument
        """
        Handle SPARTN region selection event.
        """

        # set parms to regional defaults
        reg = self._spartn_region.get()
        self._spartn_freq.set(SPARTN_PARMS[reg]["freq"])
        self._spartn_freq.set(SPARTN_PARMS[reg]["freq"])
        self._spartn_schwin.set(SPARTN_PARMS[reg]["schwin"])
        self._spartn_usesid.set(SPARTN_PARMS[reg]["usesid"])
        self._spartn_sid.set(SPARTN_PARMS[reg]["sid"])
        self._spartn_drat.set(SPARTN_PARMS[reg]["drat"])
        self._spartn_descrm.set(SPARTN_PARMS[reg]["descrm"])
        self._spartn_prescrm.set(SPARTN_PARMS[reg]["prescrm"])
        self._spartn_descrminit.set(SPARTN_PARMS[reg]["descrminit"])
        self._spartn_unqword.set(SPARTN_PARMS[reg]["unqword"])

    def _reset(self):
        """
        Reset configuration widgets.
        """

        curr = datetime.now()
        self._set_date(self._spartn_valdate1, curr)
        self._set_date(self._spartn_valdate2, curr + timedelta(weeks=4))
        self._spartn_source.set(SPARTN_DEFSRC)
        self._upload_keys.set(1)
        self._send_f9p_config.set(1)
        self._disable_nmea.set(0)
        reg = SPARTN_DEFREG
        self._spartn_region.set(reg)
        self._spartn_freq.set(SPARTN_PARMS[reg]["freq"])
        self._spartn_schwin.set(SPARTN_PARMS[reg]["schwin"])
        self._spartn_usesid.set(SPARTN_PARMS[reg]["usesid"])
        self._spartn_sid.set(SPARTN_PARMS[reg]["sid"])
        self._spartn_drat.set(PMP_DATARATES["B2400"])
        self._spartn_descrm.set(SPARTN_PARMS[reg]["descrm"])
        self._spartn_prescrm.set(SPARTN_PARMS[reg]["prescrm"])
        self._spartn_descrminit.set(SPARTN_PARMS[reg]["descrminit"])
        self._spartn_unqword.set(SPARTN_PARMS[reg]["unqword"])
        self._spartn_outport.set(INPORTS[0])
        self.set_status("", "blue")

    def set_status(self, message: str, color: str = "blue"):
        """
        Set status message.

        :param str message: message to be displayed
        :param str color: rgb color of text (blue)
        """

        message = (message[:80] + "..") if len(message) > 80 else message
        self._lbl_status.config(fg=color)
        self._status.set(" " + message)

    def on_exit(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Handle Exit button press.
        """

        # self.__master.update_idletasks()
        self._on_corr_disconnect()
        self.__app.stop_spartnconfig_thread()
        self.destroy()

    def _valid_corr_settings(self) -> bool:
        """
        Validate settings.

        :return: valid True/False
        :rtype: bool
        """

        return True  # TODO

    def _valid_gnss_settings(self) -> bool:
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

    def _on_corr_connect(self):
        """
        Connect to Correction receiver.
        """

        if self.serial_settings.status == NOPORTS:
            return

        # start serial stream thread
        self.__app.spartn_conn_status = CONNECTED
        self.spartn_stream_handler.start_read_thread(self)
        self.set_status(
            f"Connected to {self.serial_settings.port}:{self.serial_settings.port_desc} "
            + f"@ {self.serial_settings.bpsrate}",
            "green",
        )
        self._btn_d9sconnect.config(state=DISABLED)
        self._btn_d9sdisconnect.config(state=NORMAL)

        # poll current configuration
        msg = self._format_cfgpoll()
        self._send_corr_command(msg)

    def _on_corr_disconnect(self):
        """
        Disconnect from Correction receiver.
        """

        if self.__app.spartn_conn_status == CONNECTED:
            self.spartn_stream_handler.stop_read_thread()
            self.__app.spartn_conn_status = DISCONNECTED
            self.set_status(
                "Disconnected",
                "red",
            )
            self._btn_d9sconnect.config(state=NORMAL)
            self._btn_d9sdisconnect.config(state=DISABLED)

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
            f"CFG_MSGOUT_UBX_RXM_PMP_{outport}",
            f"CFG_{outport}OUTPROT_UBX",
        ]
        if outport in ("UART1", "UART2"):
            cfgdata.append(f"CFG_{outport}_BAUDRATE")

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
            (f"CFG_MSGOUT_UBX_RXM_PMP_{outport}", 1),
            (f"CFG_{outport}OUTPROT_UBX", 1),
        ]
        if outport in ("UART1", "UART2"):
            cfgdata.append(f"CFG_{outport}_BAUDRATE", int(self.serial_settings.bpsrate))

        msg = UBXMessage.config_set(SET_LAYER_RAM, TXN_NONE, cfgdata)
        return msg

    def _on_send_corr_config(self):
        """
        Send config to Correction receiver (e.g. D9S).
        """

        if not self._valid_corr_settings():
            return

        msg = self._format_cfgcorr()
        self._send_corr_command(msg)
        self.set_status(f"{CFGMSG} command sent", "green")
        self._lbl_d9ssend.config(image=self._img_pending)

    def _send_corr_command(self, msg: UBXMessage):
        """
        Send command to Correction receiver.
        """

        self.__app.spartn_outqueue.put(msg.serialize())

    def _format_cfggnss(self) -> UBXMessage:
        """
        Format UBX CFG-VALSET message to configure GNSS receiver.
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

    def _on_send_gnss_config(self):
        """
        Send config to GNSS receiver (e.g. F9P).
        """

        if not self._valid_gnss_settings():
            return

        if self.__app.conn_status != CONNECTED:
            self.set_status(NOTCONN, "red")
            # return

        if self._send_f9p_config.get():
            msgc = "config"
            msg = self._format_cfggnss()
            self._send_gnss_command(msg)
        else:
            msgc = ""
        if self._upload_keys.get():
            msgk = "keys"
            msg = self._format_rxmspartn()
            self._send_gnss_command(msg)
            # poll RXM-SPARTN-KEY to check keys have loaded
            msg = UBXMessage("RXM", RXMMSG, POLL)
            self._send_gnss_command(msg)
        else:
            msgk = ""
        if msgk == "" and msgc == "":
            self.set_status(NULLSEND, "red")
            return
        if msgk != "" and msgc != "":
            msga = " and "
        else:
            msga = ""
        self.set_status(f"{(msgk + msga + msgc).capitalize()} sent", "green")
        self._lbl_send_command.config(image=self._img_pending)

    def _send_gnss_command(self, msg: UBXMessage):
        """
        Send command to GNSS receiver.
        """

        self.__app.gnss_outqueue.put(msg.serialize())

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

    # ============================================
    # FOLLOWING METHODS REQUIRED BY STREAM_HANDLER
    # ============================================

    @property
    def appmaster(self):
        """
        Getter for application master (Tk)

        :return: reference to application master (Tk)
        """

        return self.__master

    @property
    def serial_settings(self) -> Frame:
        """
        Getter for common serial configuration panel

        :return: reference to serial form
        :rtype: Frame
        """

        return self._frm_spartn_serial

    @property
    def mode(self) -> int:
        """
        Getter for connection mode
        (0 = disconnected, 1 = serial, 2 = socket, 4 = file).
        """

        return self.__app.spartn_conn_status

    @property
    def read_event(self) -> str:
        """
        Getter for type of event to be raised when data
        is added to spartn_inqueue.
        """

        return SPARTN_EVENT

    @property
    def inqueue(self) -> Queue:
        """
        Getter for SPARTN input queue.
        """

        return self.__app.spartn_inqueue

    @property
    def outqueue(self) -> Queue:
        """
        Getter for SPARTN output queue.
        """

        return self.__app.spartn_outqueue

    @property
    def socketqueue(self) -> Queue:
        """
        Getter for socket input queue.
        """

        return self.__app.socket_inqueue
