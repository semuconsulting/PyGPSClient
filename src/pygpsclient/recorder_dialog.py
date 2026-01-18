"""
recorder_dialog.py

Configuration command Load/Save/Record dialog for commands
sent via UBX, NMEA or TTY Configuration panels.

Records commands to memory array and allows user to load or save
this array to or from a binary file.

Facilitates copying configuration from one device to another.

Created on 9 Jan 2023

:author: semuadmin (Steve Smith)
:copyright: 2020 semuadmin
:license: BSD 3-Clause
"""

# pylint: disable=unused-argument

from datetime import datetime
from threading import Event, Thread
from time import sleep
from tkinter import CENTER, EW, NSEW, Button, Frame, Label, TclError, W, filedialog

from PIL import Image, ImageTk
from pynmeagps import NMEAMessage
from pyubx2 import (
    POLL_LAYER_BBR,
    POLL_LAYER_FLASH,
    SET,
    SET_LAYER_BBR,
    SET_LAYER_FLASH,
    SET_LAYER_RAM,
    TXN_NONE,
    U1,
    UBXMessage,
    UBXReader,
    bytes2val,
    val2bytes,
)

from pygpsclient.globals import (
    BGCOL,
    ERRCOL,
    FGCOL,
    HOME,
    ICON_DELETE,
    ICON_IMPORT,
    ICON_LOAD,
    ICON_RECORD,
    ICON_SAVE,
    ICON_SEND,
    ICON_STOP,
    ICON_UNDO,
    INFOCOL,
    OKCOL,
    PNTCOL,
    UNDO,
)
from pygpsclient.helpers import nmea2preset, set_filename, tty2preset, ubx2preset
from pygpsclient.strings import DLGTRECORD, SAVETITLE
from pygpsclient.toplevel_dialog import ToplevelDialog

CFG = b"\x06"
FLASH = 0.7
MSG = b"\x01"
PLAY = 1
PRT = b"\x00"
RECORD = 2
STOP = 0
TTYONLY = 0
VALSET = b"\x8a"
VALGET = b"\x8b"


class RecorderDialog(ToplevelDialog):
    """
    Configuration command recorder panel.
    """

    def __init__(self, app, *args, **kwargs):
        """
        Constructor.

        :param Frame app: reference to main tkinter application
        :param Frame container: reference to container frame (config-dialog)
        :param args: optional args to pass to Frame parent class
        :param kwargs: optional kwargs to pass to Frame parent class
        """

        self.__app = app
        # self.__master = self.__app.appmaster  # link to root Tk window
        super().__init__(app, DLGTRECORD)
        self.width = int(kwargs.get("width", 500))
        self.height = int(kwargs.get("height", 300))

        self._img_load = ImageTk.PhotoImage(Image.open(ICON_LOAD))
        self._img_save = ImageTk.PhotoImage(Image.open(ICON_SAVE))
        self._img_play = ImageTk.PhotoImage(Image.open(ICON_SEND))
        self._img_stop = ImageTk.PhotoImage(Image.open(ICON_STOP))
        self._img_record = ImageTk.PhotoImage(Image.open(ICON_RECORD))
        self._img_import = ImageTk.PhotoImage(Image.open(ICON_IMPORT))
        self._img_undo = ImageTk.PhotoImage(Image.open(ICON_UNDO))
        self._img_delete = ImageTk.PhotoImage(Image.open(ICON_DELETE))
        self._rec_status = STOP
        self._configfile = None
        self._stop_event = Event()
        self._bg = self.cget("bg")  # default background color
        self._configfile = None
        self._configpath = None

        self._body()
        self._do_layout()
        self._attach_events()
        self._reset()
        self._finalise()

    def _body(self):
        """
        Set up frame and widgets.
        """

        self._frm_body = Frame(self.container, borderwidth=2, relief="groove", bg=BGCOL)
        self._btn_load = Button(
            self._frm_body,
            image=self._img_load,
            width=40,
            command=self._on_load,
            font=self.__app.font_md,
            highlightbackground=BGCOL,
            highlightthickness=2,
        )
        self._btn_save = Button(
            self._frm_body,
            image=self._img_save,
            width=40,
            command=self._on_save,
            highlightbackground=BGCOL,
            highlightthickness=2,
        )
        self._btn_import = Button(
            self._frm_body,
            image=self._img_import,
            width=40,
            command=self._on_import,
            highlightbackground=BGCOL,
            highlightthickness=2,
        )
        self._btn_play = Button(
            self._frm_body,
            image=self._img_play,
            width=40,
            command=self._on_play,
            highlightbackground=BGCOL,
            highlightthickness=2,
        )
        self._btn_record = Button(
            self._frm_body,
            image=self._img_record,
            width=40,
            command=self._on_record,
            highlightbackground=BGCOL,
            highlightthickness=2,
        )
        self._btn_undo = Button(
            self._frm_body,
            image=self._img_undo,
            width=40,
            command=self._on_undo,
            highlightbackground=BGCOL,
            highlightthickness=2,
        )
        self._btn_delete = Button(
            self._frm_body,
            image=self._img_delete,
            width=40,
            command=self._on_delete,
            highlightbackground=BGCOL,
            highlightthickness=2,
        )
        self._lbl_memory = Label(
            self._frm_body,
            text="",
            anchor=CENTER,
            width=4,
            fg=PNTCOL,
            bg=BGCOL,
            font=self.__app.font_lg,
        )
        self._lbl_activity = Label(
            self._frm_body, text="", anchor=CENTER, bg=BGCOL, fg=FGCOL
        )

    def _do_layout(self):
        """
        Layout widgets.
        """

        self._frm_body.grid(column=0, row=0, sticky=NSEW)
        self._btn_load.grid(column=0, row=0, ipadx=3, ipady=3, sticky=W)
        self._btn_save.grid(column=1, row=0, ipadx=3, ipady=3, sticky=W)
        self._btn_import.grid(column=2, row=0, ipadx=3, ipady=3, sticky=W)
        self._btn_play.grid(column=3, row=0, ipadx=3, ipady=3, sticky=W)
        self._btn_record.grid(column=4, row=0, ipadx=3, ipady=3, sticky=W)
        self._btn_undo.grid(column=5, row=0, ipadx=3, ipady=3, sticky=W)
        self._btn_delete.grid(column=6, row=0, ipadx=3, ipady=3, sticky=W)
        self._lbl_memory.grid(column=7, row=0, ipadx=3, ipady=3, sticky=W)
        self._lbl_activity.grid(column=0, row=2, columnspan=7, padx=3, sticky=EW)

        cols, rows = self.grid_size()
        for i in range(cols):
            self.grid_columnconfigure(i, weight=1)
        for i in range(rows):
            self.grid_rowconfigure(i, weight=1)
        self.option_add("*Font", self.__app.font_sm)

    def _attach_events(self):
        """
        Bind events to window.
        """

        self.container.bind("<Configure>", self._on_resize)

    def _reset(self):
        """
        Reset panel to initial settings
        """

        self._rec_status = STOP if self.__app.recording else RECORD
        self._on_record()
        self.update_count()

    def _set_configfile_path(self, ext: str = "bin") -> tuple:
        """
        Set configuration file path.

        :param str ext: file extension
        :return: file path
        :rtype: tuple
        """

        configpath = filedialog.askdirectory(
            parent=self.container, title=SAVETITLE, initialdir=HOME, mustexist=True
        )
        if configpath in ((), ""):
            return None, None  # User cancelled

        return set_filename(configpath, "config", ext)

    def _open_configfile(self):
        """
        Open configuration file.
        """

        return self.__app.file_handler.open_file(
            self,
            "bin",
            (
                ("config files", "*.bin"),
                ("TTY config files", "*.tty"),
                ("u-center UBX config files", "*.txt"),
                ("all files", "*.*"),
            ),
        )

    def _on_load(self):
        """
        Load commands from file into in-memory recording.
        """

        self._configfile = self._open_configfile()
        if self._configfile is None:  # user cancelled
            return

        self.__app.recorded_commands = None
        self.status_label = ("Loading commands...", INFOCOL)

        try:
            if self._configfile[-3:] == "txt":
                i = self._on_load_txt(self._configfile)
            elif self._configfile[-3:] == "tty":
                i = self._on_load_tty(self._configfile)
            else:
                i = self._on_load_ubx(self._configfile)
        except Exception:  # pylint: disable=broad-exception-caught
            i = 0
            self.status_label = (f"ERROR parsing {self._configfile}!", ERRCOL)

        self.update_count()
        if i > 0:
            fname = self._configfile.split("/")[-1]
            self.status_label = (
                f"{i} Command{'s' if i > 1 else ''} loaded from {fname}",
                OKCOL,
            )

    def _on_load_ubx(self, fname: str) -> int:
        """
        Load binary ubx configuration file

        :param str fname: input filename
        :return: no of items read
        :rtype: int
        """

        i = 0
        with open(fname, "rb") as file:
            ubr = UBXReader(file, msgmode=SET)
            eof = False
            while not eof:
                _, parsed = ubr.read()
                if parsed is not None:
                    self.__app.recorded_commands = parsed
                    i += 1
                else:
                    eof = True
        return i

    def _on_load_tty(self, fname: str) -> int:
        """
        Load binary TTY configuration file

        :param str fname: input filename
        :return: no of items read
        :rtype: int
        """

        i = 0
        with open(fname, "rb") as file:
            for line in file:
                self.__app.recorded_commands = line
                i += 1
        return i

    def _on_load_txt(self, fname: str) -> int:
        """
        Load u-center format text configuration file.

        Any messages other than CFG-MSG, CFG-PRT or CFG-VALGET are discarded.
        The CFG-VALGET messages are converted into CFG-VALGET.

        :param str fname: input file name
        :return: no of items read
        :rtype: int
        """

        i = 0
        with open(fname, "r", encoding="utf-8") as file:
            for line in file:
                parts = line.replace(" ", "").split("-")
                data = bytes.fromhex(parts[-1])
                cls = data[0:1]
                mid = data[1:2]
                if cls != CFG:
                    continue
                if mid == VALGET:
                    version = data[4:5]
                    layer = bytes2val(data[5:6], U1)
                    if layer == POLL_LAYER_BBR:
                        layers = SET_LAYER_BBR
                    elif layer == POLL_LAYER_FLASH:
                        layers = SET_LAYER_FLASH
                    else:
                        layers = SET_LAYER_RAM
                    layers = val2bytes(layers, U1)
                    transaction = val2bytes(TXN_NONE, U1)  # not transactional
                    reserved0 = b"\x00"
                    cfgdata = data[8:]
                    payload = version + layers + transaction + reserved0 + cfgdata
                    parsed = UBXMessage(CFG, VALSET, SET, payload=payload)
                else:  # legacy CFG command
                    parsed = UBXMessage(CFG, mid, SET, payload=data[4:])
                if parsed is not None:
                    self.__app.recorded_commands = parsed
                    i += 1
        return i

    def _on_save(self):
        """
        Save commands from in-memory recording to file.
        """

        if self._rec_status == RECORD:
            return

        if len(self.__app.recorded_commands) == 0:
            self.status_label = ("Nothing to save", ERRCOL)
            return

        ext = "tty" if self.__app.recording_type == TTYONLY else "bin"
        fname, self._configfile = self._set_configfile_path(ext)
        if self._configfile is None:  # user cancelled
            return

        self.status_label = ("Saving commands...", INFOCOL)
        i = 0
        with open(self._configfile, "wb") as file:
            for i, msg in enumerate(self.__app.recorded_commands):
                if isinstance(msg, (UBXMessage, NMEAMessage)):
                    msg = msg.serialize()
                file.write(msg)
        self.__app.recorded_commands = None
        self.update_count()
        self.status_label = (
            f"{i + 1} command{'s' if i > 0 else ''} saved to {fname}",
            OKCOL,
        )

    def _on_play(self):
        """
        Send commands to device from in-memory recording.
        """

        if self._rec_status == RECORD:
            return

        if len(self.__app.recorded_commands) == 0:
            self.status_label = ("Nothing to send", ERRCOL)
            return

        i = 0
        if self._rec_status == STOP:
            self._rec_status = PLAY
            for i, msg in enumerate(self.__app.recorded_commands):
                mid = getattr(self.__app.recorded_commands[-1], "identity", "tty")
                self.status_label = (f"{i} Sending {mid}", INFOCOL)
                if isinstance(msg, (UBXMessage, NMEAMessage)):
                    msg = msg.serialize()
                self.__app.send_to_device(msg)
                sleep(0.01)
            self._rec_status = STOP
        self.status_label = (
            f"{i + 1} command{'s' if i > 0 else ''} sent to device",
            OKCOL,
        )

        self._update_status()

    def _on_record(self):
        """
        Add commands to in-memory recording.
        """

        if self._rec_status == STOP:
            self._rec_status = RECORD
            self.__app.recording = True
            # start flashing record label...
            self._stop_event.clear()
            Thread(
                target=self._flash_record,
                daemon=True,
                args=(self._stop_event,),
            ).start()
        elif self._rec_status == RECORD:
            self._stop_event.set()
            self._rec_status = STOP
            self.__app.recording = False

        stat = "started" if self._rec_status else "stopped"
        self.status_label = (f"Recording {stat}", INFOCOL)
        self._update_status()

    def _on_import(self):
        """
        Import commands as presets.

        NB: Assumes all commands in a single recording are of the
        same type (i.e. UBX, NMEA or TTY).
        """

        if self._rec_status == RECORD:
            return

        if len(self.__app.recorded_commands) == 0:
            self.status_label = ("Nothing to import", ERRCOL)
            return

        try:
            now = f'Recorded commands {datetime.now().strftime("%Y-%m-%d_%H:%M:%S")}'
            if isinstance(self.__app.recorded_commands[0], UBXMessage):
                self.__app.configuration.get("ubxpresets_l").append(
                    ubx2preset(self.__app.recorded_commands, now)
                )
                typ = "UBX"
            elif isinstance(self.__app.recorded_commands[0], NMEAMessage):
                self.__app.configuration.get("nmeapresets_l").append(
                    nmea2preset(self.__app.recorded_commands, now)
                )
                typ = "NMEA"
            else:  # tty
                self.__app.configuration.get("ttypresets_l").append(
                    tty2preset(self.__app.recorded_commands, now)
                )
                typ = "TTY"

            self.status_label = (
                f"{len(self.__app.recorded_commands)} commands imported as {typ} presets",
                OKCOL,
            )
        except AttributeError:
            self.status_label = (
                "Recorded commands must be of same type",
                ERRCOL,
            )

    def _on_undo(self):
        """
        Remove last record from in-memory recording.
        """

        if len(self.__app.recorded_commands) == 0:
            self.status_label = ("Nothing to undo", ERRCOL)
            return

        if self._rec_status == STOP:
            if len(self.__app.recorded_commands) > 0:
                self.__app.recorded_commands = UNDO
                self.status_label = ("Last command undone", INFOCOL)

        self.update_count()

    def _on_delete(self):
        """
        Delete all records in in-memory recording.
        """

        if self._rec_status == RECORD:
            return

        lcs = len(self.__app.recorded_commands)
        if lcs == 0:
            self.status_label = ("Nothing to delete", ERRCOL)
            return

        self.__app.recorded_commands = None
        self.status_label = (f"{lcs} command{'s' if lcs > 1 else ''} deleted", INFOCOL)

        self.update_count()

    def _update_status(self):
        """
        Update recording status.
        """

        pimg = rimg = None
        if self._rec_status == STOP:
            pimg = self._img_play
            rimg = self._img_record
        elif self._rec_status == PLAY:
            pimg = self._img_stop
            rimg = self._img_record
        elif self._rec_status == RECORD:
            pimg = self._img_play
            rimg = self._img_stop
        self._btn_play.config(image=pimg)
        self._btn_record.config(image=rimg)

    def update_count(self):
        """
        Update command count.
        """

        self._lbl_memory.config(text=len(self.__app.recorded_commands))

    def _flash_record(self, stop: Event):
        """
        THREADED
        Flash record indicator for conspicuity.
        """

        try:
            cols = [("white", ERRCOL), (ERRCOL, "white")]
            i = 0
            while not stop.is_set():
                i = not i
                self._lbl_activity.config(
                    text="RECORDING", fg=cols[i][0], bg=cols[i][1]
                )
                sleep(FLASH)
            self._lbl_activity.config(text="", fg=FGCOL, bg=BGCOL)
        except TclError:  # if dialog closed without stopping recording
            pass
