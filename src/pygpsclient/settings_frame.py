"""
settings_frame.py

Settings frame class for PyGPSClient settings_child_frame.

Used when Settings are "docked".

Created on 12 Sep 2020

:author: semuadmin (Steve Smith)
:copyright: 2020 semuadmin
:license: BSD 3-Clause
"""

from tkinter import Frame

from pygpsclient.canvas_subclasses import CanvasContainer
from pygpsclient.settings_child_frame import SettingsChildFrame


class SettingsFrame(Frame):
    """
    Settings frame class.
    """

    def __init__(self, app: Frame, *args, **kwargs):
        """
        Constructor.

        :param Frame app: reference to main tkinter application
        :param args: optional args to pass to Frame parent class
        :param kwargs: optional kwargs to pass to Frame parent class
        """

        self.__app = app  # Reference to main application class
        self.__master = self.__app.appmaster  # Reference to root class (Tk)

        super().__init__(self.__master, *args, **kwargs)

        self._container()  # create scrollable container
        self._body()
        self._do_layout()
        self.focus_force()

    def _container(self):
        """
        Create scrollable container frame.

        NB: any expandable sub-frames must implement an on_resize()
        function which invokes the on_expand() method here.
        """

        self._can_container = CanvasContainer(self.__app, self)
        self._frm_container = self._can_container.frm_container

    def on_expand(self):
        """
        Automatically expand container canvas when sub-frames are resized.
        """

        self._can_container.event_generate("<Configure>")

    def _body(self):
        """
        Set up frame and widgets.
        """

        self.frm_settings = SettingsChildFrame(self.__app, self._frm_container)
        self.frm_serial = self.frm_settings.frm_serial
        self.frm_socketclient = self.frm_settings.frm_socketclient

    def _do_layout(self):
        """
        Position widgets in frame.
        """

        self.frm_settings.grid(column=0, row=0)

        # resize container canvas to accommodate frame
        self._frm_container.update()
        self._can_container.config(
            height=self._frm_container.winfo_height(),
            width=self._frm_container.winfo_width(),
        )
        self._can_container.update()

    def get_size(self) -> tuple:
        """
        Get current frame size.

        :return: (width, height)
        :rtype: tuple

        """

        self.update_idletasks()  # Make sure we know about any resizing
        return (self.winfo_width(), self.winfo_height())
