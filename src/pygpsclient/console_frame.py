"""
console_frame.py

Console frame class for PyGPSClient application.

This handles a scrollable text box into which the serial data is printed.

*** Remember that tcl indices look like floats but they're not! ***
("1.0:, "2.0") signifies "from the first character in
line 1 (inclusive) to the first character in line 2 (exclusive)"
i.e. the first line

Created on 12 Sep 2020

:author: semuadmin (Steve Smith)
:copyright: 2020 semuadmin
:license: BSD 3-Clause
"""

from queue import Empty
from tkinter import (
    DISABLED,
    END,
    NONE,
    NSEW,
    Frame,
    Tk,
)

from PIL import Image, ImageTk

from pygpsclient.custom_classes import ScrollableText
from pygpsclient.globals import (
    BGCOL,
    DISCONNECTED,
    ERRCOL,
    FGCOL,
    FONT_FIXED,
    FONT_TEXT,
    FORMAT_BINARY,
    FORMAT_BOTH,
    FORMAT_HEXSTR,
    FORMAT_HEXTAB,
    FORMAT_PARSED,
    HALT,
    ICON_CLIPBOARD,
    WIDGETU3,
)
from pygpsclient.helpers import hextable
from pygpsclient.strings import HALTTAGWARN


class ConsoleFrame(Frame):
    """
    Console frame class.
    """

    def __init__(self, app: Tk, parent: Frame, *args, **kwargs):
        """
        Constructor.

        :param Tk app: reference to main tkinter application
        :param Frame parent: reference to parent frame
        :param args: optional args to pass to Frame parent class
        :param kwargs: optional kwargs to pass to Frame parent class
        """

        self.__app = app  # Reference to main application class

        super().__init__(parent, *args, **kwargs)

        def_w, def_h = WIDGETU3
        self.width = kwargs.get("width", def_w)
        self.height = kwargs.get("height", def_h)
        self._colortags = self.__app.configuration.get("colortags_l")
        self._img_clipboard = ImageTk.PhotoImage(
            Image.open(ICON_CLIPBOARD).resize((16, 16))
        )
        self._body()
        self._do_layout()
        self._attach_events()
        self._halt = ""

    def _body(self):
        """
        Set up frame and widgets.
        """

        self._frm_console = ScrollableText(
            self.__app,
            self.__app,
            self,
            state=DISABLED,
            bg=BGCOL,
            fg=FGCOL,
            wrap=NONE,
            height=15,
        )
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_rowconfigure(1, weight=0)

        # set up color tagging
        for match, color in self._colortags:
            if color == HALT:
                color = ERRCOL
                match = HALT
            self._frm_console.text.tag_config(match, foreground=color)

    def _do_layout(self):
        """
        Set position of widgets in frame
        """

        self._frm_console.grid(column=0, row=0, pady=1, padx=1, sticky=NSEW)

    def _attach_events(self):
        """
        Bind events to frame
        """

        self.bind("<Configure>", self._on_resize)
        self._frm_console.text.bind("<Double-Button-1>", self._frm_console.on_clipboard)
        self._frm_console.text.bind("<Double-Button-2>", self._frm_console.on_clipboard)
        self._frm_console.text.bind("<Double-Button-3>", self._frm_console.on_clipboard)
        # self.txt_console.tag_bind(HALT, "<1>", self._on_halt) # doesn't seem to work on MacOS

    def update_frame(self):
        """
        Print the formatted data stream to the console.

        'maxlines' defines the maximum number of scrollable lines that are
        retained in the text box on a FIFO basis.

        To minimise refresh latency, only the last 'maxlines' of queued
        messages are written to the console; the remainder are discarded.

        :param list consoledata: list of tuples (raw, parsed, marker) \
            accumulated since last console update
        """

        if not self.__app.configuration.get("autoscroll_b"):
            return

        consoleformat = self.__app.configuration.get("consoleformat_s")
        maxlines = self.__app.configuration.get("maxlines_n")
        self._halt = ""
        self._frm_console.text["font"] = (
            FONT_TEXT if consoleformat in (FORMAT_BINARY, FORMAT_PARSED) else FONT_FIXED
        )
        raw_data = None
        parsed_data = None
        lines = []
        while True:
            try:
                raw_data, parsed_data, marker = self.__app.console_outqueue.get(False)
                if self.__app.console_outqueue.qsize() < maxlines:
                    if consoleformat == FORMAT_BINARY:
                        lines.append(f"{marker}{raw_data}\n")
                    elif consoleformat == FORMAT_HEXSTR:
                        lines.append(f"{marker}{raw_data.hex()}\n")
                    elif consoleformat == FORMAT_HEXTAB:
                        lines += hextable(raw_data)
                    elif consoleformat == FORMAT_BOTH:
                        lines.append(f"{marker}{parsed_data}\n")
                        lines += hextable(raw_data)
                    else:
                        lines.append(f"{marker}{parsed_data}\n")
                self.__app.console_outqueue.task_done()
            except Empty:
                break

        consolestr = "".join(lines[-maxlines:])
        numlinesbefore = self._frm_console.numlines

        self._frm_console.state(True)  # enable text insertion
        if len(lines) >= maxlines:
            self._frm_console.set(consolestr, insert=0)
            numlinesbefore = 0
        else:
            excess = self._frm_console.numlines + len(lines) - maxlines
            if excess > 0:
                self._frm_console.set(consolestr, insert=excess)
                numlinesbefore -= excess
            else:
                self._frm_console.set(consolestr, insert=-1)

        if self.__app.configuration.get("colortag_b"):
            self._tag_line(
                self._frm_console.text, numlinesbefore, self._frm_console.numlines
            )
            if self._halt != "":
                self.__app.conn_status = DISCONNECTED
                self.__app.set_status_label(HALTTAGWARN.format(self._halt), ERRCOL)

        self._frm_console.state(False)  # disable text insertion

    def _tag_line(self, con, startline: int, endline: int):
        """
        Highlights any occurrence of tags in line - each tag
        must be a tuple of (search term, highlight color)

        :param object con: console textbox
        :param int startline: starting line
        :param int endline: ending line
        :param str string: string in console

        """

        for lineidx in range(startline - 1, endline):
            for match, color in self._colortags:
                line = con.get(f"{lineidx}.0", END)
                start = line.find(match)
                end = start + len(match)
                if start != -1:  # If search string found in line
                    if color.upper() == HALT:  # "HALT" tag terminates stream
                        self._halt = match
                        match = HALT
                    con.tag_add(match, f"{lineidx}.{start}", f"{lineidx}.{end}")

    def _on_resize(self, event):  # pylint: disable=unused-argument
        """
        Resize frame

        :param event event: resize event
        """

        self.width, self.height = self.get_size()

    def get_size(self):
        """
        Get current object size.

        :return: window size (width, height)
        :rtype: tuple
        """

        self.update_idletasks()  # Make sure we know about any resizing
        return self.winfo_width(), self.winfo_height()
