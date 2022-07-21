"""
Banner frame class for PyGPSClient application.

This handles the top banner which prominently displays the current coordinates and status.

Created on 13 Sep 2020

:author: semuadmin
:copyright: SEMU Consulting © 2020
:license: BSD 3-Clause
"""
# pylint: disable=invalid-name

from platform import system
from tkinter import Frame, Label, Button, StringVar, font, N, S, W, E, SUNKEN
from PIL import ImageTk, Image
from pyubx2 import dop2str
from pygnssutils.helpers import latlon2dms, latlon2dmm
from pygpsclient.globals import (
    DMM,
    DMS,
    UMK,
    UI,
    UIK,
    ICON_CONN,
    ICON_SERIAL,
    ICON_SOCKET,
    ICON_DISCONN,
    ICON_LOGREAD,
    ICON_EXPAND,
    ICON_CONTRACT,
    ICON_TRANSMIT,
    ICON_NOTRANSMIT,
    ICON_NOCLIENT,
    CONNECTED,
    CONNECTED_SOCKET,
    CONNECTED_FILE,
    BGCOL,
    FGCOL,
)
from pygpsclient.helpers import (
    m2ft,
    ms2mph,
    ms2kmph,
    ms2knots,
)

DGPSYES = "YES"
DGPSNO = "N/A"


class BannerFrame(Frame):
    """
    Banner frame class.
    """

    def __init__(self, app, *args, **kwargs):
        """
        Constructor.

        :param Frame app: reference to main tkinter application
        :param args: optional args to pass to Frame parent class
        :param kwargs: optional kwargs to pass to Frame parent class
        """

        self.__app = app  # Reference to main application class
        self.__master = self.__app.get_master()  # Reference to root class (Tk)
        Frame.__init__(self, self.__master, *args, **kwargs)

        self._time = StringVar()
        self._lat = StringVar()
        self._lon = StringVar()
        self._alt = StringVar()
        self._speed = StringVar()
        self._alt_u = StringVar()
        self._speed_u = StringVar()
        self._track = StringVar()
        self._dop = StringVar()
        self._hvdop = StringVar()
        self._hvacc = StringVar()
        self._fix = StringVar()
        self._siv = StringVar()
        self._sip = StringVar()
        self._diffcorr = StringVar()
        self._diffstat = StringVar()
        self._status = False
        self._show_advanced = False

        self._bgcol = BGCOL
        self._fgcol = FGCOL
        self.config(bg=self._bgcol)
        self._img_conn = ImageTk.PhotoImage(Image.open(ICON_CONN))
        self._img_serial = ImageTk.PhotoImage(Image.open(ICON_SERIAL))
        self._img_socket = ImageTk.PhotoImage(Image.open(ICON_SOCKET))
        self._img_file = ImageTk.PhotoImage(Image.open(ICON_LOGREAD))
        self._img_disconn = ImageTk.PhotoImage(Image.open(ICON_DISCONN))
        self._img_expand = ImageTk.PhotoImage(Image.open(ICON_EXPAND))
        self._img_contract = ImageTk.PhotoImage(Image.open(ICON_CONTRACT))
        self._img_transmit = ImageTk.PhotoImage(Image.open(ICON_TRANSMIT))
        self._img_notransmit = ImageTk.PhotoImage(Image.open(ICON_NOTRANSMIT))
        self._img_noclient = ImageTk.PhotoImage(Image.open(ICON_NOCLIENT))

        self.width, self.height = self.get_size()

        self._body()
        self._do_layout()
        self._attach_events()

    def _body(self):
        """
        Set up frame and widgets.
        """

        for i in range(2, 5):
            self.grid_columnconfigure(i, weight=1)
            self.grid_rowconfigure(0, weight=1)
            self.grid_rowconfigure(1, weight=1)
        self._frm_connect = Frame(self, bg=BGCOL)
        self._frm_toggle = Frame(self, bg=BGCOL)
        self._frm_basic = Frame(self, bg=BGCOL, relief=SUNKEN)
        self._frm_advanced = Frame(self, bg=BGCOL)

        self.option_add("*Font", self.__app.font_md2)
        self._lbl_ltime = Label(
            self._frm_basic, text="utc:", bg=self._bgcol, fg=self._fgcol, anchor=N
        )
        self._lbl_llat = Label(
            self._frm_basic, text="lat:", bg=self._bgcol, fg=self._fgcol, anchor=N
        )
        self._lbl_llon = Label(
            self._frm_basic, text="lon:", bg=self._bgcol, fg=self._fgcol, anchor=N
        )
        self._lbl_lalt = Label(
            self._frm_basic, text="alt:", bg=self._bgcol, fg=self._fgcol, anchor=N
        )
        self._lbl_lspd = Label(
            self._frm_basic, text="speed:", bg=self._bgcol, fg=self._fgcol, anchor=N
        )
        self._lbl_ltrk = Label(
            self._frm_basic, text="track:", bg=self._bgcol, fg=self._fgcol, anchor=N
        )
        self._btn_toggle = Button(
            self._frm_toggle,
            width=30,
            height=25,
            command=self._toggle_advanced,
            image=self._img_expand,
        )
        self._lbl_lfix = Label(
            self._frm_basic, text="fix:", bg=self._bgcol, fg=self._fgcol, anchor=N
        )
        self._lbl_lsiv = Label(
            self._frm_advanced, text="siv:", bg=self._bgcol, fg=self._fgcol, anchor=N
        )
        self._lbl_lsip = Label(
            self._frm_advanced, text="sip:", bg=self._bgcol, fg=self._fgcol, anchor=N
        )
        self._lbl_lpdop = Label(
            self._frm_advanced, text="pdop:", bg=self._bgcol, fg=self._fgcol, anchor=N
        )
        self._lbl_lacc = Label(
            self._frm_advanced, text="acc:", bg=self._bgcol, fg=self._fgcol, anchor=N
        )
        self._lbl_ldgps = Label(
            self._frm_advanced,
            text="dgps:",
            bg=self._bgcol,
            fg=self._fgcol,
            anchor=N,
        )

        self.option_add("*Font", self.__app.font_lg)
        self._lbl_status_preset = Label(
            self._frm_connect, bg=self._bgcol, image=self._img_conn, fg="blue"
        )
        self._lbl_transmit_preset = Label(
            self._frm_connect,
            bg=self._bgcol,
            image=self._img_notransmit,
            text="0",
            fg="grey",
        )
        self._lbl_time = Label(
            self._frm_basic, textvariable=self._time, bg=self._bgcol, fg="cyan"
        )
        self._lbl_lat = Label(
            self._frm_basic, textvariable=self._lat, bg=self._bgcol, fg="orange"
        )
        self._lbl_lon = Label(
            self._frm_basic, textvariable=self._lon, bg=self._bgcol, fg="orange"
        )
        self._lbl_alt = Label(
            self._frm_basic, textvariable=self._alt, bg=self._bgcol, fg="orange"
        )
        self._lbl_spd = Label(
            self._frm_basic, textvariable=self._speed, bg=self._bgcol, fg="deepskyblue"
        )
        self._lbl_trk = Label(
            self._frm_basic, textvariable=self._track, bg=self._bgcol, fg="deepskyblue"
        )
        self._lbl_fix = Label(
            self._frm_basic, textvariable=self._fix, bg=self._bgcol, fg="white"
        )
        self._lbl_siv = Label(
            self._frm_advanced, textvariable=self._siv, bg=self._bgcol, fg="yellow"
        )
        self._lbl_sip = Label(
            self._frm_advanced, textvariable=self._sip, bg=self._bgcol, fg="yellow"
        )
        self._lbl_pdop = Label(
            self._frm_advanced,
            textvariable=self._dop,
            bg=self._bgcol,
            fg="mediumpurple2",
        )
        self._lbl_diffcorr = Label(
            self._frm_advanced,
            textvariable=self._diffcorr,
            bg=self._bgcol,
            fg="mediumpurple2",
        )

        self.option_add("*Font", self.__app.font_sm)
        self._lbl_lalt_u = Label(
            self._frm_basic,
            textvariable=self._alt_u,
            bg=self._bgcol,
            fg="orange",
            anchor=S,
        )
        self._lbl_lspd_u = Label(
            self._frm_basic,
            textvariable=self._speed_u,
            bg=self._bgcol,
            fg="deepskyblue",
            anchor=S,
        )
        self._lbl_hvdop = Label(
            self._frm_advanced,
            textvariable=self._hvdop,
            bg=self._bgcol,
            fg="mediumpurple2",
        )
        self._lbl_hvacc = Label(
            self._frm_advanced,
            textvariable=self._hvacc,
            bg=self._bgcol,
            fg="aquamarine2",
        )
        self._lbl_lacc_u = Label(
            self._frm_advanced,
            textvariable=self._alt_u,
            bg=self._bgcol,
            fg="aquamarine2",
            anchor=N,
        )
        self._lbl_diffstat = Label(
            self._frm_advanced,
            textvariable=self._diffstat,
            bg=self._bgcol,
            fg="mediumpurple2",
        )

    def _do_layout(self):
        """
        Position widgets in frame.
        """

        self._lbl_status_preset.grid(column=0, row=0, padx=8, pady=3, sticky=W)
        self._lbl_transmit_preset.grid(column=1, row=0, padx=8, pady=3, sticky=W)
        self._lbl_ltime.grid(column=1, row=0, pady=3, sticky=W)
        self._lbl_time.grid(column=2, row=0, pady=3, sticky=W)
        self._lbl_llat.grid(column=3, row=0, pady=3, sticky=W)
        self._lbl_lat.grid(column=4, row=0, pady=3, sticky=W)
        self._lbl_llon.grid(column=5, row=0, pady=3, sticky=W)
        self._lbl_lon.grid(column=6, row=0, pady=3, sticky=W)
        self._lbl_lalt.grid(column=7, row=0, pady=3, sticky=W)
        self._lbl_alt.grid(column=8, row=0, pady=3, sticky=W)
        self._lbl_lalt_u.grid(column=9, row=0, pady=0, sticky=W)
        self._lbl_lspd.grid(column=10, row=0, pady=3, sticky=W)
        self._lbl_spd.grid(column=11, row=0, pady=3, sticky=W)
        self._lbl_lspd_u.grid(column=12, row=0, pady=0, sticky=W)
        self._lbl_ltrk.grid(column=13, row=0, pady=3, sticky=W)
        self._lbl_trk.grid(column=14, row=0, pady=3, sticky=W)
        self._lbl_lfix.grid(column=15, row=0, pady=3, sticky=W)
        self._lbl_fix.grid(column=16, row=0, pady=3, sticky=W)

        self._lbl_lsiv.grid(column=0, row=0, pady=3, sticky=W)
        self._lbl_siv.grid(column=1, row=0, pady=3, sticky=W)
        self._lbl_lsip.grid(column=2, row=0, pady=3, sticky=W)
        self._lbl_sip.grid(column=3, row=0, pady=3, sticky=W)
        self._lbl_lpdop.grid(column=4, row=0, pady=3, sticky=W)
        self._lbl_pdop.grid(column=5, row=0, pady=3, sticky=W)
        self._lbl_hvdop.grid(column=6, row=0, pady=0, sticky=W)
        self._lbl_lacc.grid(column=7, row=0, pady=3, sticky=W)
        self._lbl_hvacc.grid(column=8, row=0, pady=0, sticky=W)
        self._lbl_lacc_u.grid(column=9, row=0, pady=0, sticky=W)
        self._lbl_ldgps.grid(column=10, row=0, pady=3, sticky=W)
        self._lbl_diffcorr.grid(column=11, row=0, pady=3, sticky=W)
        self._lbl_diffstat.grid(column=12, row=0, pady=3, sticky=W)

        self._btn_toggle.grid(column=0, row=0, padx=8, pady=3, sticky=(N, E))

        self._toggle_advanced()

    def _toggle_advanced(self):
        """
        Toggle advanced banner frame on or off.
        """

        self._frm_connect.grid(
            column=0, row=0, rowspan=2, pady=3, ipadx=3, ipady=3, sticky=(N, W)
        )
        self._frm_basic.grid(column=1, row=0, pady=3, sticky=(W))
        self._frm_toggle.grid(column=5, row=0, rowspan=2, pady=3, sticky=(N, E))
        self._show_advanced = not self._show_advanced
        if self._show_advanced:
            self._frm_advanced.grid(column=1, row=1, pady=3, sticky=(W))
            self._btn_toggle.config(image=self._img_contract)
        else:
            self._frm_advanced.grid_forget()
            self._btn_toggle.config(image=self._img_expand)

    def _attach_events(self):
        """
        Bind events to frame.
        """

        self.bind("<Configure>", self._on_resize)

    def update_conn_status(self, status: int):
        """
        Update connection status icon

        :param int status: connection status as integer (0,1,2)
        """

        if status == CONNECTED:
            self._lbl_status_preset.configure(image=self._img_serial)
        elif status == CONNECTED_SOCKET:
            self._lbl_status_preset.configure(image=self._img_socket)
        elif status == CONNECTED_FILE:
            self._lbl_status_preset.configure(image=self._img_file)
        else:
            self._lbl_status_preset.configure(image=self._img_disconn)

    def update_transmit_status(self, transmit: int = 1):
        """
        Update socket server status icon

        :param int transmit: socket server transmit status (-1, 0, 1)
        """

        if transmit > 0:
            self._lbl_transmit_preset.configure(image=self._img_transmit)
        elif transmit == 0:
            self._lbl_transmit_preset.configure(image=self._img_noclient)
        else:
            self._lbl_transmit_preset.configure(image=self._img_notransmit)

    def update_banner(self):
        """
        Sets text of banner from GNSSStatus object.
        """

        disp_format = self.__app.frm_settings.format
        units = self.__app.frm_settings.units

        self._update_time()
        self._update_pos(disp_format, units)
        self._update_track(units)
        self._update_fix()
        self._update_siv()
        self._update_dop(units)
        self._update_dgps()

    def _update_time(self):
        """
        Update GNSS time of week
        """

        tim = self.__app.gnss_status.utc
        if tim in (None, ""):
            self._time.set("N/A")
        else:
            self._time.set(tim)

    def _update_pos(self, disp_format, units):
        """
        Update position

        :param str disp_format: degrees display format as string (DMS, DMM, DDD)
        :param str units: distance units as string (UMM, UMK, UI, UIK)
        """

        lat = self.__app.gnss_status.lat
        lon = self.__app.gnss_status.lon
        if isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
            if disp_format == DMS:
                lat, lon = latlon2dms((lat, lon))
            elif disp_format == DMM:
                lat, lon = latlon2dmm((lat, lon))
            self._lat.set(f"{lat:<15}")
            self._lon.set(f"{lon:<15}")
        else:
            self._lat.set("N/A            ")
            self._lon.set("N/A            ")

        alt = self.__app.gnss_status.alt
        alt_u = "m"
        if isinstance(alt, (int, float)):
            if units in (UI, UIK):
                alt = m2ft(alt)
                alt_u = "ft"
            self._alt.set(f"{alt:.3f}")
            self._alt_u.set(f"{alt_u:<2}")
        else:
            self._alt.set("N/A  ")
            self._alt_u.set("  ")

    def _update_track(self, units):
        """
        Update track and ground speed

        :param str units: distance units as string (UMM, UMK, UI, UIK)
        """

        speed = self.__app.gnss_status.speed
        speed_u = "m/s"
        if isinstance(speed, (int, float)):
            if units == UI:
                speed = ms2mph(speed)
                speed_u = "mph"
            elif units == UIK:
                speed = ms2knots(speed)
                speed_u = "knots"
            elif units == UMK:
                speed = ms2kmph(speed)
                speed_u = "kmph"
            self._speed.set(f"{speed:.2f}")
            self._speed_u.set(f"{speed_u:<5}")
        else:
            self._speed.set("N/A")
            self._speed.set("")
        track = self.__app.gnss_status.track
        if isinstance(track, (int, float)):
            self._track.set(f"{track:05.1f}")
        else:
            self._track.set("N/A  ")

    def _update_fix(self):
        """
        Update fix type
        """

        fix = self.__app.gnss_status.fix
        if fix in ("3D", "GNSS+DR", "RTK", "RTK FIXED", "RTK FLOAT"):
            self._lbl_fix.config(fg="green2")
        elif fix in ("2D", "DR"):
            self._lbl_fix.config(fg="orange")
        else:
            self._lbl_fix.config(fg="red")
        self._fix.set(fix)

    def _update_siv(self, **kwargs):
        """
        Update siv and sip
        """

        self._siv.set(f"{self.__app.gnss_status.siv:02d}")
        self._sip.set(f"{self.__app.gnss_status.sip:02d}")

    def _update_dop(self, units, **kwargs):
        """
        Update precision and accuracy

        :param str units: distance units as string (UMM, UMK, UI, UIK)
        """

        pdop = self.__app.gnss_status.pdop
        self._dop.set(f"{pdop:.2f} {dop2str(pdop):<9}")
        self._hvdop.set(
            f"hdop {self.__app.gnss_status.hdop:.2f}\nvdop {self.__app.gnss_status.vdop:.2f}"
        )
        if units in (UI, UIK):
            self._hvacc.set(
                f"hacc {m2ft(self.__app.gnss_status.hacc):.3f}\nvacc {m2ft(self.__app.gnss_status.vacc):.3f}"
            )
        else:
            self._hvacc.set(
                f"hacc {self.__app.gnss_status.hacc:.3f}\nvacc {self.__app.gnss_status.vacc:.3f}"
            )

    def _update_dgps(self):
        """
        Update DGPS status.
        """

        self._diffcorr.set(DGPSYES if self.__app.gnss_status.diff_corr else DGPSNO)
        if self.__app.gnss_status.diff_corr:
            age = self.__app.gnss_status.diff_age
            station = self.__app.gnss_status.diff_station
            if age in [None, "", 0]:
                age = "N/A"
            else:
                age = f"{age} s"
            if station in [None, "", 0]:
                station = "N/A"
            self._diffstat.set(f"age {age}\nstation {station}")
        else:
            self._diffstat.set("")

    def _set_fontsize(self):
        """
        Adjust font sizes according to frame size
        """

        w = self.width
        # Cater for slightly different font behaviour on Linux
        if system() in ("W32", "Darwin"):
            val = 55
            lbl = 75
            sup = 85
        else:
            val = 75  # 70
            lbl = 90  # 85
            sup = 100  # 95

        sz = min(int(w / val), 18)
        for ctl in (
            self._lbl_status_preset,
            self._lbl_time,
            self._lbl_lat,
            self._lbl_lon,
            self._lbl_alt,
            self._lbl_spd,
            self._lbl_trk,
            self._lbl_pdop,
            self._lbl_fix,
            self._lbl_sip,
            self._lbl_siv,
            self._lbl_diffcorr,
        ):
            ctl.config(font=font.Font(size=sz))

        sz = min(int(w / lbl), 14)
        for ctl in (
            self._lbl_ltime,
            self._lbl_llat,
            self._lbl_llon,
            self._lbl_lalt,
            self._lbl_lspd,
            self._lbl_ltrk,
            self._lbl_lpdop,
            self._lbl_lfix,
            self._lbl_lsip,
            self._lbl_lsiv,
            self._lbl_lacc,
            self._lbl_ldgps,
        ):
            ctl.config(font=font.Font(size=sz))

        sz = min(int(w / sup), 12)
        for ctl in (
            self._lbl_lalt_u,
            self._lbl_lspd_u,
            self._lbl_hvdop,
            self._lbl_hvacc,
            self._lbl_diffstat,
        ):
            ctl.config(font=font.Font(size=sz))

    def _on_resize(self, event):  # pylint: disable=unused-argument
        """
        Resize frame

        :param event event: resize event
        """

        self.width, self.height = self.get_size()
        self._set_fontsize()

    def get_size(self):
        """
        Get current frame size.

        :return: window size (width, height)
        :rtype: tuple
        """

        self.update_idletasks()  # Make sure we know about any resizing
        width = self.winfo_width()
        height = self.winfo_height()
        return (width, height)
