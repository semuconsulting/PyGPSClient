"""
status_frane.py

Status Bar frame class for PyGPSClient application.

This handles the status bar notifications at the foot of the window.

Created on 12 Sep 2020

:author: semuadmin (Steve Smith)
:copyright: 2020 semuadmin
:license: BSD 3-Clause
"""

from tkinter import EW, NS, VERTICAL, Frame, Label, W, ttk


class StatusFrame(Frame):
    """
    Status bar frame class.
    """

    def __init__(self, app, *args, **kwargs):
        """
        Constructor

        :param Frame app: reference to main tkinter application
        :param args: optional args to pass to Frame parent class
        :param kwargs: optional kwargs to pass to Frame parent class
        """

        self.__app = app  # Reference to main application class
        self.__master = self.__app.appmaster  # Reference to root class (Tk)
        Frame.__init__(self, self.__master, *args, **kwargs)

        self.width, self.height = self.get_size()
        self._body()

        self.bind("<Configure>", self._on_resize)

    def _body(self):
        """
        Set up frame and widgets.
        """

        self.grid_rowconfigure(0, weight=1)

        self.option_add("*Font", self.__app.font_md)

        self.lbl_connection = Label(self, anchor=W)
        self.lbl_status = Label(self, anchor=W)
        self.lbl_connection.grid(column=0, row=0, sticky=EW)
        ttk.Separator(self, orient=VERTICAL).grid(column=1, row=0, sticky=NS)
        self.lbl_status.grid(column=2, row=0, sticky=EW)

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
