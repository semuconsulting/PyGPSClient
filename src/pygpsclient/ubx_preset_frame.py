"""
ubx_preset_frame.py

UBX Configuration frame for preset and user-defined commands

Created on 22 Dec 2020

:author: semuadmin
:copyright: 2020 SEMU Consulting
:license: BSD 3-Clause
"""

import logging
from tkinter import (
    HORIZONTAL,
    LEFT,
    VERTICAL,
    Button,
    Checkbutton,
    E,
    Frame,
    IntVar,
    Label,
    Listbox,
    N,
    S,
    Scrollbar,
    W,
)

from PIL import Image, ImageTk
from pyubx2 import POLL, SET, UBX_MSGIDS, UBX_PAYLOADS_POLL, UBXMessage

from pygpsclient.confirm_box import ConfirmBox
from pygpsclient.globals import (
    ERRCOL,
    ICON_CONFIRMED,
    ICON_PENDING,
    ICON_SEND,
    ICON_WARNING,
    OKCOL,
    UBX_PRESET,
)
from pygpsclient.strings import (
    CONFIRM,
    DLGACTION,
    DLGACTIONCONFIRM,
    LBLUBXPRESET,
    PSTALLINFOFF,
    PSTALLINFON,
    PSTALLLOGOFF,
    PSTALLLOGON,
    PSTALLMONOFF,
    PSTALLMONON,
    PSTALLNMEAOFF,
    PSTALLNMEAON,
    PSTALLRXMOFF,
    PSTALLRXMON,
    PSTALLSECOFF,
    PSTALLSECON,
    PSTALLUBXOFF,
    PSTALLUBXON,
    PSTMINNMEAON,
    PSTMINUBXON,
    PSTPOLLALLCFG,
    PSTPOLLALLNAV,
    PSTPOLLINFO,
    PSTPOLLPORT,
    PSTRESET,
    PSTSAVE,
    PSTUSENMEA,
    PSTUSEUBX,
)

PRESET_COMMMANDS = [
    PSTRESET,
    PSTSAVE,
    PSTUSEUBX,
    PSTUSENMEA,
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
    PSTALLSECON,
    PSTALLSECOFF,
    PSTPOLLPORT,
    PSTPOLLINFO,
    PSTPOLLALLCFG,
    PSTPOLLALLNAV,
]
CANCELLED = 0
CONFIRMED = 1
NOMINAL = 2


class UBX_PRESET_Frame(Frame):
    """
    UBX Preset and User-defined configuration command panel.
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
        self.__master = self.__app.appmaster  # Reference to root class (Tk)
        self.logger = logging.getLogger(__name__)
        self.__container = container

        Frame.__init__(self, self.__container.container, *args, **kwargs)

        self._img_send = ImageTk.PhotoImage(Image.open(ICON_SEND))
        self._img_pending = ImageTk.PhotoImage(Image.open(ICON_PENDING))
        self._img_confirmed = ImageTk.PhotoImage(Image.open(ICON_CONFIRMED))
        self._img_warn = ImageTk.PhotoImage(Image.open(ICON_WARNING))
        self._preset_command = None
        self._configfile = None
        self._port_usb = IntVar()
        self._port_uart1 = IntVar()
        self._port_uart2 = IntVar()
        self._port_i2c = IntVar()
        self._port_spi = IntVar()
        self._ports = self.__app.frm_settings.defaultports.upper()
        self._body()
        self._do_layout()
        self._attach_events()
        self.reset()

    def _body(self):
        """
        Set up frame and widgets.
        """

        self._lbl_presets = Label(self, text=LBLUBXPRESET, anchor=W)
        self._lbx_preset = Listbox(
            self,
            border=2,
            relief="sunken",
            height=12,
            width=34,
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
        self._chk_usb = Checkbutton(self, text="USB", variable=self._port_usb)
        self._chk_uart1 = Checkbutton(self, text="UART1", variable=self._port_uart1)
        self._chk_uart2 = Checkbutton(self, text="UART2", variable=self._port_uart2)
        self._chk_i2c = Checkbutton(self, text="I2C", variable=self._port_i2c)
        self._chk_spi = Checkbutton(self, text="SPI", variable=self._port_spi)

    def _do_layout(self):
        """
        Layout widgets.
        """

        self._lbl_presets.grid(column=0, row=0, columnspan=6, padx=3, sticky=(W, E))
        self._lbx_preset.grid(
            column=0, row=1, columnspan=3, rowspan=12, padx=3, pady=3, sticky=(W, E)
        )
        self._scr_presetv.grid(column=2, row=1, rowspan=12, sticky=(N, S, E))
        self._scr_preseth.grid(column=0, row=13, columnspan=3, sticky=(W, E))
        self._btn_send_command.grid(column=3, row=1, ipadx=3, ipady=3, sticky=E)
        self._lbl_send_command.grid(column=4, row=1, ipadx=3, ipady=3, sticky=E)
        self._chk_usb.grid(column=3, row=2, columnspan=2, sticky=W)
        self._chk_uart1.grid(column=3, row=3, columnspan=2, sticky=W)
        self._chk_uart2.grid(column=3, row=4, columnspan=2, sticky=W)
        self._chk_i2c.grid(column=3, row=5, columnspan=2, sticky=W)
        self._chk_spi.grid(column=3, row=6, columnspan=2, sticky=W)

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
        for prt in ("usb", "uart1", "uart2", "i2c", "spi"):
            getattr(self, f"_port_{prt}").trace_add(
                ("write", "unset"), self._on_select_port
            )

    def reset(self):
        """
        Reset panel - Load user-defined presets if there are any.
        """

        self._port_usb.set("USB" in self._ports)
        self._port_uart1.set("UART1" in self._ports)
        self._port_uart2.set("UART2" in self._ports)
        self._port_i2c.set("I2C" in self._ports)
        self._port_spi.set("SPI" in self._ports)
        idx = 0
        for pst in PRESET_COMMMANDS:
            self._lbx_preset.insert(idx, pst)
            idx += 1

        for upst in self.__app.configuration.get("ubxpresets_l"):
            self._lbx_preset.insert(idx, "USER " + upst)
            idx += 1

    def _on_select_port(self, var, index, mode):  # pylint: disable=unused-argument
        """
        Port has been selected.
        """

        ports = ""
        for prt in ("usb", "uart1", "uart2", "i2c", "spi"):
            if getattr(self, f"_port_{prt}").get():
                ports += prt.upper() + ","
        ports = ports.strip(",")
        self.__app.configuration.set("defaultport_s", ports)

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

        if self._preset_command in ("", None):
            self.__container.set_status("Select preset", ERRCOL)
            return

        status = CONFIRMED
        confids = ("MON-VER", "ACK-ACK")
        try:
            if self._preset_command == PSTRESET:
                status = self._do_factory_reset()
            elif self._preset_command == PSTSAVE:
                status = self._do_store_config()
            elif self._preset_command == PSTUSEUBX:
                self._do_set_allnmea(0)
                self._do_set_minNAV()
            elif self._preset_command == PSTUSENMEA:
                self._do_set_allNAV(0)
                self._do_set_minnmea()
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
            elif self._preset_command == PSTALLSECON:
                self._do_set_sec(1)
            elif self._preset_command == PSTALLSECOFF:
                self._do_set_sec(0)
            elif self._preset_command == PSTPOLLPORT:
                self._do_poll_prt()
            elif self._preset_command == PSTPOLLINFO:
                self._do_poll_inf()
            elif self._preset_command == PSTPOLLALLCFG:
                self._do_poll_all_CFG()
            elif self._preset_command == PSTPOLLALLNAV:
                self._do_poll_all_NAV()
            else:
                confids = ("MON-VER", "ACK-ACK", "ACK-NAK")
                if CONFIRM in self._preset_command:
                    if ConfirmBox(self, DLGACTION, DLGACTIONCONFIRM).show():
                        self._do_user_defined(self._preset_command)
                        status = CONFIRMED
                    else:
                        status = CANCELLED
                else:
                    self._do_user_defined(self._preset_command)
                    status = CONFIRMED

            if status == CONFIRMED:
                self._lbl_send_command.config(image=self._img_pending)
                self.__container.set_status(
                    "Command(s) sent",
                )
                for msgid in confids:
                    self.__container.set_pending(msgid, UBX_PRESET)
            elif status == CANCELLED:
                self.__container.set_status(
                    "Command(s) cancelled",
                )
            elif status == NOMINAL:
                self.__container.set_status(
                    "Command(s) sent, no results",
                )

        except Exception as err:  # pylint: disable=broad-except
            self.__container.set_status(f"Error {err}", ERRCOL)
            self._lbl_send_command.config(image=self._img_warn)

    def _do_poll_all_CFG(self):
        """
        Poll all CFG message configurations.
        """

        for msgtype in UBX_PAYLOADS_POLL:
            if msgtype[0:3] == "CFG" and msgtype not in (
                "CFG-INF",
                "CFG-MSG",
                "CFG-PRT-IO",
                "CFG-TP5-TPX",
            ):
                msg = UBXMessage("CFG", msgtype, POLL)
                self.__container.send_command(msg)

    def _do_poll_all_NAV(self):
        """
        Poll all NAV/NAV2 message configurations.
        """

        for msgtype in UBX_PAYLOADS_POLL:
            if msgtype[0:3] == "NAV":
                msg = UBXMessage(msgtype.split("-")[0], msgtype, POLL)
                self.__container.send_command(msg)

    def _do_poll_prt(self):
        """
        Poll PRT message configuration for each port.
        """

        for portID in range(5):
            msg = UBXMessage("CFG", "CFG-PRT", POLL, portID=portID)
            self.__container.send_command(msg)

    def _do_poll_inf(self):
        """
        Poll INF message configuration.
        """

        for protid in (0, 1):  # UBX & NMEA
            msg = UBXMessage("CFG", "CFG-INF", POLL, protocolID=protid)
            self.__container.send_command(msg)

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
            self.__container.send_command(msg)
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
            if msgtype[0:1] == b"\x0a":
                self._do_cfgmsg(msgtype, msgrate)

    def _do_set_rxm(self, msgrate):
        """
        Turn on all device receiver management messages RXM.

        :param int msgrate: message rate (i.e. every nth position solution)
        """

        for msgtype in UBX_MSGIDS:
            if msgtype[0:1] == b"\x02":
                self._do_cfgmsg(msgtype, msgrate)

    def _do_set_sec(self, msgrate):
        """
        Turn on all device security messages SEC.

        :param int msgrate: message rate (i.e. every nth position solution)
        """

        for msgtype in UBX_MSGIDS:
            if msgtype[0:1] == b"\x27":
                self._do_cfgmsg(msgtype, msgrate)

    def _do_set_minnmea(self):
        """
        Turn on minimum set of NMEA messages (GGA & GSA & GSV).
        """

        for msgtype in UBX_MSGIDS:
            if msgtype[0:1] == b"\xf0":  # standard NMEA
                if msgtype in (b"\xf0\x00", b"\xf0\x02", b"\xf0\x04"):  # GGA, GSA, RMC
                    self._do_cfgmsg(msgtype, 1)
                elif msgtype == b"\xf0\x03":  # GSV
                    self._do_cfgmsg(msgtype, 4)
                else:
                    self._do_cfgmsg(msgtype, 0)
            if msgtype[0:1] == b"\xf1":  # proprietary NMEA
                self._do_cfgmsg(msgtype, 0)

    def _do_set_minNAV(self):
        """
        Turn on minimum set of UBX-NAV messages (DOP, PVT, & SAT).
        """

        for msgtype in UBX_MSGIDS:
            if msgtype[0:1] == b"\x01":  # UBX-NAV
                if msgtype == b"\x01\x07":  # NAV-PVT
                    self._do_cfgmsg(msgtype, 1)
                elif msgtype in (b"\x01\x04", b"\x01\x35"):  # NAV-DOP, NAV-SAT
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

        The receiver ports to which the rate applies are defined
        in the `defaultport_s` configuration setting.

        :param str msgtype: type of config message
        :param int msgrate: message rate (i.e. every nth position solution)
        """

        msgclass = int.from_bytes(msgtype[0:1], "little", signed=False)
        msgid = int.from_bytes(msgtype[1:2], "little", signed=False)

        # select which receiver ports to apply rate to
        rates = {}
        prts = self.__app.configuration.get("defaultport_s").upper().split(",")
        for prt in prts:
            rates[prt] = msgrate

        # create CFG-MSG command
        msg = UBXMessage(
            "CFG",
            "CFG-MSG",
            SET,
            msgClass=msgclass,
            msgID=msgid,
            rateDDC=rates.get("I2C", 0),
            rateUART1=rates.get("UART1", 0),
            rateUART2=rates.get("UART2", 0),
            rateUSB=rates.get("USB", 0),
            rateSPI=rates.get("SPI", 0),
        )
        self.__container.send_command(msg)

    def _do_factory_reset(self) -> bool:
        """
        Restore to factory defaults stored in battery-backed RAM
        but display confirmation message box first.

        :return: boolean signifying whether OK was pressed
        :rtype: bool
        """

        if ConfirmBox(self, DLGACTION, DLGACTIONCONFIRM).show():
            msg = UBXMessage(
                "CFG",
                "CFG-CFG",
                SET,
                clearMask=b"\x1f\x1f\x00\x00",
                # saveMask=b"\x1f\x1f\x00\x00",
                loadMask=b"\x1f\x1f\x00\x00",
                devBBR=1,
                devFlash=1,
                devEEPROM=1,
            )
            self.__container.send_command(msg)
            return CONFIRMED

        return CANCELLED

    def _do_store_config(self) -> bool:
        """
        Store current configuration in persistent storage
        but display confirmation message box first.

        :return: boolean signifying whether OK was pressed
        :rtype: bool
        """

        if ConfirmBox(self, DLGACTION, DLGACTIONCONFIRM).show():
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
            self.__container.send_command(msg)
            return CONFIRMED

        return CANCELLED

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
                self.__container.send_command(msg)
        except Exception as err:  # pylint: disable=broad-except
            self.__app.set_status(f"Error {err}", ERRCOL)
            self._lbl_send_command.config(image=self._img_warn)

    def update_status(self, msg: UBXMessage):
        """
        Update pending confirmation status.

        :param UBXMessage msg: UBX config message
        """

        if msg.identity in ("ACK-ACK", "MON-VER"):
            self._lbl_send_command.config(image=self._img_confirmed)
            self.__container.set_status("Preset command(s) acknowledged", OKCOL)
        elif msg.identity == "ACK-NAK":
            self._lbl_send_command.config(image=self._img_warn)
            self.__container.set_status("Preset command(s) rejected", ERRCOL)
