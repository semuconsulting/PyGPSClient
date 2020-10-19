'''
UBX Configuration frame class for PyGPSClient application.

This handles the UBX Configuration Dialog panel and receives polled
responses from the ubx_handler module.

Created on 22 Sep 2020

@author: semuadmin
'''
# pylint: disable=invalid-name, unused-argument

from tkinter import ttk, messagebox, Toplevel, Frame, Checkbutton, Radiobutton, Listbox, \
                    Spinbox, Scrollbar, Button, Label, StringVar, \
                    IntVar, N, S, E, W, LEFT, VERTICAL, HORIZONTAL

from PIL import ImageTk, Image
from pyubx2 import UBXMessage, POLL, SET, UBX_CONFIG_MESSAGES

from .globals import BGCOL, FGCOL, ENTCOL, ICON_APP, ICON_SEND, ICON_EXIT, ICON_WARNING, \
                     ICON_PENDING, ICON_CONFIRMED, BAUDRATES, READONLY
from .strings import LBLUBXCONFIG, LBLCFGPRT, LBLCFGMSG, LBLPRESET, DLGUBXCONFIG, DLGRESET, \
                     DLGSAVE, DLGRESETCONFIRM, DLGSAVECONFIRM, PSTRESET, PSTSAVE, \
                     PSTMINNMEAON, PSTALLNMEAON, PSTALLNMEAOFF, PSTMINUBXON, PSTALLUBXON, \
                     PSTALLUBXOFF, PSTALLINFON, PSTALLINFOFF, PSTALLLOGON, PSTALLLOGOFF, \
                     PSTALLMONON, PSTALLMONOFF, PSTALLRXMON, PSTALLRXMOFF, PSTPOLLPORT, \
                     PSTPOLLINFO

from .ubx_handler import UBXHandler as ubh, CFG_MSG_OFF, CFG_MSG_ON

PRESET_COMMMANDS = [
PSTRESET, PSTSAVE, PSTMINNMEAON, PSTALLNMEAON, PSTALLNMEAOFF,
PSTMINUBXON, PSTALLUBXON, PSTALLUBXOFF, PSTALLINFON, PSTALLINFOFF,
PSTALLLOGON, PSTALLLOGOFF, PSTALLMONON, PSTALLMONOFF, PSTALLRXMON,
PSTALLRXMOFF, PSTPOLLPORT, PSTPOLLINFO
]


class UBXConfigDialog():
    ''',
    UBXConfigDialog class.
    '''

    def __init__(self, app, *args, **kwargs):
        '''
        Constructor.
        '''

        self.__app = app  # Reference to main application class
        self.__master = self.__app.get_master()  # Reference to root class (Tk)
        self._dialog = Toplevel()
        self._dialog.transient(self.__app)
        self._dialog.resizable(False, False)
        self._dialog.title = DLGUBXCONFIG
        wd, hd = self.get_size()
        wa = self.__master.winfo_width()
        ha = self.__master.winfo_height()
        self._dialog.geometry("+%d+%d" % (int(wa / 2 - wd / 2), int(ha / 2 - hd / 2)))
        self._img_icon = ImageTk.PhotoImage(Image.open (ICON_APP))
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
        self._ubx_baudrate = StringVar()
        self._ubx_inprot = IntVar()
        self._ubx_outprot = IntVar()
        self._ddc_onoff = IntVar()
        self._uart1_onoff = IntVar()
        self._usb_onoff = IntVar()
        self._spi_onoff = IntVar()

        self._body()
        self._do_layout()
        self._attach_events()
        self._reset()

    def _body(self):
        '''
        Set up frame and widgets.
        '''

        LBL_COL = "snow2"
        self._frm_container = Frame(self._dialog, borderwidth=2, relief="groove")
        con = self._frm_container
        for i in range(7):
            con.grid_columnconfigure(i, weight=1)
        con.grid_rowconfigure(1, weight=1)

        con.option_add("*Font", self.__app.font_sm)

        self._lbl_title = Label(con, text=LBLUBXCONFIG, bg=BGCOL, fg=FGCOL,
                                justify=LEFT, font=self.__app.font_md, width=55)
        # *******************************************************
        # Port Configuration
        # *******************************************************
        self._lbl_cfg_port = Label(con, text=LBLCFGPRT,
                                   bg=LBL_COL, anchor='w')
        self._lbl_ubx_baudrate = Label(con, text="Baud rate")
        self._spn_ubx_baudrate = Spinbox(con,
                                         values=(BAUDRATES),
                                         width=8, state=READONLY, readonlybackground=ENTCOL,
                                         wrap=True, textvariable=self._ubx_baudrate)
        self._lbl_inprot = Label(con, text="Input")
        self._rad_inprot_nmea = Radiobutton(con, text="NMEA",
                                             variable=self._ubx_inprot, value=2)
        self._rad_inprot_ubx = Radiobutton(con, text="UBX",
                                            variable=self._ubx_inprot, value=1)
        self._rad_inprot_rtcm = Radiobutton(con, text="RTCM",
                                            variable=self._ubx_inprot, value=4)
        self._rad_inprot_both = Radiobutton(con, text="ALL",
                                             variable=self._ubx_inprot, value=7)
        self._lbl_outprot = Label(con, text="Output")
        self._rad_outprot_nmea = Radiobutton(con, text="NMEA",
                                             variable=self._ubx_outprot, value=2)
        self._rad_outprot_ubx = Radiobutton(con, text="UBX",
                                            variable=self._ubx_outprot, value=1)
        self._rad_outprot_both = Radiobutton(con, text="ALL",
                                             variable=self._ubx_outprot, value=3)
        self._lbl_send_port = Label(con)
        self._btn_send_port = Button(con, image=self._img_send, width=50,
                                     command=self._on_send_port,
                                     font=self.__app.font_md)

        # *******************************************************
        # CFG-MSG Message Selection
        # *******************************************************
        self._lbl_cfg_msg = Label(con, text=LBLCFGMSG,
                                  bg=LBL_COL, anchor='w')
        self._lbx_cfg_msg = Listbox(con, border=2,
                                 relief="sunken", bg=ENTCOL,
                                 height=7, justify=LEFT,
                                 exportselection=False)
        self._scr_cfg_msg = Scrollbar(con, orient=VERTICAL)
        self._lbx_cfg_msg.config(yscrollcommand=self._scr_cfg_msg.set)
        self._scr_cfg_msg.config(command=self._lbx_cfg_msg.yview)
        self._chk_ddc = Checkbutton(con, text='DDC (I2C)', variable=self._ddc_onoff)
        self._chk_uart1 = Checkbutton(con, text='UART1', variable=self._uart1_onoff)
        self._chk_usb = Checkbutton(con, text='USB', variable=self._usb_onoff)
        self._chk_spi = Checkbutton(con, text='SPI', variable=self._spi_onoff)
        self._lbl_send_cfg_msg = Label(con)
        self._btn_send_cfg_msg = Button(con, image=self._img_send, width=50, fg="green",
                                       command=self._on_send_cfg_msg, font=self.__app.font_md)
        self._lbl_status_cfg_msg = Label(con, textvariable=self._status_cfgmsg, anchor='w')

        # *******************************************************
        # PRESET Message Selection
        # *******************************************************
        self._lbl_presets = Label(con, text=LBLPRESET,
                                  bg=LBL_COL, anchor='w')
        self._lbx_preset = Listbox(con, border=2,
                                 relief="sunken", bg=ENTCOL,
                                 height=7, justify=LEFT,
                                 exportselection=False)
        self._scr_presetv = Scrollbar(con, orient=VERTICAL)
        self._scr_preseth = Scrollbar(con, orient=HORIZONTAL)
        self._lbx_preset.config(yscrollcommand=self._scr_presetv.set)
        self._lbx_preset.config(xscrollcommand=self._scr_preseth.set)
        self._scr_presetv.config(command=self._lbx_preset.yview)
        self._scr_preseth.config(command=self._lbx_preset.xview)
        self._lbl_send_preset = Label(con)
        self._btn_send_preset = Button(con, image=self._img_send, width=50, fg="green",
                                       command=self._on_send_preset, font=self.__app.font_md)

        self._lbl_status = Label(con, textvariable=self._status_preset, anchor='w')
        self._btn_exit = Button(con, image=self._img_exit, width=50, fg="red",
                                command=self._on_exit, font=self.__app.font_md)

    def _do_layout(self):
        '''
        Position widgets in frame.
        '''

        self._frm_container.grid(column=0, row=0, columnspan=6, padx=3, pady=3,
                                 ipadx=5, ipady=5, sticky=(N, S, W, E))
        self._lbl_title.grid(column=0, row=0, columnspan=6, ipady=3, sticky=(W, E))
        self._lbl_cfg_port.grid(column=0, row=1, columnspan=6, padx=3, sticky=(W, E))
        self._lbl_ubx_baudrate.grid(column=0, row=2, columnspan=3, sticky=(W))
        self._spn_ubx_baudrate.grid(column=1, row=2, columnspan=3, sticky=(W))
        self._lbl_inprot.grid(column=0, row=3, sticky=(W))
        self._rad_inprot_nmea.grid(column=1, row=3, sticky=(W))
        self._rad_inprot_ubx.grid(column=2, row=3, sticky=(W))
        self._rad_inprot_rtcm.grid(column=3, row=3, sticky=(W))
        self._rad_inprot_both.grid(column=4, row=3, sticky=(W))
        self._lbl_outprot.grid(column=0, row=4, sticky=(W))
        self._rad_outprot_nmea.grid(column=1, row=4, sticky=(W))
        self._rad_outprot_ubx.grid(column=2, row=4, sticky=(W))
        self._rad_outprot_both.grid(column=3, row=4, sticky=(W))
        self._btn_send_port.grid(column=4, row=2, ipadx=3,
                                 ipady=3, sticky=(E))
        self._lbl_send_port.grid(column=5, row=2, ipadx=3,
                                 ipady=3, sticky=(W))

        # *******************************************************
        # CFG-MSG Message Selection
        # *******************************************************
        ttk.Separator(self._frm_container).grid(column=0, row=5, columnspan=6,
                                                padx=3, pady=3, sticky=(W, E))
        self._lbl_cfg_msg.grid(column=0, row=6, columnspan=6, padx=3, sticky=(W, E))
        self._lbx_cfg_msg.grid(column=0, row=7, columnspan=3, rowspan=4, padx=3,
                               pady=3, sticky=(W, E))
        self._scr_cfg_msg.grid(column=2, row=7, rowspan=4, sticky=(N, S, E))
        self._chk_ddc.grid(column=3, row=7, padx=0, pady=0, sticky=(W))
        self._chk_uart1.grid(column=3, row=8, padx=0, pady=0, sticky=(W))
        self._chk_usb.grid(column=3, row=9, padx=0, pady=0, sticky=(W))
        self._chk_spi.grid(column=3, row=10, padx=0, pady=0, sticky=(W))
        self._btn_send_cfg_msg.grid(column=4, row=7, rowspan=4, ipadx=3, ipady=3,
                                   sticky=(E))
        self._lbl_send_cfg_msg.grid(column=5, row=7, rowspan=4, ipadx=3,
                                 ipady=3, sticky=(W))

        # *******************************************************
        # PRESET Message Selection
        # *******************************************************
        ttk.Separator(self._frm_container).grid(column=0, row=14, columnspan=6,
                                                padx=3, pady=3, sticky=(W, E))
        self._lbl_presets.grid(column=0, row=15, columnspan=6, padx=3, sticky=(W, E))
        self._lbx_preset.grid(column=0, row=16, columnspan=4, padx=3, pady=3, sticky=(W, E))
        self._scr_presetv.grid(column=3, row=16, sticky=(N, S, E))
        self._scr_preseth.grid(column=0, row=17, columnspan=4, sticky=(W, E))
        self._btn_send_preset.grid(column=4, row=16, ipadx=3, ipady=3,
                                   sticky=(E))
        self._lbl_send_preset.grid(column=5, row=16, rowspan=2, ipadx=3,
                                 ipady=3, sticky=(W))

        ttk.Separator(self._frm_container).grid(column=0, row=18, columnspan=6,
                                                padx=3, pady=3, sticky=(W, E))

        self._lbl_status.grid(column=0, row=19, columnspan=4, ipadx=3, ipady=3,
                            sticky=(W, E))
        self._btn_exit.grid(column=4, row=19, ipadx=3, ipady=3,
                            sticky=(E))

    def _attach_events(self):
        '''
        Bind listbox selection events.
        '''

        self._lbx_cfg_msg.bind("<<ListboxSelect>>", self._on_select_cfg_msg)
        self._lbx_preset.bind("<<ListboxSelect>>", self._on_select_preset)

    def _reset(self):
        '''
        Reset settings to defaults.
        '''

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

    def update(self, cfgtype='CFG-MSG', **kwargs):
        '''
        Receives polled confirmation messages from the uxb_handler and
        updates panel settings according to the information received.

        NB: not absolutely bullet-proof as confirmation messages cannot
        be unequivocally linked to specific commands, but the best
        available indication of current state.
        '''

        # CFG-PRT command confirmation
        if 'baudrate' in kwargs:
            self._ubx_baudrate.set(str(kwargs['baudrate']))
        if 'inprot' in kwargs:
            self._ubx_inprot.set(kwargs['inprot'])
        if 'outprot' in kwargs:
            self._ubx_outprot.set(kwargs['outprot'])
        self._lbl_send_port.config(image=self._img_confirmed)

        # CFG-MSG command confirmation
        if self._awaiting_cfgmsg:
            if cfgtype == 'CFG-MSG':
                self.set_status(f"{cfgtype} received", "green")
                self._ddc_onoff.set(1 if kwargs['ddcrate'] > 0 else 0)
                self._uart1_onoff.set(1 if kwargs['uart1rate'] > 0 else 0)
                self._usb_onoff.set(1 if kwargs['usbrate'] > 0 else 0)
                self._spi_onoff.set(1 if kwargs['spirate'] > 0 else 0)
                self._lbl_send_cfg_msg.config(image=self._img_confirmed)
                self._awaiting_cfgmsg = False
            if cfgtype == 'ACK-NAK':
                self.set_status(f"{cfgtype} rejected", "red")
                self._lbl_send_cfg_msg.config(image=self._img_warn)
                self._awaiting_cfgmsg = False

        # PRESET command(s) confirmation
        if self._awaiting_ack:
            if cfgtype == 'ACK-ACK':
                self.set_status(f"{cfgtype} acknowledgement received", "green")
                self._lbl_send_preset.config(image=self._img_confirmed)
                self._awaiting_ack = False
            if cfgtype == 'ACK-NAK':
                self.set_status(f"{cfgtype} acknowledgement received", "red")
                self._lbl_send_preset.config(image=self._img_confirmed)
                self._awaiting_ack = False
        elif not self._awaiting_ack and cfgtype not in ('ACK-ACK', 'ACK-NAK'):
            self.set_status(f"{cfgtype} response received", "green")

    def _on_send_port(self, *args, **kwargs):
        '''
        Handle Send port config button press.
        '''

        portID = b'\x03'
        reserved0 = b'\x00'
        reserved4 = b'\x00\00'
        reserved5 = b'\x00\00'
        txReady = b'\x00\x00'
        mode = b'\x00\x00\x00\x00'
        baudRate = int.to_bytes(int(self._ubx_baudrate.get()), 4, 'little', signed=False)
        inProtoMask = int.to_bytes(self._ubx_inprot.get(), 2, 'little', signed=False)
        outProtoMask = int.to_bytes(self._ubx_outprot.get(), 2, 'little', signed=False)
        payload = portID + reserved0 + txReady + mode + baudRate + inProtoMask \
                  +outProtoMask + reserved4 + reserved5
        msg = UBXMessage('CFG', 'CFG-PRT', payload, SET)
        self.__app.serial_handler.serial_write(msg.serialize())

        self._do_poll_prt()  # poll for confirmation
        self._lbl_send_port.config(image=self._img_pending)
        self.set_status("CFG-PRT configuration message(s) sent")

    def _on_select_cfg_msg(self, *args, **kwargs):
        '''
        CFG-MSG command has been selected.
        '''

        idx = self._lbx_cfg_msg.curselection()
        self._cfg_msg_command = self._lbx_cfg_msg.get(idx)

        # poll selected message configuration to get current message rates
        msg = UBXMessage.key_from_val(UBX_CONFIG_MESSAGES, self._cfg_msg_command)
        data = UBXMessage('CFG', 'CFG-MSG', msg, POLL)
        self.__app.serial_handler.serial_write(data.serialize())
        self._awaiting_cfgmsg = True
        self._lbl_send_cfg_msg.config(image=self._img_pending)

    def _on_send_cfg_msg(self):
        '''
        CFG-MSG command send button has been clicked.
        '''

        msg = UBXMessage.key_from_val(UBX_CONFIG_MESSAGES, self._cfg_msg_command)
        rateDDC = b'\x00' if self._ddc_onoff.get() == 0 else b'\x01'
        rateUART1 = b'\x00' if self._uart1_onoff.get() == 0 else b'\x01'
        rateUART2 = b'\x00'
        rateUSB = b'\x00' if self._usb_onoff.get() == 0 else b'\x01'
        rateSPI = b'\x00' if self._spi_onoff.get() == 0 else b'\x01'
        reserved = b'\x00'
        msg_payload = msg + rateDDC + rateUART1 + rateUART2 + rateUSB + rateSPI + reserved
        data = UBXMessage('CFG', 'CFG-MSG', msg_payload, SET)
        self.__app.serial_handler.serial_write(data.serialize())
        data = UBXMessage('CFG', 'CFG-MSG', msg, POLL)  # poll for a response
        self.__app.serial_handler.serial_write(data.serialize())

        self.set_status("CFG-MSG command sent")
        self._awaiting_cfgmsg = True
        self._lbl_send_cfg_msg.config(image=self._img_pending)

    def _on_select_preset(self, *args, **kwargs):
        '''
        Preset command has been selected.
        '''

        idx = self._lbx_preset.curselection()
        self._preset_command = self._lbx_preset.get(idx)

    def _on_send_preset(self, *args, **kwargs):
        '''
        Preset command send button has been clicked.
        '''

        confirmed = True
        try:

            if self._preset_command == PSTRESET:
                confirmed = self._do_factory_reset()
            elif self._preset_command == PSTSAVE:
                confirmed = self._do_save_config()
            elif self._preset_command == PSTMINNMEAON:
                self._do_set_minnmea()
            elif self._preset_command == PSTALLNMEAON:
                self._do_set_allnmea(True)
            elif self._preset_command == PSTALLNMEAOFF:
                self._do_set_allnmea(False)
            elif self._preset_command == PSTMINUBXON:
                self._do_set_minNAV()
            elif self._preset_command == PSTALLUBXON:
                self._do_set_allNAV(True)
            elif self._preset_command == PSTALLUBXOFF:
                self._do_set_allNAV(False)
            elif self._preset_command == PSTALLINFON:
                self._do_set_inf(True)
            elif self._preset_command == PSTALLINFOFF:
                self._do_set_inf(False)
            elif self._preset_command == PSTALLLOGON:
                self._do_set_log(True)
            elif self._preset_command == PSTALLLOGOFF:
                self._do_set_log(False)
            elif self._preset_command == PSTALLMONON:
                self._do_set_mon(True)
            elif self._preset_command == PSTALLMONOFF:
                self._do_set_mon(False)
            elif self._preset_command == PSTALLRXMON:
                self._do_set_rxm(True)
            elif self._preset_command == PSTALLRXMOFF:
                self._do_set_rxm(False)
            elif self._preset_command == PSTPOLLPORT:
                self._do_poll_prt()
            elif self._preset_command == PSTPOLLINFO:
                self._do_poll_inf()
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

    def _do_poll_inf(self):
        '''
        Poll INF message configuration
        '''

        for payload in (b'\x00', b'\x01'):  # UBX & NMEA
            msg = UBXMessage('CFG', 'CFG-INF', payload, POLL)
            self.__app.serial_handler.serial_write(msg.serialize())

    def _do_poll_prt(self):
        '''
        Poll PRT message configuration
        '''

        msg = UBXMessage('CFG', 'CFG-PRT', None, POLL)
        self.__app.serial_handler.serial_write(msg.serialize())

    def _do_set_inf(self, onoff):
        '''
        Turn on device information messages INF
        '''

        if onoff:
            mask = b'\x1f'  # all INF msgs
        else:
            mask = b'\x01'  # errors only
        for protocolID in (b'\x00', b'\x01'):  # UBX and NMEA
            reserved1 = b'\x00\x00\x00'
            infMsgMaskDDC = mask
            infMsgMaskUART1 = mask
            infMsgMaskUART2 = mask
            infMsgMaskUSB = mask
            infMsgMaskSPI = mask
            reserved2 = b'\x00'
            payload = protocolID + reserved1 + infMsgMaskDDC + \
                      infMsgMaskUART1 + infMsgMaskUART2 + infMsgMaskUSB + \
                      infMsgMaskSPI + reserved2
            msg = UBXMessage('CFG', 'CFG-INF', payload, SET)
            self.__app.serial_handler.serial_write(msg.serialize())
            self._do_poll_inf()  # poll results

    def _do_set_log(self, onoff):
        '''
        Turn on all device logging messages LOG
        '''

        for msgtype in UBX_CONFIG_MESSAGES:
            if msgtype[0:1] == b'\x21':
                self._do_cfgmsg(msgtype, onoff)

    def _do_set_mon(self, onoff):
        '''
        Turn on all device monitoring messages MON
        '''

        for msgtype in UBX_CONFIG_MESSAGES:
            if msgtype[0:1] == b'\x0A':
                self._do_cfgmsg(msgtype, onoff)

    def _do_set_rxm(self, onoff):
        '''
        Turn on all device receiver management messages RXM
        '''

        for msgtype in UBX_CONFIG_MESSAGES:
            if msgtype[0:1] == b'\x02':
                self._do_cfgmsg(msgtype, onoff)

    def _do_set_minnmea(self):
        '''
        Turn on minimum set of NMEA messages (GGA & GSA & GSV)
        '''

        for msgtype in UBX_CONFIG_MESSAGES:
            if msgtype[0:1] == b'\xF0':  # standard NMEA
                if msgtype in (b'\xF0\x00', b'\xF0\x02', b'\xF0\x03'):  # GGA, GSA, GSV
                    self._do_cfgmsg(msgtype, True)
                else:
                    self._do_cfgmsg(msgtype, False)
            if msgtype[0:1] == b'\xF1':  # proprietary NMEA
                self._do_cfgmsg(msgtype, False)

    def _do_set_minNAV(self):
        '''
        Turn on minimum set of UBX-NAV messages (PVT & SVINFO)
        '''

        for msgtype in UBX_CONFIG_MESSAGES:
            if msgtype[0:1] == b'\x01':  # UBX-NAV
                if msgtype in (b'\x01\x07', b'\x01\x30'):  # NAV-PVT, NAV-SVINFO
                    self._do_cfgmsg(msgtype, True)
                else:
                    self._do_cfgmsg(msgtype, False)

    def _do_set_allnmea(self, onoff):
        '''
        Turn on all NMEA messages
        '''

        for msgtype in UBX_CONFIG_MESSAGES:
            if msgtype[0:1] not in (b'\x0A', b'\x01'):
                self._do_cfgmsg(msgtype, onoff)

    def _do_set_allNAV(self, onoff):
        '''
        Turn on all UBX-NAV messages
        '''

        for msgtype in UBX_CONFIG_MESSAGES:
            if msgtype[0:1] == b'\x01':
                self._do_cfgmsg(msgtype, onoff)

    def _do_cfgmsg(self, msgtype, onoff):
        '''
        Send CFG-MSG for specified message type
        '''

        if onoff:
            rate = CFG_MSG_ON
        else:
            rate = CFG_MSG_OFF
        payload = msgtype + rate
        msg = UBXMessage('CFG', 'CFG-MSG', payload, SET)
        self.__app.serial_handler.serial_write(msg.serialize())

    def _do_factory_reset(self) -> bool:
        '''
        Restore to factory defaults stored in battery-backed RAM
        but display confirmation message box first.
        '''

        if messagebox.askokcancel(DLGRESET, DLGRESETCONFIRM):
            clearMask = b'\x1f\x1f\x00\x00'
            saveMask = b'\x00\x00\x00\x00'
            loadMask = b'\x1f\x1f\x00\x00'
            devicerMask = b'\x01'  # battery backed RAM
            payload = clearMask + saveMask + loadMask + devicerMask
            msg = UBXMessage('CFG', 'CFG-CFG', payload, SET)
            self.__app.serial_handler.serial_write(msg.serialize())
            return True

        return False

    def _do_save_config(self) -> bool:
        '''
        Save current configuration to battery-backed RAM
        but display confirmation message box first.
        '''

        if messagebox.askokcancel(DLGSAVE, DLGSAVECONFIRM):
            clearMask = b'\x00\x00\x00\x00'
            saveMask = b'\x1f\x1f\x00\x00'
            loadMask = b'\x00\x00\x00\x00'
            devicerMask = b'\x01'  # battery backed RAM
            payload = clearMask + saveMask + loadMask + devicerMask
            msg = UBXMessage('CFG', 'CFG-CFG', payload, SET)
            self.__app.serial_handler.serial_write(msg.serialize())
            return True

        return False

    def _do_user_defined(self, command):
        '''
        Parse and send user-defined command(s).

        This could result in any number of errors if the
        uxbpresets file contains garbage, so there's a broad
        catch-all-exceptions in the calling routine.
        '''

        seg = command.split(",")
        for i in range(1, len(seg), 4):
            ubx_class = seg[i].strip()
            ubx_id = seg[i + 1].strip()
            payload = seg[i + 2].strip()
            mode = int(seg[i + 3].rstrip('\r\n'))
            if payload != '':
                payload = bytes(bytearray.fromhex(payload))
                msg = UBXMessage(ubx_class, ubx_id, payload, mode)
            else:
                msg = UBXMessage(ubx_class, ubx_id, None, mode)
            self.__app.serial_handler.serial_write(msg.serialize())

    def set_status(self, message, color="blue"):
        '''
        Set status message.
        '''

        message = (message[:50] + '..') if len(message) > 50 else message
        self._lbl_status.config(fg=color)
        self._status_preset.set("  " + message)

    def _on_exit(self, *args, **kwargs):
        '''
        Handle Exit button press.
        '''

        self.__master.update_idletasks()
        self.__app.dlg_ubxconfig = None
        self._dialog.destroy()

    def get_size(self):
        '''
        Get current frame size.
        '''

        self.__master.update_idletasks()  # Make sure we know about any resizing
        return (self._dialog.winfo_width(), self._dialog.winfo_height())
