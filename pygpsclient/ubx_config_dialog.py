"""
UBX Configuration frame class for PyGPSClient application.

This handles the UBX Configuration Dialog panel and receives polled
responses from the ubx_handler module.

Created on 22 Sep 2020

@author: semuadmin
"""
# pylint: disable=invalid-name, unused-argument

from tkinter import (
    ttk,
    messagebox,
    Toplevel,
    Frame,
    Radiobutton,
    Listbox,
    Spinbox,
    Scrollbar,
    Button,
    Label,
    StringVar,
    IntVar,
    N,
    S,
    E,
    W,
    LEFT,
    VERTICAL,
    HORIZONTAL,
)

from PIL import ImageTk, Image
from pyubx2 import UBXMessage, POLL, SET, UBX_CONFIG_MESSAGES, UBX_PAYLOADS_POLL
from pyubx2.ubxhelpers import key_from_val

from .globals import (
    BGCOL,
    FGCOL,
    ENTCOL,
    ICON_SEND,
    ICON_EXIT,
    ICON_WARNING,
    ICON_UBXCONFIG,
    ICON_PENDING,
    ICON_CONFIRMED,
    PORTIDS,
    BAUDRATES,
    READONLY,
    ANTPOWER,
    ANTSTATUS,
)
from .strings import (
    LBLUBXCONFIG,
    LBLCFGPRT,
    LBLCFGMSG,
    LBLPRESET,
    DLGUBXCONFIG,
    DLGRESET,
    DLGSAVE,
    DLGRESETCONFIRM,
    DLGSAVECONFIRM,
    PSTRESET,
    PSTSAVE,
    PSTMINNMEAON,
    PSTALLNMEAON,
    PSTALLNMEAOFF,
    PSTMINUBXON,
    PSTALLUBXON,
    PSTALLUBXOFF,
    PSTALLINFON,
    PSTALLINFOFF,
    PSTALLLOGON,
    PSTALLLOGOFF,
    PSTALLMONON,
    PSTALLMONOFF,
    PSTALLRXMON,
    PSTALLRXMOFF,
    PSTPOLLPORT,
    PSTPOLLINFO,
    PSTPOLLALL,
)

from .ubx_handler import UBXHandler as ubh

PRESET_COMMMANDS = [
    PSTRESET,
    PSTSAVE,
    PSTMINNMEAON,
    PSTALLNMEAON,
    PSTALLNMEAOFF,
    PSTMINUBXON,
    PSTALLUBXON,
    PSTALLUBXOFF,
    PSTALLINFON,
    PSTALLINFOFF,
    PSTALLLOGON,
    PSTALLLOGOFF,
    PSTALLMONON,
    PSTALLMONOFF,
    PSTALLRXMON,
    PSTALLRXMOFF,
    PSTPOLLPORT,
    PSTPOLLINFO,
    PSTPOLLALL,
]


class UBXConfigDialog:
    """,
    UBXConfigDialog class.
    """

    def __init__(self, app, *args, **kwargs):
        """
        Constructor.

        :param object app: reference to main tkinter application
        """

        self.__app = app  # Reference to main application class
        self.__master = self.__app.get_master()  # Reference to root class (Tk)
        self._dialog = Toplevel()
        #         self._dialog.transient(self.__app)
        self._dialog.resizable(False, False)
        self._dialog.title = DLGUBXCONFIG
        wd, hd = self.get_size()
        wa = self.__master.winfo_width()
        ha = self.__master.winfo_height()
        self._dialog.geometry("+%d+%d" % (int(wa / 2 - wd / 2), int(ha / 2 - hd / 2)))
        self._img_icon = ImageTk.PhotoImage(Image.open(ICON_UBXCONFIG))
        self._img_pending = ImageTk.PhotoImage(Image.open(ICON_PENDING))
        self._img_confirmed = ImageTk.PhotoImage(Image.open(ICON_CONFIRMED))
        self._img_send = ImageTk.PhotoImage(Image.open(ICON_SEND))
        self._img_exit = ImageTk.PhotoImage(Image.open(ICON_EXIT))
        self._img_warn = ImageTk.PhotoImage(Image.open(ICON_WARNING))

        #  Initialise up key variables
        self._awaiting_cfgmsg = False
        self._awaiting_ack = False
        self._cfg_msg_command = None
        self._preset_command = None
        self._status_preset = StringVar()
        self._status_cfgmsg = StringVar()
        self._ubx_baudrate = IntVar()
        self._ubx_portid = StringVar()
        self._ubx_inprot = IntVar()
        self._ubx_outprot = IntVar()
        self._ddc_rate = IntVar()
        self._uart1_rate = IntVar()
        self._usb_rate = IntVar()
        self._spi_rate = IntVar()
        self._sw_version = StringVar()
        self._hw_version = StringVar()
        self._fw_version = StringVar()
        self._ant_status = StringVar()
        self._ant_power = StringVar()
        self._protocol = StringVar()
        self._gnss_supported = StringVar()

        self._body()
        self._do_layout()
        self._attach_events()
        self._reset()

    def _body(self):
        """
        Set up frame and widgets.
        """

        LBL_COL = "snow2"
        self._frm_container = Frame(self._dialog, borderwidth=2, relief="groove")
        con = self._frm_container
        for i in range(7):
            con.grid_columnconfigure(i, weight=1)
        con.grid_rowconfigure(1, weight=1)

        con.option_add("*Font", self.__app.font_sm)

        self._lbl_title = Label(
            con,
            text=LBLUBXCONFIG,
            bg=BGCOL,
            fg=FGCOL,
            justify=LEFT,
            font=self.__app.font_md,
        )

        # *******************************************************
        # Software and Hardware versions
        # *******************************************************
        INFCOL = "steelblue3"
        self._frm_device_info = Frame(con, borderwidth=2)
        inf = self._frm_device_info
        self._lbl_swverl = Label(inf, text="Software")
        self._lbl_swver = Label(inf, textvariable=self._sw_version, fg=INFCOL)
        self._lbl_hwverl = Label(inf, text="Hardware")
        self._lbl_hwver = Label(inf, textvariable=self._hw_version, fg=INFCOL)
        self._lbl_fwverl = Label(inf, text="Firmware")
        self._lbl_fwver = Label(inf, textvariable=self._fw_version, fg=INFCOL)
        self._lbl_romverl = Label(inf, text="Protocol")
        self._lbl_romver = Label(inf, textvariable=self._protocol, fg=INFCOL)
        self._lbl_gnssl = Label(inf, text="GNSS/AS")
        self._lbl_gnss = Label(inf, textvariable=self._gnss_supported, fg=INFCOL)
        self._lbl_ant_statusl = Label(inf, text="Antenna Status")
        self._lbl_ant_status = Label(inf, textvariable=self._ant_status, fg=INFCOL)
        self._lbl_ant_powerl = Label(inf, text="Antenna Power")
        self._lbl_ant_power = Label(inf, textvariable=self._ant_power, fg=INFCOL)

        # *******************************************************
        # Port Configuration
        # *******************************************************
        self._lbl_cfg_port = Label(con, text=LBLCFGPRT, bg=LBL_COL, anchor="w")
        self._lbl_ubx_portid = Label(con, text="Port ID")
        self._spn_ubx_portid = Spinbox(
            con,
            values=PORTIDS,
            width=8,
            state=READONLY,
            readonlybackground=ENTCOL,
            wrap=True,
            textvariable=self._ubx_portid,
            command=lambda: self._on_select_portid(),
        )
        self._lbl_ubx_baudrate = Label(con, text="Baud")
        self._spn_ubx_baudrate = Spinbox(
            con,
            values=(BAUDRATES),
            width=6,
            state=READONLY,
            readonlybackground=ENTCOL,
            wrap=True,
            textvariable=self._ubx_baudrate,
        )
        self._lbl_inprot = Label(con, text="Input")
        self._rad_inprot_nmea = Radiobutton(
            con, text="NMEA", variable=self._ubx_inprot, value=2
        )
        self._rad_inprot_ubx = Radiobutton(
            con, text="UBX", variable=self._ubx_inprot, value=1
        )
        self._rad_inprot_rtcm = Radiobutton(
            con, text="RTCM", variable=self._ubx_inprot, value=4
        )
        self._rad_inprot_both = Radiobutton(
            con, text="ALL", variable=self._ubx_inprot, value=7
        )
        self._lbl_outprot = Label(con, text="Output")
        self._rad_outprot_nmea = Radiobutton(
            con, text="NMEA", variable=self._ubx_outprot, value=2
        )
        self._rad_outprot_ubx = Radiobutton(
            con, text="UBX", variable=self._ubx_outprot, value=1
        )
        self._rad_outprot_both = Radiobutton(
            con, text="ALL", variable=self._ubx_outprot, value=3
        )
        self._lbl_send_port = Label(con, image=self._img_pending)
        self._btn_send_port = Button(
            con,
            image=self._img_send,
            width=50,
            command=self._on_send_port,
            font=self.__app.font_md,
        )

        # *******************************************************
        # CFG-MSG Message Selection
        # *******************************************************
        MAX_RATE = 0xFF
        self._lbl_cfg_msg = Label(con, text=LBLCFGMSG, bg=LBL_COL, anchor="w")
        self._lbx_cfg_msg = Listbox(
            con,
            border=2,
            relief="sunken",
            bg=ENTCOL,
            height=6,
            justify=LEFT,
            exportselection=False,
        )
        self._scr_cfg_msg = Scrollbar(con, orient=VERTICAL)
        self._lbx_cfg_msg.config(yscrollcommand=self._scr_cfg_msg.set)
        self._scr_cfg_msg.config(command=self._lbx_cfg_msg.yview)
        self._lbl_ddc = Label(con, text="DDC (I2C)")
        self._spn_ddc = Spinbox(
            con,
            width=3,
            from_=0,
            to=MAX_RATE,
            textvariable=self._ddc_rate,
            state=READONLY,
            readonlybackground=ENTCOL,
        )
        self._lbl_uart1 = Label(con, text="UART1")
        self._spn_uart1 = Spinbox(
            con,
            width=3,
            from_=0,
            to=MAX_RATE,
            textvariable=self._uart1_rate,
            state=READONLY,
            readonlybackground=ENTCOL,
        )
        self._lbl_usb = Label(con, text="USB")
        self._spn_usb = Spinbox(
            con,
            width=3,
            from_=0,
            to=MAX_RATE,
            textvariable=self._usb_rate,
            state=READONLY,
            readonlybackground=ENTCOL,
        )
        self._lbl_spi = Label(con, text="SPI")
        self._spn_spi = Spinbox(
            con,
            width=3,
            from_=0,
            to=MAX_RATE,
            textvariable=self._spi_rate,
            state=READONLY,
            readonlybackground=ENTCOL,
        )
        self._lbl_send_cfg_msg = Label(con)
        self._btn_send_cfg_msg = Button(
            con,
            image=self._img_send,
            width=50,
            fg="green",
            command=self._on_send_cfg_msg,
            font=self.__app.font_md,
        )
        self._lbl_status_cfg_msg = Label(
            con, textvariable=self._status_cfgmsg, anchor="w"
        )

        # *******************************************************
        # PRESET Message Selection
        # *******************************************************
        self._lbl_presets = Label(con, text=LBLPRESET, bg=LBL_COL, anchor="w")
        self._lbx_preset = Listbox(
            con,
            border=2,
            relief="sunken",
            bg=ENTCOL,
            height=5,
            justify=LEFT,
            exportselection=False,
        )
        self._scr_presetv = Scrollbar(con, orient=VERTICAL)
        self._scr_preseth = Scrollbar(con, orient=HORIZONTAL)
        self._lbx_preset.config(yscrollcommand=self._scr_presetv.set)
        self._lbx_preset.config(xscrollcommand=self._scr_preseth.set)
        self._scr_presetv.config(command=self._lbx_preset.yview)
        self._scr_preseth.config(command=self._lbx_preset.xview)
        self._lbl_send_preset = Label(con)
        self._btn_send_preset = Button(
            con,
            image=self._img_send,
            width=50,
            fg="green",
            command=self._on_send_preset,
            font=self.__app.font_md,
        )

        self._lbl_status = Label(con, textvariable=self._status_preset, anchor="w")
        self._btn_exit = Button(
            con,
            image=self._img_exit,
            width=50,
            fg="red",
            command=self._on_exit,
            font=self.__app.font_md,
        )

    def _do_layout(self):
        """
        Position widgets in frame.
        """

        self._frm_container.grid(
            column=0,
            row=0,
            columnspan=6,
            padx=3,
            pady=3,
            ipadx=5,
            ipady=5,
            sticky=(N, S, W, E),
        )
        self._lbl_title.grid(column=0, row=0, columnspan=6, ipady=3, sticky=(W, E))

        # *******************************************************
        # MON-VER Device Information
        # *******************************************************
        self._frm_device_info.grid(column=0, row=1, columnspan=6, sticky=(W, E))
        self._lbl_swverl.grid(column=0, row=0, padx=2, sticky=(W))
        self._lbl_swver.grid(column=1, row=0, columnspan=2, padx=2, sticky=(W))
        self._lbl_hwverl.grid(column=3, row=0, padx=2, sticky=(W))
        self._lbl_hwver.grid(column=4, row=0, columnspan=2, padx=2, sticky=(W))
        self._lbl_fwverl.grid(column=0, row=1, padx=2, sticky=(W))
        self._lbl_fwver.grid(column=1, row=1, columnspan=2, padx=2, sticky=(W))
        self._lbl_romverl.grid(column=3, row=1, padx=2, sticky=(W))
        self._lbl_romver.grid(column=4, row=1, columnspan=2, padx=2, sticky=(W))
        self._lbl_gnssl.grid(column=0, row=2, columnspan=1, padx=2, sticky=(W))
        self._lbl_gnss.grid(column=1, row=2, columnspan=4, padx=2, sticky=(W))

        # *******************************************************
        # MON-HW Antenna Status
        # *******************************************************
        self._lbl_ant_statusl.grid(column=0, row=3, columnspan=1, padx=2, sticky=(W))
        self._lbl_ant_status.grid(column=1, row=3, columnspan=2, padx=2, sticky=(W))
        self._lbl_ant_powerl.grid(column=3, row=3, columnspan=1, padx=2, sticky=(W))
        self._lbl_ant_power.grid(column=4, row=3, columnspan=2, padx=2, sticky=(W))

        # *******************************************************
        # CFG-PRT Port Configuration
        # *******************************************************
        ttk.Separator(self._frm_container).grid(
            column=0, row=2, columnspan=6, padx=3, pady=3, sticky=(W, E)
        )
        self._lbl_cfg_port.grid(column=0, row=3, columnspan=6, padx=3, sticky=(W, E))
        self._lbl_ubx_portid.grid(column=0, row=4, columnspan=1, sticky=(W))
        self._spn_ubx_portid.grid(column=1, row=4, columnspan=1, sticky=(W))
        self._lbl_ubx_baudrate.grid(column=2, row=4, columnspan=1, sticky=(W))
        self._spn_ubx_baudrate.grid(column=3, row=4, columnspan=2, sticky=(W))
        self._lbl_inprot.grid(column=0, row=5, sticky=(W))
        self._rad_inprot_nmea.grid(column=1, row=5, sticky=(W))
        self._rad_inprot_ubx.grid(column=2, row=5, sticky=(W))
        self._rad_inprot_rtcm.grid(column=3, row=5, sticky=(W))
        self._rad_inprot_both.grid(column=4, row=5, sticky=(W))
        self._lbl_outprot.grid(column=0, row=6, sticky=(W))
        self._rad_outprot_nmea.grid(column=1, row=6, sticky=(W))
        self._rad_outprot_ubx.grid(column=2, row=6, sticky=(W))
        self._rad_outprot_both.grid(column=3, row=6, sticky=(W))
        self._btn_send_port.grid(column=4, row=4, ipadx=3, ipady=3, sticky=(E))
        self._lbl_send_port.grid(column=5, row=4, ipadx=3, ipady=3, sticky=(W))

        # *******************************************************
        # CFG-MSG Message Selection
        # *******************************************************
        ttk.Separator(self._frm_container).grid(
            column=0, row=7, columnspan=6, padx=3, pady=3, sticky=(W, E)
        )
        self._lbl_cfg_msg.grid(column=0, row=8, columnspan=6, padx=3, sticky=(W, E))
        self._lbx_cfg_msg.grid(
            column=0, row=9, columnspan=2, rowspan=4, padx=3, pady=3, sticky=(W, E)
        )
        self._scr_cfg_msg.grid(column=1, row=9, rowspan=4, sticky=(N, S, E))
        self._lbl_ddc.grid(column=2, row=9, padx=0, pady=0, sticky=(E))
        self._spn_ddc.grid(column=3, row=9, padx=0, pady=0, sticky=(W))
        self._lbl_uart1.grid(column=2, row=10, padx=0, pady=0, sticky=(E))
        self._spn_uart1.grid(column=3, row=10, padx=0, pady=0, sticky=(W))
        self._lbl_usb.grid(column=2, row=11, padx=0, pady=0, sticky=(E))
        self._spn_usb.grid(column=3, row=11, padx=0, pady=0, sticky=(W))
        self._lbl_spi.grid(column=2, row=12, padx=0, pady=0, sticky=(E))
        self._spn_spi.grid(column=3, row=12, padx=0, pady=0, sticky=(W))
        self._btn_send_cfg_msg.grid(
            column=4, row=9, rowspan=4, ipadx=3, ipady=3, sticky=(E)
        )
        self._lbl_send_cfg_msg.grid(
            column=5, row=9, rowspan=4, ipadx=3, ipady=3, sticky=(W)
        )

        # *******************************************************
        # PRESET Message Selection
        # *******************************************************
        ttk.Separator(self._frm_container).grid(
            column=0, row=16, columnspan=6, padx=3, pady=3, sticky=(W, E)
        )
        self._lbl_presets.grid(column=0, row=17, columnspan=6, padx=3, sticky=(W, E))
        self._lbx_preset.grid(
            column=0, row=18, columnspan=4, padx=3, pady=3, sticky=(W, E)
        )
        self._scr_presetv.grid(column=3, row=18, sticky=(N, S, E))
        self._scr_preseth.grid(column=0, row=19, columnspan=4, sticky=(W, E))
        self._btn_send_preset.grid(column=4, row=18, ipadx=3, ipady=3, sticky=(E))
        self._lbl_send_preset.grid(
            column=5, row=18, rowspan=2, ipadx=3, ipady=3, sticky=(W)
        )

        ttk.Separator(self._frm_container).grid(
            column=0, row=20, columnspan=6, padx=3, pady=3, sticky=(W, E)
        )

        self._lbl_status.grid(
            column=0, row=21, columnspan=4, ipadx=3, ipady=3, sticky=(W, E)
        )
        self._btn_exit.grid(column=4, row=21, ipadx=3, ipady=3, sticky=(E))

    def _attach_events(self):
        """
        Bind listbox selection events.
        """

        self._lbx_cfg_msg.bind("<<ListboxSelect>>", self._on_select_cfg_msg)
        self._lbx_preset.bind("<<ListboxSelect>>", self._on_select_preset)

    def _reset(self):
        """
        Reset settings to defaults.
        """

        # Poll current port & usb configuration
        if self.__app.serial_handler.connected:
            ubh.poll_ubx_config(self.__app.serial_handler.serial)

        # Load user-defined presets if there are any
        self._userpresets = self.__app.file_handler.load_user_presets()

        self._ubx_baudrate.set(str(self.__app.ubx_handler.ubx_baudrate))
        self._ubx_inprot.set(self.__app.ubx_handler.ubx_inprot)
        self._ubx_outprot.set(self.__app.ubx_handler.ubx_outprot)

        idx = 1
        for _, val in UBX_CONFIG_MESSAGES.items():
            self._lbx_cfg_msg.insert(idx, val)
            idx += 1

        idx = 1
        for pst in PRESET_COMMMANDS:
            self._lbx_preset.insert(idx, pst)
            idx += 1

        for upst in self._userpresets:
            self._lbx_preset.insert(idx, "USER " + upst)
            idx += 1

    def update(self, cfgtype="CFG-MSG", **kwargs):
        """
        Receives polled confirmation messages from the uxb_handler and
        updates panel settings according to the information received.

        NB: not absolutely bullet-proof as confirmation messages cannot
        be unequivocally linked to specific commands, but the best
        available indication of current state.

        :param str cfgtype: type of config message received
        :kwargs kwargs: optional key value pairs
        """

        # MON-VER information (for firmware version)
        if cfgtype == "MON-VER":
            self._sw_version.set(kwargs.get("swversion", ""))
            self._hw_version.set(kwargs.get("hwversion", ""))
            self._fw_version.set(kwargs.get("fwversion", ""))
            self._protocol.set(kwargs.get("protocol", ""))
            self._gnss_supported.set(kwargs.get("gnsssupported", ""))

        # MON-HW information (for antenna status)
        if cfgtype == "MON-HW":
            self._ant_status.set(ANTSTATUS[kwargs.get("antstatus", 1)])
            self._ant_power.set(ANTPOWER[kwargs.get("antpower", 2)])

        # CFG-PRT command confirmation
        if "baudrate" in kwargs:
            self._ubx_baudrate.set(str(kwargs["baudrate"]))
        if "inprot" in kwargs:
            self._ubx_inprot.set(kwargs["inprot"])
        if "outprot" in kwargs:
            self._ubx_outprot.set(kwargs["outprot"])
        self._lbl_send_port.config(image=self._img_confirmed)

        # CFG-MSG command confirmation
        if self._awaiting_cfgmsg:
            if cfgtype == "CFG-MSG":
                self.set_status(f"{cfgtype} received", "green")
                self._ddc_rate.set(kwargs.get("ddcrate", 0))
                self._uart1_rate.set(kwargs.get("uart1rate", 0))
                self._usb_rate.set(kwargs.get("usbrate", 0))
                self._spi_rate.set(kwargs.get("spirate", 0))
                self._lbl_send_cfg_msg.config(image=self._img_confirmed)
                self._awaiting_cfgmsg = False
            if cfgtype == "ACK-NAK":
                self.set_status(f"{cfgtype} rejected", "red")
                self._lbl_send_cfg_msg.config(image=self._img_warn)
                self._awaiting_cfgmsg = False

        # PRESET command(s) confirmation
        if self._awaiting_ack:
            if cfgtype == "ACK-ACK":
                self.set_status(f"{cfgtype} acknowledgement received", "green")
                self._lbl_send_preset.config(image=self._img_confirmed)
                self._awaiting_ack = False
            if cfgtype == "ACK-NAK":
                self.set_status(f"{cfgtype} acknowledgement received", "red")
                self._lbl_send_preset.config(image=self._img_confirmed)
                self._awaiting_ack = False
        elif not self._awaiting_ack and cfgtype not in ("ACK-ACK", "ACK-NAK"):
            self.set_status(f"{cfgtype} response received", "green")

    def _on_select_portid(self):
        """
        Handle portid selection
        """

        self._do_poll_prt()  # poll for confirmation
        self._lbl_send_port.config(image=self._img_pending)
        self.set_status("CFG-PRT configuration message(s) sent")

    def _on_send_port(self, *args, **kwargs):
        """
        Handle Send port config button press.
        """

        port = int(self._ubx_portid.get()[0:1])
        portID = int.to_bytes(port, 1, "little", signed=False)
        reserved0 = b"\x00"
        reserved4 = b"\x00\00"
        reserved5 = b"\x00\00"
        txReady = b"\x00\x00"
        if port == 0:  # DDC I2C
            mode = b"\x84\x00\x00\x00"
        elif port == 1:  # UART1
            mode = b"\xc0\x08\x00\x00"
        else:
            mode = b"\x00\x00\x00\x00"
        baudRate = int.to_bytes(self._ubx_baudrate.get(), 4, "little", signed=False)
        inProtoMask = int.to_bytes(self._ubx_inprot.get(), 2, "little", signed=False)
        outProtoMask = int.to_bytes(self._ubx_outprot.get(), 2, "little", signed=False)
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

        self._do_poll_prt()  # poll for confirmation
        self._lbl_send_port.config(image=self._img_pending)
        self.set_status("CFG-PRT configuration message(s) sent")

    def _on_select_cfg_msg(self, *args, **kwargs):
        """
        CFG-MSG command has been selected.
        """

        idx = self._lbx_cfg_msg.curselection()
        self._cfg_msg_command = self._lbx_cfg_msg.get(idx)

        # poll selected message configuration to get current message rates
        msg = key_from_val(UBX_CONFIG_MESSAGES, self._cfg_msg_command)
        data = UBXMessage("CFG", "CFG-MSG", POLL, payload=msg)
        self.__app.serial_handler.serial_write(data.serialize())
        self._awaiting_cfgmsg = True
        self._lbl_send_cfg_msg.config(image=self._img_pending)

    def _on_send_cfg_msg(self):
        """
        CFG-MSG command send button has been clicked.
        """

        msg = key_from_val(UBX_CONFIG_MESSAGES, self._cfg_msg_command)
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
        data = UBXMessage("CFG", "CFG-MSG", POLL, payload=msg)  # poll for a response
        self.__app.serial_handler.serial_write(data.serialize())

        self.set_status("CFG-MSG command sent")
        self._awaiting_cfgmsg = True
        self._lbl_send_cfg_msg.config(image=self._img_pending)

    def _on_select_preset(self, *args, **kwargs):
        """
        Preset command has been selected.
        """

        idx = self._lbx_preset.curselection()
        self._preset_command = self._lbx_preset.get(idx)

    def _on_send_preset(self, *args, **kwargs):
        """
        Preset command send button has been clicked.
        """

        confirmed = True
        try:

            if self._preset_command == PSTRESET:
                confirmed = self._do_factory_reset()
            elif self._preset_command == PSTSAVE:
                confirmed = self._do_save_config()
            elif self._preset_command == PSTMINNMEAON:
                self._do_set_minnmea()
            elif self._preset_command == PSTALLNMEAON:
                self._do_set_allnmea(1)
            elif self._preset_command == PSTALLNMEAOFF:
                self._do_set_allnmea(0)
            elif self._preset_command == PSTMINUBXON:
                self._do_set_minNAV()
            elif self._preset_command == PSTALLUBXON:
                self._do_set_allNAV(1)
            elif self._preset_command == PSTALLUBXOFF:
                self._do_set_allNAV(0)
            elif self._preset_command == PSTALLINFON:
                self._do_set_inf(True)
            elif self._preset_command == PSTALLINFOFF:
                self._do_set_inf(False)
            elif self._preset_command == PSTALLLOGON:
                self._do_set_log(4)
            elif self._preset_command == PSTALLLOGOFF:
                self._do_set_log(0)
            elif self._preset_command == PSTALLMONON:
                self._do_set_mon(4)
            elif self._preset_command == PSTALLMONOFF:
                self._do_set_mon(0)
            elif self._preset_command == PSTALLRXMON:
                self._do_set_rxm(4)
            elif self._preset_command == PSTALLRXMOFF:
                self._do_set_rxm(0)
            elif self._preset_command == PSTPOLLPORT:
                self._do_poll_prt()
            elif self._preset_command == PSTPOLLINFO:
                self._do_poll_inf()
            elif self._preset_command == PSTPOLLALL:
                self._do_poll_all()
            else:
                self._do_user_defined(self._preset_command)

            if confirmed:
                self.set_status("Command(s) sent", "blue")
                self._awaiting_ack = True
                self._lbl_send_preset.config(image=self._img_pending)
            else:
                self.set_status("Command(s) cancelled", "blue")

        except Exception as err:  # pylint: disable=broad-except
            self.set_status(f"Error {err}", "red")
            self._lbl_send_preset.config(image=self._img_warn)

    def _do_poll_all(self):
        """
        Poll INF message configuration
        """

        for msgtype in UBX_PAYLOADS_POLL:
            if msgtype[0:3] == "CFG" and msgtype not in (
                "CFG-INF",
                "CFG-MSG",
                "CFG-PRT-IO",
                "CFG-TP5-TPX",
            ):
                msg = UBXMessage("CFG", msgtype, POLL)
                self.__app.serial_handler.serial_write(msg.serialize())

    def _do_poll_inf(self):
        """
        Poll INF message configuration
        """

        for payload in (b"\x00", b"\x01"):  # UBX & NMEA
            msg = UBXMessage("CFG", "CFG-INF", POLL, payload=payload)
            self.__app.serial_handler.serial_write(msg.serialize())

    def _do_poll_prt(self):
        """
        Poll PRT message configuration
        """

        #         msg = UBXMessage("CFG", "CFG-PRT", POLL)
        portID = int(self._ubx_portid.get()[0:1])
        msg = UBXMessage("CFG", "CFG-PRT", POLL, portID=portID)
        self.__app.serial_handler.serial_write(msg.serialize())

    def _do_set_inf(self, onoff: int):
        """
        Turn on device information messages INF

        :param int onoff: on/off boolean
        """

        if onoff:
            mask = b"\x1f"  # all INF msgs
        else:
            mask = b"\x01"  # errors only
        for protocolID in (b"\x00", b"\x01"):  # UBX and NMEA
            reserved1 = b"\x00\x00\x00"
            infMsgMaskDDC = mask
            infMsgMaskUART1 = mask
            infMsgMaskUART2 = mask
            infMsgMaskUSB = mask
            infMsgMaskSPI = mask
            reserved2 = b"\x00"
            payload = (
                protocolID
                + reserved1
                + infMsgMaskDDC
                + infMsgMaskUART1
                + infMsgMaskUART2
                + infMsgMaskUSB
                + infMsgMaskSPI
                + reserved2
            )
            msg = UBXMessage("CFG", "CFG-INF", SET, payload=payload)
            self.__app.serial_handler.serial_write(msg.serialize())
            self._do_poll_inf()  # poll results

    def _do_set_log(self, msgrate: int):
        """
        Turn on all device logging messages LOG

        :param int msgrate: message rate (i.e. every nth position solution)
        """

        for msgtype in UBX_CONFIG_MESSAGES:
            if msgtype[0:1] == b"\x21":
                self._do_cfgmsg(msgtype, msgrate)

    def _do_set_mon(self, msgrate):
        """
        Turn on all device monitoring messages MON

        :param int msgrate: message rate (i.e. every nth position solution)
        """

        for msgtype in UBX_CONFIG_MESSAGES:
            if msgtype[0:1] == b"\x0A":
                self._do_cfgmsg(msgtype, msgrate)

    def _do_set_rxm(self, msgrate):
        """
        Turn on all device receiver management messages RXM

        :param int msgrate: message rate (i.e. every nth position solution)
        """

        for msgtype in UBX_CONFIG_MESSAGES:
            if msgtype[0:1] == b"\x02":
                self._do_cfgmsg(msgtype, msgrate)

    def _do_set_minnmea(self):
        """
        Turn on minimum set of NMEA messages (GGA & GSA & GSV)
        """

        for msgtype in UBX_CONFIG_MESSAGES:
            if msgtype[0:1] == b"\xf0":  # standard NMEA
                if msgtype in (b"\xf0\x00", b"\xf0\x02"):  # GGA, GSA
                    self._do_cfgmsg(msgtype, 1)
                elif msgtype == b"\xf0\x03":  # GSV
                    self._do_cfgmsg(msgtype, 4)
                else:
                    self._do_cfgmsg(msgtype, 0)
            if msgtype[0:1] == b"\xf1":  # proprietary NMEA
                self._do_cfgmsg(msgtype, 0)

    def _do_set_minNAV(self):
        """
        Turn on minimum set of UBX-NAV messages (PVT & SVINFO)
        """

        for msgtype in UBX_CONFIG_MESSAGES:
            if msgtype[0:1] == b"\x01":  # UBX-NAV
                if msgtype == b"\x01\x07":  # NAV-PVT
                    self._do_cfgmsg(msgtype, 1)
                #                 elif msgtype == b"\x01\x30":  # NAV-SVINFO (deprecated)
                #                     self._do_cfgmsg(msgtype, 4)
                elif msgtype == b"\x01\x35":  # NAV-SAT
                    self._do_cfgmsg(msgtype, 4)
                else:
                    self._do_cfgmsg(msgtype, 0)

    def _do_set_allnmea(self, msgrate):
        """
        Turn on all NMEA messages

        :param int msgrate: message rate (i.e. every nth position solution)
        """

        for msgtype in UBX_CONFIG_MESSAGES:
            if msgtype[0:1] in (b"\xf0", b"\xf1"):
                self._do_cfgmsg(msgtype, msgrate)

    def _do_set_allNAV(self, msgrate):
        """
        Turn on all UBX-NAV messages

        :param int msgrate: message rate (i.e. every nth position solution)
        """

        for msgtype in UBX_CONFIG_MESSAGES:
            if msgtype[0:1] == b"\x01":
                self._do_cfgmsg(msgtype, msgrate)

    def _do_cfgmsg(self, msgtype: str, msgrate: int):
        """
        Set rate for specified message type via CFG-MSG

        NB A rate of n means 'for every nth position solution',
        so values > 1 mean the message is sent less often.

        :param str msgtype: type of config message
        :param int msgrate: message rate (i.e. every nth position solution)
        """

        msgClass = int.from_bytes(msgtype[0:1], "little", signed=False)
        msgID = int.from_bytes(msgtype[1:2], "little", signed=False)
        msg = UBXMessage(
            "CFG",
            "CFG-MSG",
            SET,
            msgClass=msgClass,
            msgID=msgID,
            rateDDC=msgrate,
            rateUART1=msgrate,
            rateUSB=msgrate,
            rateSPI=msgrate,
        )
        self.__app.serial_handler.serial_write(msg.serialize())

    def _do_factory_reset(self) -> bool:
        """
        Restore to factory defaults stored in battery-backed RAM
        but display confirmation message box first.

        :return boolean signifying whether OK was pressed
        :rtype bool
        """

        if messagebox.askokcancel(DLGRESET, DLGRESETCONFIRM):
            clearMask = b"\x1f\x1f\x00\x00"
            loadMask = b"\x1f\x1f\x00\x00"
            deviceMask = b"\x07"  # target RAM, Flash and EEPROM
            msg = UBXMessage(
                "CFG",
                "CFG-CFG",
                SET,
                clearMask=clearMask,
                loadMask=loadMask,
                deviceMask=deviceMask,
            )
            self.__app.serial_handler.serial_write(msg.serialize())
            return True

        return False

    def _do_save_config(self) -> bool:
        """
        Save current configuration to persistent storage
        but display confirmation message box first.

        :return boolean signifying whether OK was pressed
        :rtype bool
        """

        if messagebox.askokcancel(DLGSAVE, DLGSAVECONFIRM):
            saveMask = b"\x1f\x1f\x00\x00"
            deviceMask = b"\x07"  # target RAM, Flash and EEPROM
            msg = UBXMessage(
                "CFG", "CFG-CFG", SET, saveMask=saveMask, deviceMask=deviceMask
            )
            self.__app.serial_handler.serial_write(msg.serialize())
            return True

        return False

    def _do_user_defined(self, command: str):
        """
        Parse and send user-defined command(s).

        This could result in any number of errors if the
        uxbpresets file contains garbage, so there's a broad
        catch-all-exceptions in the calling routine.

        :param str command: user defined message constructor(s)
        """

        try:
            seg = command.split(",")
            for i in range(1, len(seg), 4):
                ubx_class = seg[i].strip()
                ubx_id = seg[i + 1].strip()
                payload = seg[i + 2].strip()
                mode = int(seg[i + 3].rstrip("\r\n"))
                if payload != "":
                    payload = bytes(bytearray.fromhex(payload))
                    msg = UBXMessage(ubx_class, ubx_id, mode, payload=payload)
                else:
                    msg = UBXMessage(ubx_class, ubx_id, mode)
                self.__app.serial_handler.serial_write(msg.serialize())
        except Exception as err:  # pylint: disable=broad-except
            self.__app.set_status(f"Error {err}", "red")
            self._lbl_send_preset.config(image=self._img_warn)

    def set_status(self, message: str, color: str = "blue"):
        """
        Set status message.

        :param str message: message to be displayed
        :param str color: rgb color of text (blue)
        """

        message = (message[:50] + "..") if len(message) > 50 else message
        self._lbl_status.config(fg=color)
        self._status_preset.set("  " + message)

    def _on_exit(self, *args, **kwargs):
        """
        Handle Exit button press.
        """

        self.__master.update_idletasks()
        self.__app.dlg_ubxconfig = None
        self._dialog.destroy()

    def get_size(self):
        """
        Get current frame size.
        """

        self.__master.update_idletasks()  # Make sure we know about any resizing
        return (self._dialog.winfo_width(), self._dialog.winfo_height())
