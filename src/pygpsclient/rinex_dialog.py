"""
rinex_dialog.py

RINEX conversion dialog.

Created on 2 Apr 2026

:author: semuadmin (Steve Smith)
:copyright: 2020 semuadmin
:license: BSD 3-Clause
"""

# pylint: disable=use-implicit-booleaness-not-comparison

from datetime import datetime, timezone
from logging import getLogger
from pathlib import Path
from threading import Event, Thread
from tkinter import (
    EW,
    NORMAL,
    NSEW,
    Button,
    Checkbutton,
    E,
    Entry,
    Frame,
    IntVar,
    Label,
    Spinbox,
    StringVar,
    TclError,
    W,
    ttk,
)
from tkinter.ttk import Progressbar
from types import MethodType

from pygnssutils.gnssreader import (
    NMEA_PROTOCOL,
    RTCM3_PROTOCOL,
    UBX_PROTOCOL,
    GNSSReader,
)
from pygnssutils.rinex_conv import RinexConverter
from pygnssutils.rinex_globals import (
    BDS,
    GAL,
    GLO,
    GPS,
    IRN,
    MET,
    NAV,
    OBS,
    QZS,
    RINEX_CANCELLED,
    RINEX_NORECS,
    RINEX_OK,
    SBA,
)

from pygpsclient.globals import (
    ERRCOL,
    INFOCOL,
    OKCOL,
    READONLY,
    TRACEMODE_WRITE,
)
from pygpsclient.helpers import VALCUSTOM, VALNONBLANK, validate
from pygpsclient.strings import (
    DLGTRINEX,
    LBLRINEXANTENNA,
    LBLRINEXCOMMENT,
    LBLRINEXCOUNTRY,
    LBLRINEXDOI,
    LBLRINEXGNSSTYPES,
    LBLRINEXINPUTFILE,
    LBLRINEXLICENSE,
    LBLRINEXMARKER,
    LBLRINEXOBSERVER,
    LBLRINEXOBSTYPES,
    LBLRINEXOUTPUTS,
    LBLRINEXRCVR,
    LBLRINEXSTARTTIME,
    LBLRINEXSTATION,
    LBLRINEXTYPES,
    LBLRINEXVER,
    NA,
    RINEXFILEINVALID,
    RINEXFILEVALID,
    RINEXFILEVALIDATING,
)
from pygpsclient.toplevel_dialog import ToplevelDialog

RINEXVERSIONS = ("3.05", "4.02")
RINEXTYPES = (OBS, NAV, MET)
NMEASOURCE = "NMEA 0183"
RTCMSOURCE = "RTCM 3"
UBXSOURCE = "UBX (u-blox)"
RINEXSOURCES = {UBXSOURCE: "R", NMEASOURCE: "R", RTCMSOURCE: "N"}
RINEXMARKERTYPES = (
    "GEODETIC",
    "HUMAN",
    "ANIMAL",
    "BALLISTIC",
    "GLACIER",
    "FLOATING_ICE",
    "FLOATING_BUOY",
    "FIXED_BUOY",
    "AIRBORNE",
    "WATER_CRAFT",
    "GROUND_CRAFT",
    "SPACEBORNE",
    "NON_PHYSICAL",
    "NON_GEODETIC",
)
USERCOMMENTS = 5


class RINEXDialog(ToplevelDialog):
    """,
    RINEXDialog class.
    """

    def __init__(self, app, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Constructor.

        :param Frame app: reference to main tkinter application
        :param args: optional args to pass to parent class (not currently used)
        :param kwargs: optional kwargs to pass to parent class (not currently used)
        """

        self.__app = app  # Reference to main application class
        self.logger = getLogger(__name__)
        self.__master = self.__app.appmaster  # Reference to root class (Tk)

        super().__init__(app, DLGTRINEX)
        self._infile_path = Path(".")
        self._infilepath = StringVar()
        self._obssource = StringVar()
        self._navsource = StringVar()
        self._metsource = StringVar()
        self._rinexver = StringVar()
        self._countrycode = StringVar()
        self._rinexobs = IntVar()
        self._rinexnav = IntVar()
        self._rinexmet = IntVar()
        self._rxgps = IntVar()
        self._rxglonass = IntVar()
        self._rxgalileo = IntVar()
        self._rxbeidou = IntVar()
        self._rxsbas = IntVar()
        self._rxqzss = IntVar()
        self._rxnavic = IntVar()
        self._obstypes = StringVar()
        self._markernum = StringVar()
        self._markername = StringVar()
        self._markertype = StringVar()
        self._antennanum = StringVar()
        self._antennatype = StringVar()
        self._rcvrnum = StringVar()
        self._rcvrname = StringVar()
        self._rcvrversion = StringVar()
        self._observer = StringVar()
        self._starttime = StringVar()
        self._usercommentvar = []
        for _ in range(USERCOMMENTS):
            self._usercommentvar.append(StringVar())
        self._outputlabels = {}
        for rt in (OBS, NAV, MET):
            self._outputlabels[rt] = StringVar()
        self._doi = StringVar()
        self._license = StringVar()
        self._station = StringVar()
        self._settings = {}
        self._status = False
        self._filecount = 0
        self._stopevent = Event()
        self._process_result = RINEX_OK
        self._show_advanced = False

        self._body()
        self._do_layout()
        self._reset()
        self._attach_events()
        self._finalise()

    def _body(self):
        """
        Set up frame and widgets.
        """
        # pylint: disable=unnecessary-lambda

        self._frm_body = Frame(self)
        self._frm_basic = Frame(self._frm_body, borderwidth=1, relief="groove")
        self._frm_advanced = Frame(self._frm_body, borderwidth=1, relief="groove")
        self._lbl_infile = Label(self._frm_basic, text=LBLRINEXINPUTFILE)
        self._ent_infilepath = Entry(
            self._frm_basic,
            textvariable=self._infilepath,
            state=READONLY,
            relief="sunken",
        )
        self._btn_load = Button(
            self._frm_basic,
            width=45,
            height=35,
            image=self.img_load,
            command=lambda: self._on_load(),
        )
        self._btn_convert = Button(
            self._frm_basic,
            width=45,
            height=35,
            image=self.img_conn,
            command=lambda: self._on_convert(),
        )
        self._btn_cancel = Button(
            self._frm_basic,
            width=45,
            height=35,
            image=self.img_cancel,
            command=lambda: self._on_cancel(),
        )
        self._btn_toggle = Button(
            self._frm_basic,
            width=22,
            height=28,
            command=self._toggle_advanced,
            image=self._img_expandh,
        )
        self._lbl_rinexver = Label(self._frm_basic, text=LBLRINEXVER)
        self._spn_rinexver = Spinbox(
            self._frm_basic,
            values=RINEXVERSIONS,
            width=6,
            wrap=True,
            textvariable=self._rinexver,
            state=READONLY,
            repeatdelay=1000,
            repeatinterval=1000,
        )
        self._lbl_outtypes = Label(self._frm_basic, text=LBLRINEXTYPES)
        self._chk_rinexobs = Checkbutton(
            self._frm_basic,
            text="Observation",
            variable=self._rinexobs,
            state=NORMAL,
        )
        self._spn_obssource = Spinbox(
            self._frm_basic,
            values=list(RINEXSOURCES),
            width=14,
            wrap=True,
            textvariable=self._obssource,
            state=READONLY,
            repeatdelay=1000,
            repeatinterval=1000,
        )
        self._chk_rinexnav = Checkbutton(
            self._frm_basic,
            text="Navigation",
            variable=self._rinexnav,
            state=NORMAL,
        )
        self._spn_navsource = Spinbox(
            self._frm_basic,
            values=list(RINEXSOURCES),
            width=14,
            wrap=True,
            textvariable=self._navsource,
            state=READONLY,
            repeatdelay=1000,
            repeatinterval=1000,
        )
        self._chk_rinexmet = Checkbutton(
            self._frm_basic,
            text="Meteorology",
            variable=self._rinexmet,
            state=NORMAL,
        )
        self._spn_metsource = Spinbox(
            self._frm_basic,
            values=list(RINEXSOURCES),
            width=14,
            wrap=True,
            textvariable=self._metsource,
            state=READONLY,
            repeatdelay=1000,
            repeatinterval=1000,
        )
        self._lbl_gnsstypes = Label(self._frm_basic, text=LBLRINEXGNSSTYPES)
        self._chk_rxgps = Checkbutton(
            self._frm_basic,
            text="GPS",
            variable=self._rxgps,
            state=NORMAL,
        )
        self._chk_rxsbas = Checkbutton(
            self._frm_basic,
            text="SBA",
            variable=self._rxsbas,
            state=NORMAL,
        )
        self._chk_rxgalileo = Checkbutton(
            self._frm_basic,
            text="GAL",
            variable=self._rxgalileo,
            state=NORMAL,
        )
        self._chk_rxbeidou = Checkbutton(
            self._frm_basic,
            text="BDS",
            variable=self._rxbeidou,
            state=NORMAL,
        )
        self._chk_rxqzss = Checkbutton(
            self._frm_basic,
            text="QZS",
            variable=self._rxqzss,
            state=NORMAL,
        )
        self._chk_rxglonass = Checkbutton(
            self._frm_basic,
            text="GLO",
            variable=self._rxglonass,
            state=NORMAL,
        )
        self._chk_rxnavic = Checkbutton(
            self._frm_basic,
            text="IRN",
            variable=self._rxnavic,
            state=NORMAL,
        )
        self._lbl_obstypes = Label(self._frm_basic, text=LBLRINEXOBSTYPES)
        self._ent_obstypes = Entry(
            self._frm_basic,
            textvariable=self._obstypes,
            state=NORMAL,
            relief="sunken",
        )
        self._pgb_elapsed = Progressbar(
            self._frm_basic,
            orient="horizontal",
            mode="determinate",
            length=100,
        )
        self._lbl_outputs = Label(self._frm_basic, text=LBLRINEXOUTPUTS.format(path=""))
        self._lbl_output_labels = {}
        for rt in RINEXTYPES:
            self._lbl_output_labels[rt] = Label(
                self._frm_basic,
                textvariable=self._outputlabels[rt],
                anchor=W,
            )
        self._lbl_marker = Label(self._frm_advanced, text=LBLRINEXMARKER, anchor=W)
        self._ent_markernum = Entry(
            self._frm_advanced,
            width=5,
            textvariable=self._markernum,
            state=NORMAL,
            relief="sunken",
        )
        self._ent_markername = Entry(
            self._frm_advanced,
            width=30,
            textvariable=self._markername,
            state=NORMAL,
            relief="sunken",
        )
        self._spn_markertype = Spinbox(
            self._frm_advanced,
            values=RINEXMARKERTYPES,
            width=20,
            wrap=True,
            textvariable=self._markertype,
            state=NORMAL,
            repeatdelay=1000,
            repeatinterval=1000,
        )
        self._lbl_antenna = Label(self._frm_advanced, text=LBLRINEXANTENNA, anchor=W)
        self._ent_antennanum = Entry(
            self._frm_advanced,
            width=5,
            textvariable=self._antennanum,
            state=NORMAL,
            relief="sunken",
        )
        self._ent_antennatype = Entry(
            self._frm_advanced,
            width=30,
            textvariable=self._antennatype,
            state=NORMAL,
            relief="sunken",
        )
        self._lbl_receiver = Label(self._frm_advanced, text=LBLRINEXRCVR, anchor=W)
        self._ent_rcvrnum = Entry(
            self._frm_advanced,
            width=5,
            textvariable=self._rcvrnum,
            state=NORMAL,
            relief="sunken",
        )
        self._ent_rcvrtype = Entry(
            self._frm_advanced,
            width=30,
            textvariable=self._rcvrname,
            state=NORMAL,
            relief="sunken",
        )
        self._ent_rcvrversion = Entry(
            self._frm_advanced,
            width=20,
            textvariable=self._rcvrversion,
            state=NORMAL,
            relief="sunken",
        )
        self._lbl_observer = Label(self._frm_advanced, text=LBLRINEXOBSERVER, anchor=W)
        self._ent_observer = Entry(
            self._frm_advanced,
            width=30,
            textvariable=self._observer,
            state=NORMAL,
            relief="sunken",
        )
        self._lbl_country = Label(self._frm_advanced, text=LBLRINEXCOUNTRY, anchor=W)
        self._ent_country = Entry(
            self._frm_advanced,
            width=5,
            textvariable=self._countrycode,
            state=NORMAL,
            relief="sunken",
        )
        self._lbl_doi = Label(self._frm_advanced, text=LBLRINEXDOI, anchor=W)
        self._ent_doi = Entry(
            self._frm_advanced,
            width=60,
            textvariable=self._doi,
            state=NORMAL,
            relief="sunken",
        )
        self._lbl_license = Label(self._frm_advanced, text=LBLRINEXLICENSE, anchor=W)
        self._ent_license = Entry(
            self._frm_advanced,
            width=60,
            textvariable=self._license,
            state=NORMAL,
            relief="sunken",
        )
        self._lbl_station = Label(self._frm_advanced, text=LBLRINEXSTATION, anchor=W)
        self._ent_station = Entry(
            self._frm_advanced,
            width=60,
            textvariable=self._station,
            state=NORMAL,
            relief="sunken",
        )
        self._lbl_comments = Label(self._frm_advanced, text=LBLRINEXCOMMENT, anchor=W)
        self._lbl_starttime = Label(
            self._frm_advanced, text=LBLRINEXSTARTTIME, anchor=W
        )
        self._ent_starttime = Entry(
            self._frm_advanced,
            width=20,
            textvariable=self._starttime,
            state=NORMAL,
            relief="sunken",
        )
        self._entcomments = []
        for cvar in self._usercommentvar:
            self._entcomments.append(
                Entry(
                    self._frm_advanced,
                    textvariable=cvar,
                    width=50,
                    state=NORMAL,
                )
            )

    def _do_layout(self):
        """
        Position widgets in frame.
        """

        self._frm_body.grid(column=0, row=0, sticky=NSEW)
        self._frm_basic.grid(column=0, row=0, sticky=NSEW)

        self._lbl_infile.grid(column=0, row=0, columnspan=6, padx=3, sticky=W)
        self._btn_toggle.grid(column=6, row=0, padx=3, rowspan=2, sticky=E)
        self._ent_infilepath.grid(column=0, row=1, columnspan=6, padx=3, sticky=EW)
        self._btn_load.grid(column=0, row=2, padx=3, sticky=W)
        self._btn_convert.grid(column=5, row=2, padx=3, sticky=E)
        self._btn_cancel.grid(column=6, row=2, padx=3, sticky=E)

        ttk.Separator(self._frm_basic).grid(
            column=0, row=3, columnspan=7, padx=3, sticky=EW
        )
        self._lbl_rinexver.grid(column=0, row=4, padx=3, columnspan=2, sticky=W)
        self._spn_rinexver.grid(column=2, row=4, padx=3, columnspan=2, sticky=W)
        self._lbl_country.grid(column=4, row=4, padx=3, sticky=W)
        self._ent_country.grid(column=5, row=4, padx=3, sticky=W)
        self._lbl_outtypes.grid(column=0, row=5, columnspan=7, padx=3, sticky=W)
        self._chk_rinexobs.grid(column=0, row=6, columnspan=2, padx=3, sticky=W)
        self._chk_rinexnav.grid(column=2, row=6, columnspan=2, padx=3, sticky=W)
        self._chk_rinexmet.grid(column=4, row=6, columnspan=2, padx=3, sticky=W)
        self._spn_obssource.grid(column=0, row=7, padx=3, columnspan=2, sticky=W)
        self._spn_navsource.grid(column=2, row=7, padx=3, columnspan=2, sticky=W)
        self._spn_metsource.grid(column=4, row=7, padx=3, columnspan=2, sticky=W)
        self._lbl_gnsstypes.grid(column=0, row=8, columnspan=7, padx=3, sticky=W)
        self._chk_rxgps.grid(column=0, row=9, padx=3, sticky=W)
        self._chk_rxsbas.grid(column=1, row=9, padx=3, sticky=W)
        self._chk_rxgalileo.grid(column=2, row=9, padx=3, sticky=W)
        self._chk_rxbeidou.grid(column=3, row=9, padx=3, sticky=W)
        self._chk_rxqzss.grid(column=4, row=9, padx=3, sticky=W)
        self._chk_rxglonass.grid(column=5, row=9, padx=3, sticky=W)
        self._chk_rxnavic.grid(column=6, row=9, padx=3, sticky=W)
        self._lbl_obstypes.grid(column=0, row=10, columnspan=7, padx=3, sticky=W)
        self._ent_obstypes.grid(column=0, row=11, columnspan=7, padx=3, sticky=EW)
        self._pgb_elapsed.grid(column=0, row=12, columnspan=7, padx=3, sticky=EW)
        ttk.Separator(self._frm_basic).grid(
            column=0, row=13, columnspan=7, padx=3, sticky=EW
        )
        self._lbl_outputs.grid(column=0, row=14, columnspan=7, padx=3, pady=1, sticky=W)
        for i, lbl in enumerate(self._lbl_output_labels.values()):
            lbl.grid(column=0, row=15 + i, columnspan=7, padx=3, pady=1, sticky=EW)

        self._lbl_marker.grid(column=0, row=0, columnspan=3, padx=3, sticky=W)
        self._ent_markernum.grid(column=0, row=1, padx=3, sticky=W)
        self._ent_markername.grid(column=1, row=1, padx=3, sticky=W)
        self._spn_markertype.grid(column=2, row=1, padx=3, sticky=W)
        self._lbl_antenna.grid(column=0, row=2, columnspan=3, padx=3, sticky=W)
        self._ent_antennanum.grid(column=0, row=3, padx=3, sticky=W)
        self._ent_antennatype.grid(column=1, row=3, padx=3, sticky=W)
        self._lbl_receiver.grid(column=0, row=4, columnspan=3, padx=3, sticky=W)
        self._ent_rcvrnum.grid(column=0, row=5, padx=3, sticky=W)
        self._ent_rcvrtype.grid(column=1, row=5, padx=3, sticky=W)
        self._ent_rcvrversion.grid(column=2, row=5, padx=3, sticky=W)
        self._lbl_observer.grid(column=0, row=6, columnspan=3, padx=3, sticky=W)
        self._lbl_country.grid(column=2, row=6, columnspan=3, padx=3, sticky=W)
        self._ent_observer.grid(column=0, row=7, columnspan=2, padx=3, sticky=EW)
        self._ent_country.grid(column=2, row=7, padx=3, sticky=W)
        self._lbl_starttime.grid(column=0, row=8, columnspan=2, padx=3, sticky=W)
        self._ent_starttime.grid(column=2, row=8, padx=3, sticky=W)
        self._lbl_comments.grid(column=0, row=9, columnspan=3, padx=3, sticky=W)
        for i, ec in enumerate(self._entcomments):
            ec.grid(column=0, row=10 + i, columnspan=3, padx=3, sticky=EW)

        for col in range(7):  # make columns equal width
            self._frm_basic.grid_columnconfigure(col, weight=1, uniform="col")

    def _do_layout_rinex4(self, show: bool, startrow: int = 10 + USERCOMMENTS):
        """
        Position optional RINEX 4 widgets in frame.
        """

        if show:
            self._lbl_doi.grid(
                column=0, row=startrow + 1, columnspan=3, padx=3, sticky=W
            )
            self._ent_doi.grid(
                column=0, row=startrow + 2, columnspan=3, padx=3, sticky=EW
            )
            self._lbl_license.grid(
                column=0, row=startrow + 3, columnspan=3, padx=3, sticky=W
            )
            self._ent_license.grid(
                column=0, row=startrow + 4, columnspan=3, padx=3, sticky=EW
            )
            self._lbl_station.grid(
                column=0, row=startrow + 5, columnspan=3, padx=3, sticky=W
            )
            self._ent_station.grid(
                column=0, row=startrow + 6, columnspan=3, padx=3, sticky=EW
            )
        else:
            self._lbl_doi.grid_forget()
            self._ent_doi.grid_forget()
            self._lbl_license.grid_forget()
            self._ent_license.grid_forget()
            self._lbl_station.grid_forget()
            self._ent_station.grid_forget()

    def _attach_events(self):
        """
        Set up event listeners.
        """

        self._rinexver.trace_add(TRACEMODE_WRITE, self._on_update_rinexver)
        for setting in (
            self._rinexobs,
            self._rinexnav,
            self._rinexmet,
            self._rxgps,
            self._rxglonass,
            self._rxgalileo,
            self._rxbeidou,
            self._rxsbas,
            self._rxqzss,
            self._rxnavic,
        ):
            setting.trace_add(TRACEMODE_WRITE, self._on_update_config)

    def _reset(self):
        """
        Reset dialog widgets.
        """

        for chk in (
            self._rinexobs,
            self._rinexnav,
            self._rinexmet,
            self._rxgps,
            self._rxglonass,
            self._rxgalileo,
            self._rxbeidou,
            self._rxsbas,
            self._rxqzss,
            self._rxnavic,
        ):
            chk.set(1)
        self._obssource.set(UBXSOURCE)
        self._navsource.set(UBXSOURCE)
        self._metsource.set(NMEASOURCE)
        rcvrname = self.__app.gnss_status.version_data.get("hwversion", NA)
        self._rcvrname.set("" if rcvrname == NA else rcvrname)
        rcvrversion = self.__app.gnss_status.version_data.get("fwversion", NA)
        self._rcvrversion.set("" if rcvrversion == NA else rcvrversion)
        self._starttime.set(datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%z"))
        self.set_controls(self._status)

    def _on_update_rinexver(self, var, index, mode):  # pylint: disable=unused-argument
        """
        Update RINEX version.
        """

        self._do_layout_rinex4(self._rinexver.get() >= "4.00", 10 + USERCOMMENTS)

    def _on_update_config(self, var, index, mode):  # pylint: disable=unused-argument
        """
        Update in-memory configuration if setting is changed.
        """

        try:
            self.update()
            cfg = self.__app.configuration
        except (ValueError, TclError):
            pass

    def set_controls(self, status: bool):
        """
        Set controls according to status.

        :param bool status: connection status (True/False)
        :param NoneType | tuple msgt: tuple of (message, color)
        """

    def _on_convert(self):
        """
        Run conversion.
        """

        self.status_label = f"Processing {self._infile_path.name}"
        for rt in RINEXTYPES:
            self._outputlabels[rt].set("")
        self._do_conversion()

    def _on_cancel(self):
        """
        Cancel conversion process
        """

        self._stopevent.set()

    def _on_load(self):
        """
        Load input data log.
        """

        infile = self.__app.file_handler.open_file(
            self,
            "GNSS data log",
            (
                ("binary log files", "*.log"),
                ("binary UBXfiles", "*.ubx"),
                ("all files", "*.*"),
            ),
        )
        if infile in ("", None):
            return  # user cancelled

        self._infile_path = Path(infile)
        sfp = str(self._infile_path)
        if len(sfp) > 60:
            sfp = f"...{sfp[-60:]}"
        self._infilepath.set(sfp)
        self._ent_infilepath.update()
        validate(self._ent_infilepath, valmode=VALNONBLANK)
        self.status_label = (
            RINEXFILEVALIDATING.format(path=self._infile_path.name),
            OKCOL,
        )
        i = 0
        try:
            with open(self._infile_path, "rb") as infile:
                gnr = GNSSReader(infile, parsing=False)
                for raw, _ in gnr:
                    if raw is not None:
                        i += 1
            if i == 0:
                self.status_label = (
                    RINEXFILEINVALID.format(path=self._infile_path.name),
                    ERRCOL,
                )
            else:
                self.status_label = (
                    RINEXFILEVALID.format(path=self._infile_path.name, count=i),
                    INFOCOL,
                )
            self._filecount = i
        except Exception as err:  # pylint: disable=broad-exception-caught
            self.logger.error(f"Error processing  {self._infile_path} - {err}")
            self.status_label = (f"Error processing {self._infile_path.name}", ERRCOL)

    def _toggle_advanced(self):
        """
        Toggle advanced panel on or off.
        """

        self._show_advanced = not self._show_advanced
        if self._show_advanced:
            self._frm_advanced.grid(column=1, row=0, sticky=NSEW)
            self._btn_toggle.config(image=self._img_contracth)
        else:
            self._frm_advanced.grid_forget()
            self._btn_toggle.config(image=self._img_expandh)

    def _valid_settings(self) -> bool:
        """
        Validate settings.

        :return: valid True/False
        :rtype: bool
        """

        valid = True
        if not valid:
            self.status_label = ("ERROR - invalid settings", ERRCOL)

        return valid

    def _validtime(self, val: str) -> bool:
        """
        Validate start time.

        :param str val: datetime in format "%Y%m%d%H%M%S%z"
        :return: Valid/Invalid
        :rtype: bool
        """

        try:
            datetime.strptime(val, "%Y%m%d%H%M%S%z")
            return True
        except ValueError:
            return False

    def _do_conversion(self, **kwargs):
        """
        Do RINEX conversion.

        :return: return code
        :rtype: int
        """

        try:

            valid = True
            valid = valid & validate(
                self._ent_starttime, valmode=VALCUSTOM, func=self._validtime
            )
            valid = valid & validate(self._ent_infilepath, valmode=VALNONBLANK)
            if not valid:
                self.status_label = ("Invalid Parameters", ERRCOL)
                return

            rinex_version = self._rinexver.get()
            rinex_types = []
            if self._rinexobs.get():
                rinex_types.append(OBS)
            if self._rinexnav.get():
                rinex_types.append(NAV)
            if self._rinexmet.get():
                rinex_types.append(MET)
            if rinex_types == []:
                self.status_label = ("Select at least one RINEX output type", ERRCOL)
                valid = False
            gnss_filter = []
            if self._rxgps.get():
                gnss_filter.append(GPS)
            if self._rxgalileo.get():
                gnss_filter.append(GAL)
            if self._rxglonass.get():
                gnss_filter.append(GLO)
            if self._rxbeidou.get():
                gnss_filter.append(BDS)
            if self._rxqzss.get():
                gnss_filter.append(QZS)
            if self._rxnavic.get():
                gnss_filter.append(IRN)
            if self._rxsbas.get():
                gnss_filter.append(SBA)
            if gnss_filter == []:
                self.status_label = ("Select at least one GNSS", ERRCOL)
                valid = False
            if not valid:
                return

            obs_filter = self._obstypes.get().split(",")
            starttime = self._starttime.get()
            minobs = 10
            marker = [
                self._markername.get(),
                self._markernum.get(),
                self._markertype.get(),
            ]
            antenna = [self._antennanum.get(), self._antennatype.get()]
            receiver = [
                self._rcvrnum.get(),
                self._rcvrname.get(),
                self._rcvrversion.get(),
            ]
            observer = self._observer.get()
            doi = self._doi.get()
            licen = self._license.get()
            station = self._station.get()
            comments = ["PyGPSClient RINEX Converter Dialog"]
            country = self._countrycode.get()
            for cvar in self._usercommentvar:
                cval = cvar.get()
                if cval != "":
                    comments.append(cval)
            protfilter = NMEA_PROTOCOL | RTCM3_PROTOCOL | UBX_PROTOCOL
            datasource = [
                RINEXSOURCES[self._obssource.get()],
                RINEXSOURCES[self._navsource.get()],
                RINEXSOURCES[self._metsource.get()],
            ]
            rc = RinexConverter(
                self.__app,
                rinex_version=rinex_version,
                rinex_types=rinex_types,
                gnssfilter=gnss_filter,
                obsfilter=obs_filter,
                datasource=datasource,
                starttime=starttime,
                minobs=minobs,
                marker=marker,
                antenna=antenna,
                receiver=receiver,
                observer=observer,
                comments=comments,
                protfilter=protfilter,
                doi=doi,
                license=licen,
                station=station,
                country=country,
                **kwargs,
            )
            self._stopevent.clear()
            rct = Thread(
                target=self._process_input,
                args=(
                    rc,
                    self._infile_path,
                    self._stopevent,
                    self._prog_callback_threaded,
                    kwargs,
                ),
                daemon=True,
            )
            rct.start()

        except (TclError, KeyboardInterrupt):
            self.status_label = ("Conversion Failed", ERRCOL)

    def _process_input(
        self,
        rc: RinexConverter,
        infilepath: Path,
        stopevent: Event,
        progcallback: MethodType,
        kwargs: dict,
    ):
        """
        THREADED

        :param RinexConverter rc: RineXConverter instance
        :param Path infilepath: input file path
        :param Event stopevent: stopevent for remote cancellation
        :param MethodType progcallback: callback for % complete updates
        """

        res = rc.process_input(
            infile=infilepath, stopevent=stopevent, progcallback=progcallback, **kwargs
        )
        if res == RINEX_OK:
            outputs = rc.outputs
            tot = 0
            for rt in RINEXTYPES:
                rtc = outputs.get(rt, None)
                if rtc is not None:
                    tot += rtc[1]
                    self._outputlabels[rt].set(
                        f"{rt}: {outputs[rt][0].name}: {outputs[rt][1]}"
                    )
            if tot > 1:
                self.status_label = ("Conversion successful", OKCOL)
            else:
                self.status_label = ("No usable information in input", ERRCOL)
            parts = self._infile_path.parts
            path = f" (...{parts[-2]}/) " if len(parts) > 1 else " (.../)"
            self._lbl_outputs.config(text=LBLRINEXOUTPUTS.format(path=path))

        elif res == RINEX_CANCELLED:
            self.status_label = ("Conversion cancelled", ERRCOL)
        elif res == RINEX_NORECS:
            self.status_label = ("No parsable records in input", ERRCOL)
        else:
            self.status_label = ("Conversion failed", ERRCOL)

    def _prog_callback_threaded(self, progress: int):
        """
        Invoke progress callback function from thread.

        :param int progress: % complete
        """

        self.after(0, self._prog_callback(progress))

    def _prog_callback(self, progress: int):
        """
        Progress callback function.

        :param int progress: % complete
        """

        self._pgb_elapsed["value"] = progress
        self._pgb_elapsed.update()
