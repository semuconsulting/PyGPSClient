"""
console_frame.py

Console frame class for PyGPSClient application.

This handles a scrollable text box into which the serial data is printed.

*** Remember that tcl indices look like floats but they're not! ***
("1.0:, "2.0") signifies "from the first character in
line 1 (inclusive) to the first character in line 2 (exclusive)"
i.e. the first line

Created on 12 Sep 2020

:author: semuadmin
:copyright: 2020 SEMU Consulting
:license: BSD 3-Clause
"""

from tkinter import END, HORIZONTAL, NONE, VERTICAL, E, Frame, N, S, Scrollbar, Text, W

from pyubx2 import hextable

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
    WIDGETU3,
)
from pygpsclient.strings import HALTTAGWARN

HALT = "HALT"
CONSOLELINES = 20


class ConsoleFrame(Frame):
    """
    Console frame class.
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

        def_w, def_h = WIDGETU3
        self.width = kwargs.get("width", def_w)
        self.height = kwargs.get("height", def_h)
        self._colortags = self.__app.configuration.get("colortags_l")
        self._body()
        self._do_layout()
        self._attach_events()
        self._halt = ""

    def _body(self):
        """
        Set up frame and widgets.
        """

        self.option_add("*Font", self.__app.font_sm)
        self._console_fg = FGCOL
        self._console_bg = BGCOL
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.sblogv = Scrollbar(self, orient=VERTICAL)
        self.sblogh = Scrollbar(self, orient=HORIZONTAL)
        self.txt_console = Text(
            self,
            bg=self._console_bg,
            fg=self._console_fg,
            yscrollcommand=self.sblogv.set,
            xscrollcommand=self.sblogh.set,
            wrap=NONE,
            height=15,
        )
        self.sblogh.config(command=self.txt_console.xview)
        self.sblogv.config(command=self.txt_console.yview)

        # making the textbox read only and fixed width font
        self.txt_console.configure(state="disabled")

        # set up color tagging
        for match, color in self._colortags:
            if color == HALT:
                color = ERRCOL
                match = HALT
            self.txt_console.tag_config(match, foreground=color)

    def _do_layout(self):
        """
        Set position of widgets in frame
        """

        self.txt_console.grid(column=0, row=0, pady=1, padx=1, sticky=(N, S, E, W))
        self.sblogv.grid(column=1, row=0, sticky=(N, S, E))
        self.sblogh.grid(column=0, row=1, sticky=(S, E, W))

    def _attach_events(self):
        """
        Bind events to frame
        """

        self.bind("<Configure>", self._on_resize)
        self.txt_console.bind("<Double-Button-1>", self._on_clipboard)
        self.txt_console.bind("<Double-Button-2>", self._on_clipboard)
        self.txt_console.bind("<Double-Button-3>", self._on_clipboard)
        # self.txt_console.tag_bind(HALT, "<1>", self._on_halt) # doesn't seem to work on MacOS

    def update_frame(self, consoledata: list):
        """
        Print the latest data stream to the console in raw (NMEA) or
        parsed (key,value pair) format.

        'maxlines' defines the maximum number of scrollable lines that are
        retained in the text box on a FIFO basis.

        :param list consoledata: list of tuples (raw, parsed, marker) \
            accumulated since last console update
        """

        con = self.txt_console
        consoleformat = self.__app.configuration.get("consoleformat_s")
        colortagging = self.__app.configuration.get("colortag_b")
        maxlines = self.__app.configuration.get("maxlines_n")
        autoscroll = self.__app.configuration.get("autoscroll_b")
        self._halt = ""
        consolestr = ""
        con.configure(font=FONT_TEXT)
        for raw_data, parsed_data, marker in consoledata:
            if consoleformat == FORMAT_BINARY:
                data = f"{marker}{raw_data}".strip("\n")
            elif consoleformat == FORMAT_HEXSTR:
                data = f"{marker}{raw_data.hex()}"
            elif consoleformat == FORMAT_HEXTAB:
                con.configure(font=FONT_FIXED)
                data = hextable(raw_data)
            elif consoleformat == FORMAT_BOTH:
                con.configure(font=FONT_FIXED)
                data = f"{marker}{parsed_data}\n{hextable(raw_data)}"
            else:
                data = f"{marker}{parsed_data}"
            consolestr += data + "\n"

        numlinesbefore = self.numlines
        con.configure(state="normal")
        con.insert(END, consolestr)

        if colortagging:
            self._tag_line(con, numlinesbefore, self.numlines)
            if self._halt != "":
                self._on_halt(None)

        while self.numlines > maxlines:
            con.delete("1.0", "2.0")  # delete top line

        if autoscroll:
            con.see("end")
        con.configure(state="disabled")
        self.update_idletasks()

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

    @property
    def numlines(self) -> int:
        """
        Get number of lines in console.

        :return: nmber of lines
        :type: int
        """

        return int(self.txt_console.index("end-1c").split(".", 1)[0])

    def _on_halt(self, event):  # pylint: disable=unused-argument
        """
        Halt streaming.

        :param event event: HALT event
        """

        self.__app.stream_handler.stop_read_thread()
        self.__app.set_status(HALTTAGWARN.format(self._halt), ERRCOL)
        self.__app.conn_status = DISCONNECTED

    def _on_clipboard(self, event):  # pylint: disable=unused-argument
        """
        Copy console content to clipboard.

        :param event event: double click event
        """

        self.__master.clipboard_clear()
        self.__master.clipboard_append(self.txt_console.get("1.0", END))
        self.__master.update()

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
