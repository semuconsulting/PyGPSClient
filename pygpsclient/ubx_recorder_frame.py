"""
UBX Recorder frame for CFG commands entered by user.

Records commands to memory array and allows user to load or save
this array to or from a file.

Created on 9 Jan 2023

:author: semuadmin
:copyright: SEMU Consulting © 2023
:license: BSD 3-Clause
"""
# pylint: disable=invalid-name, too-many-instance-attributes, too-many-ancestors

from time import sleep
from tkinter import (
    Frame,
    Button,
    Label,
    E,
    W,
)
from PIL import ImageTk, Image
from pyubx2 import (
    UBXReader,
    SET,
    UBX_PROTOCOL,
)
from pygpsclient.globals import (
    ICON_SEND,
    ICON_STOP,
    ICON_RECORD,
    ICON_UNDO,
    ICON_LOAD,
    ICON_SAVE,
)
from .strings import LBLCFGRECORD

STOP = 0
PLAY = 1
RECORD = 2


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
        self.__master = self.__app.get_master()  # Reference to root class (Tk)
        self.__container = container

        Frame.__init__(self, self.__container.container, *args, **kwargs)

        self._img_load = ImageTk.PhotoImage(Image.open(ICON_LOAD))
        self._img_save = ImageTk.PhotoImage(Image.open(ICON_SAVE))
        self._img_play = ImageTk.PhotoImage(Image.open(ICON_SEND))
        self._img_stop = ImageTk.PhotoImage(Image.open(ICON_STOP))
        self._img_record = ImageTk.PhotoImage(Image.open(ICON_RECORD))
        self._img_undo = ImageTk.PhotoImage(Image.open(ICON_UNDO))
        self._cmds_stored = []
        self._rec_status = STOP
        self._configfile = None

        self._body()
        self._do_layout()
        self._attach_events()
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
        self._lbl_status = Label(self, text="", fg="blue", anchor="w")
        self._lbl_activity = Label(self, text="", fg="red", anchor="w")

    def _do_layout(self):
        """
        Layout widgets.
        """

        self._lbl_recorder.grid(column=0, row=0, columnspan=6, padx=3, sticky=(W, E))
        self._btn_load.grid(column=0, row=1, ipadx=3, ipady=3, sticky=(W))
        self._btn_save.grid(column=1, row=1, ipadx=3, ipady=3, sticky=(W))
        self._btn_play.grid(column=2, row=1, ipadx=3, ipady=3, sticky=(W))
        self._btn_record.grid(column=3, row=1, ipadx=3, ipady=3, sticky=(W))
        self._btn_undo.grid(column=4, row=1, ipadx=3, ipady=3, sticky=(W))
        self._lbl_status.grid(column=0, row=2, columnspan=6, padx=3, sticky=(W, E))
        self._lbl_activity.grid(column=0, row=3, columnspan=6, padx=3, sticky=(W, E))

        (cols, rows) = self.grid_size()
        for i in range(cols):
            self.grid_columnconfigure(i, weight=1)
        for i in range(rows):
            self.grid_rowconfigure(i, weight=1)
        self.option_add("*Font", self.__app.font_sm)

    def _attach_events(self):
        """
        Bind events to widget.
        """

    def reset(self):
        """
        Reset panel to initial settings
        """

        self._rec_status = STOP
        self._update_activity()
        self._update_status()

    def _on_load(self):
        """
        Load commands from file into memory array.
        """

        self._configfile = self.__app.file_handler.open_configfile()
        if self._configfile is None:  # user cancelled
            return

        self._cmds_stored = []
        self._lbl_activity.config(text="Loading commands...", fg="blue")

        with open(self._configfile, "rb") as file:
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
        if i > 0:
            self._lbl_activity.config(text=f"{i} Commands loaded", fg="blue")

        self._update_status()

    def _on_save(self):
        """
        Save commands from memory array to file.
        """

        if len(self._cmds_stored) == 0:
            self._lbl_activity.config(text="Nothing to save", fg="red")
            return

        self._configfile = self.__app.file_handler.set_configfile_path()
        if self._configfile is None:
            return

        self._lbl_activity.config(text="Saving commands...", fg="blue")
        with open(self._configfile, "wb") as file:
            i = 0
            for i, msg in enumerate(self._cmds_stored):
                file.write(msg.serialize())
        self._cmds_stored = []
        self._lbl_activity.config(text=f"{i + 1} Commands saved", fg="blue")
        self._update_status()

    def _on_play(self):
        """
        Send commands to device from memory array.
        """

        if len(self._cmds_stored) == 0:
            self._lbl_activity.config(text="Nothing to send", fg="red")
            return

        if self._rec_status == STOP:
            self._rec_status = PLAY
            i = 0
            for i, msg in enumerate(self._cmds_stored):
                self._lbl_activity.config(
                    text=f"{i} Sending {msg.identity}", fg="green"
                )
                self.__app.stream_handler.serial_write(msg.serialize())
                sleep(0.01)
            self._lbl_activity.config(text=f"{i + 1} Commands sent", fg="green")
            self._rec_status = STOP
        self._update_status()
        self._update_activity()

    def _on_record(self):
        """
        Record commands to memory array.
        TODO NOT YET FULLY IMPLEMENTED
        """

        if self._rec_status == STOP:
            self._rec_status = RECORD
        elif self._rec_status == RECORD:
            self._rec_status = STOP
        self._update_activity()
        self._update_status()

    def _on_undo(self):
        """
        Remove last command from memory array.
        """

        if len(self._cmds_stored) == 0:
            self._lbl_activity.config(text="Nothing to undo", fg="red")
            return

        if self._rec_status == STOP:
            if len(self._cmds_stored) > 0:
                self._cmds_stored.pop()
                self._update_status()
                self._lbl_activity.config(text="Last command undone", fg="purple")

    def _update_status(self):
        """
        Update status label.
        """

        lcs = len(self._cmds_stored)
        lst = f" , Last Command: {self._cmds_stored[-1].identity}" if lcs > 0 else ""
        self._lbl_status.config(
            text=f"Commands Stored: {lcs}{lst}",
            fg="blue",
        )

    def _update_activity(self):
        """
        Update activity label.
        """

        if self._rec_status == RECORD:
            pimg = self._img_play
            rimg = self._img_stop
            atxt = "RECORDING"
            acol = "red"
        elif self._rec_status == STOP:
            pimg = self._img_play
            rimg = self._img_record
            atxt = "STOPPED"
            acol = "black"
        elif self._rec_status == PLAY:
            pimg = self._img_stop
            rimg = self._img_record
            atxt = "PLAYING"
            acol = "green"
        self._btn_play.config(image=pimg)
        self._btn_record.config(image=rimg)
        self._lbl_activity.config(text=atxt, fg=acol)
