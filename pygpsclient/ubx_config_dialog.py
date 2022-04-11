"""
UBX configuration container dialog

This is the pop-up dialog containing the various
UBX configuration command widgets.

NB: Individual UBX configuration commands do not have uniquely
identifiable synchronous or asynchronous responses (e.g. unique
txn ID). The way we keep tabs on confirmation status is to
maintain a list of all commands sent and the responses they're
expecting. When we receive a response, we check against the list
of awaited responses of the same type and flag the first one we
find as 'confirmed'. This is generally reliable but not absolutely
foolproof - if several commands awaiting the same response type are
sent in quick succession, it's possible their responses may arrive
out of order (or not at all) and we may flag the wrong command as
'confirmed', or leave a confirmed command as 'pending'.

Created on 19 Sep 2020

:author: semuadmin
:copyright: SEMU Consulting © 2020
:license: BSD 3-Clause
"""
# pylint: disable=invalid-name

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
    UBX_MONVER,
    UBX_MONHW,
    UBX_CFGPRT,
    UBX_CFGRATE,
    UBX_CFGMSG,
    UBX_CFGVAL,
    UBX_PRESET,
)
from pygpsclient.strings import DLGUBXCONFIG
from pygpsclient.globals import POPUP_TRANSIENT
from pygpsclient.ubx_info_frame import UBX_INFO_Frame
from pygpsclient.ubx_port_frame import UBX_PORT_Frame
from pygpsclient.ubx_msgrate_frame import UBX_MSGRATE_Frame
from pygpsclient.ubx_preset_frame import UBX_PRESET_Frame
from pygpsclient.ubx_cfgval_frame import UBX_CFGVAL_Frame
from pygpsclient.ubx_solrate_frame import UBX_RATE_Frame


class UBXConfigDialog(Toplevel):
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
        self.__master = self.__app.get_master()  # Reference to root class (Tk)
        Toplevel.__init__(self, app)
        if POPUP_TRANSIENT:
            self.transient(self.__app)
        self.resizable(True, True)  # allow for MacOS resize glitches
        self.title(DLGUBXCONFIG)  # pylint: disable=E1102
        self.protocol("WM_DELETE_WINDOW", self.on_exit)
        self._img_exit = ImageTk.PhotoImage(Image.open(ICON_EXIT))
        self._cfg_msg_command = None
        self._pending_confs = {
            UBX_MONVER: (),
            UBX_MONHW: (),
            UBX_CFGPRT: (),
            UBX_CFGMSG: (),
            UBX_CFGVAL: (),
            UBX_PRESET: (),
            UBX_CFGRATE: (),
        }
        self._status = StringVar()
        self._status_cfgmsg = StringVar()

        self._body()
        self._do_layout()
        self._reset()
        # self._centre()

    def _body(self):
        """
        Set up frame and widgets.
        """

        self._frm_container = Frame(self, borderwidth=2, relief="groove")
        self._frm_status = Frame(self._frm_container, borderwidth=2, relief="groove")
        self._lbl_status = Label(
            self._frm_status, textvariable=self._status, anchor="w"
        )
        self._btn_exit = Button(
            self._frm_status,
            image=self._img_exit,
            width=50,
            fg="red",
            command=self.on_exit,
            font=self.__app.font_md,
        )
        # add configuration widgets
        self._frm_device_info = UBX_INFO_Frame(
            self.__app, self, borderwidth=2, relief="groove"
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
        self._frm_configdb = UBX_CFGVAL_Frame(
            self.__app, self, borderwidth=2, relief="groove"
        )
        self._frm_preset = UBX_PRESET_Frame(
            self.__app, self, borderwidth=2, relief="groove"
        )

    def _do_layout(self):
        """
        Position widgets in frame.
        """

        # top of grid
        col = 0
        row = 0
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
        rowsp = 0
        for frm in (
            self._frm_device_info,
            self._frm_config_port,
            self._frm_config_rate,
            self._frm_config_msg,
        ):
            row += rowsp
            (colsp, rowsp) = frm.grid_size()
            frm.grid(
                column=col,
                row=row,
                columnspan=colsp,
                rowspan=rowsp,
                sticky=(N, S, W, E),
            )
        # right column of grid
        row = 0
        rowsp = 0
        col += colsp
        for frm in (self._frm_configdb, self._frm_preset):
            row += rowsp
            (colsp, rowsp) = frm.grid_size()
            frm.grid(
                column=col,
                row=row,
                columnspan=colsp,
                rowspan=rowsp,
                sticky=(N, S, W, E),
            )
        # bottom of grid
        col = 0
        row += rowsp
        (colsp, rowsp) = self._frm_container.grid_size()
        self._frm_status.grid(column=col, row=row, columnspan=colsp, sticky=(W, E))
        self._lbl_status.grid(
            column=0, row=0, columnspan=colsp - 1, ipadx=3, ipady=3, sticky=(W, E)
        )
        self._btn_exit.grid(column=colsp - 1, row=0, ipadx=3, ipady=3, sticky=(E))

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

        self._frm_config_rate.reset()
        self._frm_config_port.reset()
        self._frm_device_info.reset()
        if not self.__app.serial_handler.connected:
            self.set_status("Device not connected", "red")

    def _centre(self):
        """
        Roughly center dialog in master window
        NB: behaviour is slightly different across Windows, MacOS and Linux
        """

        dw = self.winfo_width()
        dh = self.winfo_height()
        mx = self.__master.winfo_x()
        my = self.__master.winfo_y()
        mw = self.__master.winfo_width()
        mh = self.__master.winfo_height()
        self.geometry(f"+{int(mx + (mw/2 - dw/2))}+{int(my + (mh/2 - dh/2))}")

    def set_pending(self, key: int, val: list):
        """
        Set pending confirmation flag for configuration widget to
        signify that it's waiting for a confirmation message.

        :param int key: integer representing UBX configuration widget (0-6)
        :param list val: list of confirmation messages that widget is awaiting
        """

        self._pending_confs[key] = val

    def update_pending(self, cfgtype, **kwargs):
        """
        Receives polled confirmation message from the ubx_handler and
        updates the widget that is waiting for this confirmation.

        :param str cfgtype: identity of UBX message containing config info
        :param kwargs: status keywords and values from UBX config message
        """

        for (key, val) in self._pending_confs.items():
            if cfgtype in val:
                self.set_status(
                    f"{cfgtype} GET message received",
                    "red" if cfgtype == "ACK-NAK" else "green",
                )
                self._pending_confs[key] = ()  # reset awaiting conf flag
                if key == UBX_MONVER:
                    self._frm_device_info.update_status(cfgtype, **kwargs)
                elif key == UBX_MONHW:
                    self._frm_device_info.update_status(cfgtype, **kwargs)
                elif key == UBX_CFGPRT:
                    self._frm_config_port.update_status(cfgtype, **kwargs)
                elif key == UBX_CFGRATE:
                    self._frm_config_rate.update_status(cfgtype, **kwargs)
                elif key == UBX_CFGMSG:
                    self._frm_config_msg.update_status(cfgtype, **kwargs)
                elif key == UBX_CFGVAL:
                    self._frm_configdb.update_status(cfgtype, **kwargs)
                elif key == UBX_PRESET:
                    self._frm_preset.update_status(cfgtype, **kwargs)

    def set_status(self, message: str, color: str = "blue"):
        """
        Set status message.

        :param str message: message to be displayed
        :param str color: rgb color of text (blue)
        """

        message = (message[:120] + "..") if len(message) > 120 else message
        self._lbl_status.config(fg=color)
        self._status.set("  " + message)

    def on_exit(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Handle Exit button press.
        """

        # self.__master.update_idletasks()
        self.__app.stop_ubxconfig_thread()
        self.destroy()

    def get_size(self):
        """
        Get current frame size.

        :return: window size (width, height)
        :rtype: tuple
        """

        self.__master.update_idletasks()  # Make sure we know about any resizing
        return (self.winfo_width(), self.winfo_height())

    @property
    def container(self):
        """
        Getter for container frame.

        :return: reference to container frame
        :rtype: tkinter.Frame
        """

        return self._frm_container
