"""
about_dialog.py

About Dialog Box class for PyGPSClient application.

Created on 20 Sep 2020

:author: semuadmin
:copyright: 2020 SEMU Consulting
:license: BSD 3-Clause
"""

import logging
from inspect import currentframe, getfile
from os import path
from platform import python_version
from subprocess import CalledProcessError, run
from sys import executable
from tkinter import Button, Checkbutton, E, Frame, IntVar, Label, Tcl, Toplevel, W
from webbrowser import open_new_tab

from PIL import Image, ImageTk
from pygnssutils import version as PGVERSION
from pynmeagps import version as NMEAVERSION
from pyrtcm import version as RTCMVERSION
from pysbf2 import version as SBFVERSION
from pyspartn import version as SPARTNVERSION
from pyubx2 import version as UBXVERSION

from pygpsclient._version import __version__ as VERSION
from pygpsclient.globals import (
    ERRCOL,
    ICON_APP128,
    ICON_EXIT,
    ICON_GITHUB,
    ICON_SPONSOR,
    INFOCOL,
    LICENSE_URL,
    OKCOL,
    SPONSOR_URL,
)
from pygpsclient.helpers import check_latest
from pygpsclient.strings import ABOUTTXT, COPYRIGHTTXT, DLGABOUT, DLGTABOUT, GITHUB_URL

LIBVERSIONS = {
    "PyGPSClient": VERSION,
    "pygnssutils": PGVERSION,
    "pyubx2": UBXVERSION,
    "pysbf2": SBFVERSION,
    "pynmeagps": NMEAVERSION,
    "pyrtcm": RTCMVERSION,
    "pyspartn": SPARTNVERSION,
}


class AboutDialog:
    """
    About dialog box class
    """

    def __init__(self, app, **kwargs):  # pylint: disable=unused-argument
        """
        Initialise Toplevel dialog

        :param Frame app: reference to main tkinter application
        """

        self.__app = app  # Reference to main application class
        self.__master = self.__app.appmaster  # Reference to root class (Tk)
        self.logger = logging.getLogger(__name__)
        self._dialog = Toplevel()
        self._dialog.title = DLGABOUT
        self._dialog.geometry(
            f"+{self.__master.winfo_rootx() + 50}+{self.__master.winfo_rooty() + 50}"
        )
        self._dialog.attributes("-topmost", "true")
        self._img_icon = ImageTk.PhotoImage(Image.open(ICON_APP128).resize((64, 64)))
        self._img_github = ImageTk.PhotoImage(Image.open(ICON_GITHUB).resize((32, 32)))
        self._img_exit = ImageTk.PhotoImage(Image.open(ICON_EXIT))
        self._img_sponsor = ImageTk.PhotoImage(Image.open(ICON_SPONSOR))
        self._checkonstartup = IntVar()
        self._checkonstartup.set(self.__app.configuration.get("checkforupdate_b"))
        self._updates = []

        self._body()
        self._do_layout()
        self._attach_events()

    def _body(self):
        """
        Set up widgets.
        """

        self._frm_container = Frame(self._dialog, borderwidth=2, relief="groove")
        self._lbl_title = Label(self._frm_container, text=DLGABOUT)
        self._lbl_title.config(font=self.__app.font_md2)
        self._lbl_icon = Label(self._frm_container, image=self._img_icon)
        self._lbl_desc = Label(
            self._frm_container,
            text=ABOUTTXT,
            wraplength=350,
            font=self.__app.font_sm,
        )
        tkv = Tcl().call("info", "patchlevel")
        self._lbl_python_version = Label(
            self._frm_container,
            text=f"Python: {python_version()}  Tk: {tkv}",
            font=self.__app.font_sm,
        )
        self._lbl_lib_versions = []
        for nam, ver in LIBVERSIONS.items():
            self._lbl_lib_versions.append(
                Label(
                    self._frm_container,
                    text=f"{nam}: {ver}",
                    font=self.__app.font_sm,
                )
            )
        self._btn_checkupdate = Button(
            self._frm_container,
            text="Check for updates",
            width=12,
            font=self.__app.font_sm,
            cursor="hand2",
        )
        self._chk_checkupdate = Checkbutton(
            self._frm_container,
            text="Check on startup",
            variable=self._checkonstartup,
        )
        self._lbl_giticon = Label(
            self._frm_container,
            image=self._img_github,
            cursor="hand2",
        )
        self._lbl_sponsoricon = Label(
            self._frm_container,
            image=self._img_sponsor,
            cursor="hand2",
        )
        self._lbl_github = Label(
            self._frm_container,
            text=GITHUB_URL,
            font=self.__app.font_sm,
            fg=INFOCOL,
            cursor="hand2",
        )
        self._lbl_copyright = Label(
            self._frm_container,
            text=COPYRIGHTTXT,
            font=self.__app.font_sm,
            cursor="hand2",
        )
        self._btn_ok = Button(
            self._frm_container,
            image=self._img_exit,
            width=55,
            command=self._ok_press,
            cursor="hand2",
        )

    def _do_layout(self):
        """
        Arrange widgets in dialog.
        """

        self._frm_container.grid(column=0, row=0, padx=5, pady=5, ipadx=5, ipady=5)
        self._lbl_title.grid(column=0, row=0, columnspan=2, padx=3, pady=3)
        self._lbl_icon.grid(column=0, row=1, columnspan=2, padx=3, pady=3)
        self._lbl_desc.grid(column=0, row=2, columnspan=2, padx=3, pady=3)
        self._lbl_python_version.grid(column=0, row=3, columnspan=2, padx=3, pady=3)
        i = 0
        for i, _ in enumerate(LIBVERSIONS):
            self._lbl_lib_versions[i].grid(
                column=0, row=4 + i, columnspan=2, padx=2, pady=2
            )
        self._btn_checkupdate.grid(
            column=0, row=5 + i, ipadx=3, ipady=3, padx=3, pady=3
        )
        self._chk_checkupdate.grid(
            column=1, row=5 + i, ipadx=3, ipady=3, padx=3, pady=3
        )
        self._lbl_giticon.grid(column=0, row=6 + i, padx=(3, 1), pady=3, sticky=E)
        self._lbl_sponsoricon.grid(column=1, row=6 + i, padx=(3, 1), pady=3, sticky=W)
        self._lbl_github.grid(column=0, row=7 + i, columnspan=2, padx=(1, 3), pady=3)
        self._lbl_copyright.grid(column=0, row=8 + i, columnspan=2, padx=3, pady=3)
        self._btn_ok.grid(
            column=0, row=9 + i, ipadx=3, ipady=3, columnspan=2, padx=5, pady=3
        )

    def _attach_events(self):
        """
        Bind events to dialog.
        """

        self._btn_checkupdate.bind("<Button>", self._check_for_update)
        self._lbl_giticon.bind("<Button>", self._on_github)
        self._lbl_github.bind("<Button>", self._on_github)
        self._lbl_sponsoricon.bind("<Button>", self._on_sponsor)
        self._lbl_copyright.bind("<Button>", self._on_license)
        self._btn_ok.bind("<Return>", self._ok_press)
        self._btn_ok.focus_set()
        self._checkonstartup.trace_add("write", self._on_update_config)

    def _on_update_config(self, var, index, mode):  # pylint: disable=unused-argument
        """
        Save current settings to saved app config dict.
        """

        self.__app.configuration.set(
            "checkforupdate_b", int(self._checkonstartup.get())
        )

    def _on_github(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Close dialog and go to GitHub.
        """

        open_new_tab(GITHUB_URL)
        self._ok_press()

    def _on_sponsor(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Close dialog and go to Sponsor website.
        """

        open_new_tab(SPONSOR_URL)
        self._ok_press()

    def _on_license(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Close dialog and go to GitHub LICENSE file.
        """

        open_new_tab(LICENSE_URL)
        self._ok_press()

    def _ok_press(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Handle OK button press.
        """

        self.__app.stop_dialog(DLGTABOUT)
        self._dialog.destroy()

    def _check_for_update(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Check for updates.
        """

        self._updates = []
        for i, (nam, current) in enumerate(LIBVERSIONS.items()):
            latest = check_latest(nam)
            txt = f"{nam}: {current}"
            if latest == current:
                txt += ". ✓"
                col = OKCOL
            elif latest == "N/A":
                txt += ". Info not available!"
                col = ERRCOL
            else:
                self._updates.append(nam)
                txt += f". Latest version is {latest}"
                col = ERRCOL
            self._lbl_lib_versions[i].config(text=txt, fg=col)

        if len(self._updates) > 0:
            self._btn_checkupdate.config(text="UPDATE", fg=INFOCOL)
            self._btn_checkupdate.bind("<Button>", self._do_update)

    def _do_update(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Run python update.
        """

        self._btn_checkupdate.config(text="UPDATING...", fg=INFOCOL)
        self._dialog.update_idletasks()
        pth = path.dirname(path.abspath(getfile(currentframe())))
        if "pipx" in pth:  # installed into venv using pipx
            cmd = [
                "pipx",
                "upgrade",
                "pygpsclient",
            ]
        else:  # installed using pip
            cmd = [
                executable,  # i.e. python3 or python
                "-m",
                "pip",
                "install",
                "--upgrade",
            ]
            for pkg in self._updates:
                cmd.append(pkg)

        result = None
        try:
            result = run(cmd, check=True, capture_output=True)
            self.logger.debug(result.stdout)
        except CalledProcessError:
            self.logger.error(result.stdout)
            self._btn_checkupdate.config(text="UPDATE FAILED", fg=ERRCOL)
            self._btn_checkupdate.bind("<Button>", self._check_for_update)
            return

        self._btn_checkupdate.config(text="RESTART APP", fg=OKCOL)
        self._btn_checkupdate.bind("<Button>", self.__app.on_exit)
