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
from tkinter import (
    CENTER,
    EW,
    NSEW,
    Button,
    Checkbutton,
    Frame,
    IntVar,
    Label,
    Tcl,
    ttk,
)
from webbrowser import open_new_tab

from PIL import Image, ImageTk

from pygpsclient.globals import (
    CLICK_CURSOR,
    ERRCOL,
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

        :param Tk app: reference to main tkinter application
        """

        self.__app = app  # Reference to main application class
        self.logger = logging.getLogger(__name__)
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
        self._lbl_desc = Label(
            self._frm_body,
            text=ABOUTTXT,
            wraplength=400,
            justify=CENTER,
            anchor=CENTER,
        )
        self._lbl_github = Label(
            self._frm_body,
            text=GITHUB_URL,
            foreground=INFOCOL,
            cursor=CLICK_CURSOR,
            anchor=CENTER,
        )
        tkv = Tcl().call("info", "patchlevel")
        self._lbl_python_version = Label(
            self._frm_body,
            text=(
                f"Arch: {machine()}  "
                f"Python: {python_version()}  Tk: {tkv}  "
                f"Spatial: {SQLSTATUS[self.__app.db_enabled]}"
            ),
            anchor=CENTER,
        )
        self._lbl_lib_versions = []
        for nam, ver in LIBVERSIONS.items():
            self._lbl_lib_versions.append(
                Label(
                    self._frm_body,
                    text=f"{nam}: {ver}",
                    anchor=CENTER,
                    border=0,
                    highlightthickness=0,
                )
            )
        self._btn_checkupdate = Button(
            self._frm_body,
            text="",
            width=16,
            cursor=CLICK_CURSOR,
        )
        self._chk_checkupdate = Checkbutton(
            self._frm_body,
            text="Check on startup",
            variable=self._checkonstartup,
        )
        self._lbl_sponsoricon = Label(
            self._frm_body,
            image=self._img_sponsor,
            cursor=CLICK_CURSOR,
            anchor=CENTER,
        )
        self._lbl_copyright = Label(
            self._frm_body,
            text=COPYRIGHT,
            foreground=INFOCOL,
            cursor=CLICK_CURSOR,
            anchor=CENTER,
        )

    def _do_layout(self):
        """
        Arrange widgets in dialog.
        """

        self._frm_body.grid(column=0, row=0, ipadx=2, ipady=2, sticky=NSEW)
        self._lbl_desc.grid(column=0, row=1, columnspan=2, padx=3, pady=0, sticky=EW)
        self._lbl_github.grid(column=0, row=2, columnspan=2, padx=3, pady=0, sticky=EW)
        ttk.Separator(self._frm_body).grid(
            column=0, row=3, columnspan=2, padx=3, pady=3, sticky=EW
        )
        self._lbl_python_version.grid(
            column=0, row=4, columnspan=2, padx=3, pady=1, sticky=EW
        )
        for i, lbl in enumerate(self._lbl_lib_versions):
            lbl.grid(column=0, row=5 + i, columnspan=2, padx=2, pady=0, sticky=EW)
        lv = len(self._lbl_lib_versions)
        self._btn_checkupdate.grid(
            column=0, row=6 + lv, ipadx=3, ipady=3, padx=3, pady=3
        )
        self._chk_checkupdate.grid(
            column=1, row=6 + lv, ipadx=3, ipady=3, padx=3, pady=3
        )
        ttk.Separator(self._frm_body).grid(
            column=0, row=7 + lv, columnspan=2, padx=3, pady=3, sticky=EW
        )
        self._lbl_sponsoricon.grid(
            column=0, row=8 + lv, columnspan=2, padx=3, pady=3, sticky=EW
        )
        self._lbl_copyright.grid(
            column=0, row=9 + lv, columnspan=2, padx=3, pady=3, sticky=EW
        )

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
            self.set_status_label(BREWWARN, INFOCOL)
            return

        open_new_tab(GITHUB_URL)
        self.on_exit()

    def _on_sponsor(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Close dialog and go to Sponsor website.
        """

        if brew_installed():
            self.set_status_label(BREWWARN, INFOCOL)
            return

        open_new_tab(SPONSOR_URL)
        self.on_exit()

    def _on_license(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Close dialog and go to GitHub LICENSE file.
        """

        if brew_installed():
            self.set_status_label(BREWWARN, INFOCOL)
            return

        open_new_tab(LICENSE_URL)
        self.on_exit()

    def _check_for_update(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Check for updates.
        """

        self.set_status_label("Checking for updates...", INFOCOL)
        versions = check_for_updates()
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
            self._lbl_lib_versions[i]["text"] = txt
            self._lbl_lib_versions[i]["foreground"] = col
        updates = [nam for (nam, current, latest) in versions if latest != current]
        if len(updates) > 0:
            self.set_status_label("Updates available", OKCOL)
            self._set_update_btn_mode(True)
        else:
            self.set_status_label("No updates available", INFOCOL)

    def _do_update(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Run python update.
        """

        if brew_installed():
            self.set_status_label(BREWUPDATE, INFOCOL)
            return

        self.set_status_label(UPDATEINPROG, INFOCOL)
        rc = self.__app.do_app_update()
        if rc:
            self.set_status_label(UPDATERESTART, OKCOL)
        else:
            self.set_status_label(UPDATEERR.format(err=rc), ERRCOL)
        self._set_update_btn_mode(False)

    def _set_update_btn_mode(self, update: bool):
        """
        Set Check for update button label and binding.

        :param bool update: False = check, True = update
        """

        if update:
            self._btn_checkupdate["text"] = "UPDATE"
            self._btn_checkupdate["foreground"] = OKCOL
            self._btn_checkupdate.bind("<Button>", self._do_update)
        else:
            self._btn_checkupdate["text"] = "CHECK FOR UPDATES"
            self._btn_checkupdate["foreground"] = INFOCOL
            self._btn_checkupdate.bind("<Button>", self._check_for_update)
        self.__app.update_idletasks()
