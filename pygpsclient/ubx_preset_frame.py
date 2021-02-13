"""
UBX Configuration widget for preset and user-defined commands

Created on 22 Dec 2020

@author: semuadmin
"""
# pylint: disable=invalid-name, too-many-instance-attributes, too-many-ancestors

from tkinter import (
    messagebox,
    Frame,
    Listbox,
    Scrollbar,
    Button,
    Label,
    N,
    S,
    E,
    W,
    LEFT,
    VERTICAL,
    HORIZONTAL,
)
from PIL import ImageTk, Image
from pyubx2 import (
    UBXMessage,
    POLL,
    SET,
    UBX_MSGIDS,
    UBX_PAYLOADS_POLL,
)
from .globals import (
    ENTCOL,
    ICON_SEND,
    ICON_WARNING,
    ICON_PENDING,
    ICON_CONFIRMED,
    UBX_PRESET,
)
from .strings import (
    LBLPRESET,
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


class UBX_PRESET_Frame(Frame):
    """
    UBX Preset and User-defined configuration command panel.
    """

    def __init__(self, app, container, *args, **kwargs):
        """
        Constructor.

        :param object app: reference to main tkinter application
        :param frame container: container frame
        """

        self.__app = app  # Reference to main application class
        self.__master = self.__app.get_master()  # Reference to root class (Tk)
        self.__container = container

        Frame.__init__(self, self.__container.container, *args, **kwargs)

        self._img_send = ImageTk.PhotoImage(Image.open(ICON_SEND))
        self._img_pending = ImageTk.PhotoImage(Image.open(ICON_PENDING))
        self._img_confirmed = ImageTk.PhotoImage(Image.open(ICON_CONFIRMED))
        self._img_warn = ImageTk.PhotoImage(Image.open(ICON_WARNING))
        self._preset_command = None
        self._body()
        self._do_layout()
        self._attach_events()
        self._reset()

    def _body(self):
        """
        Set up frame and widgets.
        """

        self._lbl_presets = Label(self, text=LBLPRESET, anchor="w")
        self._lbx_preset = Listbox(
            self,
            border=2,
            relief="sunken",
            bg=ENTCOL,
            height=5,
            width=30,
            justify=LEFT,
            exportselection=False,
        )
        self._scr_presetv = Scrollbar(self, orient=VERTICAL)
        self._scr_preseth = Scrollbar(self, orient=HORIZONTAL)
        self._lbx_preset.config(yscrollcommand=self._scr_presetv.set)
        self._lbx_preset.config(xscrollcommand=self._scr_preseth.set)
        self._scr_presetv.config(command=self._lbx_preset.yview)
        self._scr_preseth.config(command=self._lbx_preset.xview)
        self._lbl_send_command = Label(self)
        self._btn_send_command = Button(
            self,
            image=self._img_send,
            width=50,
            command=self._on_send_preset,
        )

    def _do_layout(self):
        """
        Layout widgets.
        """

        self._lbl_presets.grid(column=0, row=0, columnspan=6, padx=3, sticky=(W, E))
        self._lbx_preset.grid(
            column=0, row=1, columnspan=3, rowspan=6, padx=3, pady=3, sticky=(W, E)
        )
        self._scr_presetv.grid(column=2, row=1, rowspan=6, sticky=(N, S, E))
        self._scr_preseth.grid(column=0, row=7, columnspan=3, sticky=(W, E))
        self._btn_send_command.grid(
            column=3, row=1, rowspan=6, ipadx=3, ipady=3, sticky=(E)
        )
        self._lbl_send_command.grid(
            column=4, row=1, rowspan=6, ipadx=3, ipady=3, sticky=(E)
        )

        (cols, rows) = self.grid_size()
        for i in range(cols):
            self.grid_columnconfigure(i, weight=1)
        for i in range(rows):
            self.grid_rowconfigure(i, weight=1)
        self.option_add("*Font", self.__app.font_sm)

    def _attach_events(self):
        """
        Bind listbox selection events.
        """

        self._lbx_preset.bind("<<ListboxSelect>>", self._on_select_preset)

    def _reset(self):
        """
        Reset panel.
        """

        # Load user-defined presets if there are any
        self._userpresets = self.__app.file_handler.load_user_presets()

        idx = 0
        for pst in PRESET_COMMMANDS:
            self._lbx_preset.insert(idx, pst)
            idx += 1

        for upst in self._userpresets:
            self._lbx_preset.insert(idx, "USER " + upst)
            idx += 1

    def _on_select_preset(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Preset command has been selected.
        """

        idx = self._lbx_preset.curselection()
        self._preset_command = self._lbx_preset.get(idx)

    def _on_send_preset(self, *args, **kwargs):  # pylint: disable=unused-argument
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
                self._lbl_send_command.config(image=self._img_pending)
                self.__container.set_status("Command(s) sent", "blue")
                self.__container.set_pending(
                    UBX_PRESET, ("ACK-ACK", "ACK-NAK", "MON-VER")
                )
            else:
                self.__container.set_status("Command(s) cancelled", "blue")

        except Exception as err:  # pylint: disable=broad-except
            self.__container.set_status(f"Error {err}", "red")
            self._lbl_send_command.config(image=self._img_warn)

    def _do_poll_all(self):
        """
        Poll INF message configuration.
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

    def _do_poll_prt(self):
        """
        Poll PRT message configuration for each port.
        """

        for portID in range(5):
            msg = UBXMessage("CFG", "CFG-PRT", POLL, portID=portID)
            self.__app.serial_handler.serial_write(msg.serialize())

    def _do_poll_inf(self):
        """
        Poll INF message configuration.
        """

        for payload in (b"\x00", b"\x01"):  # UBX & NMEA
            msg = UBXMessage("CFG", "CFG-INF", POLL, payload=payload)
            self.__app.serial_handler.serial_write(msg.serialize())

    def _do_set_inf(self, onoff: int):
        """
        Turn on device information messages INF.

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
        Turn on all device logging messages LOG.

        :param int msgrate: message rate (i.e. every nth position solution)
        """

        for msgtype in UBX_MSGIDS:
            if msgtype[0:1] == b"\x21":
                self._do_cfgmsg(msgtype, msgrate)

    def _do_set_mon(self, msgrate):
        """
        Turn on all device monitoring messages MON.

        :param int msgrate: message rate (i.e. every nth position solution)
        """

        for msgtype in UBX_MSGIDS:
            if msgtype[0:1] == b"\x0A":
                self._do_cfgmsg(msgtype, msgrate)

    def _do_set_rxm(self, msgrate):
        """
        Turn on all device receiver management messages RXM.

        :param int msgrate: message rate (i.e. every nth position solution)
        """

        for msgtype in UBX_MSGIDS:
            if msgtype[0:1] == b"\x02":
                self._do_cfgmsg(msgtype, msgrate)

    def _do_set_minnmea(self):
        """
        Turn on minimum set of NMEA messages (GGA & GSA & GSV).
        """

        for msgtype in UBX_MSGIDS:
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
        Turn on minimum set of UBX-NAV messages (PVT & SVINFO).
        """

        for msgtype in UBX_MSGIDS:
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
        Turn on all NMEA messages.

        :param int msgrate: message rate (i.e. every nth position solution)
        """

        for msgtype in UBX_MSGIDS:
            if msgtype[0:1] in (b"\xf0", b"\xf1"):
                self._do_cfgmsg(msgtype, msgrate)

    def _do_set_allNAV(self, msgrate):
        """
        Turn on all UBX-NAV messages.

        :param int msgrate: message rate (i.e. every nth position solution)
        """

        for msgtype in UBX_MSGIDS:
            if msgtype[0:1] == b"\x01":
                self._do_cfgmsg(msgtype, msgrate)

    def _do_cfgmsg(self, msgtype: str, msgrate: int):
        """
        Set rate for specified message type via CFG-MSG.

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
            self._lbl_send_command.config(image=self._img_warn)

    def update_status(self, cfgtype, **kwargs):
        """
        Update pending confirmation status.
        """

        if cfgtype in ("ACK-ACK", "MON-VER"):
            self._lbl_send_command.config(image=self._img_confirmed)
            self.__container.set_status(f"{cfgtype} GET message received", "green")
        elif cfgtype == "ACK-NAK":
            self._lbl_send_command.config(image=self._img_warn)
            self.__container.set_status("PRESET command rejected", "red")
