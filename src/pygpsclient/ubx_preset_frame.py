"""
ubx_preset_frame.py

UBX Configuration frame for preset and user-defined commands

Created on 22 Dec 2020

:author: semuadmin (Steve Smith)
:copyright: 2020 semuadmin
:license: BSD 3-Clause
"""

import logging
from tkinter import (
    EW,
    HORIZONTAL,
    LEFT,
    VERTICAL,
    Button,
    E,
    Frame,
    Label,
    Listbox,
    N,
    S,
    Scrollbar,
    W,
)

from PIL import Image, ImageTk
from pyubx2 import UBXMessage

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
)

CANCELLED = 0
CONFIRMED = 1
NOMINAL = 2


class UBX_PRESET_Frame(Frame):
    """
    UBX Preset and User-defined configuration command panel.
    """

    def __init__(self, app: Frame, parent: Frame, *args, **kwargs):
        """
        Constructor.

        :param Frame app: reference to main tkinter application
        :param Frame parent: reference to parent frame (config-dialog)
        :param args: optional args to pass to Frame parent class
        :param kwargs: optional kwargs to pass to Frame parent class
        """

        self.__app = app  # Reference to main application class
        self.__master = self.__app.appmaster  # Reference to root class (Tk)
        self.logger = logging.getLogger(__name__)
        self.__container = parent

        super().__init__(parent.container, *args, **kwargs)

        self._img_send = ImageTk.PhotoImage(Image.open(ICON_SEND))
        self._img_pending = ImageTk.PhotoImage(Image.open(ICON_PENDING))
        self._img_confirmed = ImageTk.PhotoImage(Image.open(ICON_CONFIRMED))
        self._img_warn = ImageTk.PhotoImage(Image.open(ICON_WARNING))
        self._preset_command = None
        self._configfile = None
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
            width=40,
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

        self._lbl_presets.grid(column=0, row=0, columnspan=6, padx=3, sticky=EW)
        self._lbx_preset.grid(
            column=0, row=1, columnspan=3, rowspan=12, padx=3, pady=3, sticky=EW
        )
        self._scr_presetv.grid(column=2, row=1, rowspan=12, sticky=(N, S, E))
        self._scr_preseth.grid(column=0, row=13, columnspan=3, sticky=EW)
        self._btn_send_command.grid(column=3, row=1, ipadx=3, ipady=3, sticky=EW)
        self._lbl_send_command.grid(column=3, row=3, ipadx=3, ipady=3, sticky=EW)

        cols, rows = self.grid_size()
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

    def reset(self):
        """
        Reset panel - load user-defined presets if there are any.
        """

        self.__app.configuration.init_presets("ubx")
        for i, preset in enumerate(self.__app.configuration.get("ubxpresets_l")):
            self._lbx_preset.insert(i, preset)

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
            self.__container.status_label = ("Select preset", ERRCOL)
            return

        status = CONFIRMED
        confids = ("MON-VER", "ACK-ACK")
        try:
            confids = ("MON-VER", "ACK-ACK", "ACK-NAK")
            if CONFIRM in self._preset_command:
                if ConfirmBox(self, DLGACTION, DLGACTIONCONFIRM).show():
                    self._format_preset(self._preset_command)
                    status = CONFIRMED
                else:
                    status = CANCELLED
            else:
                self._format_preset(self._preset_command)
                status = CONFIRMED

            if status == CONFIRMED:
                self._lbl_send_command.config(image=self._img_pending)
                self.__container.status_label = "Command(s) sent"
                for msgid in confids:
                    self.__container.set_pending(msgid, UBX_PRESET)
            elif status == CANCELLED:
                self.__container.status_label = "Command(s) cancelled"
            elif status == NOMINAL:
                self.__container.status_label = "Command(s) sent, no results"

        except Exception as err:  # pylint: disable=broad-except
            self.__container.status_label = (f"Error {err}", ERRCOL)
            self._lbl_send_command.config(image=self._img_warn)

    def _format_preset(self, command: str):
        """
        Format user-defined command(s).

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
            self.__container.status_label = (f"Error {err}", ERRCOL)
            self._lbl_send_command.config(image=self._img_warn)

    def update_status(self, msg: UBXMessage):
        """
        Update pending confirmation status.

        :param UBXMessage msg: UBX config message
        """

        if msg.identity in ("ACK-ACK", "MON-VER"):
            self._lbl_send_command.config(image=self._img_confirmed)
            self.__container.status_label = ("Preset command(s) acknowledged", OKCOL)
        elif msg.identity == "ACK-NAK":
            self._lbl_send_command.config(image=self._img_warn)
            self.__container.status_label = ("Preset command(s) rejected", ERRCOL)
