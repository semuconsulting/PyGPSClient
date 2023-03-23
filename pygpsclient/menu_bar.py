"""
Menubar class for PyGPSClient application.

This handles the menu bar.

Created on 12 Sep 2020

:author: semuadmin
:copyright: SEMU Consulting © 2020
:license: BSD 3-Clause
"""

from tkinter import Menu, NORMAL

from pygpsclient.strings import (
    MENUFILE,
    MENUVIEW,
    MENUOPTION,
    MENUEXIT,
    MENUABOUT,
    MENUHELP,
    MENUUBXCONFIG,
    MENUNTRIPCONFIG,
    MENUGPXVIEWER,
    WDGSETTINGS,
    WDGSTATUS,
    WDGCONSOLE,
    WDGSATS,
    WDGLEVELS,
    WDGMAP,
    WDGSPECTRUM,
    WDGSCATTER,
    MENURESET,
    MENUSPARTNCONFIG,
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
        #         self.file_menu.add_command(label=MENUSAVE, underline=1,
        #                                    command=self.__app.frm_settings._save_settings)
        #         self.file_menu.add_command(label=MENULOAD, underline=1,
        #                                    command=self.__app.frm_settings._load_settings)
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
        self.view_menu.add_command(
            underline=1,
            command=lambda: self._toggle_widget(WDGSETTINGS),
        )
        self.view_menu.add_command(
            underline=1,
            command=lambda: self._toggle_widget(WDGSTATUS),
        )
        self.view_menu.add_command(
            underline=1,
            command=lambda: self._toggle_widget(WDGCONSOLE),
        )
        self.view_menu.add_command(
            underline=1,
            command=lambda: self._toggle_widget(WDGSATS),
        )
        self.view_menu.add_command(
            underline=1,
            command=lambda: self._toggle_widget(WDGLEVELS),
        )
        self.view_menu.add_command(
            underline=1,
            command=lambda: self._toggle_widget(WDGMAP),
        )
        self.view_menu.add_command(
            underline=1,
            command=lambda: self._toggle_widget(WDGSPECTRUM),
        )
        self.view_menu.add_command(
            underline=1,
            command=lambda: self._toggle_widget(WDGSCATTER),
        )
        self.view_menu.add_command(
            underline=1,
            label=MENURESET,
            command=lambda: self._reset_widgets(),  # pylint: disable=unnecessary-lambda
        )

        self.add_cascade(menu=self.view_menu, label=MENUVIEW)

        # Create a pull-down menu for view operations
        self.options_menu = Menu(self, tearoff=False)
        self.options_menu.add_command(
            label=MENUUBXCONFIG,
            underline=1,
            command=self.__app.ubxconfig,
            state=NORMAL,
        )
        self.options_menu.add_command(
            label=MENUNTRIPCONFIG,
            underline=1,
            command=self.__app.ntripconfig,
            state=NORMAL,
        )
        self.options_menu.add_command(
            label=MENUSPARTNCONFIG,
            underline=1,
            command=self.__app.spartnconfig,
            state=NORMAL,
        )
        self.options_menu.add_command(
            label=MENUGPXVIEWER,
            underline=1,
            command=self.__app.gpxviewer,
            state=NORMAL,
        )
        self.add_cascade(menu=self.options_menu, label=MENUOPTION)

        # Create a pull-down menu for help operations
        self.help_menu = Menu(self, tearoff=False)
        self.help_menu.add_command(
            label=MENUABOUT, underline=1, command=self.__app.on_about
        )
        self.add_cascade(menu=self.help_menu, label=MENUHELP)

    def _toggle_widget(self, widget: str):
        """
        Set widget visibility.

        :param str widget: name of widget
        """

        self.__app.toggle_widget(widget)

    def _reset_widgets(self):
        """
        Reset widgets to default layout
        """

        self.__app.reset_widgets()
