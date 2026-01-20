"""
settings_dialog.py

Settings Toplevel dialog container class for PyGPSClient settings_child_frame.

Used when Settings are "undocked".

Created on 14 Jan 2026

:author: semuadmin (Steve Smith)
:copyright: 2020 semuadmin
:license: BSD 3-Clause
"""

from tkinter import NSEW, Frame

from pygpsclient.settings_child_frame import SettingsChildFrame
from pygpsclient.strings import DLGTSETTINGS
from pygpsclient.toplevel_dialog import ToplevelDialog


class SettingsDialog(ToplevelDialog):
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

        super().__init__(app, DLGTSETTINGS)

        self._body()
        self._do_layout()
        self._finalise()
        self.focus_force()

    def on_expand(self):
        """
        Automatically expand container canvas when sub-frames are resized.
        """

        self._can_container.event_generate("<Configure>")

    def _body(self):
        """
        Set up frame and widgets.
        """

        self.frm_settings = SettingsChildFrame(self.__app, self.container)
        self.frm_serial = self.frm_settings.frm_serial
        self.frm_socketclient = self.frm_settings.frm_socketclient

    def _do_layout(self):
        """
        Position widgets in frame.
        """

        self.frm_settings.grid(column=0, row=0, sticky=NSEW)

    def on_exit(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Overridden method - closing this dialog 'docks' the Settings panel
        back onto the main application window.
        """

        self.__app.settings_dock()
