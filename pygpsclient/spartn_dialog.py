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
from os import getenv
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
from pygpsclient.mqtt_handler import MQTTHandler
from pygpsclient.globals import (
    ICON_EXIT,
    ICON_SEND,
    ICON_CONFIRMED,
    ICON_PENDING,
    ICON_WARNING,
    ICON_SERIAL,
    ICON_DISCONN,
    ICON_BLANK,
    ICON_SOCKET,
    ENTCOL,
    POPUP_TRANSIENT,
    CONNECTED,
    DISCONNECTED,
    NOPORTS,
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
    LBLSPARTNIP,
    LBLSPARTNLB,
    LBLSPARTNGN,
)
from pygpsclient.helpers import (
    valid_entry,
    get_gpswnotow,
    VALHEX,
    VALDMY,
    VALLEN,
    VALINT,
)
from pygpsclient.serialconfig_frame import SerialConfigFrame
from pygpsclient.stream_handler import StreamHandler

U2MAX = 2e16 - 1
U8MAX = 2e64 - 1
BAUDRATE = 38400
SPARTN_KEYLEN = 16
RESERVED0 = b"\x00\x00"
RESERVED1 = b"\x00"
RXMMSG = "RXM-SPARTN-KEY"
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
PPSERVER = "pp.services.u-blox.com"
PPREGIONS = ("eu", "us", "au")


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
        # if POPUP_TRANSIENT:
        #     self.transient(self.__app)
        self.resizable(False, False)
        self.title(DLGSPARTNCONFIG)  # pylint: disable=E1102
        self.protocol("WM_DELETE_WINDOW", self.on_exit)
        self._img_blank = ImageTk.PhotoImage(Image.open(ICON_BLANK))
        self._img_pending = ImageTk.PhotoImage(Image.open(ICON_PENDING))
        self._img_confirmed = ImageTk.PhotoImage(Image.open(ICON_CONFIRMED))
        self._img_warn = ImageTk.PhotoImage(Image.open(ICON_WARNING))
        self._img_exit = ImageTk.PhotoImage(Image.open(ICON_EXIT))
        self._img_send = ImageTk.PhotoImage(Image.open(ICON_SEND))
        self._img_serial = ImageTk.PhotoImage(Image.open(ICON_SERIAL))
        self._img_socket = ImageTk.PhotoImage(Image.open(ICON_SOCKET))
        self._img_disconn = ImageTk.PhotoImage(Image.open(ICON_DISCONN))
        self.lband_stream_handler = StreamHandler(self)
        self.mqtt_stream_handler = None
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
        self._spartn_enabledbg = IntVar()
        self._mqtt_server = StringVar()
        self._mqtt_region = StringVar()
        self._mqtt_clientid = StringVar()
        self._mqtt_iptopic = IntVar()
        self._mqtt_mgatopic = IntVar()
        self._mqtt_keytopic = IntVar()
        self._ports = INPORTS

        self._body()
        self._do_layout()
        self._reset()

    def _body(self):
        """
        Set up frame and widgets.
        """
        # pylint: disable=unnecessary-lambda

        self._frm_container = Frame(self)
        self._frm_corrip = Frame(self._frm_container, borderwidth=2, relief="groove")
        self._frm_corrlband = Frame(self._frm_container, borderwidth=2, relief="groove")
        self._frm_gnss = Frame(self._frm_container, borderwidth=2, relief="groove")
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

        # IP Correction receiver (MQTT) configuration widgets
        self._lbl_corrip = Label(self._frm_corrip, text=LBLSPARTNIP)
        self._lbl_mqttserver = Label(self._frm_corrip, text="Server")
        self._ent_mqttserver = Entry(
            self._frm_corrip,
            textvariable=self._mqtt_server,
            bg=ENTCOL,
            state=NORMAL,
            relief="sunken",
            width=20,
        )
        self._lbl_mqttregion = Label(self._frm_corrip, text="Region")
        self._spn_mqttregion = Spinbox(
            self._frm_corrip,
            values=PPREGIONS,
            textvariable=self._mqtt_region,
            readonlybackground=ENTCOL,
            state=READONLY,
            width=4,
            wrap=True,
        )
        self._lbl_mqttclientid = Label(self._frm_corrip, text="Client ID")
        self._ent_mqttclientid = Entry(
            self._frm_corrip,
            textvariable=self._mqtt_clientid,
            bg=ENTCOL,
            state=NORMAL,
            relief="sunken",
            width=32,
        )
        self._lbl_topics = Label(self._frm_corrip, text="Topics:")
        self._chk_mqtt_iptopic = Checkbutton(
            self._frm_corrip,
            text="IP",
            variable=self._mqtt_iptopic,
        )
        self._chk_mqtt_mgatopic = Checkbutton(
            self._frm_corrip,
            text="MGA",
            variable=self._mqtt_mgatopic,
        )
        self._chk_mqtt_keytopic = Checkbutton(
            self._frm_corrip,
            text="SPARTNKEY",
            variable=self._mqtt_keytopic,
        )
        self._btn_mqttconnect = Button(
            self._frm_corrip,
            width=45,
            image=self._img_socket,
            command=lambda: self._on_mqtt_connect(),
        )
        self._btn_mqttdisconnect = Button(
            self._frm_corrip,
            width=45,
            image=self._img_disconn,
            command=lambda: self._on_mqtt_disconnect(),
            state=DISABLED,
        )

        # L-Band Correction receiver (D9S) configuration widgets
        self._lbl_corrlband = Label(self._frm_corrlband, text=LBLSPARTNLB)
        # Correction receiver serial port configuration panel
        self._frm_spartn_serial = SerialConfigFrame(
            self._frm_corrlband,
            preselect=KNOWNGPS,
            timeouts=TIMEOUTS,
            bpsrates=BPSRATES,
            msgmodes=list(MSGMODES.keys()),
            userport=self.__app.spartn_user_port,  # user-defined serial port
        )
        self._lbl_freq = Label(self._frm_corrlband, text="L-Band Frequency (Hz)")
        self._ent_freq = Entry(
            self._frm_corrlband,
            textvariable=self._spartn_freq,
            bg=ENTCOL,
            state=NORMAL,
            relief="sunken",
            width=10,
        )
        self._chk_enabledbg = Checkbutton(
            self._frm_corrlband,
            text="Enable Debug?",
            variable=self._spartn_enabledbg,
        )
        self._lbl_schwin = Label(self._frm_corrlband, text="Search window")
        self._ent_schwin = Entry(
            self._frm_corrlband,
            textvariable=self._spartn_schwin,
            bg=ENTCOL,
            state=NORMAL,
            relief="sunken",
            width=10,
        )
        self._chk_usesid = Checkbutton(
            self._frm_corrlband,
            text="Use Service ID?",
            variable=self._spartn_usesid,
        )
        self._lbl_sid = Label(self._frm_corrlband, text="Service ID")
        self._ent_sid = Entry(
            self._frm_corrlband,
            textvariable=self._spartn_sid,
            bg=ENTCOL,
            state=NORMAL,
            relief="sunken",
            width=10,
        )
        self._lbl_drat = Label(self._frm_corrlband, text="Data Rate")
        self._spn_drat = Spinbox(
            self._frm_corrlband,
            values=list(PMP_DATARATES.values()),
            textvariable=self._spartn_drat,
            readonlybackground=ENTCOL,
            state=READONLY,
            width=5,
            wrap=True,
        )
        self._chk_descrm = Checkbutton(
            self._frm_corrlband,
            text="Use Descrambler?",
            variable=self._spartn_descrm,
        )
        self._chk_prescram = Checkbutton(
            self._frm_corrlband,
            text="Use Prescrambling?",
            variable=self._spartn_prescrm,
        )
        self._lbl_descraminit = Label(self._frm_corrlband, text="Descrambler Init")
        self._ent_descraminit = Entry(
            self._frm_corrlband,
            textvariable=self._spartn_descrminit,
            bg=ENTCOL,
            state=NORMAL,
            relief="sunken",
            width=10,
        )
        self._lbl_unqword = Label(self._frm_corrlband, text="Unique Word")
        self._ent_unqword = Entry(
            self._frm_corrlband,
            textvariable=self._spartn_unqword,
            bg=ENTCOL,
            state=NORMAL,
            relief="sunken",
            width=20,
        )
        self._lbl_outport = Label(self._frm_corrlband, text="Output Port")
        self._spn_outport = Spinbox(
            self._frm_corrlband,
            values=INPORTS + (PASSTHRU,),
            textvariable=self._spartn_outport,
            readonlybackground=ENTCOL,
            state=READONLY,
            width=10,
            wrap=True,
        )
        self._btn_lbandconnect = Button(
            self._frm_corrlband,
            width=45,
            image=self._img_serial,
            command=lambda: self._on_lband_connect(),
        )
        self._btn_lbanddisconnect = Button(
            self._frm_corrlband,
            width=45,
            image=self._img_disconn,
            command=lambda: self._on_lband_disconnect(),
            state=DISABLED,
        )
        self._lbl_lbandsend = Label(self._frm_corrlband, image=self._img_blank)
        self._btn_lbandsend = Button(
            self._frm_corrlband,
            image=self._img_send,
            width=45,
            command=self._on_send_lband_config,
        )

        # GNSS Receiver (F9P) configuration widgets
        self._lbl_gnss = Label(self._frm_gnss, text=LBLSPARTNGN)
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
        self._lbl_send_command = Label(self._frm_gnss, image=self._img_blank)
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

        self._do_mqtt_layout()
        self._do_lband_layout()
        self._do_gnss_layout()

        # bottom of grid
        self._frm_status.grid(
            column=0,
            row=1,
            columnspan=3,
            ipadx=5,
            ipady=5,
            sticky=(W, E),
        )
        self._lbl_status.grid(column=0, row=0, columnspan=2, sticky=W)
        self._btn_exit.grid(column=2, row=0, sticky=E)

        for frm in (self._frm_status,):
            colsp, rowsp = frm.grid_size()
            for i in range(colsp):
                frm.grid_columnconfigure(i, weight=1)
            for i in range(rowsp):
                frm.grid_rowconfigure(i, weight=1)

        self._frm_gnss.option_add("*Font", self.__app.font_sm)
        self._frm_corrlband.option_add("*Font", self.__app.font_sm)
        self._frm_status.option_add("*Font", self.__app.font_sm)

    def _do_mqtt_layout(self):
        """
        Arrange IP spartn (MQTT) configuration widgets in frame.
        """

        self._frm_corrip.grid(
            column=0,
            row=0,
            ipadx=5,
            ipady=5,
            sticky=(N, S, W, E),
        )
        self._lbl_corrip.grid(column=0, row=0, columnspan=4, padx=3, pady=2, sticky=W)
        self._lbl_mqttserver.grid(column=0, row=1, padx=3, pady=2, sticky=W)
        self._ent_mqttserver.grid(
            column=1, row=1, columnspan=3, padx=3, pady=2, sticky=W
        )
        self._lbl_mqttregion.grid(column=0, row=2, padx=3, pady=2, sticky=W)
        self._spn_mqttregion.grid(
            column=1, row=2, columnspan=3, padx=3, pady=2, sticky=W
        )
        self._lbl_mqttclientid.grid(column=0, row=3, padx=3, pady=2, sticky=W)
        self._ent_mqttclientid.grid(
            column=1, row=3, columnspan=3, padx=3, pady=2, sticky=W
        )
        self._lbl_topics.grid(column=0, row=4, padx=3, pady=2, sticky=W)
        self._chk_mqtt_iptopic.grid(column=1, row=4, padx=3, pady=2, sticky=W)
        self._chk_mqtt_mgatopic.grid(column=2, row=4, padx=3, pady=2, sticky=W)
        self._chk_mqtt_keytopic.grid(column=3, row=4, padx=3, pady=2, sticky=W)
        ttk.Separator(self._frm_corrip).grid(
            column=0, row=5, columnspan=4, padx=2, pady=3, sticky=(W, E)
        )
        self._btn_mqttconnect.grid(column=0, row=6, padx=3, pady=2, sticky=W)
        self._btn_mqttdisconnect.grid(column=1, row=6, padx=3, pady=2, sticky=W)

    def _do_lband_layout(self):
        """
        Arrange L-Band spartn (D9S) configuration widgets in frame.
        """

        self._frm_corrlband.grid(
            column=1,
            row=0,
            ipadx=5,
            ipady=5,
            sticky=(N, S, W, E),
        )
        self._lbl_corrlband.grid(
            column=0, row=0, columnspan=4, padx=3, pady=2, sticky=W
        )
        self._frm_spartn_serial.grid(
            column=0, row=1, columnspan=4, padx=3, pady=2, sticky=(N, S, W, E)
        )
        ttk.Separator(self._frm_corrlband).grid(
            column=0, row=2, columnspan=4, padx=2, pady=3, sticky=(W, E)
        )
        self._lbl_freq.grid(column=0, row=3, sticky=W)
        self._ent_freq.grid(column=1, row=3, sticky=W)
        self._chk_enabledbg.grid(column=2, row=3, columnspan=2, sticky=W)
        self._lbl_schwin.grid(column=0, row=4, sticky=W)
        self._ent_schwin.grid(column=1, row=4, columnspan=3, sticky=W)
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
        ttk.Separator(self._frm_corrlband).grid(
            column=0, row=11, columnspan=4, padx=2, pady=3, sticky=(W, E)
        )
        self._btn_lbandconnect.grid(column=0, row=12, padx=3, pady=2, sticky=W)
        self._btn_lbanddisconnect.grid(column=1, row=12, padx=3, pady=2, sticky=W)
        self._btn_lbandsend.grid(column=2, row=12, padx=3, pady=2, sticky=W)
        self._lbl_lbandsend.grid(column=3, row=12, padx=3, pady=2, sticky=W)

    def _do_gnss_layout(self):
        """
        Arrange gnss (F9P) configuration widgets in frame.
        """

        self._frm_gnss.grid(
            column=2,
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
        self._rad_source0.grid(column=1, row=9, columnspan=3, padx=3, pady=2, sticky=W)
        self._chk_upload_keys.grid(column=0, row=10, padx=3, pady=2, sticky=W)
        self._chk_send_config.grid(column=1, row=10, padx=3, pady=2, sticky=W)
        self._chk_disable_nmea.grid(
            column=2, row=10, columnspan=2, padx=3, pady=2, sticky=W
        )
        ttk.Separator(self._frm_gnss).grid(
            column=0, row=11, columnspan=4, padx=2, pady=3, sticky=(W, E)
        )
        self._btn_send_command.grid(column=2, row=12, padx=3, pady=2, sticky=W)
        self._lbl_send_command.grid(column=3, row=12, padx=3, pady=2, sticky=W)

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
        self._spartn_enabledbg.set(0)
        self._spartn_drat.set(PMP_DATARATES["B2400"])
        self._spartn_freq.set(SPARTN_DEFAULT["freq"])
        self._spartn_freq.set(SPARTN_DEFAULT["freq"])
        self._spartn_schwin.set(SPARTN_DEFAULT["schwin"])
        self._spartn_usesid.set(SPARTN_DEFAULT["usesid"])
        self._spartn_sid.set(SPARTN_DEFAULT["sid"])
        self._spartn_descrm.set(SPARTN_DEFAULT["descrm"])
        self._spartn_prescrm.set(SPARTN_DEFAULT["prescrm"])
        self._spartn_descrminit.set(SPARTN_DEFAULT["descrminit"])
        self._spartn_unqword.set(SPARTN_DEFAULT["unqword"])
        self._spartn_outport.set(PASSTHRU)
        self._mqtt_server.set(PPSERVER)
        self._mqtt_region.set(PPREGIONS[0])
        self._mqtt_iptopic.set(1)
        self._mqtt_mgatopic.set(0)
        self._mqtt_keytopic.set(1)
        self._mqtt_clientid.set(getenv("MQTTCLIENTID", default=""))
        self.set_status("", "blue")
        self.set_mqtt_controls(DISCONNECTED)
        self.set_lband_controls(DISCONNECTED)

    def set_mqtt_controls(self, status: int):
        """
        Enable or disable MQTT Correction widgets depending on
        connection status.

        :param int status: connection status (0 = disconnected, 1 = connected)
        """

        stat = NORMAL if status == CONNECTED else DISABLED
        for wdg in (self._btn_mqttdisconnect,):
            wdg.config(state=stat)
        stat = DISABLED if status == CONNECTED else NORMAL
        for wdg in (
            self._ent_mqttserver,
            self._btn_mqttconnect,
            self._ent_mqttclientid,
            self._chk_mqtt_iptopic,
            self._chk_mqtt_mgatopic,
            self._chk_mqtt_keytopic,
        ):
            wdg.config(state=stat)
        stat = DISABLED if status == CONNECTED else READONLY
        for wdg in (self._spn_mqttregion,):
            wdg.config(state=stat)

    def set_lband_controls(self, status: int):
        """
        Enable or disable L-Band Correction widgets depending on
        connection status.

        :param int status: connection status (0 = disconnected, 1 = connected)
        """

        stat = DISABLED if status == CONNECTED else NORMAL
        for wdg in (self._btn_lbandconnect,):
            wdg.config(state=stat)
        stat = NORMAL if status == CONNECTED else DISABLED
        for wdg in (
            self._ent_freq,
            self._ent_schwin,
            self._ent_sid,
            self._ent_unqword,
            self._ent_descraminit,
            self._chk_enabledbg,
            self._chk_descrm,
            self._chk_prescram,
            self._chk_usesid,
            self._btn_lbanddisconnect,
            self._btn_lbandsend,
        ):
            wdg.config(state=stat)
        stat = READONLY if status == CONNECTED else DISABLED
        for wdg in (
            self._spn_drat,
            self._spn_outport,
        ):
            wdg.config(state=stat)

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
        self._on_mqtt_disconnect()
        self._on_lband_disconnect()
        self.__app.stop_spartnconfig_thread()
        self.destroy()

    def _valid_corr_settings(self) -> bool:
        """
        Validate Correction receiver settings.

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
            self.set_status("ERROR - invalid settings", "red")

        return valid

    def _valid_gnss_settings(self) -> bool:
        """
        Validate GNSS receiver settings.

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

    def _on_mqtt_connect(self):
        """
        Connect to MQTT client.
        """

        self.__app.spartn_conn_status = CONNECTED
        server = PPSERVER
        region = self._mqtt_region.get()
        topics = []
        if self._mqtt_iptopic.get():
            topics.append((f"/pp/ip/{region}", 0))
        if self._mqtt_mgatopic.get():
            topics.append(("/pp/ubx/mga", 0))
        if self._mqtt_keytopic.get():
            topics.append(("/pp/ubx/0236/ip", 0))

        self.mqtt_stream_handler = MQTTHandler(
            self.__app,
            "eu",
            self.__app.spartn_inqueue,
            clientid=self._mqtt_clientid.get(),
            mqtt_topics=topics,
            server=server,
        )
        self.mqtt_stream_handler.start()
        self.set_status(
            f"Connected to MQTT server {server}",
            "green",
        )
        self.set_mqtt_controls(CONNECTED)

    def _on_mqtt_disconnect(self):
        """
        Disconnect from MQTT client.
        """

        if self.mqtt_stream_handler is not None:
            self.__app.spartn_conn_status = DISCONNECTED
            self.mqtt_stream_handler.stop()
            self.mqtt_stream_handler = None
            self.set_status(
                "Disconnected",
                "red",
            )
        self.set_mqtt_controls(DISCONNECTED)

    def _on_lband_connect(self):
        """
        Connect to Correction receiver.
        """

        if self.serial_settings.status == NOPORTS:
            return

        # start serial stream thread
        self.__app.spartn_conn_status = CONNECTED
        self.lband_stream_handler.start_read_thread(self)
        self.set_status(
            f"Connected to {self.serial_settings.port}:{self.serial_settings.port_desc} "
            + f"@ {self.serial_settings.bpsrate}",
            "green",
        )
        self.set_lband_controls(CONNECTED)

        # poll current configuration
        msg = self._format_cfgpoll()
        self._send_lband_command(msg)

    def _on_lband_disconnect(self):
        """
        Disconnect from Correction receiver.
        """

        if self.__app.spartn_conn_status == CONNECTED:
            self.lband_stream_handler.stop_read_thread()
            self.__app.spartn_conn_status = DISCONNECTED
            self.set_status(
                "Disconnected",
                "red",
            )
            self.set_lband_controls(DISCONNECTED)

    def _format_cfgpoll(self) -> UBXMessage:
        """
        Format UBX CFG-VALGET message to poll Correction receiver
        configuration.
        """

        # We figured it out. Turns out the issue was with the parameter CFG-NAVSPG-CONSTR_DGNSSTO,
        # which seems to specify how long to wait between correction messages before dropping RTK.
        # It was set to 10 seconds: much too short to accomodate the infrequent messages from the D9S.
        # The default factory value is 60 seconds, but I still find occasional RTK dropouts, so
        # I've settled on 90 seconds for now. The reason it was set to 10 seconds was because of
        # our previous testing of RTCM streaming.

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
            if self._spartn_enabledbg.get():
                cfgdata.append((f"CFG_INFMSG_UBX_{port}", b"\x1f"))
            else:
                cfgdata.append((f"CFG_INFMSG_UBX_{port}", b"\x07"))
        if outport in ("UART1", "UART2"):
            cfgdata.append(f"CFG_{outport}_BAUDRATE", int(self.serial_settings.bpsrate))

        msg = UBXMessage.config_set(SET_LAYER_RAM, TXN_NONE, cfgdata)
        return msg

    def _on_send_lband_config(self):
        """
        Send config to L-Band Correction receiver (e.g. D9S).
        """

        if not self._valid_corr_settings():
            return

        msg = self._format_cfgcorr()
        self._send_lband_command(msg)
        self.set_status(f"{CFGSET} command sent", "green")
        self._lbl_lbandsend.config(image=self._img_pending)

        # poll for acknowledgement
        msg = self._format_cfgpoll()
        self._send_lband_command(msg)

    def _send_lband_command(self, msg: UBXMessage):
        """
        Send command to L-Band Correction receiver.
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

        if not hasattr(msg, "identity"):
            return

        if msg.identity == RXMMSG:
            if msg.numKeys == 2:  # check both keys have been uploaded
                self._lbl_send_command.config(image=self._img_confirmed)
                self.set_status(CONFIGOK.format(RXMMSG), "green")
            else:
                self._lbl_send_command.config(image=self._img_warn)
                self.set_status(CONFIGBAD.format(RXMMSG), "red")
        elif msg.identity == "ACK-ACK":
            self._lbl_send_command.config(image=self._img_confirmed)
            self.set_status(CONFIGOK.format(CFGSET), "green")
        elif msg.identity == "ACK-NAK":
            self._lbl_send_command.config(image=self._img_warn)
            self.set_status(CONFIGBAD.format(CFGSET), "red")
        elif msg.identity == CFGPOLL:
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
            self.set_status(f"{CFGPOLL} received", "green")
            self._lbl_lbandsend.config(image=self._img_confirmed)
            self.update_idletasks()

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

    def _parse_spartn(self, msg) -> str:
        """
        Parse SPARTN message.
        """

    # ============================================
    # FOLLOWING METHODS REQUIRED BY STREAM_HANDLER
    # ============================================

    @property
    def appmaster(self) -> object:
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
