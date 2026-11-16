"""
menu_bar.py

Menubar class for PyGPSClient application.

This handles the menu bar.

Created on 12 Sep 2020

:author: semuadmin (Steve Smith)
:copyright: 2020 semuadmin
:license: BSD 3-Clause
"""

from tkinter import Menu

from pygpsclient.globals import (
    DLGGUIOPTIONS,
    DLGTGPX,
    DLGTIMPORTMAP,
    DLGTNMEA,
    DLGTNTRIP,
    DLGTRECORD,
    DLGTRINEX,
    DLGTSERVER,
    DLGTTTY,
    DLGTUBX,
    DLGTUBXLEGACY,
    _,
)

DIALOGS = (
    DLGTUBX,
    DLGTUBXLEGACY,
    DLGTNMEA,
    DLGTNTRIP,
    DLGTSERVER,
    DLGTGPX,
    DLGTIMPORTMAP,
    DLGTTTY,
    DLGTRECORD,
    DLGTRINEX,
    DLGGUIOPTIONS,
)


class MenuBar(Menu):
    """
    Menu bar class.
    """

    def __init__(self, app, *args, **kwargs):
        """
        Constructor

        :param Tk app: reference to main tkinter application
        :param args: optional args to pass to Menu parent class
        :param kwargs: optional kwargs to pass to Menu parent class
        """

        self.__app = app  # Reference to main Tk application class
        super().__init__(self.__app, *args, **kwargs)

        self.option_add("*Font", "TkMenuFont")
        # Create a pull-down menu for file operations
        self.file_menu = Menu(self, tearoff=False)
        self.file_menu.add_command(
            label=_("Save Configuration"), underline=5, command=self.__app.save_config
        )
        self.file_menu.add_command(
            label=_("Load Configuration"), underline=5, command=self.__app.load_config
        )
        self.file_menu.add_command(
            label=_("Exit"),
            underline=1,
            accelerator="Ctrl-Q",
            command=self.__app.on_exit,
        )
        self.add_cascade(menu=self.file_menu, label=_("File"))

        # Create a pull-down menu for view operations
        # Menu labels are set in app._grid_widgets() function
        self.view_menu = Menu(self, tearoff=False)
        self.view_menu.add_command(
            underline=1,
            label=_("Undock Settings"),
            command=self.__app.settings_dock,
        )
        self.view_menu.add_command(
            underline=1,
            label=_("Hide Settings"),
            command=self.__app.settings_toggle,
        )
        for nam in self.__app.widget_state.state:
            self.view_menu.add_command(
                underline=1, command=lambda i=nam: self.__app.widget_toggle(i)
            )
        self.view_menu.add_command(
            underline=1,
            label=_("Reset Layout"),
            command=lambda: self.__app.reset_layout(),  # pylint: disable=unnecessary-lambda
        )
        self.add_cascade(menu=self.view_menu, label=_("View"))

        # Create a pull-down menu for view operations
        dialogs = DIALOGS
        self.options_menu = Menu(self, tearoff=False)
        for dlg in dialogs:
            self.options_menu.add_command(
                label=dlg,
                underline=1,
                command=lambda i=dlg: self.__app.start_dialog(i),
            )
        self.add_cascade(menu=self.options_menu, label=_("Options"))

        # Create a pull-down menu for help operations
        self.help_menu = Menu(self, tearoff=False)
        self.help_menu.add_command(
            label=_("About"),
            underline=1,
            command=lambda: self.__app.start_dialog(_("About PyGPSClient")),
        )
        self.add_cascade(menu=self.help_menu, label=_("Help"))
