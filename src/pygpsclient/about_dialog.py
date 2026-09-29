"""
about_dialog.py

About Dialog Box class for PyGPSClient application.

Includes functionality to display system information and
check for Python application package updates.

Created on 20 Sep 2020

:author: semuadmin (Steve Smith)
:copyright: 2020 semuadmin
:license: BSD 3-Clause
"""

import logging
from datetime import datetime
from platform import python_version, uname
from tkinter import (
    CENTER,
    DISABLED,
    EW,
    NONE,
    NORMAL,
    NSEW,
    Button,
    Checkbutton,
    Frame,
    IntVar,
    Label,
    N,
    S,
    Tcl,
    W,
    ttk,
)
from webbrowser import open_new_tab

from PIL import Image, ImageTk

from pygpsclient.custom_classes import ScrollableText
from pygpsclient.globals import (
    CLICK_CURSOR,
    ERRCOL,
    FONT_FIXED,
    ICON_APP128,
    ICON_CLIPBOARD,
    ICON_INFO,
    ICON_SPONSOR,
    ICON_UPDATE,
    INFOCOL,
    LICENSE_URL,
    OKCOL,
    SPONSOR_URL,
    TRACEMODE_WRITE,
)
from pygpsclient.helpers import (
    brew_installed,
    check_for_updates,
    secs2unit,
)
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

try:
    from sys import _is_gil_enabled

    IGE = True
except ImportError:
    IGE = False

NSW = (N, S, W)


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
        self._img_icon = ImageTk.PhotoImage(Image.open(ICON_APP128).resize((64, 64)))
        self._img_clipboard = ImageTk.PhotoImage(Image.open(ICON_CLIPBOARD))
        self._img_info = ImageTk.PhotoImage(Image.open(ICON_INFO))
        self._img_sponsor = ImageTk.PhotoImage(Image.open(ICON_SPONSOR))
        self._img_update = ImageTk.PhotoImage(Image.open(ICON_UPDATE))
        self._checkonstartup = IntVar()
        self._checkonstartup.set(self.__app.configuration.get("checkforupdate_b"))
        self._sysinfo = ""
        self._updates_available = False

        super().__init__(app, DLGTABOUT)

        self._body()
        self._do_layout()
        self._attach_events()
        self._finalise()
        self.after(50, self._reset)

    def _body(self):
        """
        Set up widgets.
        """

        self._frm_body = Frame(self.container)
        self._lbl_icon = Label(
            self._frm_body,
            image=self._img_icon,
            borderwidth=0,
            anchor=CENTER,
        )
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
        self.frm_sysinfo = ScrollableText(
            self.__app,
            self,
            self._frm_body,
            font=FONT_FIXED,
            state=DISABLED,
            wrap=NONE,
            height=10,
            width=53,
        )
        self._btn_info = Button(
            self._frm_body,
            image=self._img_info,
            width=16,
            cursor=CLICK_CURSOR,
            command=self._reset,
        )
        self._btn_update = Button(
            self._frm_body,
            image=self._img_update,
            width=16,
            command=self._on_update,
            state=DISABLED,
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
        self._lbl_icon.grid(column=0, row=0, columnspan=4, padx=3, pady=0, sticky=EW)
        self._lbl_desc.grid(column=0, row=1, columnspan=4, padx=3, pady=0, sticky=EW)
        self._lbl_github.grid(column=0, row=2, columnspan=4, padx=3, pady=0, sticky=EW)
        ttk.Separator(self._frm_body).grid(
            column=0, row=3, columnspan=4, padx=3, pady=3, sticky=EW
        )
        self.frm_sysinfo.grid(column=0, row=4, columnspan=3, sticky=NSEW)
        self._btn_info.grid(column=0, row=6, ipadx=3, ipady=3, padx=3, pady=3)
        self._btn_update.grid(column=1, row=6, ipadx=3, ipady=3, padx=3, pady=3)
        self._chk_checkupdate.grid(column=2, row=6, ipadx=3, ipady=3, padx=3, pady=3)
        ttk.Separator(self._frm_body).grid(
            column=0, row=7, columnspan=4, padx=3, pady=3, sticky=EW
        )
        self._lbl_sponsoricon.grid(
            column=0, row=8, columnspan=4, padx=3, pady=3, sticky=EW
        )
        self._lbl_copyright.grid(
            column=0, row=9, columnspan=4, padx=3, pady=3, sticky=EW
        )

    def _attach_events(self):
        """
        Bind events to dialog.
        """

        self._lbl_github.bind("<Button>", self._on_github)
        self._lbl_sponsoricon.bind("<Button>", self._on_sponsor)
        self._lbl_copyright.bind("<Button>", self._on_license)
        self._btn_info.bind("<Enter>", self._on_info_enter)
        self._btn_info.bind("<Leave>", self._on_info_leave)
        self._btn_update.bind("<Enter>", self._on_update_enter)
        self._btn_update.bind("<Leave>", self._on_update_leave)
        self._checkonstartup.trace_add(TRACEMODE_WRITE, self._on_update_startup)
        self._btn_exit.focus_set()

    def _reset(self):
        """
        Refresh system information.
        """

        self._refresh_sysinfo()
        self._btn_update["state"] = NORMAL if self._updates_available else DISABLED
        self.frm_sysinfo.state(True)
        self.frm_sysinfo.set(self._sysinfo, insert=0, scroll=0)
        self.frm_sysinfo.state(False)

    def _on_info_enter(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Info button enter (mouseover) event.
        """

        self.set_status_label("Refresh System Info")

    def _on_info_leave(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Info button leave event.
        """

        if not self._updates_available:
            self.set_status_label("")

    def _on_update_enter(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Update button enter (mouseover) event.
        """

        if self._btn_update["state"] == NORMAL:
            self.set_status_label("Update Python Application Package(s)")

    def _on_update_leave(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Update button leave event.
        """

        if self._btn_update["state"] == NORMAL:
            self.set_status_label("")

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

    def _on_update(self):
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

    def _refresh_sysinfo(self):
        """
        Refresh system information.
        """

        self.set_status_label("Refreshing System Info...", INFOCOL)
        sys, nod, rel, ver, mcn, pro = tuple(uname())
        sys = sys.replace("Darwin", "MacOS")
        tki = Tcl().call("info", "patchlevel")
        now = datetime.now()
        runtime, rununit = secs2unit((now - self.__app.starttime).total_seconds())
        versions = check_for_updates()
        self._sysinfo = "Python Application Packages:\n\n"
        self._updates_available = False
        for mod, cver, lver in versions:
            mod = f"{mod}:"
            if lver == NA:
                lts = " ?"
            elif lver == cver:
                lts = " ✓"
            else:
                self._updates_available = True
                lts = f" Update Available: {lver:<6}"
            self._sysinfo += f"{mod:<14}{cver:<6}{lts}\n"
        if IGE:
            gil = "GIL" if _is_gil_enabled() else "free threading"
        else:
            gil = "GIL"
        spl = SQLSTATUS[self.__app.db_enabled]
        hw = self.__app.gnss_status.version_data["hwversion"]
        sw = self.__app.gnss_status.version_data["swversion"]
        fw = self.__app.gnss_status.version_data["fwversion"]
        rom = self.__app.gnss_status.version_data["romversion"]
        self._sysinfo += (
            "\nSystem Information:\n\n"
            f"{'Datetime:':<14}{now}\n"
            f"{'Runtime:':<14}{round(runtime,2)} {rununit}\n"
            f"{'System:':<14}{sys}\n"
            f"{'Node:':<14}{nod}\n"
            f"{'Release:':<14}{rel}\n"
            f"{'Version:':<14}{ver}\n"
            f"{'Machine:':<14}{mcn}\n"
            f"{'Processor:':<14}{pro}\n"
            f"{'Python:':<14}{python_version()} {gil}\n"
            f"{'Tkinter:':<14}{tki}\n"
            f"{'Spatialite:':<14}{spl}\n"
            "\nReceiver Information (if available):\n\n"
            f"{'Hardware:':<14}{hw}\n"
            f"{'Software:':<14}{sw}\n"
            f"{'Firmware:':<14}{fw}\n"
            f"{'Protocol:':<14}{rom}\n"
        )
        if self._updates_available:
            self.set_status_label("Application Update(s) Available", ERRCOL)
            self._btn_update["cursor"] = CLICK_CURSOR
        else:
            self.set_status_label("", INFOCOL)
            self._btn_update["cursor"] = ""
