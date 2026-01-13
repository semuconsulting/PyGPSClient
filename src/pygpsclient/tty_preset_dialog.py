"""
tty_preset_dialog.py

TTY Configuration frame for user-defined TTY (AT+) commands

Created on 7 May 2025

:author: semuadmin (Steve Smith)
:copyright: 2020 semuadmin
:license: BSD 3-Clause
"""

from tkinter import (
    EW,
    HORIZONTAL,
    LEFT,
    NE,
    NS,
    NSEW,
    VERTICAL,
    Button,
    Checkbutton,
    E,
    Entry,
    Frame,
    IntVar,
    Label,
    Listbox,
    N,
    S,
    Scrollbar,
    StringVar,
    W,
    ttk,
)

from pygpsclient.confirm_box import ConfirmBox
from pygpsclient.globals import (
    ASCII,
    BSR,
    CRLF,
    ERRCOL,
    INFOCOL,
    OKCOL,
    TRACEMODE_WRITE,
    TTYERR,
    TTYMARKER,
    TTYOK,
)
from pygpsclient.strings import (
    CONFIRM,
    DLGACTION,
    DLGACTIONCONFIRM,
    DLGTTTY,
)
from pygpsclient.toplevel_dialog import ToplevelDialog

CANCELLED = 0
CONFIRMED = 1
NOMINAL = 2


class TTYPresetDialog(ToplevelDialog):
    """
    TTY Preset and User-defined configuration command dialog.
    """

    def __init__(self, app, **kwargs):  # pylint: disable=unused-argument
        """
        Constructor.

        :param Frame app: reference to main tkinter application
        :param kwargs: optional kwargs to pass to Frame parent class
        """

        self.__app = app
        self.__master = self.__app.appmaster  # Reference to root class (Tk)

        super().__init__(app, DLGTTTY)
        self._confirm = False
        self._command = StringVar()
        self._crlf = IntVar()
        self._echo = IntVar()
        self._delay = IntVar()
        self._body()
        self._do_layout()
        self.reset()
        self._attach_events()
        self._finalise()

    def _body(self):
        """
        Set up frame and widgets.
        """

        self._frm_body = Frame(self.container)
        self._lbl_command = Label(
            self._frm_body,
            text="Command",
        )
        self._ent_command = Entry(
            self._frm_body,
            textvariable=self._command,
            relief="sunken",
            width=50,
        )
        self._chk_crlf = Checkbutton(
            self._frm_body,
            text="CRLF",
            variable=self._crlf,
        )
        self._chk_echo = Checkbutton(
            self._frm_body,
            text="Echo",
            variable=self._echo,
        )
        self._chk_delay = Checkbutton(
            self._frm_body,
            text="Delay",
            variable=self._delay,
        )
        self._lbl_presets = Label(self._frm_body, text="Preset TTY Commands", anchor=W)
        self._lbx_preset = Listbox(
            self._frm_body,
            border=2,
            relief="sunken",
            height=25,
            width=55,
            justify=LEFT,
            exportselection=False,
        )
        self._scr_presetv = Scrollbar(self._frm_body, orient=VERTICAL)
        self._scr_preseth = Scrollbar(self._frm_body, orient=HORIZONTAL)
        self._lbx_preset.config(yscrollcommand=self._scr_presetv.set)
        self._lbx_preset.config(xscrollcommand=self._scr_preseth.set)
        self._scr_presetv.config(command=self._lbx_preset.yview)
        self._scr_preseth.config(command=self._lbx_preset.xview)
        self._lbl_send_command = Label(self._frm_body)
        self._btn_send_command = Button(
            self._frm_body,
            image=self.img_send,
            width=50,
            command=self._on_send_command,
        )

    def _do_layout(self):
        """
        Layout widgets.
        """

        self._frm_body.grid(
            column=0, row=0, padx=5, pady=5, ipadx=5, ipady=5, sticky=NSEW
        )
        self._lbl_command.grid(column=0, row=0, padx=3, sticky=W)
        self._ent_command.grid(column=1, row=0, columnspan=3, padx=3, sticky=EW)
        self._chk_crlf.grid(column=0, row=1, padx=3, sticky=W)
        self._chk_echo.grid(column=1, row=1, padx=3, sticky=W)
        self._chk_delay.grid(column=2, row=1, padx=3, sticky=W)
        ttk.Separator(self._frm_body).grid(
            column=0, row=2, columnspan=4, padx=2, pady=2, sticky=EW
        )
        self._lbl_presets.grid(column=0, row=3, columnspan=3, padx=3, sticky=EW)
        self._lbx_preset.grid(
            column=0,
            row=3,
            columnspan=3,
            rowspan=10,
            padx=3,
            pady=3,
            sticky=NS,
        )
        self._scr_presetv.grid(column=2, row=3, rowspan=21, sticky=(N, S, E))
        self._scr_preseth.grid(column=0, row=24, columnspan=3, sticky=EW)
        self._btn_send_command.grid(
            column=3, row=3, padx=3, ipadx=3, ipady=3, sticky=NE
        )
        self._lbl_send_command.grid(
            column=3, row=4, padx=3, ipadx=3, ipady=3, sticky=EW
        )
        self.container.grid_columnconfigure(0, weight=10)
        self.container.grid_rowconfigure(0, weight=10)
        self.grid_columnconfigure(0, weight=10)
        self.grid_rowconfigure(0, weight=10)
        colsp, _ = self._frm_body.grid_size()
        for col in range(colsp - 1):
            self._frm_body.grid_columnconfigure(col, weight=10)
        self._frm_body.grid_rowconfigure(3, weight=10)

    def _attach_events(self):
        """
        Bind listbox selection events.
        """

        self._command.trace_add(TRACEMODE_WRITE, self._on_update_command)
        for setting in (self._crlf, self._echo):
            setting.trace_add(TRACEMODE_WRITE, self._on_update_settings)
        self._lbx_preset.bind("<<ListboxSelect>>", self._on_select_preset)
        # self.bind("<Configure>", self._on_resize)

    def reset(self):
        """
        Reset panel - Load user-defined presets if there are any.
        """

        self._crlf.set(self.__app.configuration.get("ttycrlf_b"))
        self._echo.set(self.__app.configuration.get("ttyecho_b"))
        self._delay.set(self.__app.configuration.get("ttydelay_b"))
        self.__app.configuration.init_presets("tty")
        for i, preset in enumerate(self.__app.configuration.get("ttypresets_l")):
            self._lbx_preset.insert(i, preset)

    def _on_update_command(self, var, index, mode):  # pylint: disable=unused-argument
        """
        Command has been updated.
        """

        self._lbl_send_command.config(image=self.img_none)

    def _on_update_settings(self, var, index, mode):  # pylint: disable=unused-argument
        """
        Settings have been updated.
        """

        self.__app.configuration.set("ttycrlf_b", self._crlf.get())
        self.__app.configuration.set("ttyecho_b", self._echo.get())
        self.__app.configuration.set("ttydelay_b", self._delay.get())

    def _on_select_preset(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Preset command has been selected.
        """

        try:
            self.status_label = ("", INFOCOL)
            idx = self._lbx_preset.curselection()
            preset = self._lbx_preset.get(idx).split(";", 1)
            self._confirm = CONFIRM in preset[0]
            self._command.set(preset[1])
        except IndexError:
            self.status_label = ("Invalid preset format", ERRCOL)

    def _on_send_command(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Preset command send button has been clicked.
        """

        if self._command.get() in ("", None):
            self.status_label = ("Enter or select command", ERRCOL)
            return

        try:
            if self._confirm:
                if ConfirmBox(self, DLGACTION, DLGACTIONCONFIRM).show():
                    self._parse_command(self._command.get())
                    status = CONFIRMED
                else:
                    status = CANCELLED
            else:
                self._parse_command(self._command.get())
                status = CONFIRMED
            if status == CONFIRMED:
                self._lbl_send_command.config(image=self.img_pending)
                self.status_label = "Command(s) sent"
            elif status == CANCELLED:
                self.status_label = "Command(s) cancelled"
            elif status == NOMINAL:
                self.status_label = "Command(s) sent, no results"
            self._confirm = False

        except Exception as err:  # pylint: disable=broad-except
            self.status_label = (f"Error {err}", ERRCOL)
            self._lbl_send_command.config(image=self.img_warn)

    def _parse_command(self, command: str):
        """
        Parse and send user-defined command(s).

        This could result in any number of errors if the
        ttypresets list contains garbage, so there's a broad
        catch-all-exceptions in the calling routine.

        :param str command: semicolon-delimited list of TTY commands
        """

        try:
            for cmd in command.split(";"):
                cmd = cmd.strip().encode(ASCII, errors=BSR)
                if self._crlf.get():
                    cmd += CRLF
                self.__app.send_to_device(cmd)
                self._record_command(cmd)
                if self._echo.get():  # echo output command to console
                    self.__app.consoledata.append(
                        (cmd, cmd.decode(ASCII, errors=BSR), TTYMARKER)
                    )
        except Exception as err:  # pylint: disable=broad-except
            self.status_label = (f"Error {err}", ERRCOL)
            self._lbl_send_command.config(image=self.img_warn)

    def _record_command(self, msg: bytes):
        """
        Record command to memory if in 'record' mode.

        :param bytes msg: configuration message
        """

        if self.__app.recording:
            self.__app.recorded_commands = msg

    def update_status(self, msg: bytes):
        """
        Update pending confirmation status.

        :param bytes msg: ASCII config message
        """

        msgstr = msg.decode(ASCII, errors=BSR).upper()
        for ack in TTYOK:
            if ack in msgstr:
                self._lbl_send_command.config(image=self.img_confirmed)
                self.status_label = ("Command(s) acknowledged", OKCOL)
                return
        for nak in TTYERR:
            if nak in msgstr:
                self._lbl_send_command.config(image=self.img_warn)
                self.status_label = ("Command(s) rejected", ERRCOL)
                break
