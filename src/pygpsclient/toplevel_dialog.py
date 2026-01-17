"""
toplevel_dialog.py

Top Level container dialog which displays child frames
depending on resize behaviour and available screen resolution:

- If frame is resizeable (defined in dialog_state), display as such.
- If frame is non-resizeable and child frame dimensions exceed screen
  dimensions, frame will be embedded as a window inside a scrollable
  and resizeable canvas (can_container).
- Otherwise, frame will be displayed as a fixed, non-resizeable
  dialog (frm_container).

Created on 19 Sep 2020

:author: semuadmin (Steve Smith)
:copyright: 2020 semuadmin
:license: BSD 3-Clause
"""

import logging
from tkinter import (
    EW,
    NSEW,
    Button,
    E,
    Frame,
    Label,
    Toplevel,
    W,
)

from PIL import Image, ImageTk

from pygpsclient.canvas_subclasses import CanvasContainer
from pygpsclient.globals import (
    APPNAME,
    ERRCOL,
    ICON_BLANK,
    ICON_CONFIRMED,
    ICON_CONN,
    ICON_DISCONN,
    ICON_END,
    ICON_EXIT,
    ICON_LOAD,
    ICON_PENDING,
    ICON_REDRAW,
    ICON_SEND,
    ICON_START,
    ICON_WARNING,
    INFOCOL,
    RESIZE,
)
from pygpsclient.helpers import check_lowres
from pygpsclient.strings import DLG


class ToplevelDialog(Toplevel):
    """
    ToplevelDialog class.
    """

    def __init__(self, app, dlgname: str, *args, **kwargs):
        """
        Constructor.

        :param Frame app: reference to main tkinter application
        :param str dlgname: dialog name
        """

        self.__app = app  # Reference to main application class
        self.__master = self.__app.appmaster  # Reference to root class (Tk)
        self._dlgname = dlgname
        self.logger = logging.getLogger(f"{APPNAME}.{dlgname}")
        self.width, self.height = 300, 300  # initial, updated in finalise()
        self._resizable = kwargs.pop(
            "resizable", self.__app.dialog_state.state[self._dlgname].get(RESIZE, False)
        )
        transient = kwargs.pop(
            "transient", self.__app.configuration.get("transient_dialog_b")
        )

        super().__init__(self.__master, *args, **kwargs)

        if transient:
            self.transient(self.__app)
        self.title(dlgname)  # pylint: disable=E1102
        self.resizable(self._resizable, self._resizable)
        self.protocol("WM_DELETE_WINDOW", self.on_exit)
        self.img_none = ImageTk.PhotoImage(Image.open(ICON_BLANK))
        self.img_confirmed = ImageTk.PhotoImage(Image.open(ICON_CONFIRMED))
        self.img_conn = ImageTk.PhotoImage(Image.open(ICON_CONN))
        self.img_disconn = ImageTk.PhotoImage(Image.open(ICON_DISCONN))
        self.img_end = ImageTk.PhotoImage(Image.open(ICON_END))
        self.img_exit = ImageTk.PhotoImage(Image.open(ICON_EXIT))
        self.img_load = ImageTk.PhotoImage(Image.open(ICON_LOAD))
        self.img_pending = ImageTk.PhotoImage(Image.open(ICON_PENDING))
        self.img_redraw = ImageTk.PhotoImage(Image.open(ICON_REDRAW))
        self.img_send = ImageTk.PhotoImage(Image.open(ICON_SEND))
        self.img_start = ImageTk.PhotoImage(Image.open(ICON_START))
        self.img_warn = ImageTk.PhotoImage(Image.open(ICON_WARNING))

        self._con_body(self._resizable)

    def _con_body(self, resizable: bool):
        """
        Set up scrollable frame and widgets.

        :param bool resizable: resizable
        """

        # create container frame for non-resizeable dialogs
        if resizable:
            self._frm_container = Frame(self)
            self._frm_container.grid(column=0, row=0, sticky=NSEW)
        else:
            self._can_container = CanvasContainer(self.__app, self)
            self._frm_container = self._can_container.frm_container

        # create status frame
        self._frm_status = Frame(self, borderwidth=2, relief="groove")
        self._lbl_status = Label(self._frm_status, anchor=W)
        self._btn_exit = Button(
            self._frm_status,
            image=self.img_exit,
            width=45,
            fg=ERRCOL,
            command=self.on_exit,
        )
        self._frm_status.grid(column=0, row=2, sticky=EW)
        self._lbl_status.grid(column=0, row=0, sticky=EW)
        self._btn_exit.grid(column=1, row=0, padx=4, sticky=E)

        # set column and row weights
        # NB!!! these govern the 'pack' behaviour of the frames on resize
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._frm_status.grid_columnconfigure(0, weight=1)
        colsp, rowsp = self._frm_container.grid_size()
        for i in range(colsp):
            self._frm_status.grid_columnconfigure(i, weight=1)
        for i in range(rowsp):
            self._frm_status.grid_rowconfigure(i, weight=1)

    def _finalise(self):
        """
        Finalise Toplevel dialog after child frames have been created.

        If screen is smaller than dialog (`lowres=True`), display within
        smaller, resizeable and scrollable canvas container.

        Otherwise, make the container the same size as the dialog and hide
        the scrollbars.

        NB Some Linux platforms appear to require Toplevel dialog windows
        to be non-transient for the window 'maximise' icon to work properly
        """

        if hasattr(self, "_can_container"):
            self._frm_container.update_idletasks()
            fh = self._frm_container.winfo_height()
            fw = self._frm_container.winfo_width()
            lowres, (sh, sw) = check_lowres(self.__master, (fh, fw))
            if lowres:
                self._can_container.config(
                    height=min(int(sh * 0.75), fh), width=min(int(sw * 0.75), fw)
                )
                self.resizable(True, True)
            else:
                self._can_container.config(height=fh, width=fw)
                self._can_container.show_scroll(False)
                self.resizable(self._resizable, self._resizable)

    def on_exit(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Handle Exit button press.
        """

        self.__app.dialog_state.state[self._dlgname][DLG] = None
        self.destroy()

    def on_expand(self):
        """
        Automatically expand container canvas when sub-frames are resized.
        """

        if hasattr(self, "_can_container"):
            self._can_container.event_generate("<Configure>")

    def _on_resize(self, event):  # pylint: disable=unused-argument
        """
        Resize frame.

        :param event event: resize event
        """

        self.width, self.height = self.get_size()

    def get_size(self) -> tuple[int, int]:
        """
        Get current frame size.

        :return: window size (width, height)
        :rtype: tuple[int,int]
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

    @property
    def status_label(self) -> Label:
        """
        Getter for status_label.

        :param self: Description
        :return: Description
        :rtype: Label
        """

        return self._lbl_status

    @status_label.setter
    def status_label(self, message: str | tuple[str, str]):
        """
        Setter for status_label.

        :param self: Description
        :param tuple | str message: (message, color))
        """

        if isinstance(message, tuple):
            message, color = message
        else:
            color = INFOCOL

        # truncate very long messages
        if len(message) > 100:
            message = "..." + message[-100:]

        self.status_label.after(
            0, self.status_label.config, {"text": message, "fg": color}
        )
        self.update_idletasks()
