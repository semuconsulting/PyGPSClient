"""
UBX Configuration frame for CFG-VAL commands

Created on 22 Dec 2020

:author: semuadmin
:copyright: SEMU Consulting © 2020
:license: BSD 3-Clause
"""
# pylint: disable=invalid-name

from tkinter import (
    Frame,
    Radiobutton,
    Listbox,
    Spinbox,
    Scrollbar,
    Button,
    Label,
    StringVar,
    IntVar,
    Entry,
    N,
    S,
    E,
    W,
    LEFT,
    VERTICAL,
    HORIZONTAL,
    NORMAL,
)
from PIL import ImageTk, Image
from pyubx2 import UBXMessage, UBX_CONFIG_DATABASE
from pyubx2.ubxhelpers import atttyp, attsiz, cfgname2key
from pygpsclient.globals import (
    ENTCOL,
    ERRCOL,
    INFCOL,
    ICON_SEND,
    ICON_WARNING,
    ICON_PENDING,
    ICON_CONFIRMED,
    READONLY,
    UBX_CFGVAL,
)

UBX_CONFIG_CATEGORIES = [
    "CFG_ANA",
    "CFG_BATCH",
    "CFG_BDS",
    "CFG_GEOFENCE",
    "CFG_HW_ANT",
    "CFG_HW_RF",
    "CFG_I2C",
    "CFG_INFMSG",
    "CFG_ITFM",
    "CFG_LOGFILTER",
    "CFG_MOT",
    "CFG_MSGOUT_NMEA",
    "CFG_MSGOUT_PUBX",
    "CFG_MSGOUT_RTCM",
    "CFG_MSGOUT_UBX",
    "CFG_NAV2",
    "CFG_NAVHPG",
    "CFG_NAVSPG",
    "CFG_NMEA",
    "CFG_ODO",
    "CFG_PM",
    "CFG_PMP",
    "CFG_QZSS",
    "CFG_RATE",
    "CFG_RINV",
    "CFG_RTCM",
    "CFG_SBAS",
    "CFG_SEC",
    "CFG_SFCORE",
    "CFG_SFIMU",
    "CFG_SFODO",
    "CFG_SIGNAL",
    "CFG_SPARTN",
    "CFG_SPI",
    "CFG_TMODE",
    "CFG_TP",
    "CFG_TXREADY",
    "CFG_UART1",
    "CFG_UART2",
    "CFG_USB",
]

VALSET = 0
VALDEL = 1
VALGET = 2
ATTDICT = {
    "U": "unsigned int",
    "I": "signed int",
    "R": "float",
    "L": "bool",
    "E": "unsigned int",
    "X": "byte(s) as hex string",
    "C": "char(s)",
}


class UBX_CFGVAL_Frame(Frame):
    """
    UBX CFG-VAL configuration command panel.
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
        self._cfgval_cat = None
        self._cfgval_keyname = None
        self._cfgval_keyid = None
        self._cfgmode = IntVar()
        self._cfgatt = StringVar()
        self._cfgkeyid = StringVar()
        self._cfgval = StringVar()
        self._cfglayer = StringVar()

        self._body()
        self._do_layout()
        self._attach_events()
        self.reset()

    def _body(self):
        """
        Set up frame and widgets.
        """

        self._lbl_configdb = Label(
            self, text="CFG-VALSET/DEL/GET Configuration Interface", anchor="w"
        )
        self._lbl_cat = Label(self, text="Category", anchor="w")
        self._lbx_cat = Listbox(
            self,
            border=2,
            relief="sunken",
            bg=ENTCOL,
            height=5,
            justify=LEFT,
            exportselection=False,
        )
        self._scr_catv = Scrollbar(self, orient=VERTICAL)
        self._scr_cath = Scrollbar(self, orient=HORIZONTAL)
        self._lbx_cat.config(yscrollcommand=self._scr_catv.set)
        self._lbx_cat.config(xscrollcommand=self._scr_cath.set)
        self._scr_catv.config(command=self._lbx_cat.yview)
        self._scr_cath.config(command=self._lbx_cat.xview)
        self._lbl_parm = Label(self, text="Keyname", anchor="w")
        self._lbx_parm = Listbox(
            self,
            border=2,
            relief="sunken",
            bg=ENTCOL,
            height=5,
            justify=LEFT,
            exportselection=False,
        )
        self._scr_parmv = Scrollbar(self, orient=VERTICAL)
        self._scr_parmh = Scrollbar(self, orient=HORIZONTAL)
        self._lbx_parm.config(yscrollcommand=self._scr_parmv.set)
        self._lbx_parm.config(xscrollcommand=self._scr_parmh.set)
        self._scr_parmv.config(command=self._lbx_parm.yview)
        self._scr_parmh.config(command=self._lbx_parm.xview)

        self._rad_cfgset = Radiobutton(
            self, text="CFG-VALSET", variable=self._cfgmode, value=0
        )
        self._rad_cfgdel = Radiobutton(
            self, text="CFG-VALDEL", variable=self._cfgmode, value=1
        )
        self._rad_cfgget = Radiobutton(
            self, text="CFG-VALGET", variable=self._cfgmode, value=2
        )
        self._lbl_key = Label(self, text="KeyID")
        self._lbl_keyid = Label(
            self,
            textvariable=self._cfgkeyid,
            bg=ENTCOL,
            width=10,
            fg=INFCOL,
            border=1,
            relief="sunken",
        )
        self._lbl_type = Label(self, text="Type")
        self._lbl_att = Label(
            self,
            textvariable=self._cfgatt,
            bg=ENTCOL,
            width=5,
            fg=INFCOL,
            border=1,
            relief="sunken",
        )
        self._lbl_layer = Label(self, text="Layer")
        self._spn_layer = Spinbox(
            self,
            textvariable=self._cfglayer,
            values=("RAM", "BBR", "FLASH", "DEFAULT"),
            bg=ENTCOL,
            wrap=True,
            width=8,
            state=READONLY,
            readonlybackground=ENTCOL,
        )
        self._lbl_val = Label(self, text="Value")
        self._ent_val = Entry(
            self,
            textvariable=self._cfgval,
            readonlybackground=ENTCOL,
            fg=INFCOL,
            state=READONLY,
            relief="sunken",
        )

        self._lbl_send_command = Label(self)
        self._btn_send_command = Button(
            self,
            image=self._img_send,
            width=50,
            command=self._on_send_config,
        )

    def _do_layout(self):
        """
        Layout widgets.
        """

        self._lbl_configdb.grid(column=0, row=0, columnspan=6, padx=3, sticky=(W, E))
        self._lbl_cat.grid(column=0, row=1, padx=3, sticky=(W, E))
        self._lbx_cat.grid(column=0, row=2, rowspan=5, padx=3, pady=3, sticky=(W, E))
        self._scr_catv.grid(column=0, row=2, rowspan=5, sticky=(N, S, E))
        self._scr_cath.grid(column=0, row=7, sticky=(W, E))
        self._lbl_parm.grid(column=1, row=1, columnspan=4, padx=3, sticky=(W, E))
        self._lbx_parm.grid(
            column=1, row=2, columnspan=4, rowspan=5, padx=3, pady=3, sticky=(W, E)
        )
        self._scr_parmv.grid(column=4, row=2, rowspan=5, sticky=(N, S, E))
        self._scr_parmh.grid(column=1, row=7, columnspan=4, sticky=(W, E))
        self._rad_cfgget.grid(column=0, row=8, padx=3, pady=0, sticky=(W))
        self._rad_cfgset.grid(column=0, row=9, padx=3, pady=0, sticky=(W))
        self._rad_cfgdel.grid(column=0, row=10, padx=3, pady=0, sticky=(W))
        self._lbl_key.grid(column=1, row=8, padx=3, pady=0, sticky=(E))
        self._lbl_keyid.grid(column=2, row=8, padx=3, pady=0, sticky=(W))
        self._lbl_type.grid(column=3, row=8, padx=3, pady=0, sticky=(E))
        self._lbl_att.grid(column=4, row=8, padx=3, pady=0, sticky=(W))
        self._lbl_layer.grid(column=1, row=9, padx=3, pady=0, sticky=(E))
        self._spn_layer.grid(column=2, row=9, padx=3, pady=0, sticky=(W))
        self._lbl_val.grid(column=1, row=10, padx=3, pady=0, sticky=(E))
        self._ent_val.grid(
            column=2, row=10, columnspan=3, padx=3, pady=0, sticky=(W, E)
        )

        self._btn_send_command.grid(
            column=3, row=12, rowspan=2, ipadx=3, ipady=3, sticky=(E)
        )
        self._lbl_send_command.grid(
            column=4, row=13, rowspan=2, ipadx=3, ipady=3, sticky=(E)
        )

        (cols, rows) = self.grid_size()
        for i in range(cols):
            self.grid_columnconfigure(i, weight=1)
        for i in range(rows):
            self.grid_rowconfigure(i, weight=1)
        self.option_add("*Font", self.__app.font_sm)

    def _attach_events(self):
        """
        Bind events to widgets.
        """

        self._lbx_cat.bind("<<ListboxSelect>>", self._on_select_cat)
        self._lbx_parm.bind("<<ListboxSelect>>", self._on_select_parm)
        self._cfgmode.trace_add("write", self._on_select_mode)

    def reset(self):
        """
        Reset panel.
        """

        for i, cat in enumerate(UBX_CONFIG_CATEGORIES):
            self._lbx_cat.insert(i, cat)
        self._cfgmode.set(2)

    def _on_select_mode(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Mode has been selected.
        """

        if self._cfgmode.get() == VALSET:
            self._ent_val.config(state=NORMAL, bg=ENTCOL, fg="Black")
        else:
            self._ent_val.config(state=READONLY, readonlybackground=ENTCOL, fg=INFCOL)

    def _on_select_cat(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Configuration category has been selected.
        """

        idx = self._lbx_cat.curselection()
        self._cfgval_cat = self._lbx_cat.get(idx)

        self._lbx_parm.delete(0, "end")
        self._cfgkeyid.set("")
        self._cfgatt.set("")
        idx = 0
        for keyname, (_, _) in UBX_CONFIG_DATABASE.items():
            if self._cfgval_cat in keyname:
                self._lbx_parm.insert(idx, keyname)
                idx += 1
        self._cfgval.set("")

    def _on_select_parm(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Configuration parameter (keyname) has been selected.
        """

        idx = self._lbx_parm.curselection()
        self._cfgval_keyname = self._lbx_parm.get(idx)

        (keyid, att) = cfgname2key(self._cfgval_keyname)
        self._cfgkeyid.set(hex(keyid))
        self._cfgatt.set(att)
        self._cfgval.set("")

    def _on_send_config(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Config interface send button has been clicked.
        """

        if self._cfgval_keyname is not None:
            if self._cfgmode.get() == VALSET:
                self._do_valset()
            elif self._cfgmode.get() == VALDEL:
                self._do_valdel()
            else:
                self._do_valget()

    def _do_valset(self):
        """
        Send a CFG-VALSET message.

        :return: valid entry flag
        :rtype: bool
        """

        valid_entry = True
        att = atttyp(self._cfgatt.get())
        atts = attsiz(self._cfgatt.get())
        val = self._cfgval.get()
        layers = self._cfglayer.get()
        if layers == "BBR":
            layers = 2
        elif layers == "FLASH":
            layers = 4
        else:
            layers = 1
        try:
            if att in ("C", "X"):  # byte or char
                if len(val) == atts * 2:  # 2 hex chars per byte
                    val = bytearray.fromhex(val)
                else:
                    valid_entry = False
            elif att in ("E", "U"):  # unsigned integer
                val = int(val)
                if val < 0:
                    valid_entry = False
            elif att == "L":  # bool
                val = int(val)
                if val not in (0, 1):
                    valid_entry = False
            elif att == "I":  # signed integer
                val = int(val)
            elif att == "R":  # floating point
                val = float(val)
            transaction = 0
            cfgData = [
                (self._cfgval_keyname, val),
            ]
        except ValueError:
            valid_entry = False

        if valid_entry:
            msg = UBXMessage.config_set(layers, transaction, cfgData)
            self.__app.stream_handler.serial_write(msg.serialize())
            self._ent_val.configure(bg=ENTCOL)
            self._lbl_send_command.config(image=self._img_pending)
            self.__container.set_status("CFG-VALSET SET message sent", "blue")
            for msgid in ("ACK-ACK", "ACK-NAK"):
                self.__container.set_pending(msgid, UBX_CFGVAL)
        else:
            self._ent_val.configure(bg=ERRCOL)
            self._lbl_send_command.config(image=self._img_warn)
            typ = ATTDICT[att]
            self.__container.set_status(
                (
                    "INVALID ENTRY - must conform to parameter "
                    f"type {att} ({typ}) and size {atts} bytes"
                ),
                "red",
            )

        return valid_entry

    def _do_valdel(self):
        """
        Send a CFG-VALDEL message.
        """

        layers = self._cfglayer.get()
        if layers == "BBR":
            layers = 2
        elif layers == "FLASH":
            layers = 4
        else:
            layers = 1
        transaction = 0
        key = [
            self._cfgval_keyname,
        ]
        msg = UBXMessage.config_del(layers, transaction, key)
        self.__app.stream_handler.serial_write(msg.serialize())
        self._ent_val.configure(bg=ENTCOL)
        self._lbl_send_command.config(image=self._img_pending)
        self.__container.set_status("CFG-VALDEL SET message sent", "blue")
        for msgid in ("ACK-ACK", "ACK-NAK"):
            self.__container.set_pending(msgid, UBX_CFGVAL)

    def _do_valget(self):
        """
        Send a CFG-VALGET message.
        """

        layers = self._cfglayer.get()
        if layers == "BBR":
            layers = 1
        elif layers == "FLASH":
            layers = 2
        elif layers == "DEFAULT":
            layers = 7
        else:
            layers = 0
        transaction = 0
        keys = [
            self._cfgval_keyname,
        ]
        msg = UBXMessage.config_poll(layers, transaction, keys)
        self.__app.stream_handler.serial_write(msg.serialize())
        self._ent_val.configure(bg=ENTCOL)
        self._lbl_send_command.config(image=self._img_pending)
        self.__container.set_status("CFG-VALGET POLL message sent", "blue")
        for msgid in ("CFG-VALGET", "ACK-ACK", "ACK-NAK"):
            self.__container.set_pending(msgid, UBX_CFGVAL)

    def update_status(self, msg: UBXMessage):  # pylint: disable=unused-argument
        """
        Update pending confirmation status.

        :param UBXMessage msg: UBX config message
        """

        if msg.identity == "CFG-VALGET":
            self._lbl_send_command.config(image=self._img_confirmed)
            val = getattr(msg, self._cfgval_keyname, None)
            if val is not None:
                if isinstance(val, bytes):
                    val = val.hex()
                self._cfgval.set(val)
            self.__container.set_status("CFG-VALGET GET message received", "green")

        elif msg.identity == "ACK-ACK":
            self._lbl_send_command.config(image=self._img_confirmed)
            self.__container.set_status("CFG-VAL command acknowledged", "green")

        elif msg.identity == "ACK-NAK":
            self._lbl_send_command.config(image=self._img_warn)
            self.__container.set_status("CFG-VAL command rejected", "red")
