"""
About Dialog Box class for PyGPSClient application.

Created on 20 Sep 2020

@author: semuadmin
"""

from tkinter import Toplevel, Label, Button
from webbrowser import open_new_tab
from PIL import ImageTk, Image
from pynmea2 import version as PNVERSION
from pyubx2 import version as PUVERSION
from .globals import ICON_APP, GITHUB_URL
from .strings import ABOUTTXT, COPYRIGHTTXT, DLGABOUT
from ._version import __version__ as VERSION


class AboutDialog:
    """
    About dialog box class
    """

    def __init__(self, app):
        """
        Initialise Toplevel dialog

        :param app: reference to main tkinter application
        """

        self.__app = app  # Reference to main application class
        self.__master = self.__app.get_master()  # Reference to root class (Tk)
        self._dialog = Toplevel()
        self._dialog.title = DLGABOUT
        self._dialog.geometry(
            "+%d+%d"
            % (self.__master.winfo_rootx() + 50, self.__master.winfo_rooty() + 50)
        )
        self._dialog.attributes("-topmost", "true")
        self._img_icon = ImageTk.PhotoImage(Image.open(ICON_APP))

        self._body()
        self._do_layout()
        self._attach_events()

    def _body(self):
        """
        Set up widgets.
        """

        self._lbl_title = Label(self._dialog, text=DLGABOUT)
        self._lbl_title.config(font=self.__app.font_md2)
        self._lbl_icon = Label(self._dialog, image=self._img_icon)
        self._lbl_desc = Label(
            self._dialog, text=ABOUTTXT, wraplength=250, font=self.__app.font_sm
        )
        self._lbl_version = Label(
            self._dialog, text="Version: " + VERSION, font=self.__app.font_sm
        )
        self._lbl_pyubx2_version = Label(
            self._dialog, text="pyubx2 Version: " + PUVERSION, font=self.__app.font_sm
        )
        self._lbl_pynmea2_version = Label(
            self._dialog, text="pynmea2 Version: " + PNVERSION, font=self.__app.font_sm
        )
        self._lbl_copyright = Label(
            self._dialog,
            text=COPYRIGHTTXT,
            fg="blue",
            font=self.__app.font_sm,
            cursor="hand2",
        )
        self._btn_ok = Button(
            self._dialog,
            text="OK",
            width=8,
            command=self.ok_press,
            font=self.__app.font_md,
        )

    def _do_layout(self):
        """
        Arrange widgets in dialog.
        """

        self._lbl_title.grid(column=0, row=0, padx=5, pady=3)
        self._lbl_icon.grid(column=0, row=1, padx=5, pady=3)
        self._lbl_desc.grid(column=0, row=2, padx=5, pady=3)
        self._lbl_version.grid(column=0, row=3, padx=5, pady=0)
        self._lbl_pynmea2_version.grid(column=0, row=4, padx=5, pady=0)
        self._lbl_pyubx2_version.grid(column=0, row=5, padx=5, pady=0)
        self._lbl_copyright.grid(column=0, row=6, padx=5, pady=3)
        self._btn_ok.grid(column=0, row=7, ipadx=3, ipady=3, padx=5, pady=3)

    def _attach_events(self):
        """
        Bind events to dialog.
        """

        self._lbl_copyright.bind("<Button-1>", lambda e: open_new_tab(GITHUB_URL))
        self._btn_ok.bind("<Return>", self.ok_press)
        self._btn_ok.focus_set()

    def ok_press(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Handle OK button press.
        """

        self.__master.update_idletasks()
        self._dialog.destroy()
