"""
UBX Player/Recorder widget for CFG commands entered by user via UBX
Configuration panel.

Records commands to memory array and allows user to load or save
this array to or from a file.

Facilitates copying configuration from one device to another.

Created on 9 Jan 2023

:author: semuadmin
:copyright: SEMU Consulting © 2023
:license: BSD 3-Clause
"""

from threading import Event, Thread
from time import sleep
from tkinter import Button, E, Frame, Label, TclError, W, filedialog

from PIL import Image, ImageTk
from pyubx2 import (
    POLL_LAYER_BBR,
    POLL_LAYER_FLASH,
    SET,
    SET_LAYER_BBR,
    SET_LAYER_FLASH,
    SET_LAYER_RAM,
    TXN_NONE,
    U1,
    UBX_PROTOCOL,
    UBXMessage,
    UBXReader,
    bytes2val,
    val2bytes,
)

from pygpsclient.globals import (
    HOME,
    ICON_DELETE,
    ICON_LOAD,
    ICON_RECORD,
    ICON_SAVE,
    ICON_SEND,
    ICON_STOP,
    ICON_UNDO,
)
from pygpsclient.helpers import set_filename
from pygpsclient.strings import LBLCFGRECORD, READTITLE, SAVETITLE

STOP = 0
PLAY = 1
RECORD = 2
FLASH = 0.7
CFG = b"\x06"
VALSET = b"\x8a"
VALGET = b"\x8b"


class UBX_Recorder_Frame(Frame):
    """
    UBX Configuration command recorder panel.
    """

    def __init__(self, app, container, *args, **kwargs):
        """
        Constructor.

        :param Frame app: reference to main tkinter application
        :param Frame container: reference to container frame (config-dialog)
        :param args: optional args to pass to Frame parent class
        :param kwargs: optional kwargs to pass to Frame parent class
        """

        self.__app = app  # Reference to main application class
        self.__master = self.__app.appmaster  # Reference to root class (Tk)
        self.__container = container  # Reference to UBX Configuration dialog

        Frame.__init__(self, self.__container.container, *args, **kwargs)

        self._img_load = ImageTk.PhotoImage(Image.open(ICON_LOAD))
        self._img_save = ImageTk.PhotoImage(Image.open(ICON_SAVE))
        self._img_play = ImageTk.PhotoImage(Image.open(ICON_SEND))
        self._img_stop = ImageTk.PhotoImage(Image.open(ICON_STOP))
        self._img_record = ImageTk.PhotoImage(Image.open(ICON_RECORD))
        self._img_undo = ImageTk.PhotoImage(Image.open(ICON_UNDO))
        self._img_delete = ImageTk.PhotoImage(Image.open(ICON_DELETE))
        self._cmds_stored = []
        self._rec_status = STOP
        self._configfile = None
        self._stop_event = Event()
        self._bg = self.cget("bg")  # default background color
        self._configfile = None
        self._configpath = None

        self._body()
        self._do_layout()
        self.reset()

    def _body(self):
        """
        Set up frame and widgets.
        """

        self._lbl_recorder = Label(self, text=LBLCFGRECORD, anchor="w")

        self._btn_load = Button(
            self,
            image=self._img_load,
            width=40,
            command=self._on_load,
            font=self.__app.font_md,
        )
        self._btn_save = Button(
            self,
            image=self._img_save,
            width=40,
            command=self._on_save,
            font=self.__app.font_md,
        )
        self._btn_play = Button(
            self,
            image=self._img_play,
            width=40,
            command=self._on_play,
            font=self.__app.font_md,
        )
        self._btn_record = Button(
            self,
            image=self._img_record,
            width=40,
            command=self._on_record,
            font=self.__app.font_md,
        )
        self._btn_undo = Button(
            self,
            image=self._img_undo,
            width=40,
            command=self._on_undo,
            font=self.__app.font_md,
        )
        self._btn_delete = Button(
            self,
            image=self._img_delete,
            width=40,
            command=self._on_delete,
            font=self.__app.font_md,
        )
        self._lbl_status = Label(self, text="", anchor="center")
        self._lbl_activity = Label(self, text="", anchor="center")

    def _do_layout(self):
        """
        Layout widgets.
        """

        self._lbl_recorder.grid(column=0, row=0, columnspan=6, padx=3, sticky=(W, E))
        self._btn_load.grid(column=0, row=1, ipadx=3, ipady=3, sticky=W)
        self._btn_save.grid(column=1, row=1, ipadx=3, ipady=3, sticky=W)
        self._btn_play.grid(column=2, row=1, ipadx=3, ipady=3, sticky=W)
        self._btn_record.grid(column=3, row=1, ipadx=3, ipady=3, sticky=W)
        self._btn_undo.grid(column=4, row=1, ipadx=3, ipady=3, sticky=W)
        self._btn_delete.grid(column=5, row=1, ipadx=3, ipady=3, sticky=W)
        self._lbl_status.grid(column=0, row=2, columnspan=6, padx=3, sticky=(W, E))
        self._lbl_activity.grid(column=0, row=3, columnspan=6, padx=3, sticky=(W, E))

        (cols, rows) = self.grid_size()
        for i in range(cols):
            self.grid_columnconfigure(i, weight=1)
        for i in range(rows):
            self.grid_rowconfigure(i, weight=1)
        self.option_add("*Font", self.__app.font_sm)

    def reset(self):
        """
        Reset panel to initial settings
        """

        self._rec_status = STOP
        self._update_status()

    def _set_configfile_path(self) -> tuple:
        """
        Set configuration file path.

        :return: file path
        :rtype: tuple
        """

        configpath = filedialog.askdirectory(
            parent=self.__container, title=SAVETITLE, initialdir=HOME, mustexist=True
        )
        if configpath in ((), ""):
            return None, None  # User cancelled

        return set_filename(configpath, "config", "ubx")

    def _open_configfile(self):
        """
        Open configuration file.
        """

        self._configfile = filedialog.askopenfilename(
            parent=self.__container,
            title=READTITLE,
            initialdir=HOME,
            defaultextension="ubx",
            filetypes=(
                ("ubx config files", "*.ubx"),
                ("u-center config files", "*.txt"),
                ("all files", "*.*"),
            ),
        )
        if self._configfile in ((), ""):
            return None  # User cancelled
        return self._configfile

    def _on_load(self):
        """
        Load commands from file into in-memory recording.
        """

        self._configfile = self._open_configfile()
        if self._configfile is None:  # user cancelled
            return

        self._cmds_stored = []
        self._update_activity("Loading commands...")

        if self._configfile[-3:] == "txt":
            i = self._on_load_txt(self._configfile)
        else:
            i = self._on_load_ubx(self._configfile)

        if i > 0:
            fname = self._configfile.split("/")[-1]
            self._update_activity(
                f"{i} Command{'s' if i > 1 else ''} loaded from {fname}"
            )

        self._update_status()

    def _on_load_ubx(self, fname: str) -> int:
        """
        Load binary ubx configuration file

        :param str fname: input filename
        :return: no of items read
        :rtype: int
        """

        try:
            with open(fname, "rb") as file:
                ubr = UBXReader(file, protfilter=UBX_PROTOCOL, msgmode=SET)
                eof = False
                i = 0
                while not eof:
                    _, parsed = ubr.read()
                    if parsed is not None:
                        self._cmds_stored.append(parsed)
                        i += 1
                    else:
                        eof = True
        except Exception:  # pylint: disable=broad-exception-caught
            self._update_activity(f"ERROR parsing {fname}!")
            return 0

        return i

    def _on_load_txt(self, fname: str) -> int:
        """
        Load u-center format text configuration file.

        Any messages other than CFG-VALGET (0x068b) are discarded.
        The CFG-VALGET messages are converted into CFG-VALGET.

        :param str fname: input file name
        :return: no of items read
        :rtype: int
        """

        try:
            with open(fname, "r", encoding="utf-8") as file:
                i = 0
                for line in file:
                    parts = line.replace(" ", "").split("-")
                    data = bytes.fromhex(parts[-1])
                    cls = data[0:1]
                    mid = data[1:2]
                    if cls != CFG or mid != VALGET:
                        continue
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
                    if parsed is not None:
                        self._cmds_stored.append(parsed)
                        i += 1
        except Exception:  # pylint: disable=broad-exception-caught
            self._update_activity(f"ERROR parsing {fname}!")
            return 0

        return i

    def _on_save(self):
        """
        Save commands from in-memory recording to file.
        """

        if self._rec_status == RECORD:
            return

        if len(self._cmds_stored) == 0:
            self._update_activity("Nothing to save")
            return

        fname, self._configfile = self._set_configfile_path()
        if self._configfile is None:
            return

        self._update_activity("Saving commands...")
        with open(self._configfile, "wb") as file:
            i = 0
            for i, msg in enumerate(self._cmds_stored):
                file.write(msg.serialize())
        self._cmds_stored = []
        self._update_activity(f"{i + 1} command{'s' if i > 0 else ''} saved to {fname}")
        self._update_status()

    def _on_play(self):
        """
        Send commands to device from in-memory recording.
        """

        if self._rec_status == RECORD:
            return

        if len(self._cmds_stored) == 0:
            self._update_activity("Nothing to send")
            return

        if self._rec_status == STOP:
            self._rec_status = PLAY
            i = 0
            for i, msg in enumerate(self._cmds_stored):
                self._update_activity(f"{i} Sending {msg.identity}")
                self.__app.gnss_outqueue.put(msg.serialize())
                sleep(0.01)
            self._update_activity(
                f"{i + 1} command{'s' if i > 0 else ''} sent to device"
            )
            self._rec_status = STOP
        self._update_status()

    def _on_record(self):
        """
        Add commands to in-memory recording.
        """

        if self._rec_status == STOP:
            self._rec_status = RECORD
            self.__container.recordmode = True
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
            self.__container.recordmode = False
            self._update_activity("Recording stopped")
        self._update_status()

    def _on_undo(self):
        """
        Remove last record from in-memory recording.
        """

        if len(self._cmds_stored) == 0:
            self._update_activity("Nothing to undo")
            return

        if self._rec_status == STOP:
            if len(self._cmds_stored) > 0:
                self._cmds_stored.pop()
                self._update_activity("Last command undone")
                self._update_status()

    def _on_delete(self):
        """
        Delete all records in in-memory recording.
        """

        if self._rec_status == RECORD:
            return

        if len(self._cmds_stored) == 0:
            self._update_activity("Nothing to delete")
            return

        i = len(self._cmds_stored)
        self._update_activity(f"{i} command{'s' if i > 1 else ''} deleted")
        self._cmds_stored = []
        self._update_status()

    def _update_status(self):
        """
        Update status label.
        """

        lcs = len(self._cmds_stored)
        lst = f". Last command: {self._cmds_stored[-1].identity}" if lcs > 0 else ""
        self._lbl_status.config(text=f"Commands in memory: {lcs}{lst}")

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

    def _update_activity(self, msg: str):
        """
        Update activity label.

        :param str msg: message
        """

        if len(msg) > 55:
            msg = f"{msg[0:30]}...{msg[-22:]}"
        self._lbl_activity.config(text=msg)

    def update_record(self, msg: UBXMessage):
        """
        Add UBX CFG SET command to in-memory recording.

        :param UBXMessage msg: message to record
        """

        if msg.msgmode == SET:
            self._cmds_stored.append(msg)
            self._update_status()

    def _flash_record(self, stop: Event):
        """
        THREADED
        Flash record indicator for conspicuity.
        """

        try:
            cols = [("white", "red"), ("red", "white")]
            i = 0
            while not stop.is_set():
                i = not i
                self._lbl_activity.config(
                    text="RECORDING", fg=cols[i][0], bg=cols[i][1]
                )
                sleep(FLASH)
        except TclError:  # if dialog closed without stopping recording
            pass
