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

from pygpsclient.dynamic_config_frame import Dynamic_Config_Frame
from pygpsclient.globals import (
    CONNECTED,
    CONNECTED_SIMULATOR,
    CONNECTED_SOCKET,
    ENABLE_CFG_LEGACY,
    ERRCOL,
    UBX_CFGMSG,
    UBX_CFGOTHER,
    UBX_CFGPRT,
    UBX_CFGRATE,
    UBX_CFGVAL,
    UBX_MONHW,
    UBX_MONRF,
    UBX_MONVER,
    UBX_PRESET,
)
from pygpsclient.hardware_info_frame import Hardware_Info_Frame
from pygpsclient.strings import DLGTUBX
from pygpsclient.toplevel_dialog import ToplevelDialog
from pygpsclient.ubx_cfgval_frame import UBX_CFGVAL_Frame
from pygpsclient.ubx_msgrate_frame import UBX_MSGRATE_Frame
from pygpsclient.ubx_port_frame import UBX_PORT_Frame
from pygpsclient.ubx_preset_frame import UBX_PRESET_Frame
from pygpsclient.ubx_solrate_frame import UBX_RATE_Frame


class UBXConfigDialog(ToplevelDialog):
    """,
    UBXConfigDialog class.
    """

    def __init__(self, app, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Constructor.

        :param Frame app: reference to main tkinter application
        :param args: optional args to pass to parent class (not currently used)
        :param kwargs: optional kwargs to pass to parent class (not currently used)
        """

        self.__app = app  # Reference to main application class

        super().__init__(app, DLGTUBX)

        self._cfg_msg_command = None
        self._pending_confs = {}
        self._recordmode = False

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
            self.__app, self, borderwidth=2, relief="groove", protocol="UBX"
        )
        self._frm_config_port = UBX_PORT_Frame(
            self.__app, self, borderwidth=2, relief="groove"
        )
        self._frm_config_rate = UBX_RATE_Frame(
            self.__app, self, borderwidth=2, relief="groove"
        )
        self._frm_config_msg = UBX_MSGRATE_Frame(
            self.__app, self, borderwidth=2, relief="groove"
        )
        self._frm_config_dynamic = Dynamic_Config_Frame(
            self.__app, self, borderwidth=2, relief="groove", protocol="UBX"
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

        # top of grid
        col = 0
        row = 0
        colsp = 0
        for frm in (
            self._frm_device_info,
            self._frm_config_port,
            self._frm_config_rate,
            self._frm_config_msg,
        ):
            colsp, rowsp = frm.grid_size()
            frm.grid(
                column=col,
                row=row,
                columnspan=colsp,
                rowspan=rowsp,
                sticky=NSEW,
            )
            row += rowsp
        # middle column of grid
        row = 0
        col += colsp
        for frm in (self._frm_configdb, self._frm_preset):
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
        if ENABLE_CFG_LEGACY:
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

        self._frm_config_rate.reset()
        self._frm_config_port.reset()
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
                self._frm_device_info.update_status(msg)
            elif ubxfrm == UBX_CFGPRT:
                self._frm_config_port.update_status(msg)
            elif ubxfrm == UBX_CFGRATE:
                self._frm_config_rate.update_status(msg)
            elif ubxfrm == UBX_CFGMSG:
                self._frm_config_msg.update_status(msg)
            elif ubxfrm == UBX_CFGVAL:
                self._frm_configdb.update_status(msg)
            elif ubxfrm == UBX_PRESET:
                self._frm_preset.update_status(msg)
            elif ubxfrm == UBX_CFGOTHER:
                self._frm_config_dynamic.update_status(msg)

            # reset all confirmation flags for this frame
            for msgid in (msg.identity, "ACK-ACK", "ACK-NAK"):
                if self._pending_confs.get(msgid, None) == ubxfrm:
                    self._pending_confs.pop(msgid)

    @property
    def recordmode(self) -> bool:
        """
        Getter for recording status.

        :return: recording yes/no
        :rtype: bool
        """

        return self._recordmode

    @recordmode.setter
    def recordmode(self, recordmode: bool):
        """
        Setter for record mode.

        :param bool recordmode: recording yes/no
        """

        self._recordmode = recordmode

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
