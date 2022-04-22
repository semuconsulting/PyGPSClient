"""
About Dialog Box class for PyGPSClient application.

Created on 20 Sep 2020

:author: semuadmin
:copyright: SEMU Consulting © 2020
:license: BSD 3-Clause
"""

from tkinter import Toplevel, Label, Button
from platform import python_version
from webbrowser import open_new_tab
from PIL import ImageTk, Image
from pynmeagps import version as PNVERSION
from pyubx2 import version as PUVERSION
from pyrtcm import version as RTVERSION
from pygpsclient.helpers import check_for_update
from pygpsclient.globals import ICON_APP, GITHUB_URL, PYPI_URL
from pygpsclient.strings import ABOUTTXT, COPYRIGHTTXT, DLGABOUT
from pygpsclient._version import __version__ as VERSION


class AboutDialog:
    """
    About dialog box class
    """

    def __init__(self, app):
        """
        Initialise Toplevel dialog

        :param Frame app: reference to main tkinter application
        """

        self.__app = app  # Reference to main application class
        self.__master = self.__app.get_master()  # Reference to root class (Tk)
        self._dialog = Toplevel()
        self._dialog.title = DLGABOUT
        self._dialog.geometry(
            f"+{self.__master.winfo_rootx() + 50}+{self.__master.winfo_rooty() + 50}"
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
            self._dialog,
            text=ABOUTTXT,
            wraplength=350,
            font=self.__app.font_sm,
            cursor="hand2",
        )
        self._lbl_version = Label(
            self._dialog, text="Version: " + VERSION, font=self.__app.font_sm
        )
        self._lbl_python_version = Label(
            self._dialog,
            text="Python Version: " + python_version(),
            font=self.__app.font_sm,
        )
        self._btn_checkupdate = Button(
            self._dialog,
            text="Check for update",
            width=12,
            font=self.__app.font_sm,
            cursor="hand2",
        )
        self._lbl_update = Label(
            self._dialog,
            text="",
            fg="blue",
            font=self.__app.font_sm,
            cursor="hand2",
        )
        self._lbl_pyubx2_version = Label(
            self._dialog, text="pyubx2 Version: " + PUVERSION, font=self.__app.font_sm
        )
        self._lbl_pynmea2_version = Label(
            self._dialog,
            text="pynmeagps Version: " + PNVERSION,
            font=self.__app.font_sm,
        )
        self._lbl_pyrtcm_version = Label(
            self._dialog,
            text="pyrtcm Version: " + RTVERSION,
            font=self.__app.font_sm,
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
            command=self._ok_press,
            font=self.__app.font_md,
            cursor="hand2",
        )

    def _do_layout(self):
        """
        Arrange widgets in dialog.
        """

        self._lbl_title.grid(column=0, row=0, padx=5, pady=3)
        self._lbl_icon.grid(column=0, row=1, padx=5, pady=3)
        self._lbl_desc.grid(column=0, row=2, padx=15, pady=3)
        self._lbl_version.grid(column=0, row=3, padx=5, pady=0)
        self._btn_checkupdate.grid(column=0, row=4, ipadx=3, ipady=3, padx=5, pady=3)
        self._lbl_update.grid(column=0, row=5, padx=5, pady=3)
        self._lbl_python_version.grid(column=0, row=6, padx=5, pady=0)
        self._lbl_pynmea2_version.grid(column=0, row=7, padx=5, pady=0)
        self._lbl_pyubx2_version.grid(column=0, row=8, padx=5, pady=0)
        self._lbl_pyrtcm_version.grid(column=0, row=9, padx=5, pady=0)
        self._lbl_copyright.grid(column=0, row=10, padx=15, pady=3)
        self._btn_ok.grid(column=0, row=11, ipadx=3, ipady=3, padx=5, pady=3)

    def _attach_events(self):
        """
        Bind events to dialog.
        """

        self._btn_checkupdate.bind("<Button>", self._check_for_update)
        self._lbl_update.bind("<Button-1>", lambda e: open_new_tab(PYPI_URL))
        self._lbl_desc.bind("<Button-1>", lambda e: open_new_tab(GITHUB_URL))
        self._lbl_copyright.bind("<Button-1>", lambda e: open_new_tab(GITHUB_URL))
        self._btn_ok.bind("<Return>", self._ok_press)
        self._btn_ok.focus_set()

    def _ok_press(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Handle OK button press.
        """

        # self.__master.update_idletasks()
        self._dialog.destroy()

    def _check_for_update(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Check for update.
        """

        self._lbl_update.config(
            text="               Checking...               ", fg="blue"
        )
        self.__master.update_idletasks()
        latest, ver = check_for_update("PyGPSClient")
        if latest:
            self._lbl_update.config(text="This is the latest version.", fg="green")
        else:
            self._lbl_update.config(text=f"Latest official release is {ver}", fg="red")
