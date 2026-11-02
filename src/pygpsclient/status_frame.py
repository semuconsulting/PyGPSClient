"""
status_frame.py

Status Bar frame class for PyGPSClient application.

This handles the status bar notifications at the foot of the window.

Created on 12 Sep 2020

:author: semuadmin (Steve Smith)
:copyright: 2020 semuadmin
:license: BSD 3-Clause
"""

from tkinter import EW, NS, VERTICAL, Frame, Label, Tk, W, ttk

from pygpsclient.globals import BGCOL, INFOCOL, STATUS_TIMEOUT


class StatusFrame(Frame):
    """
    Status bar frame class.
    """

    def __init__(self, app: Tk, *args, **kwargs):
        """
        Constructor

        :param Tk app: reference to main tkinter application
        :param args: optional args to pass to Frame parent class
        :param kwargs: optional kwargs to pass to Frame parent class
        """

        self.__app = app  # Reference to main application class

        super().__init__(app, *args, **kwargs)

        self.width, self.height = self.get_size()
        self._status_msg_timer = None
        self._body()
        self._do_layout()
        self._attach_events()

    def _body(self):
        """
        Set up frame and widgets.
        """

        self.lbl_connection = Label(self, anchor=W, bg=BGCOL)
        self.lbl_device = Label(self, anchor=W, bg=BGCOL)
        self.lbl_status = Label(self, anchor=W, bg=BGCOL)

    def _do_layout(self):
        """
        Position widgets in frame.
        """

        self.lbl_connection.grid(column=0, row=0, sticky=EW)
        ttk.Separator(self, orient=VERTICAL).grid(column=1, row=0, sticky=NS)
        self.lbl_device.grid(column=2, row=0, sticky=EW)
        ttk.Separator(self, orient=VERTICAL).grid(column=3, row=0, sticky=NS)
        self.lbl_status.grid(column=4, row=0, sticky=EW)

    def _attach_events(self):
        """
        Bind events to frame.
        """

        self.bind("<Configure>", self._on_resize)

    def _on_resize(self, event):  # pylint: disable=unused-argument
        """
        Resize frame

        :param event event: resize event

        """

        self.width, self.height = self.get_size()

    def get_size(self):
        """
        Get current frame size.

        :return: window size (width, height)
        :rtype: tuple
        """

        self.update_idletasks()  # Make sure we know about any resizing
        return self.winfo_width(), self.winfo_height()

    def _set_label(self, label: Label, msg: str, col: str, maxlen: int = 80):
        """
        Update label.

        :param Label label: label
        :param str msg: message
        :param str col: color
        :param int maxlen: maximum length
        """

        if len(msg) > maxlen:
            msg = f"...{msg[-maxlen:]}"
        label["text"] = msg
        label["fg"] = col
        label.update()

    def set_connection(self, msg: str = "", col: str = INFOCOL, maxlen: int = 80):
        """
        Update connection label.

        :param str msg: message
        :param str col: color
        :param int maxlen: maximum length
        """

        self._set_label(self.lbl_connection, msg, col, maxlen)

    def set_device(self, msg: str = "", col: str = INFOCOL, maxlen: int = 30):
        """
        Update device label.

        :param str msg: message
        :param str col: color
        :param int maxlen: maximum length
        """

        self._set_label(self.lbl_device, msg, col, maxlen)

    def set_status(
        self, msg: str = "", col: str = INFOCOL, maxlen: int = 200, expire: bool = True
    ):
        """
        Update status label.

        :param str msg: message
        :param str col: color
        :param int maxlen: maximum length
        :param bool expire: message expires (blanks)
        """

        if self._status_msg_timer is not None:
            self.after_cancel(self._status_msg_timer)

        self._set_label(self.lbl_status, msg, col, maxlen)

        if expire and msg.strip() != "":
            self._status_msg_timer = self.after(STATUS_TIMEOUT, self.set_status)
