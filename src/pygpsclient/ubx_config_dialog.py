"""
ubx_config_dialog.py

UBX configuration container dialog

This is the pop-up dialog containing the various
UBX configuration command frames.

Supply initial settings via `config` keyword argument.

NB: Individual UBX configuration commands do not have uniquely
identifiable synchronous or asynchronous responses (e.g. unique
txn ID). The way we keep tabs on confirmation status is to
maintain a list of all commands sent and the responses they're
expecting. When we receive a response, we check against the list
of awaited responses of the same type and flag the first one we
find as 'confirmed'.

Created on 19 Sep 2020

:author: semuadmin (Steve Smith)
:copyright: 2020 semuadmin
:license: BSD 3-Clause
"""

from tkinter import NSEW

from pyubx2 import SET, UBXMessage

from pygpsclient.globals import (
    CONNECTED,
    CONNECTED_SIMULATOR,
    CONNECTED_SOCKET,
    ERRCOL,
    ROMVER_NEW,
    UBX_CFGVAL,
    UBX_MONHW,
    UBX_MONRF,
    UBX_MONVER,
    UBX_PRESET,
)
from pygpsclient.hardware_info_frame import Hardware_Info_Frame
from pygpsclient.strings import DLGTUBX, NA, NOTCONN, ROMVERWARN
from pygpsclient.toplevel_dialog import ToplevelDialog
from pygpsclient.ubx_cfgval_frame import UBX_CFGVAL_Frame
from pygpsclient.ubx_preset_frame import UBX_PRESET_Frame


class UBXConfigDialog(ToplevelDialog):
    """,
    UBXConfigDialog class.
    """

    def __init__(self, app, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Constructor.

        :param Tk app: reference to main tkinter application
        :param args: optional args to pass to parent class (not currently used)
        :param kwargs: optional kwargs to pass to parent class (not currently used)
        """

        self.__app = app  # Reference to main application class

        super().__init__(app, DLGTUBX)

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
        self.frm_device_info = Hardware_Info_Frame(
            self.__app, self, protocol="UBX", borderwidth=2, relief="groove"
        )
        self._frm_configdb = UBX_CFGVAL_Frame(
            self.__app, self, borderwidth=2, relief="groove"
        )
        self._frm_preset = UBX_PRESET_Frame(
            self.__app,
            self,
            borderwidth=2,
            relief="groove",
        )

    def _do_layout(self):
        """
        Position widgets in frame.
        """

        self.frm_device_info.grid(column=0, row=0, columnspan=3, sticky=NSEW)
        self._frm_configdb.grid(column=0, row=1, rowspan=1, sticky=NSEW)
        self._frm_preset.grid(column=1, row=1, rowspan=1, sticky=NSEW)

        for col in range(0, 2):
            self.container.grid_columnconfigure(col, weight=1)
        for row in range(1, 2):
            self.container.grid_rowconfigure(row, weight=1)
        self._frm_configdb.grid_columnconfigure(0, weight=1)
        self._frm_configdb.grid_columnconfigure(1, weight=2)
        self._frm_configdb.grid_rowconfigure(2, weight=1)
        self._frm_preset.grid_columnconfigure(0, weight=1)
        self._frm_preset.grid_rowconfigure(2, weight=1)

    def _reset(self):
        """
        Reset configuration widgets.
        """

        if self.__app.conn_status not in (
            CONNECTED,
            CONNECTED_SOCKET,
            CONNECTED_SIMULATOR,
        ):
            self.set_status_label(NOTCONN, ERRCOL)
            return

        # check for modern ROM version
        hwver = self.__app.gnss_status.version_data["hwversion"]
        romver = self.__app.gnss_status.version_data["romversion"]
        if "u-blox" not in hwver or (romver < ROMVER_NEW and romver != NA):
            self.set_status_label(ROMVERWARN.format(generation="modern"), ERRCOL)
        else:
            self.frm_device_info.reset()

    def _attach_events(self):
        """
        Bind events to window.
        """

        # self.bind("<Configure>", self._on_resize)

    def set_pending(self, msgid: int, ubxfrm: int):
        """
        Set pending confirmation flag for UBX configuration frame to
        signify that it's waiting for a confirmation message.

        :param int msgid: UBX message identity
        :param int ubxfrm: integer representing UBX configuration frame (0-6)
        """

        self._pending_confs[msgid] = ubxfrm

    def update_pending(self, msg: UBXMessage):
        """
        Receives polled confirmation message from the ubx_handler and
        updates whichever UBX config frame is waiting for this confirmation.

        :param UBXMessage msg: UBX config message
        """

        ubxfrm = self._pending_confs.get(msg.identity, None)

        if ubxfrm is not None:
            if ubxfrm in (UBX_MONVER, UBX_MONHW, UBX_MONRF):
                self.frm_device_info.reset()
            elif ubxfrm == UBX_CFGVAL:
                self._frm_configdb.update_status(msg)
            elif ubxfrm == UBX_PRESET:
                self._frm_preset.update_status(msg)

            # reset all confirmation flags for this frame
            for msgid in (msg.identity, "ACK-ACK", "ACK-NAK"):
                if self._pending_confs.get(msgid, None) == ubxfrm:
                    self._pending_confs.pop(msgid)

    def send_command(self, msg: UBXMessage):
        """
        Send command to receiver.
        """

        self.__app.send_to_device(msg.serialize())
        self._record_command(msg)

    def _record_command(self, msg: UBXMessage):
        """
        Record command to memory if in 'record' mode.

        :param bytes msg: configuration message
        """

        if self.__app.recording and msg.msgmode == SET:
            self.__app.recorded_commands = msg
