"""
nmea_config_dialog.py

NMEA configuration container dialog

This is the pop-up dialog containing the various
proprietary NMEA configuration command frames.

Supply initial settings via `config` keyword argument.

Created on 22 Mar 2025

:author: semuadmin (Steve Smith)
:copyright: 2020 semuadmin
:license: BSD 3-Clause
"""

from tkinter import NSEW

from pynmeagps import SET, NMEAMessage

from pygpsclient.dynamic_config_frame import Dynamic_Config_Frame
from pygpsclient.globals import (
    CONNECTED,
    CONNECTED_SIMULATOR,
    CONNECTED_SOCKET,
    ERRCOL,
    NMEA_CFGOTHER,
    NMEA_MONHW,
    NMEA_PRESET,
)
from pygpsclient.hardware_info_frame import Hardware_Info_Frame
from pygpsclient.nmea_preset_frame import NMEA_PRESET_Frame
from pygpsclient.strings import DLGTNMEA
from pygpsclient.toplevel_dialog import ToplevelDialog


class NMEAConfigDialog(ToplevelDialog):
    """
    NMEAConfigDialog class.
    """

    def __init__(self, app, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Constructor.

        :param Frame app: reference to main tkinter application
        :param args: optional args to pass to parent class (not currently used)
        :param kwargs: optional kwargs to pass to parent class (not currently used)
        """

        self.__app = app  # Reference to main application class

        super().__init__(app, DLGTNMEA)

        self._cfg_msg_command = None
        self._pending_confs = {}

        self._body()
        self._do_layout()
        self._reset()
        self._attach_events()
        self._finalise()

    def _body(self):
        """
        Set up frame and widgets.
        """

        # add configuration widgets
        self._frm_device_info = Hardware_Info_Frame(
            self.__app, self, borderwidth=2, relief="groove", protocol="NMEA"
        )
        self._frm_config_dynamic = Dynamic_Config_Frame(
            self.__app, self, borderwidth=2, relief="groove", protocol="NMEA"
        )
        self._frm_preset = NMEA_PRESET_Frame(
            self.__app,
            self,
            borderwidth=2,
            relief="groove",
        )

    def _do_layout(self):
        """
        Position widgets in frame.
        """

        # top of grid
        col = 0
        row = 0
        # left column of grid
        for frm in (self._frm_device_info, self._frm_preset):
            colsp, rowsp = frm.grid_size()
            frm.grid(
                column=col,
                row=row,
                columnspan=colsp,
                rowspan=rowsp,
                sticky=NSEW,
            )
            row += rowsp
        # right column of grid
        row = 0
        col += colsp
        for frm in (self._frm_config_dynamic,):
            colsp, rowsp = frm.grid_size()
            frm.grid(
                column=col,
                row=row,
                columnspan=colsp,
                rowspan=rowsp,
                sticky=NSEW,
            )
            row += rowsp

    def _reset(self):
        """
        Reset configuration widgets.
        """

        self._frm_config_dynamic.reset()
        self._frm_device_info.reset()
        if self.__app.conn_status not in (
            CONNECTED,
            CONNECTED_SOCKET,
            CONNECTED_SIMULATOR,
        ):
            self.status_label = ("Device not connected", ERRCOL)

    def _attach_events(self):
        """
        Bind events to window.
        """

        # self.bind("<Configure>", self._on_resize)

    def set_pending(self, msgid: int, ubxfrm: int):
        """
        Set pending confirmation flag for NMEA configuration frame to
        signify that it's waiting for a confirmation message.

        :param int msgid: NMEA message identity
        :param int ubxfrm: integer representing UBX configuration frame (0-6)
        """

        self._pending_confs[msgid] = ubxfrm

    def update_pending(self, msg: NMEAMessage):
        """
        Receives polled confirmation message from the nmea_handler and
        updates whichever NMEA config frame is waiting for this confirmation.

        :param NMEAMessage msg: NMEA config message
        """

        nmeafrm = self._pending_confs.get(msg.identity, None)

        if nmeafrm is not None:
            if nmeafrm == NMEA_MONHW:
                self._frm_device_info.update_status(msg)
            elif nmeafrm == NMEA_PRESET:
                self._frm_preset.update_status(msg)
            elif nmeafrm == NMEA_CFGOTHER:
                self._frm_config_dynamic.update_status(msg)

            # reset all confirmation flags for this frame
            for msgid in (msg.identity, "ACK-ACK", "ACK-NAK"):
                if self._pending_confs.get(msgid, None) == nmeafrm:
                    self._pending_confs.pop(msgid)

    def send_command(self, msg: NMEAMessage):
        """
        Send command to receiver.
        """

        self.__app.send_to_device(msg.serialize())
        self._record_command(msg)

    def _record_command(self, msg: NMEAMessage):
        """
        Record command to memory if in 'record' mode.

        :param bytes msg: configuration message
        """

        if self.__app.recording and msg.msgmode == SET:
            self.__app.recorded_commands = msg
