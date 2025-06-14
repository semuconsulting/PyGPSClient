"""
tty_preset_dialog.py

TTY Configuration frame for user-defined TTY (AT+) commands

Created on 7 May 2025

:author: semuadmin
:copyright: 2020 SEMU Consulting
:license: BSD 3-Clause
"""

from tkinter import (
    HORIZONTAL,
    LEFT,
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
    Toplevel,
    W,
    ttk,
)

from PIL import Image, ImageTk

from pygpsclient.confirm_box import ConfirmBox
from pygpsclient.globals import (
    ASCII,
    BSR,
    CRLF,
    ERRCOL,
    ICON_BLANK,
    ICON_CONFIRMED,
    ICON_EXIT,
    ICON_PENDING,
    ICON_SEND,
    ICON_WARNING,
    INFOCOL,
    OKCOL,
    POPUP_TRANSIENT,
    TTY_EVENT,
    TTYERR,
    TTYOK,
)
from pygpsclient.strings import (
    CONFIRM,
    DLGACTION,
    DLGACTIONCONFIRM,
    DLGTTTY,
)

CANCELLED = 0
CONFIRMED = 1
NOMINAL = 2


class TTYPresetDialog(Toplevel):
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

        Toplevel.__init__(self, app)
        if POPUP_TRANSIENT:
            self.transient(self.__app)
        self.resizable(True, True)
        self.title(DLGTTTY)  # pylint: disable=E1102
        self.protocol("WM_DELETE_WINDOW", self.on_exit)
        self._img_none = ImageTk.PhotoImage(Image.open(ICON_BLANK))
        self._img_send = ImageTk.PhotoImage(Image.open(ICON_SEND))
        self._img_pending = ImageTk.PhotoImage(Image.open(ICON_PENDING))
        self._img_confirmed = ImageTk.PhotoImage(Image.open(ICON_CONFIRMED))
        self._img_warn = ImageTk.PhotoImage(Image.open(ICON_WARNING))
        self._img_exit = ImageTk.PhotoImage(Image.open(ICON_EXIT))
        self._confirm = False
        self._command = StringVar()
        self._crlf = IntVar()
        self._echo = IntVar()
        self._delay = IntVar()
        self._body()
        self._do_layout()
        self.reset()
        self._attach_events()

    def _body(self):
        """
        Set up frame and widgets.
        """

        self._frm_container = Frame(self, borderwidth=2, relief="groove")
        self._lbl_command = Label(
            self._frm_container,
            text="Command",
        )
        self._ent_command = Entry(
            self._frm_container,
            textvariable=self._command,
            relief="sunken",
            width=50,
        )
        self._chk_crlf = Checkbutton(
            self._frm_container,
            text="CRLF",
            variable=self._crlf,
        )
        self._chk_echo = Checkbutton(
            self._frm_container,
            text="Echo",
            variable=self._echo,
        )
        self._chk_delay = Checkbutton(
            self._frm_container,
            text="Delay",
            variable=self._delay,
        )
        self._lbl_presets = Label(
            self._frm_container, text="Preset TTY Commands", anchor=W
        )
        self._lbx_preset = Listbox(
            self._frm_container,
            border=2,
            relief="sunken",
            height=25,
            width=55,
            justify=LEFT,
            exportselection=False,
        )
        self._scr_presetv = Scrollbar(self._frm_container, orient=VERTICAL)
        self._scr_preseth = Scrollbar(self._frm_container, orient=HORIZONTAL)
        self._lbx_preset.config(yscrollcommand=self._scr_presetv.set)
        self._lbx_preset.config(xscrollcommand=self._scr_preseth.set)
        self._scr_presetv.config(command=self._lbx_preset.yview)
        self._scr_preseth.config(command=self._lbx_preset.xview)
        self._lbl_send_command = Label(self._frm_container)
        self._btn_send_command = Button(
            self._frm_container,
            image=self._img_send,
            width=50,
            command=self._on_send_command,
        )
        self._btn_exit = Button(
            self._frm_container,
            image=self._img_exit,
            width=40,
            command=self.on_exit,
        )
        self._lbl_status = Label(self._frm_container, anchor=W)

    def _do_layout(self):
        """
        Layout widgets.
        """

        self._frm_container.grid(
            column=0, row=0, padx=5, pady=5, ipadx=5, ipady=5, sticky=(N, S, E, W)
        )
        self._lbl_command.grid(column=0, row=0, padx=3, sticky=W)
        self._ent_command.grid(column=1, row=0, columnspan=3, padx=3, sticky=(W, E))
        self._chk_crlf.grid(column=0, row=1, padx=3, sticky=W)
        self._chk_echo.grid(column=1, row=1, padx=3, sticky=W)
        self._chk_delay.grid(column=2, row=1, padx=3, sticky=W)
        ttk.Separator(self._frm_container).grid(
            column=0, row=2, columnspan=4, padx=2, pady=2, sticky=(W, E)
        )
        self._lbl_presets.grid(column=0, row=3, columnspan=3, padx=3, sticky=(W, E))
        self._lbx_preset.grid(
            column=0,
            row=3,
            columnspan=3,
            rowspan=10,
            padx=3,
            pady=3,
            sticky=(W, E),
        )
        self._scr_presetv.grid(column=2, row=4, rowspan=20, sticky=(N, S, E))
        self._scr_preseth.grid(column=0, row=24, columnspan=3, sticky=(W, E))
        self._btn_send_command.grid(
            column=3, row=3, padx=3, ipadx=3, ipady=3, sticky=(N, E)
        )
        self._lbl_send_command.grid(
            column=3, row=4, padx=3, ipadx=3, ipady=3, sticky=(N, W, E)
        )
        ttk.Separator(self._frm_container).grid(
            column=0, row=25, padx=2, columnspan=4, pady=2, sticky=(W, E)
        )
        self._lbl_status.grid(
            column=0, row=26, padx=3, ipadx=3, columnspan=3, ipady=3, sticky=(W, E)
        )
        self._btn_exit.grid(column=3, row=26, padx=3, ipadx=3, ipady=3)

        # self._frm_container.grid_columnconfigure(0, weight=10)
        # for col in range(1, 4):
        #     self._frm_container.grid_columnconfigure(col, weight=0)
        # for row in range(3):
        #     self._frm_container.grid_rowconfigure(row, weight=0)
        # self._frm_container.grid_rowconfigure(3, weight=10)
        self._frm_container.option_add("*Font", self.__app.font_sm)

    def _attach_events(self):
        """
        Bind listbox selection events.
        """

        self._command.trace_add("write", self._on_update_command)
        for setting in (self._crlf, self._echo):
            setting.trace_add("write", self._on_update_settings)
        self._lbx_preset.bind("<<ListboxSelect>>", self._on_select_preset)

    def reset(self):
        """
        Reset panel - Load user-defined presets if there are any.
        """

        self._crlf.set(self.__app.configuration.get("ttycrlf_b"))
        self._echo.set(self.__app.configuration.get("ttyecho_b"))
        self._delay.set(self.__app.configuration.get("ttydelay_b"))
        idx = 0
        for tcmd in self.__app.configuration.get("ttypresets_l"):
            self._lbx_preset.insert(idx, tcmd)
            idx += 1

    def _on_update_command(self, var, index, mode):  # pylint: disable=unused-argument
        """
        Command has been updated.
        """

        self._lbl_send_command.config(image=self._img_none)

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
            self.set_status("", INFOCOL)
            idx = self._lbx_preset.curselection()
            preset = self._lbx_preset.get(idx).split(";", 1)
            self._confirm = CONFIRM in preset[0]
            self._command.set(preset[1])
        except IndexError:
            self.set_status("Invalid preset format", ERRCOL)

    def _on_send_command(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Preset command send button has been clicked.
        """

        if self._command.get() in ("", None):
            self.set_status("Enter or select command", ERRCOL)
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
                self._lbl_send_command.config(image=self._img_pending)
                self.set_status("Command(s) sent")
            elif status == CANCELLED:
                self.set_status("Command(s) cancelled")
            elif status == NOMINAL:
                self.set_status("Command(s) sent, no results")
            self._confirm = False

        except Exception as err:  # pylint: disable=broad-except
            self.set_status(f"Error {err}", ERRCOL)
            self._lbl_send_command.config(image=self._img_warn)

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
                self.__app.gnss_outqueue.put(cmd)
                # self.logger.debug(f"command sent {cmd=}")
                if self._echo.get():  # echo output command to console
                    self.__app.gnss_inqueue.put((cmd, cmd.decode(ASCII, errors=BSR)))
                    self.__master.event_generate(TTY_EVENT)
        except Exception as err:  # pylint: disable=broad-except
            self.set_status(f"Error {err}", ERRCOL)
            self._lbl_send_command.config(image=self._img_warn)

    def update_status(self, msg: bytes):
        """
        Update pending confirmation status.

        :param bytes msg: ASCII config message
        """

        msgstr = msg.decode(ASCII, errors=BSR).upper()
        for ack in TTYOK:
            if ack in msgstr:
                self._lbl_send_command.config(image=self._img_confirmed)
                self.set_status("Command(s) acknowledged", OKCOL)
                return
        for nak in TTYERR:
            if nak in msgstr:
                self._lbl_send_command.config(image=self._img_warn)
                self.set_status("Command(s) rejected", ERRCOL)
                break

    def set_status(self, msg: str, col: str = INFOCOL):
        """
        Set status message.

        :param str msg: message
        :param str col: color
        """

        self._lbl_status.configure(text=msg, fg=col)

    def on_exit(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Handle Exit button press.
        """

        self.__app.stop_dialog(DLGTTTY)
        self.destroy()
