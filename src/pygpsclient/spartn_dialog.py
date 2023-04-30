"""
SPARTN configuration dialog

This is the pop-up dialog containing the various
SPARTN configuration functions.

This dialog maintains its own threaded serial
stream handler for incoming and outgoing Correction
receiver (D9S) data (RXM-PMP), and must remain open for
SPARTN passthrough to work.

Created on 26 Jan 2023

:author: semuadmin
:copyright: SEMU Consulting © 2023
:license: BSD 3-Clause
"""

from tkinter import Button, E, Frame, Label, N, S, StringVar, Toplevel, W

from PIL import Image, ImageTk
from pyubx2 import UBXMessage

from pygpsclient.globals import (
    CONNECTED_SPARTNIP,
    CONNECTED_SPARTNLB,
    DLGTSPARTN,
    ICON_BLANK,
    ICON_CONFIRMED,
    ICON_EXIT,
    ICON_PENDING,
    ICON_WARNING,
    POPUP_TRANSIENT,
    SPARTN_GNSS,
    SPARTN_LBAND,
    SPARTN_MQTT,
)
from pygpsclient.spartn_gnss_frame import SPARTNGNSSDialog
from pygpsclient.spartn_lband_frame import SPARTNLBANDDialog
from pygpsclient.spartn_mqtt_frame import SPARTNMQTTDialog
from pygpsclient.strings import DLGSPARTNCONFIG

RXMMSG = "RXM-SPARTN-KEY"
CFGSET = "CFG-VALGET/SET"
CFGPOLL = "CFG-VALGET"


class SPARTNConfigDialog(Toplevel):
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
        Toplevel.__init__(self, app)
        if POPUP_TRANSIENT:
            self.transient(self.__app)
        self.resizable(False, False)
        self.title(DLGSPARTNCONFIG)  # pylint: disable=E1102
        self.protocol("WM_DELETE_WINDOW", self.on_exit)
        self._img_blank = ImageTk.PhotoImage(Image.open(ICON_BLANK))
        self._img_pending = ImageTk.PhotoImage(Image.open(ICON_PENDING))
        self._img_confirmed = ImageTk.PhotoImage(Image.open(ICON_CONFIRMED))
        self._img_warn = ImageTk.PhotoImage(Image.open(ICON_WARNING))
        self._img_exit = ImageTk.PhotoImage(Image.open(ICON_EXIT))
        self._status = StringVar()
        self._pending_confs = {}

        self._body()
        self._do_layout()
        self._reset()

    def _body(self):
        """
        Set up frame and widgets.
        """
        # pylint: disable=unnecessary-lambda

        self._frm_container = Frame(self)
        self._frm_status = Frame(self._frm_container, borderwidth=2, relief="groove")
        self._lbl_status = Label(
            self._frm_status, textvariable=self._status, anchor="w"
        )
        self._btn_exit = Button(
            self._frm_status,
            image=self._img_exit,
            width=55,
            fg="red",
            command=self.on_exit,
            font=self.__app.font_md,
        )

        self._frm_corrip = SPARTNMQTTDialog(
            self.__app, self, borderwidth=2, relief="groove"
        )
        self._frm_corrlband = SPARTNLBANDDialog(
            self.__app, self, borderwidth=2, relief="groove"
        )
        self._frm_gnss = SPARTNGNSSDialog(
            self.__app, self, borderwidth=2, relief="groove"
        )

    def _do_layout(self):
        """
        Position widgets in frame.
        """

        self._frm_corrip.grid(
            column=0,
            row=0,
            ipadx=5,
            ipady=5,
            sticky=(N, S, W, E),
        )
        self._frm_corrlband.grid(
            column=1,
            row=0,
            ipadx=5,
            ipady=5,
            sticky=(N, S, W, E),
        )
        self._frm_gnss.grid(
            column=2,
            row=0,
            ipadx=5,
            ipady=5,
            sticky=(N, S, W, E),
        )

        # bottom of grid
        self._frm_container.grid(
            column=0,
            row=0,
            columnspan=3,
            rowspan=2,
            padx=3,
            pady=3,
            ipadx=5,
            ipady=5,
            sticky=(N, S, W, E),
        )
        self._frm_status.grid(
            column=0,
            row=1,
            columnspan=3,
            ipadx=5,
            ipady=5,
            sticky=(W, E),
        )
        self._lbl_status.grid(column=0, row=0, columnspan=2, sticky=W)
        self._btn_exit.grid(column=2, row=0, sticky=E)

        (colsp, rowsp) = self._frm_container.grid_size()
        for frm in (self._frm_container, self._frm_status):
            for i in range(colsp):
                frm.grid_columnconfigure(i, weight=1)
            for i in range(rowsp):
                frm.grid_rowconfigure(i, weight=1)

        self._frm_container.option_add("*Font", self.__app.font_sm)
        self._frm_status.option_add("*Font", self.__app.font_sm)

    def _reset(self):
        """
        Reset configuration widgets.
        """

        self.set_status("")

    def set_status(self, message: str, color: str = ""):
        """
        Set status message.
        :param str message: message to be displayed
        :param str color: rgb color of text
        """

        message = (message[:180] + "..") if len(message) > 180 else message
        if color != "":
            self._lbl_status.config(fg=color)
        self._status.set(" " + message)

    def on_exit(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Handle Exit button press.
        """

        self.__app.stop_dialog(DLGTSPARTN)
        self.destroy()

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

        spartnfrm = self._pending_confs.get(msg.identity, None)

        if spartnfrm is not None:
            if spartnfrm == SPARTN_GNSS:
                self._frm_gnss.update_status(msg)
            elif spartnfrm == SPARTN_LBAND:
                self._frm_corrlband.update_status(msg)
            elif spartnfrm == SPARTN_MQTT:
                self._frm_corrip.update_status(msg)

            # reset all confirmation flags for this frame
            for msgid in (msg.identity, "ACK-ACK", "ACK-NAK"):
                if self._pending_confs.get(msgid, None) == spartnfrm:
                    self._pending_confs.pop(msgid)

    def set_controls(self, status: bool, msgt: tuple = None):
        """
        Set controls in IP or L-Band clients.

        :param bool status: connected to SPARTN server yes/no
        :param tuple msgt: tuple of (message, color)
        """

        if status == CONNECTED_SPARTNIP:
            self._frm_corrip.set_controls(status)
        elif status == CONNECTED_SPARTNLB:
            self._frm_corrlband.set_controls(status)
        if msgt is not None:
            msg, col = msgt
            self.set_status(msg, col)

    def disconnect_ip(self, msg: str = ""):
        """
        Disconnect from IP (MQTT) client.

        :param str msg: optional disconnection message
        """

        self._frm_corrip.on_disconnect(msg)

    def disconnect_lband(self, msg: str = ""):
        """
        Disconnect from L-Band client.

        :param str msg: optional disconnection message
        """

        self._frm_corrlband.on_disconnect(msg)

    @property
    def container(self):
        """
        Getter for container.
        """

        return self._frm_container

    @property
    def server(self) -> str:
        """
        Getter for server.

        :return: server
        :rtype: str
        """

        return self._frm_corrip.server

    @server.setter
    def server(self, server: str):
        """
        Setter for server.

        :param str clientid: Client ID
        """

        self._frm_corrip.server = server

    @property
    def clientid(self) -> str:
        """
        Getter for Client ID from IP configuration dialog.

        :return: client ID
        :rtype: str
        """

        return self._frm_corrip.clientid

    @clientid.setter
    def clientid(self, clientid: str):
        """
        Setter for Client ID.

        :param str clientid: Client ID
        """

        self._frm_corrip.clientid = clientid
