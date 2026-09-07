"""
app_config_dialog.py

App Configuration setting dialog.

Created on 27 Aug 2026

:author: semuadmin (Steve Smith)
:copyright: 2020 semuadmin
:license: BSD 3-Clause
"""

# pylint: disable=unused-argument

from tkinter import (
    DISABLED,
    EW,
    NORMAL,
    NSEW,
    BooleanVar,
    Button,
    Checkbutton,
    E,
    Entry,
    Frame,
    Label,
    Spinbox,
    StringVar,
    Tk,
    W,
)

from PIL import Image, ImageTk

from pygpsclient.globals import (
    CLICK_CURSOR,
    ERRCOL,
    ICON_SAVE,
    ICON_SAVE_DISABLED,
    INFOCOL,
    OKCOL,
    READONLY,
    TRACEMODE_WRITE,
)
from pygpsclient.helpers import (  # pylint: disable=unused-import
    PasswordButton,
    trace_update,
)
from pygpsclient.strings import DLGGUIOPTIONS
from pygpsclient.toplevel_dialog import ToplevelDialog

GUI_INTERVALS = (
    "100",
    "200",
    "300",
    "400",
    "500",
    "750",
    "1000",
    "2000",
    "5000",
    "10000",
)
MAP_INTERVALS = ("1", "2", "5", "10", "30", "60", "120", "240", "360")
LOG_SIZES = ("1", "2", "5", "10", "20", "50", "100", "200", "500", "1000")
PLOT_CHANS = [str(i) for i in range(4, 21, 2)]


class AppConfigDialog(ToplevelDialog):
    """
    App Configuration Options panel.
    """

    def __init__(self, app: Tk, *args, **kwargs):
        """
        Constructor.

        :param Tk app: reference to main tkinter application
        :param args: optional args to pass to Frame parent class
        :param kwargs: optional kwargs to pass to Frame parent class
        """

        self.__app = app
        super().__init__(app, DLGGUIOPTIONS)
        self.width = int(kwargs.get("width", 600))
        self.height = int(kwargs.get("height", 300))
        self._img_save = ImageTk.PhotoImage(Image.open(ICON_SAVE))
        self._img_save_disabled = ImageTk.PhotoImage(Image.open(ICON_SAVE_DISABLED))
        self._guirefresh = StringVar()
        self._maprefresh = StringVar()
        self._mapkey = StringVar()
        self._logsize = StringVar()
        self._plotchans = StringVar()
        self._resizedialog = BooleanVar()
        self._transientdialog = BooleanVar()

        self._body()
        self._do_layout()
        self._reset()
        self._attach_events()
        self._finalise()

    def _body(self):
        """
        Set up frame and widgets.
        """

        self._frm_body = Frame(self.container)
        self._lbl_guirefresh = Label(
            self._frm_body, text="GUI Refresh Interval", anchor=W
        )
        self._lbl_guirefreshu = Label(self._frm_body, text="ms", anchor=W)
        self._spn_guirefresh = Spinbox(
            self._frm_body,
            values=GUI_INTERVALS,
            width=6,
            state=READONLY,
            wrap=True,
            textvariable=self._guirefresh,
        )
        self._lbl_maprefresh = Label(
            self._frm_body, text="MapQuest Refresh Interval", anchor=W
        )
        self._lbl_maprefreshu = Label(self._frm_body, text="s", anchor=W)
        self._spn_maprefresh = Spinbox(
            self._frm_body,
            values=MAP_INTERVALS,
            width=6,
            state=READONLY,
            wrap=True,
            textvariable=self._maprefresh,
        )
        self._frm_mapkey = Frame(self._frm_body)
        self._lbl_mapkey = Label(self._frm_mapkey, text="MapQuest API Key", anchor=W)
        self._ent_mapkey = Entry(
            self._frm_body,
            width=35,
            textvariable=self._mapkey,
            show="*",
        )
        self._btn_mapkey = PasswordButton(self._frm_mapkey, self._ent_mapkey)
        self._lbl_logsize = Label(
            self._frm_body, text="Datalog Max File Size", anchor=W
        )
        self._lbl_logsizeu = Label(self._frm_body, text="MB", anchor=W)
        self._spn_logsize = Spinbox(
            self._frm_body,
            values=LOG_SIZES,
            width=6,
            state=READONLY,
            wrap=True,
            textvariable=self._logsize,
        )
        self._lbl_plotchans = Label(
            self._frm_body, text="Chart Plotter Channels", anchor=W
        )
        self._spn_plotchans = Spinbox(
            self._frm_body,
            values=PLOT_CHANS,
            width=6,
            state=READONLY,
            wrap=True,
            textvariable=self._plotchans,
        )
        self._lbl_resizedialog = Label(
            self._frm_body, text="Resizeable TopLevel Dialogs", anchor=W
        )
        self._chk_resizedialog = Checkbutton(
            self._frm_body,
            text="",
            variable=self._resizedialog,
        )
        self._lbl_transientdialog = Label(
            self._frm_body, text="Transient TopLevel Dialogs", anchor=W
        )
        self._chk_transientdialog = Checkbutton(
            self._frm_body,
            text="",
            variable=self._transientdialog,
        )
        self._btn_save = Button(
            self._frm_body,
            command=self._on_save_updates,
            image=self._img_save_disabled,
            width=45,
        )

    def _do_layout(self):
        """
        Layout widgets.
        """

        self._frm_body.grid(column=0, row=0, sticky=NSEW)
        self._lbl_guirefresh.grid(column=0, row=0, sticky=W)
        self._spn_guirefresh.grid(column=1, row=0, sticky=W)
        self._lbl_guirefreshu.grid(column=2, row=0, padx=2, sticky=W)
        self._lbl_maprefresh.grid(column=0, row=1, sticky=W)
        self._spn_maprefresh.grid(column=1, row=1, sticky=W)
        self._lbl_maprefreshu.grid(column=2, row=1, padx=2, sticky=W)
        self._lbl_logsize.grid(column=0, row=2, sticky=W)
        self._spn_logsize.grid(column=1, row=2, sticky=W)
        self._lbl_logsizeu.grid(column=2, row=2, padx=2, sticky=W)
        self._lbl_plotchans.grid(column=0, row=3, sticky=W)
        self._spn_plotchans.grid(column=1, row=3, sticky=W)
        self._frm_mapkey.grid(column=0, row=4, sticky=EW)
        self._lbl_mapkey.grid(column=0, row=0, sticky=W)
        self._btn_mapkey.grid(column=1, row=0, sticky=E)
        self._ent_mapkey.grid(column=1, row=4, columnspan=2, sticky=EW)
        self._lbl_resizedialog.grid(column=0, row=5, sticky=W)
        self._chk_resizedialog.grid(column=1, row=5, columnspan=2, sticky=W)
        self._lbl_transientdialog.grid(column=0, row=6, sticky=W)
        self._chk_transientdialog.grid(column=1, row=6, columnspan=2, sticky=W)
        self._btn_save.grid(column=1, row=7, columnspan=2, padx=4, pady=3, sticky=E)
        self._frm_body.columnconfigure(2, weight=1)

    def _attach_events(self):
        """
        Bind events to window.
        """

        self.container.bind("<Configure>", self._on_resize)
        for var in (
            self._guirefresh,
            self._maprefresh,
            self._logsize,
            self._plotchans,
            self._resizedialog,
            self._transientdialog,
            self._mapkey,
        ):
            var.trace_update(TRACEMODE_WRITE, self._on_update, True)

    def _reset(self):
        """
        Reset panel to initial settings
        """

        self._guirefresh.set(
            int(self.__app.configuration.get("guiupdateinterval_f") * 1000)
        )
        self._maprefresh.set(self.__app.configuration.get("mapupdateinterval_n"))
        self._logsize.set(int(self.__app.configuration.get("logsize_n") / 1048576))
        self._plotchans.set(
            int(self.__app.configuration.get("chartsettings_d")["numchn_n"])
        )
        self._mapkey.set(self.__app.configuration.get("mqapikey_s"))
        self._resizedialog.set(int(self.__app.configuration.get("resizeable_dialog_b")))
        self._transientdialog.set(
            int(self.__app.configuration.get("transient_dialog_b"))
        )
        self._enable_save_button(False)
        self.set_status_label("Update with caution! Restart after updating", ERRCOL)

    def _on_update(self, var, index, mode):
        """
        Setting has been updated.
        """

        updates = (
            (
                self.__app.configuration.get("guiupdateinterval_f")
                != float(self._guirefresh.get()) / 1000
            )
            | (
                self.__app.configuration.get("mapupdateinterval_n")
                != int(self._maprefresh.get())
            )
            | (
                self.__app.configuration.get("logsize_n")
                != int(self._logsize.get()) * 1048576
            )
            | (
                self.__app.configuration.get("chartsettings_d")["numchn_n"]
                != int(self._plotchans.get())
            )
            | (self.__app.configuration.get("mqapikey_s") != self._mapkey.get())
            | (
                self.__app.configuration.get("resizeable_dialog_b")
                != int(self._resizedialog.get())
            )
            | (
                self.__app.configuration.get("transient_dialog_b")
                != int(self._transientdialog.get())
            )
        )
        msg = "Settings updated" if updates else ""
        if int(self._maprefresh.get()) < 60:
            msg += ". Check MapQuest Fees!"
        self._enable_save_button(updates)
        self.set_status_label(msg, INFOCOL)

    def _enable_save_button(self, enabled: bool):
        """
        Enable or disable save button.

        :param bool enabled: enabled state
        """

        if enabled:
            state = NORMAL
            cursor = CLICK_CURSOR
            image = self._img_save
        else:
            state = DISABLED
            cursor = ""
            image = self._img_save_disabled
        self._btn_save["state"] = state
        self._btn_save["cursor"] = cursor
        self._btn_save["image"] = image

    def _on_save_updates(self):
        """
        Save updated values to configuration file.
        """

        self.__app.configuration.set(
            "guiupdateinterval_f", float(self._guirefresh.get()) / 1000
        )
        self.__app.configuration.set("mapupdateinterval_n", int(self._maprefresh.get()))
        self.__app.configuration.set("logsize_n", int(self._logsize.get()) * 1048576)
        chartsettings = self.__app.configuration.get("chartsettings_d")
        self.__app.configuration.set(
            "chartsettings_d",
            {
                "numchn_n": int(self._plotchans.get()),
                "timrng_n": chartsettings["timrng_n"],
                "maxpoints_n": chartsettings["maxpoints_n"],
            },
        )
        self.__app.configuration.set("mqapikey_s", self._mapkey.get())
        self.__app.configuration.set(
            "resizeable_dialog_b", int(self._resizedialog.get())
        )
        self.__app.configuration.set(
            "transient_dialog_b", int(self._transientdialog.get())
        )
        self.set_status_label("Save configuration to file and restart", OKCOL)
        if self.__app.save_config() != "":
            self.set_status_label("Save cancelled", INFOCOL)
        else:
            self.set_status_label("Restart app", OKCOL)
            self._enable_save_button(False)
