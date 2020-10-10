'''
UBX Configuration frame class for PyGPSClient application.

This handles the configuration of a U-BLox GPS device via the UBX protocol.

Created on 22 Sep 2020

@author: semuadmin
'''

from tkinter import ttk, Toplevel, Frame, Checkbutton, Radiobutton, Listbox, \
                    Scrollbar, messagebox, Button, Label, IntVar, \
                    N, S, E, W, LEFT, VERTICAL

from PIL import ImageTk, Image
from pyubx2 import UBXMessage, SET, UBX_CONFIG_MESSAGES

from .globals import BGCOL, FGCOL, ENTCOL, ICON_APP, ICON_SEND, ICON_EXIT
from .strings import DLGUBXCONFIG
from .ubx_handler import UBXHandler as ubh, CFG_MSG_OFF, CFG_MSG_ON, BOTH, UBX, NMEA

MSG_PRESETS = {
'CFG-CFG - Restore factory defaults': 'CFG-CFG',
'CFG-CFG - Store current configuration': 'CFG-CFG',
'CFG-MSG - Turn ON all NMEA msgs': 'CFG-MSG',
'CFG-MSG - Turn OFF all NMEA msgs': 'CFG-MSG',
'CFG-MSG - Turn ON all UBX NAV msgs': 'CFG-MSG',
'CFG-MSG - Turn OFF all UBX NAV msgs': 'CFG-MSG',
'CFG-MSG - Turn ON all MON msgs': 'CFG-MSG',
'CFG-MSG - Turn OFF all MON msgs': 'CFG-MSG',
'CFG-INF - Turn ON all INF msgs': 'CFG-INF'
}


class UBXConfigDialog():
    ''',
    Frame inheritance class for application settings and controls.
    '''

    def __init__(self, app, *args, **kwargs):
        '''
        Constructor.
        '''

        self.__app = app  # Reference to main application class
        self.__master = self.__app.get_master()  # Reference to root class (Tk)
        self._dialog = Toplevel()
        self._dialog.title = DLGUBXCONFIG
        wd, hd = self.get_size()
        wa = self.__master.winfo_width()
        ha = self.__master.winfo_height()
        self._dialog.geometry("+%d+%d" % (int(wa / 2 - wd / 2), int(ha / 2 - hd / 2)))
        self._dialog.attributes('-topmost', 'true')
        self._img_icon = ImageTk.PhotoImage(Image.open (ICON_APP))
        self._img_send = ImageTk.PhotoImage(Image.open(ICON_SEND))
        self._img_exit = ImageTk.PhotoImage(Image.open(ICON_EXIT))

        # Poll current UBX configuration
        if self.__app.serial_handler.connected:
            ubh.poll_ubx_config(self.__app.serial_handler.serial)

        # Load user presets if there are any
        self._userpresets = self.__app.file_handler.load_user_presets()

        #  Initialise up key variables
        self._preset_command = None
        self._ubx_baudrate = IntVar()
        self._ubx_prot = IntVar()
        self._dtm_state = IntVar()
        self._gbs_state = IntVar()
        self._gga_state = IntVar()
        self._gll_state = IntVar()
        self._gsa_state = IntVar()
        self._gsv_state = IntVar()
        self._rmc_state = IntVar()
        self._txt_state = IntVar()
        self._vtg_state = IntVar()
        self._zda_state = IntVar()
        self._xxx_state = IntVar()
        self._ubx00_state = IntVar()
        self._ubx03_state = IntVar()
        self._ubx04_state = IntVar()
        self._ubx05_state = IntVar()
        self._ubx06_state = IntVar()
        self._navaopstatus_state = IntVar()
        self._navdop_state = IntVar()
        self._navposllh_state = IntVar()
        self._navpvt_state = IntVar()
        self._navsol_state = IntVar()
        self._navsvinfo_state = IntVar()
        self._navsbas_state = IntVar()
        self._navtimeutc_state = IntVar()
        self._navvelned_state = IntVar()

#         self._cfg_msg_states = {
#         'DTM': self._dtm_state,
#         'GBS': self._gbs_state,
#         'GGA': self._gga_state,
#         'GLL': self._gll_state,
#         'GSA': self._gsa_state,
#         'GSV': self._gsv_state,
#         'RMC': self._rmc_state,
#         'TXT': self._txt_state,
#         'VTG': self._vtg_state,
#         'ZDA': self._zda_state,
#         'XXX': self._xxx_state,  # for error testing
#         'UBX00': self._ubx00_state,
#         'UBX03': self._ubx03_state,
#         'UBX04': self._ubx04_state,
#         'UBX05': self._ubx05_state,
#         'UBX06': self._ubx06_state,
#         'NAV-AOPSTATUS': self._navaopstatus_state,
#         'NAV-DOP': self._navdop_state,
#         'NAV-POSLLH': self._navposllh_state,
#         'NAV-PVT': self._navpvt_state,
#         'NAV-SOL': self._navsol_state,
#         'NAV-SVINFO': self._navsvinfo_state,
#         'NAV-SBAS': self._navsbas_state,
#         'NAV-TIMEUTC': self._navtimeutc_state,
#         'NAV-VELNED': self._navvelned_state}

        self._body()
        self._do_layout()
        self._attach_events()
        self._reset()

    def _body(self):
        '''
        Set up frame and widgets.
        '''

        self._frm_container = Frame(self._dialog, borderwidth=2, relief="groove")
        con = self._frm_container
        for i in range(7):
            con.grid_columnconfigure(i, weight=1)
        con.grid_rowconfigure(1, weight=1)

        con.option_add("*Font", self.__app.font_sm)

        self._lbl_title = Label(con, text="UBX Configuration", bg=BGCOL, fg=FGCOL,
                                justify=LEFT, font=self.__app.font_md)
        self._lbl_cfg_prt = Label(con, text="CFG-PRT Port Configuration")
#         self._lbl_ubx_baudrate = Label(con, text="Baud rate")
#         self._spn_ubx_baudrate = Spinbox(con,
#                                          values=(BAUDRATES),
#                                          width=8, state=READONLY, readonlybackground=ENTCOL,
#                                          wrap=True, textvariable=self._ubx_baudrate)
        self._lbl_ubx_prot = Label(con, text="Output Protocol(s)")
        self._rad_ubx_protnmea = Radiobutton(con, text="NMEA",
                                    command=lambda: self._on_cfg_prot(),
                                    variable=self._ubx_prot, value=NMEA)
        self._rad_ubx_protubx = Radiobutton(con, text="UBX",
                                    command=lambda: self._on_cfg_prot(),
                                    variable=self._ubx_prot, value=UBX)
        self._rad_ubx_protboth = Radiobutton(con, text="NMEA + UBX",
                                    command=lambda: self._on_cfg_prot(),
                                    variable=self._ubx_prot, value=BOTH)
        self._lbl_cfg_msg = Label(con, text="CFG-MSG - NMEA Message Filters")
        self._chk_dtm = Checkbutton(con, text="DTM",
                                    command=lambda: self._on_cfg_msg(msg=b'\xF0\x0A', var=self._dtm_state),
                                    variable=self._dtm_state)
        self._chk_gbs = Checkbutton(con, text="GBS",
                                    command=lambda: self._on_cfg_msg(msg=b'\xF0\x09', var=self._gbs_state),
                                    variable=self._gbs_state)
        self._chk_gll = Checkbutton(con, text="GLL",
                                    command=lambda: self._on_cfg_msg(msg=b'\xF0\x01', var=self._gll_state),
                                    variable=self._gll_state)
        self._chk_gga = Checkbutton(con, text="GGA",
                                    command=lambda: self._on_cfg_msg(msg=b'\xF0\x00', var=self._gga_state),
                                    variable=self._gga_state)
        self._chk_gsa = Checkbutton(con, text="GSA",
                                    command=lambda: self._on_cfg_msg(msg=b'\xF0\x02', var=self._gsa_state),
                                    variable=self._gsa_state)
        self._chk_gsv = Checkbutton(con, text="GSV",
                                    command=lambda: self._on_cfg_msg(msg=b'\xF0\x03', var=self._gsv_state),
                                    variable=self._gsv_state)
        self._chk_rmc = Checkbutton(con, text="RMC",
                                    command=lambda: self._on_cfg_msg(msg=b'\xF0\x04', var=self._rmc_state),
                                    variable=self._rmc_state)
        self._chk_vtg = Checkbutton(con, text="VTG",
                                    command=lambda: self._on_cfg_msg(msg=b'\xF0\x05', var=self._vtg_state),
                                    variable=self._vtg_state)
        self._chk_txt = Checkbutton(con, text="TXT",
                                    command=lambda: self._on_cfg_msg(msg=b'\xF0\x41', var=self._txt_state),
                                    variable=self._txt_state)
        self._chk_zda = Checkbutton(con, text="ZDA",
                                    command=lambda: self._on_cfg_msg(msg=b'\xF0\x08', var=self._zda_state),
                                    variable=self._zda_state)
        self._chk_xxx = Checkbutton(con, text="XXX",
                                    command=lambda: self._on_cfg_msg(msg=b'\x66\x66', var=self._xxx_state),
                                    variable=self._xxx_state)
        self._lbl_ubx_msg = Label(con, text="CFG-MSG - UBX Message Filters")
        self._chk_ubx00 = Checkbutton(con, text="UBX,00",
                                      command=lambda: self._on_cfg_msg(msg=b'\xF1\x00', var=self._ubx00_state),
                                      variable=self._ubx00_state)
        self._chk_ubx03 = Checkbutton(con, text="UBX,03",
                                      command=lambda: self._on_cfg_msg(msg=b'\xF1\x03', var=self._ubx03_state),
                                      variable=self._ubx03_state)
        self._chk_ubx04 = Checkbutton(con, text="UBX,04",
                                      command=lambda: self._on_cfg_msg(msg=b'\xF1\x04', var=self._ubx04_state),
                                      variable=self._ubx04_state)
        self._chk_navaopstatus = Checkbutton(con, text="NAV-AOPSTATUS",
                                    command=lambda: self._on_cfg_msg(msg=b'\x01\x03', var=self._navaopstatus_state),
                                    variable=self._navaopstatus_state)
        self._chk_navsol = Checkbutton(con, text="NAV-SOL",
                                    command=lambda: self._on_cfg_msg(msg=b'\x01\x06', var=self._navsol_state),
                                    variable=self._navsol_state)
        self._chk_navdop = Checkbutton(con, text="NAV-DOP",
                                    command=lambda: self._on_cfg_msg(msg=b'\x01\x04', var=self._navdop_state),
                                    variable=self._navdop_state)
        self._chk_navposllh = Checkbutton(con, text="NAV-POSLLH",
                                    command=lambda: self._on_cfg_msg(msg=b'\x01\x02', var=self._navposllh_state),
                                    variable=self._navposllh_state)
        self._chk_navpvt = Checkbutton(con, text="NAV-PVT",
                                    command=lambda: self._on_cfg_msg(msg=b'\x01\x07', var=self._navpvt_state),
                                    variable=self._navpvt_state)
        self._chk_navsvinfo = Checkbutton(con, text="NAV-SVINFO",
                                    command=lambda: self._on_cfg_msg(msg=b'\x01\x30', var=self._navsvinfo_state),
                                    variable=self._navsvinfo_state)
        self._chk_navsbas = Checkbutton(con, text="NAV-SBAS",
                                      command=lambda: self._on_cfg_msg(msg=b'\x01\x32', var=self._navsbas_state),
                                      variable=self._navsbas_state)
        self._chk_navvelned = Checkbutton(con, text="NAV-VELNED",
                                      command=lambda: self._on_cfg_msg(msg=b'\x01\x12', var=self._navvelned_state),
                                      variable=self._navvelned_state)
        self._chk_navtimeutc = Checkbutton(con, text="NAV-TIMEUTC",
                                      command=lambda: self._on_cfg_msg(msg=b'\x01\x21', var=self._navtimeutc_state),
                                      variable=self._navtimeutc_state)

        self._frm_preset = Frame(con)
        man = self._frm_preset
        self._lbl_presets = Label(man, text="CFG-MSG - Presets")
        self._lbl_preset = Label(man, text="Preset")
        self._lbx_preset = Listbox(man, border=2,
                                 relief="sunken", bg=ENTCOL,
                                 height=5, width=70, justify=LEFT,
                                 exportselection=False)
        self._scr_preset = Scrollbar(man, orient=VERTICAL)
        self._lbx_preset.config(yscrollcommand=self._scr_preset.set)
        self._scr_preset.config(command=self._lbx_preset.yview)

        self._btn_send = Button(man, image=self._img_send, fg="green", command=self._on_send,
                              font=self.__app.font_md)
        self._btn_exit = Button(con, image=self._img_exit, width=70, fg="red", command=self._on_exit,
                              font=self.__app.font_md)

    def _do_layout(self):
        '''
        Position widgets in frame.
        '''

        self._frm_container.grid(column=0, row=0, columnspan=6, padx=3, pady=3,
                                 ipadx=5, ipady=5, sticky=(N, S, W, E))
        self._lbl_title.grid(column=0, row=0, columnspan=6, sticky=(W, E))
        self._lbl_cfg_prt.grid(column=0, row=1, columnspan=6, sticky=(W))
#         self._lbl_ubx_baudrate.grid(column=0, row=2, columnspan=3, sticky=(W))
#         self._spn_ubx_baudrate.grid(column=1, row=2, columnspan=3, sticky=(W))
        self._lbl_ubx_prot.grid(column=0, row=3, sticky=(W))
        self._rad_ubx_protnmea.grid(column=1, row=3, sticky=(W))
        self._rad_ubx_protubx.grid(column=2, row=3, sticky=(W))
        self._rad_ubx_protboth.grid(column=3, row=3, sticky=(W))

        ttk.Separator(self._frm_container).grid(column=0, row=5, columnspan=6,
                                                padx=3, pady=3, sticky=(W, E))
        self._lbl_cfg_msg.grid(column=0, row=6, columnspan=6, sticky=(W))
        self._chk_dtm.grid(column=0, row=7, sticky=(W))
        self._chk_gbs.grid(column=1, row=7, sticky=(W))
        self._chk_gga.grid(column=2, row=7, sticky=(W))
        self._chk_gll.grid(column=3, row=7, sticky=(W))
        self._chk_gsa.grid(column=4, row=7, sticky=(W))
        self._chk_gsv.grid(column=5, row=7, sticky=(W))
        self._chk_rmc.grid(column=0, row=8, sticky=(W))
        self._chk_txt.grid(column=1, row=8, sticky=(W))
        self._chk_vtg.grid(column=2, row=8, sticky=(W))
        self._chk_zda.grid(column=3, row=8, sticky=(W))
        self._chk_xxx.grid(column=4, row=8, sticky=(W))
        self._chk_ubx00.grid(column=0, row=9, sticky=(W))
        self._chk_ubx03.grid(column=1, row=9, sticky=(W))
        self._chk_ubx04.grid(column=2, row=9, sticky=(W))

        ttk.Separator(self._frm_container).grid(column=0, row=10, columnspan=6,
                                                padx=3, pady=3, sticky=(W, E))
        self._lbl_ubx_msg.grid(column=0, row=11, columnspan=6, sticky=(W))
        self._chk_navaopstatus.grid(column=0, row=12, sticky=(W))
        self._chk_navdop.grid(column=1, row=12, sticky=(W))
        self._chk_navposllh.grid(column=2, row=12, sticky=(W))
        self._chk_navpvt.grid(column=3, row=12, sticky=(W))
        self._chk_navsbas.grid(column=4, row=12, sticky=(W))
        self._chk_navsol.grid(column=5, row=12, sticky=(W))
        self._chk_navsvinfo.grid(column=0, row=13, sticky=(W))
        self._chk_navtimeutc.grid(column=1, row=13, sticky=(W))
        self._chk_navvelned.grid(column=2, row=13, sticky=(W))

        ttk.Separator(self._frm_container).grid(column=0, row=14, columnspan=6,
                                                padx=3, pady=3, sticky=(W, E))
        self._frm_preset.grid(column=0, row=15, columnspan=6, sticky=(W))
        self._lbl_presets.grid(column=0, row=0, columnspan=6, sticky=(W))
        self._lbl_preset.grid(column=0, row=1, padx=3, pady=3, sticky=(W, E))
        self._lbx_preset.grid(column=1, row=1, columnspan=3, padx=3, pady=3, sticky=(W))
        self._scr_preset.grid(column=4, row=1, sticky=(N, S))
        self._btn_send.grid(column=5, row=1, columnspan=1, ipadx=3, ipady=3, padx=10, pady=3)

        ttk.Separator(self._frm_container).grid(column=0, row=16, columnspan=6,
                                                padx=3, pady=3, sticky=(W, E))

        self._btn_exit.grid(column=0, row=17, ipadx=3, ipady=3, padx=5, pady=3)

    def _attach_events(self):
        '''
        Bind events
        '''

        self._lbx_preset.bind("<<ListboxSelect>>", self._on_select_preset)

    def _reset(self):
        '''
        Reset settings to defaults.
        '''

        self._ubx_prot.set(BOTH)
        self._gbs_state.set(False)
        self._dtm_state.set(False)
        self._gbs_state.set(False)
        self._gll_state.set(True)
        self._gga_state.set(True)
        self._gsa_state.set(True)
        self._gsv_state.set(True)
        self._rmc_state.set(True)
        self._vtg_state.set(True)
        self._txt_state.set(True)
        self._zda_state.set(False)
        self._ubx00_state.set(False)
        self._ubx03_state.set(False)
        self._ubx04_state.set(False)

        idx = 0
        for pre in MSG_PRESETS:
            idx += 1
            self._lbx_preset.insert(idx, pre)
        for userpre in self._userpresets:
            idx += 1
            self._lbx_preset.insert(idx, userpre)

    def _on_cfg_msg(self, *args, **kwargs):
        '''
        Send CFG_MSG message to turn individual NMEA message types on or off
        '''

        msg = kwargs['msg']
        state = kwargs['var'].get()
        if state:  # if checkbutton checked
            onoff = CFG_MSG_ON
        else:
            onoff = CFG_MSG_OFF
        msg_payload = msg + onoff
        data = UBXMessage('CFG', 'CFG-MSG', msg_payload, 1).serialize()
        self.__app.serial_handler.serial_write(data)

    def _on_cfg_prot(self, *args, **kwargs):
        '''
        Send CFG_PRT message to select receiver output protocol(s)
        '''

        if self._ubx_prot.get() == NMEA:
            outProtoMask = b'\x02\x00'
        elif self._ubx_prot.get() == UBX:
            outProtoMask = b'\x01\x00'
        else:
            outProtoMask = b'\x03\x00'
        portID = b'\x03'
        reserved0 = b'\x00'
        txReady = b'\x00\x00'
        mode = b'\x00\x00\x00\x00'
        baudRate = b'\x00\x00\x00\x00'
        inProtoMask = b'\x07\x00'
        reserved4 = b'\x00\00'
        reserved5 = b'\x00\00'
        payload = portID + reserved0 + txReady + mode + baudRate + inProtoMask \
                  +outProtoMask + reserved4 + reserved5
        msg = UBXMessage('CFG', 'CFG-PRT', payload, SET)
        self.__app.serial_handler.serial_write(msg.serialize())

    def _on_select_preset(self, *args, **kwargs):
        '''
        Actions when preset message is selected
        '''

        idx = self._lbx_preset.curselection()
        self._preset_command = self._lbx_preset.get(idx)
#        TODO do stuff here

    def _on_send(self, *args, **kwargs):
        '''
        Handle Send button press.
        '''

        if self._preset_command == 'CFG-CFG - Restore factory defaults':
            self._do_factory_reset()
        elif self._preset_command == 'CFG-INF - Turn ON all INF msgs':
            self._do_setinfo()
        elif self._preset_command == 'CFG-MSG - Turn ON all MON msgs':
            self._do_setmon(True)
        elif self._preset_command == 'CFG-MSG - Turn OFF all MON msgs':
            self._do_setmon(False)
        elif self._preset_command == 'CFG-MSG - Turn ON all NMEA msgs':
            self._do_setnmea(True)
        elif self._preset_command == 'CFG-MSG - Turn OFF all NMEA msgs':
            self._do_setnmea(False)
        elif self._preset_command == 'CFG-MSG - Turn ON all UBX NAV msgs':
            self._do_setNAV(True)
        elif self._preset_command == 'CFG-MSG - Turn OFF all UBX NAV msgs':
            self._do_setNAV(False)
        else:
            messagebox.showwarning("UBX Configuration Presets", "Sorry - not yet implemented!\n\nWatch this space.",)

    def _do_setinfo(self):
        '''
        Turn on device information messages INF
        '''

        for protocolID in (b'\x00', b'\x01'):  # UBX and NMEA
            reserved0 = b'\x00'
            reserved1 = b'\x00\x00'
            infMsgMask = b'\x00\x31\x00\x00\x00\x00'
            payload = protocolID + reserved0 + reserved1 + infMsgMask
            msg = UBXMessage('CFG', 'CFG-INF', payload, SET)
            self.__app.serial_handler.serial_write(msg.serialize())

    def _do_setmon(self, onoff):
        '''
        Turn on all device monitoring messages MON
        '''

        for msgtype in UBX_CONFIG_MESSAGES:
            if msgtype[0:1] == b'\x0A':
                self._do_cfgmsg(msgtype, onoff)

    def _do_setnmea(self, onoff):
        '''
        Turn on all NMEA messages
        '''

        for msgtype in UBX_CONFIG_MESSAGES:
            if msgtype[0:1] not in (b'\x0A', b'\x01'):
                self._do_cfgmsg(msgtype, onoff)

    def _do_setNAV(self, onoff):
        '''
        Turn on all device monitoring messages MON
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

    def _do_factory_reset(self):
        '''
        Restore to factory defaults
        '''

        clearMask = b'\x07\x00\x00\x00'
        saveMask = b'\x00\x00\x00\x00'
        loadMask = b'\x07\x00\x00\x00'
        devicerMask = b'\x01'
        payload = clearMask + saveMask + loadMask + devicerMask
        msg = UBXMessage('CFG', 'CFG-CFG', payload, SET)
        self.__app.serial_handler.serial_write(msg.serialize())

    def _on_exit(self, *args, **kwargs):
        '''
        Handle Exit button press.
        '''

        self.__master.update_idletasks()
        self._dialog.destroy()

    def get_size(self):
        '''
        Get current frame size.
        '''

        self.__master.update_idletasks()  # Make sure we know about any resizing
        return (self._dialog.winfo_width(), self._dialog.winfo_height())
