"""
nmea_preset_frame.py

NMEA Configuration frame for preset and user-defined commands

Created on 22 Mar 2025

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
from pynmeagps import NMEAMessage

from pygpsclient.confirm_box import ConfirmBox
from pygpsclient.globals import (
    ERRCOL,
    ICON_CONFIRMED,
    ICON_PENDING,
    ICON_SEND,
    ICON_WARNING,
    NMEA_PRESET,
    OKCOL,
)
from pygpsclient.strings import (
    CONFIRM,
    DLGACTION,
    DLGACTIONCONFIRM,
    LBLNMEAPRESET,
)

CANCELLED = 0
CONFIRMED = 1
NOMINAL = 2


class NMEA_PRESET_Frame(Frame):
    """
    NMEA Preset and User-defined configuration command panel.
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
        self._body()
        self._do_layout()
        self._attach_events()
        self.reset()

    def _body(self):
        """
        Set up frame and widgets.
        """

        self._lbl_presets = Label(self, text=LBLNMEAPRESET, anchor=W)
        self._lbx_preset = Listbox(
            self,
            border=2,
            relief="sunken",
            height=35,
            width=55,
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
            column=0, row=1, columnspan=3, rowspan=20, padx=3, pady=3, sticky=(W, E)
        )
        self._scr_presetv.grid(column=2, row=1, rowspan=20, sticky=(N, S, E))
        self._scr_preseth.grid(column=0, row=21, columnspan=3, sticky=(W, E))
        self._btn_send_command.grid(column=3, row=1, padx=3, ipadx=3, ipady=3, sticky=E)
        self._lbl_send_command.grid(
            column=3, row=2, padx=3, ipadx=3, ipady=3, sticky=(W, E)
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

    def reset(self):
        """
        Reset panel - Load user-defined presets if there are any.
        """

        idx = 0
        for upst in self.__app.configuration.get("nmeapresets_l"):
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

        if self._preset_command in ("", None):
            self.__container.set_status("Select preset", ERRCOL)
            return

        confids = []
        try:
            if CONFIRM in self._preset_command:
                if ConfirmBox(self, DLGACTION, DLGACTIONCONFIRM).show():
                    confids = self._do_user_defined(self._preset_command)
                    status = CONFIRMED
                else:
                    status = CANCELLED
            else:
                confids = self._do_user_defined(self._preset_command)
                status = CONFIRMED

            if status == CONFIRMED:
                self._lbl_send_command.config(image=self._img_pending)
                self.__container.set_status(
                    "Command(s) sent",
                )
                for msgid in confids:
                    self.__container.set_pending(msgid, NMEA_PRESET)
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

    def _do_user_defined(self, command: str) -> list:
        """
        Parse and send user-defined command(s).

        This could result in any number of errors if the
        nmeapresets file contains garbage, so there's a broad
        catch-all-exceptions in the calling routine.

        :param str command: user defined message constructor(s)
        :return: list of confirmation msgids expected
        :rtype: list
        """

        confids = []
        try:
            seg = command.split(";")
            for i in range(1, len(seg), 4):
                talker = seg[i].strip()
                msg_id = seg[i + 1].strip()
                payload = seg[i + 2].strip()
                mode = int(seg[i + 3].strip().rstrip("\r\n"))
                if payload == "":
                    msg = NMEAMessage(talker, msg_id, mode)
                else:
                    payload = f"{payload}".split(",")
                    msg = NMEAMessage(talker, msg_id, mode, payload=payload)
                confids.append(msg.identity)
                # self.logger.debug(f"{str(msg)=} - {msg.serialize()=} {confids=}")
                self.__container.send_command(msg)
        except Exception as err:  # pylint: disable=broad-except
            self.__app.set_status(f"Error {err}", ERRCOL)
            self._lbl_send_command.config(image=self._img_warn)

        return confids

    def update_status(self, msg: NMEAMessage):
        """
        Update pending confirmation status.

        :param NMEAMessage msg: NMEA config message
        """

        status = getattr(msg, "status", "OK")
        if status == "OK":
            self._lbl_send_command.config(image=self._img_confirmed)
            self.__container.set_status("Preset command(s) acknowledged", OKCOL)
        elif status == "ERROR":
            self._lbl_send_command.config(image=self._img_warn)
            self.__container.set_status("Preset command(s) rejected", ERRCOL)
