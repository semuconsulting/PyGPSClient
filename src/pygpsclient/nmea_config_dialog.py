"""
nmea_config_dialog.py

NMEA configuration container dialog

This is the pop-up dialog containing the various
proprietary NMEA configuration command frames.

Supply initial settings via `config` keyword argument.

Created on 22 Mar 2025

:author: semuadmin
:copyright: 2020 SEMU Consulting
:license: BSD 3-Clause
"""

from tkinter import Button, E, Frame, Label, N, S, StringVar, Toplevel, W

from PIL import Image, ImageTk
from pynmeagps import NMEAMessage

from pygpsclient.dynamic_config_frame import Dynamic_Config_Frame
from pygpsclient.globals import (
    CONNECTED,
    CONNECTED_SIMULATOR,
    CONNECTED_SOCKET,
    ERRCOL,
    ICON_EXIT,
    NMEA_CFGOTHER,
    NMEA_MONHW,
    NMEA_PRESET,
    POPUP_TRANSIENT,
)
from pygpsclient.hardware_info_frame import Hardware_Info_Frame
from pygpsclient.nmea_preset_frame import NMEA_PRESET_Frame
from pygpsclient.strings import DLGNMEACONFIG, DLGTNMEA


class NMEAConfigDialog(Toplevel):
    """,
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
        self.__master = self.__app.appmaster  # Reference to root class (Tk)

        Toplevel.__init__(self, app)
        if POPUP_TRANSIENT:
            self.transient(self.__app)
        self.resizable(True, True)  # allow for MacOS resize glitches
        self.title(DLGNMEACONFIG)  # pylint: disable=E1102
        self.protocol("WM_DELETE_WINDOW", self.on_exit)
        self._img_exit = ImageTk.PhotoImage(Image.open(ICON_EXIT))
        self._cfg_msg_command = None
        self._pending_confs = {}
        self._status = StringVar()
        self._status_cfgmsg = StringVar()

        self._body()
        self._do_layout()
        self._reset()

    def _body(self):
        """
        Set up frame and widgets.
        """

        self._frm_container = Frame(self, borderwidth=2, relief="groove")
        self._frm_status = Frame(self._frm_container, borderwidth=2, relief="groove")
        self._lbl_status = Label(self._frm_status, textvariable=self._status, anchor=W)
        self._btn_exit = Button(
            self._frm_status,
            image=self._img_exit,
            width=50,
            fg=ERRCOL,
            command=self.on_exit,
            font=self.__app.font_md,
        )
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
        col = colsp = 0
        row = rowsp = 0
        self._frm_container.grid(
            column=col,
            row=row,
            columnspan=12,
            rowspan=22,
            padx=3,
            pady=3,
            ipadx=5,
            ipady=5,
            sticky=(N, S, W, E),
        )
        # left column of grid
        for frm in (self._frm_device_info, self._frm_preset):
            (colsp, rowsp) = frm.grid_size()
            frm.grid(
                column=col,
                row=row,
                columnspan=colsp,
                rowspan=rowsp,
                sticky=(N, S, W, E),
            )
            row += rowsp
        maxrow = row
        # right column of grid
        row = 0
        col += colsp
        for frm in (self._frm_config_dynamic,):
            (colsp, rowsp) = frm.grid_size()
            frm.grid(
                column=col,
                row=row,
                columnspan=colsp,
                rowspan=rowsp,
                sticky=(N, S, W, E),
            )
            row += rowsp
        maxrow = max(maxrow, row)
        # bottom of grid
        col = 0
        row = maxrow
        (colsp, rowsp) = self._frm_container.grid_size()
        self._frm_status.grid(column=col, row=row, columnspan=colsp, sticky=(W, E))
        self._lbl_status.grid(
            column=0, row=0, columnspan=colsp - 1, ipadx=3, ipady=3, sticky=(W, E)
        )
        self._btn_exit.grid(column=colsp - 1, row=0, ipadx=3, ipady=3, sticky=E)

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

        self._frm_config_dynamic.reset()
        self._frm_device_info.reset()
        if self.__app.conn_status not in (
            CONNECTED,
            CONNECTED_SOCKET,
            CONNECTED_SIMULATOR,
        ):
            self.set_status("Device not connected", ERRCOL)

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

    def set_status(self, message: str, color: str = ""):
        """
        Set status message.

        :param str message: message to be displayed
        :param str color: rgb color of text (blue)
        """

        message = (message[:120] + "..") if len(message) > 120 else message
        if color != "":
            self._lbl_status.config(fg=color)
        self._status.set("  " + message)

    def on_exit(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Handle Exit button press.
        """

        self.__app.stop_dialog(DLGTNMEA)
        self.destroy()

    def get_size(self):
        """
        Get current frame size.

        :return: window size (width, height)
        :rtype: tuple
        """

        self.__master.update_idletasks()  # Make sure we know about any resizing
        return self.winfo_width(), self.winfo_height()

    @property
    def container(self):
        """
        Getter for container frame.

        :return: reference to container frame
        :rtype: tkinter.Frame
        """

        return self._frm_container

    def send_command(self, msg: NMEAMessage):
        """
        Send command to receiver.
        """

        self.__app.gnss_outqueue.put(msg.serialize())
