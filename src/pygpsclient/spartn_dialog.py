"""
spartn_dialog.py

SPARTN client configuration dialog.

Initial settings are from the saved configuration.
Once started, the persisted state for the SPARTN client is held in
the threaded SPARTN handler itself, NOT in this frame.

The dialog may be closed while the SPARTN client is running.

Created on 26 Jan 2023

:author: semuadmin (Steve Smith)
:copyright: 2020 semuadmin
:license: BSD 3-Clause
"""

from tkinter import NSEW
from types import NoneType

from pyubx2 import UBXMessage

from pygpsclient.globals import (
    CONNECTED_SPARTNIP,
    CONNECTED_SPARTNLB,
    SPARTN_GNSS,
    SPARTN_LBAND,
    SPARTN_MQTT,
)
from pygpsclient.spartn_gnss_frame import SPARTNGNSSDialog
from pygpsclient.spartn_lband_frame import SpartnLbandDialog
from pygpsclient.spartn_mqtt_frame import SPARTNMQTTDialog
from pygpsclient.strings import DLGTSPARTN
from pygpsclient.toplevel_dialog import ToplevelDialog

RXMMSG = "RXM-SPARTN-KEY"
CFGSET = "CFG-VALGET/SET"
CFGPOLL = "CFG-VALGET"

MINDIM = (408, 758)


class SPARTNConfigDialog(ToplevelDialog):
    """,
    SPARTNConfigDialog class.
    """

    def __init__(self, app, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Constructor.

        :param Frame app: reference to main tkinter application
        :param args: optional args to pass to parent class (not currently used)
        :param kwargs: optional kwargs to pass to parent class (not currently used)
        """

        self.__app = app  # Reference to main application class
        self.__master = self.__app.appmaster  # Reference to root class (Tk)

        super().__init__(app, DLGTSPARTN, MINDIM)
        self._pending_confs = {}
        self._lband_enabled = self.__app.configuration.get("lband_enabled_b")

        self._body()
        self._do_layout()
        self._reset()
        self._attach_events()
        self._finalise()

    def _body(self):
        """
        Set up frame and widgets.
        """
        # pylint: disable=unnecessary-lambda

        self.frm_corrip = SPARTNMQTTDialog(
            self.__app,
            self,
            borderwidth=2,
            relief="groove",
        )
        if self._lband_enabled:
            self.frm_corrlband = SpartnLbandDialog(
                self.__app,
                self,
                borderwidth=2,
                relief="groove",
            )
        self.frm_gnss = SPARTNGNSSDialog(
            self.__app, self, borderwidth=2, relief="groove"
        )

    def _do_layout(self):
        """
        Position widgets in frame.
        """

        self.frm_corrip.grid(
            column=0,
            row=0,
            ipadx=5,
            ipady=5,
            sticky=NSEW,
        )
        col = 1
        if self._lband_enabled:
            self.frm_corrlband.grid(
                column=col,
                row=0,
                ipadx=5,
                ipady=5,
                sticky=NSEW,
            )
            col += 1
        self.frm_gnss.grid(
            column=col,
            row=0,
            ipadx=5,
            ipady=5,
            sticky=NSEW,
        )

    def _reset(self):
        """
        Reset configuration widgets.
        """

        self.status_label = ""

    def _attach_events(self):
        """
        Bind events to window.
        """

        # self.bind("<Configure>", self._on_resize)

    def set_pending(self, msgid: int, spartnfrm: int):
        """
        Set pending confirmation flag for UBX configuration frame to
        signify that it's waiting for a confirmation message.

        :param int msgid: UBX message identity
        :param int spartnfrm: integer representing SPARTN configuration frame
        """

        self._pending_confs[msgid] = spartnfrm

    def update_pending(self, msg: UBXMessage):
        """
        Update pending confirmation status.
        :param UBXMessage msg: UBX config message
        """

        if not hasattr(msg, "identity"):
            return

        # update ebno & fecBits values
        if msg.identity == "RXM-PMP":
            self.frm_corrlband.update_status(msg)
            return

        spartnfrm = self._pending_confs.get(msg.identity, None)

        if spartnfrm is not None:
            if spartnfrm == SPARTN_GNSS:
                self.frm_gnss.update_status(msg)
            elif spartnfrm == SPARTN_LBAND:
                self.frm_corrlband.update_status(msg)
            elif spartnfrm == SPARTN_MQTT:
                self.frm_corrip.update_status(msg)

            # reset all confirmation flags for this frame
            for msgid in (msg.identity, "ACK-ACK", "ACK-NAK"):
                if self._pending_confs.get(msgid, None) == spartnfrm:
                    self._pending_confs.pop(msgid)

    def set_controls(self, status: bool, msgt: tuple | NoneType = None):
        """
        Set controls in IP or L-Band clients.

        :param bool status: connected to SPARTN server yes/no
        :param tuple | Nonetype msgt: tuple of (message, color) or None
        """

        if status == CONNECTED_SPARTNIP:
            self.frm_corrip.set_controls(status)
        elif status == CONNECTED_SPARTNLB:
            self.frm_corrlband.set_controls(status)
        if msgt is not None:
            self.status_label = msgt

    def disconnect_ip(self, msg: str = ""):
        """
        Disconnect from IP (MQTT) client.

        :param str msg: optional disconnection message
        """

        self.frm_corrip.on_disconnect(msg)

    def disconnect_lband(self, msg: str = ""):
        """
        Disconnect from L-Band client.

        :param str msg: optional disconnection message
        """

        self.frm_corrlband.on_disconnect(msg)

    @property
    def server(self) -> str:
        """
        Getter for server.

        :return: server
        :rtype: str
        """

        return self.frm_corrip.server

    @server.setter
    def server(self, server: str):
        """
        Setter for server.

        :param str clientid: Client ID
        """

        self.frm_corrip.server = server

    @property
    def clientid(self) -> str:
        """
        Getter for Client ID from IP configuration dialog.

        :return: client ID
        :rtype: str
        """

        return self.frm_corrip.clientid

    @clientid.setter
    def clientid(self, clientid: str):
        """
        Setter for Client ID.

        :param str clientid: Client ID
        """

        self.frm_corrip.clientid = clientid
