'''
UBX Configuration frame class for PyGPSClient application.

This handles the configuration of a U-BLox GPS device via the UBX protocol.

Created on 22 Sep 2020

@author: semuadmin
'''

from tkinter import ttk, Toplevel, Frame, Checkbutton, Listbox, Scrollbar, \
                         Entry, Button, Label, Spinbox, IntVar, \
                         N, S, E, W, LEFT, VERTICAL, END

from PIL import ImageTk, Image

from pygpsclient.globals import BGCOL, FGCOL, ENTCOL, READONLY, BAUDRATES, ICON_APP
from pygpsclient.strings import DLGUBXCONFIG
from pyubx2.ubxmessage import UBXMessage
import pyubx2.ubxtypes_core as ubt

CFG_MSG_OFF = b'\x00\x00\x00\x00\x00\x01'
CFG_MSG_ON = b'\x00\x01\x01\x01\x00\x01'


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

        #  Initialise up key variables
        self._ubx_baudrate = IntVar()
        self._ubx_prtnmeain = IntVar()
        self._ubx_prtubxin = IntVar()
        self._ubx_prtnmeaout = IntVar()
        self._ubx_prtubxout = IntVar()
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

        self._cfg_msg_states = {
        'DTM': self._dtm_state,
        'GBS': self._gbs_state,
        'GGA': self._gga_state,
        'GLL': self._gll_state,
        'GSA': self._gsa_state,
        'GSV': self._gsv_state,
        'RMC': self._rmc_state,
        'TXT': self._txt_state,
        'VTG': self._vtg_state,
        'ZDA': self._zda_state,
        'XXX': self._xxx_state,  # for error testing
        'UBX00': self._ubx00_state,
        'UBX03': self._ubx03_state,
        'UBX04': self._ubx04_state,
        'UBX05': self._ubx05_state,
        'UBX06': self._ubx06_state}

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
        for i in range(5):
            con.grid_columnconfigure(i, weight=1)
        con.grid_rowconfigure(1, weight=1)

        con.option_add("*Font", self.__app.font_sm)

        self._lbl_title = Label(con, text="UBX Configuration", bg=BGCOL, fg=FGCOL,
                                justify=LEFT, font=self.__app.font_md)
        self._lbl_cfg_prt = Label(con, text="CFG-PRT Port Protocols")
        self._lbl_ubx_baudrate = Label(con, text="Baud rate")
        self._spn_ubx_baudrate = Spinbox(con,
                                         values=(BAUDRATES),
                                         width=8, state=READONLY, readonlybackground=ENTCOL,
                                         wrap=True, textvariable=self._ubx_baudrate)
        self._lbl_ubx_prtnmea = Label(con, text="NMEA Protocol")
        self._chk_ubx_prtnmeain = Checkbutton(con, text="In",
                                    command=lambda: self._on_cfg_msg(msg="PRTNMEAIN"),
                                    variable=self._ubx_prtnmeain)
        self._chk_ubx_prtnmeaout = Checkbutton(con, text="Out",
                                    command=lambda: self._on_cfg_msg(msg="PRTNMEAOUT"),
                                    variable=self._ubx_prtnmeaout)
        self._lbl_ubx_prtubx = Label(con, text="UBX Protocol")
        self._chk_ubx_prtubxin = Checkbutton(con, text="In",
                                    command=lambda: self._on_cfg_msg(msg="PRTUBXIN"),
                                    variable=self._ubx_prtubxin)
        self._chk_ubx_prtubxout = Checkbutton(con, text="Out",
                                    command=lambda: self._on_cfg_msg(msg="PRTUBXOUT"),
                                    variable=self._ubx_prtubxout)
        self._lbl_cfg_msg = Label(con, text="CFG-MSG Message Filters")
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
        self._chk_ubx00 = Checkbutton(con, text="UBX,00",
                                      command=lambda: self._on_cfg_msg(msg=b'\xF1\x00', var=self._ubx00_state),
                                      variable=self._ubx00_state)
        self._chk_ubx03 = Checkbutton(con, text="UBX,03",
                                      command=lambda: self._on_cfg_msg(msg=b'\xF1\x03', var=self._ubx03_state),
                                      variable=self._ubx03_state)
        self._chk_ubx04 = Checkbutton(con, text="UBX,04",
                                      command=lambda: self._on_cfg_msg(msg=b'\xF1\x04', var=self._ubx04_state),
                                      variable=self._ubx04_state)
        self._frm_manual = Frame(con)
        man = self._frm_manual
        self._lbl_manual = Label(man, text="Manual Message Entry")
        self._lbl_clsid = Label(man, text="ClsID")
        self._lbx_clsid = Listbox(man, border=2,
                                 relief="sunken", bg=ENTCOL,
                                 width=5, height=5, justify=LEFT,
                                 exportselection=False)
        self._scr_clsid = Scrollbar(man, orient=VERTICAL)
        self._lbx_clsid.config(yscrollcommand=self._scr_clsid.set)
        self._scr_clsid.config(command=self._lbx_clsid.yview)
        self._lbl_msgid = Label(man, text="MsgID")
        self._lbx_msgid = Listbox(self._frm_manual, border=2,
                                 relief="sunken", bg=ENTCOL,
                                 width=14, height=5, justify=LEFT,
                                 exportselection=False)
        self._scr_msgid = Scrollbar(man, orient=VERTICAL)
        self._lbx_msgid.config(yscrollcommand=self._scr_msgid.set)
        self._scr_msgid.config(command=self._lbx_msgid.yview)
        self._lbl_payload = Label(man, text="Payload")
        self._ent_payload = Entry(man, bg=ENTCOL)

        self._btn_send = Button(con, text="Send", width=8, fg="green", command=self._on_send,
                              font=self.__app.font_md)
        self._btn_exit = Button(con, text="Exit", width=8, fg="red", command=self._on_exit,
                              font=self.__app.font_md)

    def _do_layout(self):
        '''
        Position widgets in frame.
        '''

        self._frm_container.grid(column=0, row=0, columnspan=4, padx=3, pady=3,
                                 ipadx=5, ipady=5, sticky=(N, S, W, E))
        self._lbl_title.grid(column=0, row=0, columnspan=4, sticky=(W, E))
        self._lbl_cfg_prt.grid(column=0, row=1, columnspan=4, sticky=(W))
        self._lbl_ubx_baudrate.grid(column=0, row=2, columnspan=3, sticky=(W))
        self._spn_ubx_baudrate.grid(column=1, row=2, columnspan=3, sticky=(W))
        self._lbl_ubx_prtnmea.grid(column=0, row=3, sticky=(W))
        self._chk_ubx_prtnmeain.grid(column=1, row=3, sticky=(W))
        self._chk_ubx_prtnmeaout.grid(column=2, row=3, sticky=(W))
        self._lbl_ubx_prtubx.grid(column=0, row=4, columnspan=3, sticky=(W))
        self._chk_ubx_prtubxin.grid(column=1, row=4, sticky=(W))
        self._chk_ubx_prtubxout.grid(column=2, row=4, sticky=(W))

        ttk.Separator(self._frm_container).grid(column=0, row=5, columnspan=4,
                                                padx=3, pady=3, sticky=(W, E))
        self._lbl_cfg_msg.grid(column=0, row=6, columnspan=4, sticky=(W))
        self._chk_dtm.grid(column=0, row=7, sticky=(W))
        self._chk_gbs.grid(column=1, row=7, sticky=(W))
        self._chk_gga.grid(column=2, row=7, sticky=(W))
        self._chk_gll.grid(column=3, row=7, sticky=(W))
        self._chk_gsa.grid(column=0, row=8, sticky=(W))
        self._chk_gsv.grid(column=1, row=8, sticky=(W))
        self._chk_rmc.grid(column=2, row=8, sticky=(W))
        self._chk_txt.grid(column=3, row=8, sticky=(W))
        self._chk_vtg.grid(column=0, row=9, sticky=(W))
        self._chk_zda.grid(column=1, row=9, sticky=(W))
        self._chk_xxx.grid(column=2, row=9, sticky=(W))
        self._chk_ubx00.grid(column=0, row=10, sticky=(W))
        self._chk_ubx03.grid(column=1, row=10, sticky=(W))
        self._chk_ubx04.grid(column=2, row=10, sticky=(W))

        ttk.Separator(self._frm_container).grid(column=0, row=11, columnspan=4,
                                                padx=3, pady=3, sticky=(W, E))
        self._frm_manual.grid(column=0, row=12, columnspan=7, sticky=(W))
        self._lbl_manual.grid(column=0, row=0, columnspan=6, sticky=(W))
        self._lbl_clsid.grid(column=0, row=1, padx=3, pady=3, sticky=(W))
        self._lbx_clsid.grid(column=1, row=1, padx=3, pady=3, columnspan=2, sticky=(W))
        self._scr_clsid.grid(column=3, row=1, sticky=(N, S))
        self._lbl_msgid.grid(column=4, row=1, padx=3, pady=3, sticky=(W))
        self._lbx_msgid.grid(column=5, row=1, padx=3, pady=3, columnspan=2, sticky=(W))
        self._scr_msgid.grid(column=7, row=1, sticky=(N, S))
        self._lbl_payload.grid(column=0, row=2, padx=3, pady=3, sticky=(W))
        self._ent_payload.grid(column=1, row=2, padx=3, pady=3, columnspan=7, sticky=(W, E))

        ttk.Separator(self._frm_container).grid(column=0, row=13, columnspan=4,
                                                padx=3, pady=3, sticky=(W, E))
        self._btn_send.grid(column=0, row=14, columnspan=2, ipadx=3, ipady=3, padx=5, pady=3)
        self._btn_exit.grid(column=2, row=14, columnspan=2, ipadx=3, ipady=3, padx=5, pady=3)

    def _attach_events(self):
        '''
        Bind events
        '''

        self._lbx_clsid.bind("<<ListboxSelect>>", self._on_select_clsid)

    def _reset(self):
        '''
        Reset settings to defaults.
        '''

        self._ubx_baudrate.set(BAUDRATES[4])
        self._ubx_prtnmeain.set(True)
        self._ubx_prtubxin.set(True)
        self._ubx_prtnmeaout.set(True)
        self._ubx_prtubxout.set(False)
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

        for idx, cls in enumerate(ubt.UBX_CLASSES):
            self._lbx_clsid.insert(idx, ubt.UBX_CLASSES[cls])

    def _on_cfg_msg(self, *args, **kwargs):
        '''
        Send CFG_MSG message to turn individual NMEA message types on or off
        '''

        # msg = CFG_MSG_TYPES[kwargs['msg']]
        msg = kwargs['msg']
        state = kwargs['var'].get()
        if state:  # if checkbutton checked
            onoff = CFG_MSG_ON
        else:
            onoff = CFG_MSG_OFF
        msg_payload = msg + onoff
        data = UBXMessage('CFG', 'CFG-MSG', msg_payload, 1).serialize()
        self.__app.serial_handler.serial_write(data)

    def _on_select_clsid(self, *args, **kwargs):
        '''
        Actions when clsid is selected
        '''

        self._lbx_msgid.delete(0, END)
        cls = None
        idx = self._lbx_clsid.curselection()
        clsname = self._lbx_clsid.get(idx)
        for key, value in ubt.UBX_CLASSES.items():
            if clsname == value:
                cls = key
        for idx, msg in enumerate(ubt.UBX_MSGIDS[cls]):
            self._lbx_msgid.insert(idx, ubt.UBX_MSGIDS[cls][msg])

    def _on_send(self, *args, **kwargs):
        '''
        Handle OK button press.
        '''

        self.__master.update_idletasks()
        self._dialog.destroy()

    def _on_exit(self, *args, **kwargs):
        '''
        Handle OK button press.
        '''

        self.__master.update_idletasks()
        self._dialog.destroy()

    def get_size(self):
        '''
        Get current frame size.
        '''

        self.__master.update_idletasks()  # Make sure we know about any resizing
        return (self._dialog.winfo_width(), self._dialog.winfo_height())
