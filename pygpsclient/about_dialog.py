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
from pygnssutils import version as PGVERSION
from pyubx2 import version as UBXVERSION
from pynmeagps import version as NMEAVERSION
from pyrtcm import version as RTCMVERSION
from pygpsclient.helpers import check_latest
from pygpsclient.globals import ICON_APP, ICON_EXIT, GITHUB_URL
from pygpsclient.strings import ABOUTTXT, COPYRIGHTTXT, DLGABOUT
from pygpsclient._version import __version__ as VERSION

LIBVERSIONS = {
    "PyGPSClient": VERSION,
    "pygnssutils": PGVERSION,
    "pyubx2": UBXVERSION,
    "pynmeagps": NMEAVERSION,
    "pyrtcm": RTCMVERSION,
}


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
        self._img_exit = ImageTk.PhotoImage(Image.open(ICON_EXIT))

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
            wraplength=300,
            font=self.__app.font_sm,
            cursor="hand2",
        )
        self._lbl_python_version = Label(
            self._dialog,
            text=f"Python: {python_version()}",
            font=self.__app.font_sm,
        )
        self._lbl_lib_versions = []
        for (nam, ver) in LIBVERSIONS.items():
            self._lbl_lib_versions.append(
                Label(
                    self._dialog,
                    text=f"{nam}: {ver}",
                    font=self.__app.font_sm,
                )
            )
        self._btn_checkupdate = Button(
            self._dialog,
            text="Check for updates",
            width=12,
            font=self.__app.font_sm,
            cursor="hand2",
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
            image=self._img_exit,
            width=55,
            command=self._ok_press,
            cursor="hand2",
        )

    def _do_layout(self):
        """
        Arrange widgets in dialog.
        """

        self._lbl_title.grid(column=0, row=0, padx=5, pady=3)
        self._lbl_icon.grid(column=0, row=1, padx=5, pady=3)
        self._lbl_desc.grid(column=0, row=2, padx=15, pady=3)
        self._lbl_python_version.grid(column=0, row=3, padx=5, pady=3)
        i = 0
        for i, _ in enumerate(LIBVERSIONS):
            self._lbl_lib_versions[i].grid(column=0, row=4 + i, padx=5, pady=1)
        self._btn_checkupdate.grid(
            column=0, row=5 + i, ipadx=3, ipady=3, padx=5, pady=3
        )
        self._lbl_copyright.grid(column=0, row=6 + i, padx=15, pady=3)
        self._btn_ok.grid(column=0, row=7 + i, ipadx=3, ipady=3, padx=5, pady=3)

    def _attach_events(self):
        """
        Bind events to dialog.
        """

        self._btn_checkupdate.bind("<Button>", self._check_for_update)
        self._lbl_desc.bind("<Button-1>", lambda e: open_new_tab(GITHUB_URL))
        self._lbl_copyright.bind("<Button-1>", lambda e: open_new_tab(GITHUB_URL))
        self._btn_ok.bind("<Return>", self._ok_press)
        self._btn_ok.focus_set()

    def _ok_press(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Handle OK button press.
        """

        self._dialog.destroy()

    def _check_for_update(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Check for updates.
        """

        for i, (nam, current) in enumerate(LIBVERSIONS.items()):
            latest = check_latest(nam)
            txt = f"{nam}: {current}"
            if latest == current:
                col = "green"
            elif latest == "N/A":
                txt += ". Info not available!"
                col = "red"
            else:
                txt += f". Latest version is {latest}"
                col = "red"
            self._lbl_lib_versions[i].config(text=txt, fg=col)
