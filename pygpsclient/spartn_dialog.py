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
# pylint: disable=invalid-name, too-many-locals, too-many-instance-attributes

from tkinter import (
    Toplevel,
    Frame,
    Button,
    Label,
    StringVar,
    N,
    S,
    E,
    W,
)
from PIL import ImageTk, Image
from pygpsclient.globals import (
    ICON_EXIT,
    ICON_CONFIRMED,
    ICON_PENDING,
    ICON_WARNING,
    ICON_BLANK,
)
from pygpsclient.strings import DLGSPARTNCONFIG
from pygpsclient.spartn_gnss_dialog import SPARTNGNSSDialog
from pygpsclient.spartn_lband_dialog import SPARTNLBANDDialog
from pygpsclient.spartn_mqtt_dialog import SPARTNMQTTDialog


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
        # if POPUP_TRANSIENT:
        #     self.transient(self.__app)
        self.resizable(False, False)
        self.title(DLGSPARTNCONFIG)  # pylint: disable=E1102
        self.protocol("WM_DELETE_WINDOW", self.on_exit)
        self._img_blank = ImageTk.PhotoImage(Image.open(ICON_BLANK))
        self._img_pending = ImageTk.PhotoImage(Image.open(ICON_PENDING))
        self._img_confirmed = ImageTk.PhotoImage(Image.open(ICON_CONFIRMED))
        self._img_warn = ImageTk.PhotoImage(Image.open(ICON_WARNING))
        self._img_exit = ImageTk.PhotoImage(Image.open(ICON_EXIT))
        self._status = StringVar()

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

        # self._frm_corrip = SPARTNMQTTDialog(
        #     self.__app, self, borderwidth=2, relief="groove"
        # )
        # self._frm_corrlband = SPARTNLBANDDialog(
        #     self.__app, self, borderwidth=2, relief="groove"
        # )
        # self._frm_gnss = SPARTNGNSSDialog(
        #     self.__app, self, borderwidth=2, relief="groove"
        # )

    def _do_layout(self):
        """
        Position widgets in frame.
        """

        # self._frm_corrip.grid(
        #     column=0,
        #     row=0,
        #     ipadx=5,
        #     ipady=5,
        #     sticky=(N, S, W, E),
        # )
        # self._frm_corrlband.grid(
        #     column=0,
        #     row=1,
        #     ipadx=5,
        #     ipady=5,
        #     sticky=(N, S, W, E),
        # )
        # self._frm_gnss.grid(
        #     column=0,
        #     row=2,
        #     ipadx=5,
        #     ipady=5,
        #     sticky=(N, S, W, E),
        # )

        # bottom of grid
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

        self.set_status("", "blue")

    def set_status(self, message: str, color: str = "blue"):
        """
        Set status message.
        :param str message: message to be displayed
        :param str color: rgb color of text (blue)
        """

        message = (message[:80] + "..") if len(message) > 80 else message
        # self._lbl_status.config(fg=color)
        self._status.set(" " + message)

    def on_exit(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Handle Exit button press.
        """

        self.__app.stop_spartnconfig_thread()
        self.destroy()

    # def update_status(self, msg: UBXMessage):
    #     """
    #     Update pending confirmation status.
    #     :param UBXMessage msg: UBX config message
    #     """

    #     if not hasattr(msg, "identity"):
    #         return

    #     if msg.identity == RXMMSG:
    #         if msg.numKeys == 2:  # check both keys have been uploaded
    #             self._lbl_send_command.config(image=self._img_confirmed)
    #             self.set_status(CONFIGOK.format(RXMMSG), "green")
    #         else:
    #             self._lbl_send_command.config(image=self._img_warn)
    #             self.set_status(CONFIGBAD.format(RXMMSG), "red")
    #     elif msg.identity == "ACK-ACK":
    #         self._lbl_send_command.config(image=self._img_confirmed)
    #         self.set_status(CONFIGOK.format(CFGSET), "green")
    #     elif msg.identity == "ACK-NAK":
    #         self._lbl_send_command.config(image=self._img_warn)
    #         self.set_status(CONFIGBAD.format(CFGSET), "red")
    #     elif msg.identity == CFGPOLL:
    #         if hasattr(msg, "CFG_PMP_CENTER_FREQUENCY"):
    #             self._spartn_freq.set(msg.CFG_PMP_CENTER_FREQUENCY)
    #         if hasattr(msg, "CFG_PMP_SEARCH_WINDOW"):
    #             self._spartn_schwin.set(msg.CFG_PMP_SEARCH_WINDOW)
    #         if hasattr(msg, "CFG_PMP_USE_SERVICE_ID"):
    #             self._spartn_usesid.set(msg.CFG_PMP_USE_SERVICE_ID)
    #         if hasattr(msg, "CFG_PMP_SERVICE_ID"):
    #             self._spartn_sid.set(msg.CFG_PMP_SERVICE_ID)
    #         if hasattr(msg, "CFG_PMP_DATA_RATE"):
    #             self._spartn_drat.set(msg.CFG_PMP_DATA_RATE)
    #         if hasattr(msg, "CFG_PMP_USE_DESCRAMBLER"):
    #             self._spartn_descrm.set(msg.CFG_PMP_USE_DESCRAMBLER)
    #         if hasattr(msg, "CFG_PMP_DESCRAMBLER_INIT"):
    #             self._spartn_descrminit.set(msg.CFG_PMP_DESCRAMBLER_INIT)
    #         if hasattr(msg, "CFG_PMP_USE_PRESCRAMBLING"):
    #             self._spartn_prescrm.set(msg.CFG_PMP_USE_PRESCRAMBLING)
    #         if hasattr(msg, "CFG_PMP_UNIQUE_WORD"):
    #             self._spartn_unqword.set(msg.CFG_PMP_UNIQUE_WORD)
    #         self.set_status(f"{CFGPOLL} received", "green")
    #         self._lbl_lbandsend.config(image=self._img_confirmed)
    #         self.update_idletasks()

    @property
    def container(self):
        """
        Getter for container.
        """

        return self._frm_container
