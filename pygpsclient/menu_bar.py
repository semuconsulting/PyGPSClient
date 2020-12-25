"""
Menubar class for PyGPSClient application.

This handles the menu bar.

Created on 12 Sep 2020

@author: semuadmin
"""
# pylint: disable=invalid-name, too-many-instance-attributes, too-many-ancestors

from tkinter import Menu

from .strings import (
    MENUFILE,
    MENUVIEW,
    MENUOPTION,
    MENUEXIT,
    MENUHIDESE,
    MENUHIDESB,
    MENUHIDECON,
    MENUHIDEMAP,
    MENUHIDESATS,
    MENUABOUT,
    MENUHELP,
    MENUUBXCONFIG,
)


class MenuBar(Menu):
    """
    Menu inheritance class for menu bar.
    """

    def __init__(self, app, *args, **kwargs):
        """
        Constructor

        :param object app: reference to main tkinter application
        """

        self.__app = app  # Reference to main application class
        self.__master = self.__app.get_master()  # Reference to root class (Tk)
        Menu.__init__(self, self.__master, *args, **kwargs)

        self.option_add("*Font", "TkMenuFont")
        # Create a pull-down menu for file operations
        self.file_menu = Menu(self, tearoff=False)
        #         self.file_menu.add_command(label=MENUSAVE, underline=1,
        #                                    command=self.__app.frm_settings._save_settings)
        #         self.file_menu.add_command(label=MENULOAD, underline=1,
        #                                    command=self.__app.frm_settings._load_settings)
        self.file_menu.add_command(
            label=MENUEXIT, underline=1, accelerator="Ctrl-Q", command=self.__app.exit
        )
        self.add_cascade(menu=self.file_menu, label=MENUFILE)

        # Create a pull-down menu for view operations
        self.view_menu = Menu(self, tearoff=False)
        self.view_menu.add_command(
            label=MENUHIDESE, underline=1, command=self.__app.toggle_settings
        )
        self.view_menu.add_command(
            label=MENUHIDESB, underline=1, command=self.__app.toggle_status
        )
        self.view_menu.add_command(
            label=MENUHIDECON, underline=1, command=self.__app.toggle_console
        )
        self.view_menu.add_command(
            label=MENUHIDEMAP, underline=1, command=self.__app.toggle_map
        )
        self.view_menu.add_command(
            label=MENUHIDESATS, underline=1, command=self.__app.toggle_sats
        )
        self.add_cascade(menu=self.view_menu, label=MENUVIEW)

        # Create a pull-down menu for view operations
        self.options_menu = Menu(self, tearoff=False)
        self.options_menu.add_command(
            label=MENUUBXCONFIG, underline=1, command=self.__app.ubxconfig
        )
        self.add_cascade(menu=self.options_menu, label=MENUOPTION)

        # Create a pull-down menu for help operations
        self.help_menu = Menu(self, tearoff=False)
        self.help_menu.add_command(
            label=MENUABOUT, underline=1, command=self.__app.about
        )
        self.add_cascade(menu=self.help_menu, label=MENUHELP)
