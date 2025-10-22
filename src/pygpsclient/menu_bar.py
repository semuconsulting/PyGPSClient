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

from pygpsclient.strings import DLGTSPARTN  # service discontinued by u-blox
from pygpsclient.strings import (
    DLGTABOUT,
    DLGTGPX,
    DLGTIMPORTMAP,
    DLGTNMEA,
    DLGTNTRIP,
    DLGTTTY,
    DLGTUBX,
    MENUABOUT,
    MENUEXIT,
    MENUFILE,
    MENUHELP,
    MENULOAD,
    MENUOPTION,
    MENURESET,
    MENUSAVE,
    MENUVIEW,
)
from pygpsclient.widget_state import MENU

DIALOGS = (
    DLGTUBX,
    DLGTNMEA,
    DLGTNTRIP,
    # DLGTSPARTN,  # service discontinued by u-blox
    DLGTGPX,
    DLGTIMPORTMAP,
    DLGTTTY,
)


class MenuBar(Menu):
    """
    Menu bar class.
    """

    def __init__(self, app, *args, **kwargs):
        """
        Constructor

        :param Frame app: reference to main tkinter application
        :param args: optional args to pass to Menu parent class
        :param kwargs: optional kwargs to pass to Menu parent class
        """

        self.__app = app  # Reference to main application class
        self.__master = self.__app.appmaster  # Reference to root class (Tk)
        Menu.__init__(self, self.__master, *args, **kwargs)

        self.option_add("*Font", "TkMenuFont")
        # Create a pull-down menu for file operations
        self.file_menu = Menu(self, tearoff=False)
        self.file_menu.add_command(
            label=MENUSAVE, underline=5, command=self.__app.save_config
        )
        self.file_menu.add_command(
            label=MENULOAD, underline=5, command=self.__app.load_config
        )
        self.file_menu.add_command(
            label=MENUEXIT,
            underline=1,
            accelerator="Ctrl-Q",
            command=self.__app.on_exit,
        )
        self.add_cascade(menu=self.file_menu, label=MENUFILE)

        # Create a pull-down menu for view operations
        # Menu labels are set in app._grid_widgets() function
        self.view_menu = Menu(self, tearoff=False)
        for wdg, wdict in self.__app.widget_state.state.items():
            if wdict.get(MENU, True):
                self.view_menu.add_command(
                    underline=1, command=lambda i=wdg: self.__app.widget_toggle(i)
                )
        self.view_menu.add_command(
            underline=1,
            label=MENURESET,
            command=lambda: self.__app.widget_reset(),  # pylint: disable=unnecessary-lambda
        )
        self.add_cascade(menu=self.view_menu, label=MENUVIEW)

        # Create a pull-down menu for view operations
        dialogs = DIALOGS
        # since u-blox discontinued SPARTN services, this menu
        # option is now conditional
        if self.__app.configuration.get("lband_enabled_b"):
            dialogs += (DLGTSPARTN,)
        self.options_menu = Menu(self, tearoff=False)
        for dlg in dialogs:
            self.options_menu.add_command(
                label=dlg,
                underline=1,
                command=lambda i=dlg: self.__app.start_dialog(i),
            )
        self.add_cascade(menu=self.options_menu, label=MENUOPTION)

        # Create a pull-down menu for help operations
        self.help_menu = Menu(self, tearoff=False)
        self.help_menu.add_command(
            label=MENUABOUT,
            underline=1,
            command=lambda: self.__app.start_dialog(DLGTABOUT),
        )
        self.add_cascade(menu=self.help_menu, label=MENUHELP)
