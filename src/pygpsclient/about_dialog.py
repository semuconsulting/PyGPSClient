"""
about_dialog.py

About Dialog Box class for PyGPSClient application.

Created on 20 Sep 2020

:author: semuadmin (Steve Smith)
:copyright: 2020 semuadmin
:license: BSD 3-Clause
"""

import logging
from platform import machine, python_version
from tkinter import Button, Checkbutton, Frame, IntVar, Label, Tcl
from webbrowser import open_new_tab

from PIL import Image, ImageTk

from pygpsclient.globals import (
    ERRCOL,
    ICON_APP128,
    ICON_GITHUB,
    ICON_SPONSOR,
    INFOCOL,
    LICENSE_URL,
    OKCOL,
    SPONSOR_URL,
    TRACEMODE_WRITE,
)
from pygpsclient.helpers import LIBVERSIONS, brew_installed, check_for_updates
from pygpsclient.sqlite_handler import SQLSTATUS
from pygpsclient.strings import (
    ABOUTTXT,
    BREWUPDATE,
    BREWWARN,
    COPYRIGHT,
    DLGTABOUT,
    GITHUB_URL,
    NA,
    UPDATEERR,
    UPDATEINPROG,
    UPDATERESTART,
)
from pygpsclient.toplevel_dialog import ToplevelDialog


class AboutDialog(ToplevelDialog):
    """
    About dialog box class
    """

    def __init__(self, app, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Initialise Toplevel dialog

        :param Frame app: reference to main tkinter application
        """

        self.__app = app  # Reference to main application class
        self.__master = self.__app.appmaster  # Reference to root class (Tk)
        self.logger = logging.getLogger(__name__)
        self._img_icon = ImageTk.PhotoImage(Image.open(ICON_APP128).resize((64, 64)))
        self._img_github = ImageTk.PhotoImage(Image.open(ICON_GITHUB).resize((32, 32)))
        self._img_sponsor = ImageTk.PhotoImage(Image.open(ICON_SPONSOR))
        self._checkonstartup = IntVar()
        self._checkonstartup.set(self.__app.configuration.get("checkforupdate_b"))

        super().__init__(app, DLGTABOUT)

        self._body()
        self._do_layout()
        self._attach_events()
        self._finalise()

    def _body(self):
        """
        Set up widgets.
        """

        self._frm_body = Frame(self.container)
        self._lbl_icon = Label(self._frm_body, image=self._img_icon, borderwidth=0)
        self._lbl_descs = []
        for txt in ABOUTTXT:
            self._lbl_descs.append(
                Label(
                    self._frm_body,
                    text=txt,
                    borderwidth=0,
                )
            )
        tkv = Tcl().call("info", "patchlevel")
        self._lbl_python_version = Label(
            self._frm_body,
            text=(
                f"Arch: {machine()}  "
                f"Python: {python_version()}  Tk: {tkv}  "
                f"Spatial: {SQLSTATUS[self.__app.db_enabled]}"
            ),
        )
        self._lbl_lib_versions = []
        for nam, ver in LIBVERSIONS.items():
            self._lbl_lib_versions.append(
                Label(
                    self._frm_body,
                    text=f"{nam}: {ver}",
                    borderwidth=0,
                    highlightthickness=0,
                )
            )
        self._btn_checkupdate = Button(
            self._frm_body,
            text="",
            width=14,
            cursor="hand2",
        )
        self._chk_checkupdate = Checkbutton(
            self._frm_body,
            text="Check on startup",
            variable=self._checkonstartup,
        )
        self._lbl_sponsoricon = Label(
            self._frm_body,
            image=self._img_sponsor,
            cursor="hand2",
        )
        self._lbl_github = Label(
            self._frm_body,
            text=GITHUB_URL,
            fg=INFOCOL,
            cursor="hand2",
        )
        self._lbl_copyright = Label(
            self._frm_body,
            text=COPYRIGHT,
            cursor="hand2",
        )

    def _do_layout(self):
        """
        Arrange widgets in dialog.
        """

        i = 0
        self._frm_body.grid(column=0, row=0, padx=5, pady=5, ipadx=5, ipady=5)
        self._lbl_icon.grid(column=0, row=1, columnspan=2, padx=3, pady=0)
        for i, lbl in enumerate(self._lbl_descs):
            lbl.grid(column=0, row=2 + i, columnspan=2, padx=3, pady=0)
        self._lbl_python_version.grid(column=0, row=3 + i, columnspan=2, padx=3, pady=1)
        n = 4 + i
        for i, lbl in enumerate(self._lbl_lib_versions):
            lbl.grid(column=0, row=n + i, columnspan=2, padx=2)
        self._btn_checkupdate.grid(
            column=0, row=1 + n + i, ipadx=3, ipady=3, padx=3, pady=3
        )
        self._chk_checkupdate.grid(
            column=1, row=1 + n + i, ipadx=3, ipady=3, padx=3, pady=3
        )
        self._lbl_sponsoricon.grid(
            column=0, row=2 + n + i, columnspan=2, padx=3, pady=3
        )
        self._lbl_github.grid(column=0, row=3 + n + i, columnspan=2, padx=3, pady=0)
        self._lbl_copyright.grid(column=0, row=4 + n + i, columnspan=2, padx=3, pady=0)

    def _attach_events(self):
        """
        Bind events to dialog.
        """

        self._set_update_btn_mode(False)
        self._lbl_github.bind("<Button>", self._on_github)
        self._lbl_sponsoricon.bind("<Button>", self._on_sponsor)
        self._lbl_copyright.bind("<Button>", self._on_license)
        self._checkonstartup.trace_add(TRACEMODE_WRITE, self._on_update_startup)
        self._btn_exit.focus_set()

    def _on_update_startup(self, var, index, mode):  # pylint: disable=unused-argument
        """
        Action when check on startup flag updated.
        """

        self.__app.configuration.set(
            "checkforupdate_b", int(self._checkonstartup.get())
        )

    def _on_github(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Close dialog and go to GitHub.
        """

        if brew_installed():
            self.status_label = (BREWWARN, INFOCOL)
            return

        open_new_tab(GITHUB_URL)
        self.on_exit()

    def _on_sponsor(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Close dialog and go to Sponsor website.
        """

        if brew_installed():
            self.status_label = (BREWWARN, INFOCOL)
            return

        open_new_tab(SPONSOR_URL)
        self.on_exit()

    def _on_license(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Close dialog and go to GitHub LICENSE file.
        """

        if brew_installed():
            self.status_label = (BREWWARN, INFOCOL)
            return

        open_new_tab(LICENSE_URL)
        self.on_exit()

    def _check_for_update(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Check for updates.
        """

        versions = check_for_updates()
        self.status_label = ("Checking for updates...", INFOCOL)
        for i, (nam, current, latest) in enumerate(versions):
            txt = f"{nam}: {current}"
            if latest == current:
                txt += " ✓"
                col = OKCOL
            elif latest == NA:
                txt += " - Info not available!"
                col = ERRCOL
            else:
                txt += f" - Latest version is {latest}"
                col = ERRCOL
            self._lbl_lib_versions[i].config(text=txt, fg=col)

        updates = [nam for (nam, current, latest) in versions if latest != current]
        if len(updates) > 0:
            self.status_label = ("Updates available", OKCOL)
            self._set_update_btn_mode(True)
        else:
            self.status_label = ("No updates available", INFOCOL)

    def _do_update(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Run python update.
        """

        if brew_installed():
            self.status_label = (BREWUPDATE, INFOCOL)
            return

        self.status_label = (UPDATEINPROG, INFOCOL)
        rc = self.__app.do_app_update()
        if rc:
            self.status_label = (UPDATERESTART, OKCOL)
        else:
            self.status_label = (UPDATEERR.format(err=rc), ERRCOL)
        self._set_update_btn_mode(False)

    def _set_update_btn_mode(self, update: bool):
        """
        Set Check for update button label and binding.

        :param bool update: False = check, True = update
        """

        if update:
            self._btn_checkupdate.config(text="UPDATE", fg=OKCOL)
            self._btn_checkupdate.bind("<Button>", self._do_update)
        else:
            self._btn_checkupdate.config(text="CHECK FOR UPDATES", fg=INFOCOL)
            self._btn_checkupdate.bind("<Button>", self._check_for_update)
        self.update_idletasks()
