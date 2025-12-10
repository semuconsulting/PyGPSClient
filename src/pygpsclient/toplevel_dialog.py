"""
toplevel_dialog.py

Top Level container dialog which displays child frames
within a scrollable and resizeable canvas, primarily
to allow dialog to be usable on low resolution screens.

Created on 19 Sep 2020

:author: semuadmin (Steve Smith)
:copyright: 2020 semuadmin
:license: BSD 3-Clause
"""

import logging
from tkinter import (
    ALL,
    EW,
    HORIZONTAL,
    NS,
    NSEW,
    NW,
    VERTICAL,
    Button,
    Canvas,
    E,
    Frame,
    Label,
    Scrollbar,
    Toplevel,
    W,
)

from PIL import Image, ImageTk

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
    MINHEIGHT,
    MINWIDTH,
    RESIZE,
)
from pygpsclient.helpers import check_lowres
from pygpsclient.strings import DLG


class ToplevelDialog(Toplevel):
    """
    ToplevelDialog class.
    """

    def __init__(self, app, dlgname: str, dim: tuple = (MINHEIGHT, MINWIDTH)):
        """
        Constructor.

        :param Frame app: reference to main tkinter application
        :param str dlgname: dialog name
        :param tuple dim: initial dimensions (height, width)
        """

        self.__app = app  # Reference to main application class
        self.__master = self.__app.appmaster  # Reference to root class (Tk)
        self._dlgname = dlgname
        self.logger = logging.getLogger(f"{APPNAME}.{dlgname}")
        self.lowres, (self.height, self.width) = check_lowres(self.__master, dim)

        super().__init__()

        if self.__app.configuration.get("transient_dialog_b"):
            self.transient(self.__app)
        self.title(dlgname)  # pylint: disable=E1102
        if self.__app.dialog_state.state[dlgname][RESIZE]:
            self.resizable(True, True)
        else:
            self.resizable(self.lowres, self.lowres)
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

        self._con_body()

    def on_expand(self):
        """
        Automatically expand container canvas when sub-frames are resized.
        """

        self._can_container.event_generate("<Configure>")

    def _con_body(self):
        """
        Set up scrollable frame and widgets.
        """

        # create container frame
        if self.lowres:
            x_scrollbar = Scrollbar(self, orient=HORIZONTAL)
            y_scrollbar = Scrollbar(self, orient=VERTICAL)
            self._can_container = Canvas(
                self,
                width=self.width,
                height=self.height,
                xscrollcommand=x_scrollbar.set,
                yscrollcommand=y_scrollbar.set,
            )
            self._frm_container = Frame(
                self._can_container, borderwidth=2, relief="groove"
            )
            self._can_container.grid(column=0, row=0, sticky=NSEW)
            x_scrollbar.grid(column=0, row=1, sticky=EW)
            y_scrollbar.grid(column=1, row=0, sticky=NS)
            x_scrollbar.config(command=self._can_container.xview)
            y_scrollbar.config(command=self._can_container.yview)
            # ensure container canvas expands to accommodate child frames
            self._can_container.create_window(
                (0, 0), window=self._frm_container, anchor=NW
            )
            self._can_container.bind(
                "<Configure>",
                lambda e: self._can_container.config(
                    scrollregion=self._can_container.bbox(ALL)
                ),
            )
        else:  # normal resolution
            self._frm_container = Frame(self, borderwidth=2, relief="groove")
            self._frm_container.grid(column=0, row=0, sticky=NSEW)

        # create status frame
        self._frm_status = Frame(self, borderwidth=2, relief="groove")
        self._lbl_status = Label(self._frm_status, anchor=W)
        self._btn_exit = Button(
            self._frm_status,
            image=self.img_exit,
            width=50,
            fg=ERRCOL,
            command=self.on_exit,
        )
        self._frm_status.grid(column=0, row=2, sticky=EW)
        self._lbl_status.grid(column=0, row=0, sticky=EW)
        self._btn_exit.grid(column=1, row=0, sticky=E)

        # set column and row weights
        # NB!!! these govern the 'pack' behaviour of the frames on resize
        self.grid_columnconfigure(0, weight=10)
        self.grid_rowconfigure(0, weight=10)
        self._frm_status.grid_columnconfigure(0, weight=10)
        if self.lowres:
            colsp, rowsp = self._can_container.grid_size()
        else:
            colsp, rowsp = self._frm_container.grid_size()
        for i in range(colsp):
            self._frm_status.grid_columnconfigure(i, weight=10)
        for i in range(rowsp):
            self._frm_status.grid_rowconfigure(i, weight=10)

    def _finalise(self):
        """
        Finalise Toplevel window after child frames have been created.
        """

        # self.status_label = (f"{self.height}, {self.width}") # testing only

    def on_exit(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Handle Exit button press.
        """

        self.__app.dialog_state.state[self._dlgname][DLG] = None
        self.destroy()

    def _on_resize(self, event):  # pylint: disable=unused-argument
        """
        Resize frame.

        :param event event: resize event
        """

        self.width, self.height = self.get_size()

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
