"""
Status Bar frame class for PyGPSClient application.

This handles the status bar notifications at the foot of the window.

Created on 12 Sep 2020

:author: semuadmin
:copyright: SEMU Consulting © 2020
:license: BSD 3-Clause
"""

from tkinter import ttk, Frame, Label, StringVar, N, S, W, E, VERTICAL


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
        self.__master = self.__app.get_master()  # Reference to root class (Tk)
        Frame.__init__(self, self.__master, *args, **kwargs)

        self._status = StringVar()
        self._connection = StringVar()
        self.width, self.height = self.get_size()
        self._body()

        self.bind("<Configure>", self._on_resize)

    def _body(self):
        """
        Set up frame and widgets.
        """

        self.grid_rowconfigure(0, weight=1)

        self.option_add("*Font", self.__app.font_md)

        self._lbl_connection = Label(self, textvariable=self._connection, anchor=W)
        self._lbl_status_preset = Label(self, textvariable=self._status, anchor=W)
        self._lbl_connection.grid(column=0, row=0, sticky=(W, E))
        ttk.Separator(self, orient=VERTICAL).grid(column=1, row=0, sticky=(N, S))
        self._lbl_status_preset.grid(column=2, row=0, sticky=(W, E))

    def set_connection(self, connection: str, color="blue"):
        """
        Sets connection description in status bar.

        :param str connection: description of connection
        :param str color: rgb color string (default=blue)

        """

        if len(connection) > 100:
            connection = "..." + connection[-100:]
        self._lbl_connection.config(fg=color)
        self._connection.set("  " + connection)

    def set_status(self, message, color="blue"):
        """
        Sets message in status bar.

        :param str message: message to be displayed in status bar
        :param str color: rgb color string (default=blue)

        """

        if len(message) > 80:
            message = "..." + message[-80:]
        self._lbl_status_preset.config(fg=color)
        self._status.set("  " + message)

    def clear_status(self):
        """
        Clears status bar.
        """

        self._connection.set("")
        self._status.set("")

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
        width = self.winfo_width()
        height = self.winfo_height()
        return (width, height)
