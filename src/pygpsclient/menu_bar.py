"""
Menubar class for PyGPSClient application.

This handles the menu bar.

Created on 12 Sep 2020

:author: semuadmin
:copyright: SEMU Consulting © 2020
:license: BSD 3-Clause
"""

from tkinter import Menu

from pygpsclient.globals import DLGTABOUT, DLGTGPX, DLGTNTRIP, DLGTSPARTN, DLGTUBX
from pygpsclient.strings import (
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
from pygpsclient.widgets import widget_grid

DIALOGS = (DLGTUBX, DLGTNTRIP, DLGTSPARTN, DLGTGPX)


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
        for wdg, wdict in widget_grid.items():
            if wdict["menu"] is not None:
                self.view_menu.add_command(
                    underline=1, command=lambda i=wdg: self.__app.toggle_widget(i)
                )
        self.view_menu.add_command(
            underline=1,
            label=MENURESET,
            command=lambda: self.__app.reset_widgets(),  # pylint: disable=unnecessary-lambda
        )
        self.add_cascade(menu=self.view_menu, label=MENUVIEW)

        # Create a pull-down menu for view operations
        self.options_menu = Menu(self, tearoff=False)
        for dlg in DIALOGS:
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
