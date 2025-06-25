"""
banner_frame.py

Banner frame class for PyGPSClient application.

This handles the top banner which prominently displays the current coordinates and status.

Created on 13 Sep 2020

:author: semuadmin
:copyright: 2020 SEMU Consulting
:license: BSD 3-Clause
"""

from tkinter import SUNKEN, Button, E, Frame, Label, N, S, StringVar, W

from PIL import Image, ImageTk
from pynmeagps.nmeahelpers import latlon2dmm, latlon2dms, llh2ecef

from pygpsclient.globals import (
    BGCOL,
    CONNECTED,
    CONNECTED_FILE,
    CONNECTED_NTRIP,
    CONNECTED_SOCKET,
    CONNECTED_SPARTNIP,
    CONNECTED_SPARTNLB,
    DMM,
    DMS,
    ECEF,
    ERRCOL,
    FGCOL,
    ICON_BLANK,
    ICON_CONN,
    ICON_CONTRACT,
    ICON_DISCONN,
    ICON_EXPAND,
    ICON_LOGREAD,
    ICON_NOCLIENT,
    ICON_NTRIPCONFIG,
    ICON_SERIAL,
    ICON_SOCKET,
    ICON_SPARTNCONFIG,
    ICON_TRANSMIT,
    UI,
    UIK,
    UMK,
)
from pygpsclient.helpers import dop2str, m2ft, ms2kmph, ms2knots, ms2mph, scale_font
from pygpsclient.strings import NA

DGPSYES = "YES"
M2MILES = 5280


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
        self.__master = self.__app.appmaster  # Reference to root class (Tk)
        Frame.__init__(self, self.__master, *args, **kwargs)

        self._time = StringVar()
        self._lat = StringVar()
        self._lon = StringVar()
        self._alt = StringVar()
        self._hae = StringVar()
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
        self._img_noclient = ImageTk.PhotoImage(Image.open(ICON_NOCLIENT))
        self._img_ntrip = ImageTk.PhotoImage(Image.open(ICON_NTRIPCONFIG))
        self._img_spartn = ImageTk.PhotoImage(Image.open(ICON_SPARTNCONFIG))
        self._img_blank = ImageTk.PhotoImage(Image.open(ICON_BLANK))

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
            self._frm_basic, text="hmsl:", bg=self._bgcol, fg=self._fgcol, anchor=N
        )
        self._lbl_lhae = Label(
            self._frm_basic, text="hae:", bg=self._bgcol, fg=self._fgcol, anchor=N
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
            self._frm_connect, bg=self._bgcol, image=self._img_conn
        )
        self._lbl_rtk_preset = Label(
            self._frm_connect, bg=self._bgcol, image=self._img_blank
        )
        self._lbl_transmit_preset = Label(
            self._frm_connect, bg=self._bgcol, image=self._img_blank
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
        self._lbl_hae = Label(
            self._frm_basic, textvariable=self._hae, bg=self._bgcol, fg="orange"
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
            fg="mediumpurple1",
        )
        self._lbl_diffcorr = Label(
            self._frm_advanced,
            textvariable=self._diffcorr,
            bg=self._bgcol,
            fg="hotpink",
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
            fg="mediumpurple1",
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
            fg="hotpink",
        )

    def _do_layout(self):
        """
        Position widgets in frame.
        """

        self._lbl_status_preset.grid(column=0, row=0, padx=2, pady=3, sticky=W)
        self._lbl_rtk_preset.grid(column=1, row=0, padx=2, pady=3, sticky=W)
        self._lbl_transmit_preset.grid(column=2, row=0, padx=2, pady=3, sticky=W)
        self._lbl_ltime.grid(column=1, row=0, pady=3, sticky=W)
        self._lbl_time.grid(column=2, row=0, pady=3, sticky=W)
        self._lbl_llat.grid(column=3, row=0, pady=3, sticky=W)
        self._lbl_lat.grid(column=4, row=0, pady=3, sticky=W)
        self._lbl_llon.grid(column=5, row=0, pady=3, sticky=W)
        self._lbl_lon.grid(column=6, row=0, pady=3, sticky=W)
        self._lbl_lalt.grid(column=7, row=0, pady=3, sticky=W)
        self._lbl_alt.grid(column=8, row=0, pady=3, sticky=W)
        self._lbl_lhae.grid(column=9, row=0, pady=3, sticky=W)
        self._lbl_hae.grid(column=10, row=0, pady=3, sticky=W)
        self._lbl_lalt_u.grid(column=11, row=0, pady=0, sticky=W)
        self._lbl_lspd.grid(column=12, row=0, pady=3, sticky=W)
        self._lbl_spd.grid(column=13, row=0, pady=3, sticky=W)
        self._lbl_lspd_u.grid(column=14, row=0, pady=0, sticky=W)
        self._lbl_ltrk.grid(column=15, row=0, pady=3, sticky=W)
        self._lbl_trk.grid(column=16, row=0, pady=3, sticky=W)
        self._lbl_lfix.grid(column=17, row=0, pady=3, sticky=W)
        self._lbl_fix.grid(column=18, row=0, pady=3, sticky=W)

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
        self._frm_basic.grid(column=1, row=0, pady=3, sticky=W)
        self._frm_toggle.grid(column=5, row=0, rowspan=2, pady=3, sticky=(N, E))
        self._show_advanced = not self._show_advanced
        if self._show_advanced:
            self._frm_advanced.grid(column=1, row=1, pady=3, sticky=W)
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

    def update_rtk_status(self, rtk: int = 0):
        """
        Update RTK status icon.

        :param int rtk: rtk transmit status (none = 0, ntrip = 1, spartn = 2/4)
        """

        if rtk == CONNECTED_NTRIP:
            self._lbl_rtk_preset.configure(image=self._img_ntrip)
        elif rtk in (CONNECTED_SPARTNIP, CONNECTED_SPARTNLB):
            self._lbl_rtk_preset.configure(image=self._img_spartn)
        else:
            self._lbl_rtk_preset.configure(image=self._img_blank)

    def update_transmit_status(self, transmit: int = 1):
        """
        Update socket server status icon.
        - -1 = not transmitting
        - 0 transmitting, no clients
        - 1 transmitting with clients

        :param int transmit: socket server transmit status
        """

        if transmit > 0:
            self._lbl_transmit_preset.configure(image=self._img_transmit)
        elif transmit == 0:
            self._lbl_transmit_preset.configure(image=self._img_noclient)
        else:
            self._lbl_transmit_preset.configure(image=self._img_blank)

    def update_frame(self):
        """
        Sets text of banner from GNSSStatus object.
        """

        deg_format = self.__app.configuration.get("degreesformat_s")
        units = self.__app.configuration.get("units_s")

        self._update_time()
        self._update_pos(deg_format, units)
        self._update_track(units)
        self._update_fix()
        self._update_siv()
        self._update_dop(units)
        self._update_dgps(units)

    def _update_time(self):
        """
        Update GNSS time of week
        """

        tim = self.__app.gnss_status.utc
        if tim in (None, ""):
            self._time.set(f"{NA:<15}")
        else:
            self._time.set(f"{tim:%H:%M:%S.%f}")

    def _update_pos(self, pos_format, units):
        """
        Update position.

        :param str pos_format: position display format as string (DMS, DMM, DDD, ECEF)
        :param str units: distance units as string (UMM, UMK, UI, UIK)
        """

        lat = self.__app.gnss_status.lat
        lon = self.__app.gnss_status.lon
        alt = self.__app.gnss_status.alt  # hMSL
        hae = self.__app.gnss_status.hae
        self._lbl_llat.config(text="lat:")
        self._lbl_llon.config(text="lon:")
        self._lbl_lalt.config(text="hmsl:")
        self._lbl_lhae.config(text="hae:")
        alt_u = "ft" if units in (UI, UIK) else "m"

        try:
            if pos_format == ECEF:
                lat, lon, alt = llh2ecef(lat, lon, alt)
                if units in (UI, UIK):
                    lat, lon = (m2ft(x) for x in (lat, lon))
                self._lbl_llat.config(text="X:")
                self._lbl_llon.config(text="Y:")
                self._lbl_lalt.config(text="Z:")
                self._lat.set(f"{lat:.4f}")
                self._lon.set(f"{lon:.4f}")
            else:
                deg_f = "<15"
                if pos_format == DMS:
                    lat, lon = latlon2dms(lat, lon)
                elif pos_format == DMM:
                    lat, lon = latlon2dmm(lat, lon)
                else:
                    deg_f = ".9f"
                if units in (UI, UIK):
                    alt = m2ft(alt)
                    hae = m2ft(hae)
                self._lat.set(f"{lat:{deg_f}}")
                self._lon.set(f"{lon:{deg_f}}")
            self._alt.set(f"{alt:.4f}")
            self._hae.set(f"{hae:.4f}")
            self._alt_u.set(f"{alt_u:<2}")
        except (TypeError, ValueError):
            self._lat.set(f"{NA:<15}")
            self._lon.set(f"{NA:<15}")
            self._alt.set(f"{NA:<6}")
            self._hae.set(f"{NA:<6}")
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
            self._speed.set(NA)
        track = self.__app.gnss_status.track
        if isinstance(track, (int, float)):
            self._track.set(f"{track:05.1f}")
        else:
            self._track.set(f"{NA:<4}")

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
            self._lbl_fix.config(fg=ERRCOL)
        self._fix.set(fix)

    def _update_siv(self):
        """
        Update siv and sip
        """

        try:
            self._siv.set(f"{self.__app.gnss_status.siv:02d}")
            self._sip.set(f"{self.__app.gnss_status.sip:02d}")
        except (TypeError, ValueError):
            self._siv.set(NA)
            self._sip.set(NA)

    def _update_dop(self, units):
        """
        Update precision and accuracy

        :param str units: distance units as string (UMM, UMK, UI, UIK)
        """

        try:
            pdop = self.__app.gnss_status.pdop
            self._dop.set(f"{pdop:.2f} {dop2str(pdop):<9}")
        except (TypeError, ValueError):
            self._dop.set(NA)

        try:
            self._hvdop.set(
                f"hdop {self.__app.gnss_status.hdop:.2f}\n"
                + f"vdop {self.__app.gnss_status.vdop:.2f}"
            )
        except (TypeError, ValueError):
            self._hvdop.set(f"hdop {NA}\nvdop {NA}")

        try:
            if units in (UI, UIK):
                self._hvacc.set(
                    f"hacc {m2ft(self.__app.gnss_status.hacc):.3f}\n"
                    + f"vacc {m2ft(self.__app.gnss_status.vacc):.3f}"
                )
            else:
                self._hvacc.set(
                    f"hacc {self.__app.gnss_status.hacc:.3f}\n"
                    + f"vacc {self.__app.gnss_status.vacc:.3f}"
                )
        except (TypeError, ValueError):
            self._hvacc.set(f"hacc {NA}\nvacc {NA}")

    def _update_dgps(self, units):
        """
        Update DGPS status.

        :param str units: distance units as string (UMM, UMK, UI, UIK)
        """

        self._diffcorr.set(DGPSYES if self.__app.gnss_status.diff_corr else NA)
        baseline = self.__app.gnss_status.rel_pos_length
        bl = NA
        bl_u = ""
        if isinstance(baseline, (int, float)):
            if baseline > 0.0:
                if units in (UI, UIK):
                    bl = m2ft(baseline / 100)  # cm to ft
                    if bl > M2MILES:
                        bl_u = "miles"
                        bl = bl / M2MILES  # cm to miles
                    else:
                        bl_u = "ft"
                else:
                    if baseline > 100000:
                        bl_u = "km"
                        bl = baseline / 100000  # cm to km
                    else:
                        bl_u = "m"
                        bl = baseline / 100  # cm to m

        if self.__app.gnss_status.diff_corr:
            age = self.__app.gnss_status.diff_age
            station = self.__app.gnss_status.diff_station
            if age in [None, "", 0]:
                age = NA
            else:
                age = f"{age} s"
            if station in [None, "", 0]:
                station = NA
            if bl == NA:
                self._diffstat.set(f"age {age}\nstation {station} baseline {bl}")
            else:
                self._diffstat.set(
                    f"age {age}\nstation {station} baseline {bl:.2f} {bl_u}"
                )
        else:
            self._diffstat.set("")

    def _set_fontsize(self):
        """
        Adjust font sizes according to frame size
        """

        w = self.width
        txt = 100
        for ctl in (
            self._lbl_status_preset,
            self._lbl_time,
            self._lbl_lat,
            self._lbl_lon,
            self._lbl_alt,
            self._lbl_hae,
            self._lbl_spd,
            self._lbl_trk,
            self._lbl_pdop,
            self._lbl_fix,
            self._lbl_sip,
            self._lbl_siv,
            self._lbl_diffcorr,
        ):
            fnt, _ = scale_font(w, 16, txt)
            ctl.config(font=fnt)

        for ctl in (
            self._lbl_ltime,
            self._lbl_llat,
            self._lbl_llon,
            self._lbl_lalt,
            self._lbl_lhae,
            self._lbl_lspd,
            self._lbl_ltrk,
            self._lbl_lpdop,
            self._lbl_lfix,
            self._lbl_lsip,
            self._lbl_lsiv,
            self._lbl_lacc,
            self._lbl_ldgps,
        ):
            fnt, _ = scale_font(w, 12, txt)
            ctl.config(font=fnt)

        for ctl in (
            self._lbl_lalt_u,
            self._lbl_lspd_u,
            self._lbl_hvdop,
            self._lbl_hvacc,
            self._lbl_diffstat,
        ):
            fnt, _ = scale_font(w, 10, txt)
            ctl.config(font=fnt)

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
        return self.winfo_width(), self.winfo_height()
