"""
Console frame class for PyGPSClient application.

This handles a scrollable text box into which the serial data is printed.

Created on 12 Sep 2020

:author: semuadmin
:copyright: SEMU Consulting © 2020
:license: BSD 3-Clause
"""
# pylint: disable=invalid-name

from tkinter import Frame, Text, Scrollbar, S, E, W, END, HORIZONTAL, VERTICAL, N
from pyubx2 import hextable
from pygpsclient.globals import (
    BGCOL,
    FGCOL,
    FORMATS,
    FONT_TEXT,
    FONT_FIXED,
)


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
        self.__master = self.__app.get_master()  # Reference to root class (Tk)

        Frame.__init__(self, self.__master, *args, **kwargs)

        self.width, self.height = self.get_size()
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
        self.width, self.height = self.get_size()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.sblogv = Scrollbar(self, orient=VERTICAL)
        self.sblogh = Scrollbar(self, orient=HORIZONTAL)
        self.txt_console = Text(
            self,
            bg=self._console_bg,
            fg=self._console_fg,
            yscrollcommand=self.sblogv.set,
            xscrollcommand=self.sblogh.set,
            wrap="none",
        )
        self.sblogh.config(command=self.txt_console.xview)
        self.sblogv.config(command=self.txt_console.yview)
        # Making the textbox read only and fixed width font
        self.txt_console.configure(font=FONT_FIXED, state="disabled")

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

    def update_console(self, raw_data, parsed_data):
        """
        Print the latest data stream to the console in raw (NMEA) or
        parsed (key,value pair) format.

        'maxlines' defines the maximum number of scrollable lines that are
        retained in the text box on a FIFO basis.

        :param str data: data from input stream

        """

        self._halt = ""
        self.txt_console.configure(font=FONT_FIXED)
        if self.__app.frm_settings.display_format == FORMATS[1]:  # binary
            data = str(raw_data).strip("\n")
        elif self.__app.frm_settings.display_format == FORMATS[2]:  # hex string
            data = str(raw_data.hex())
        elif self.__app.frm_settings.display_format == FORMATS[3]:  # hex tabular
            data = hextable(raw_data)
        else:
            self.txt_console.configure(font=FONT_TEXT)
            data = str(parsed_data)

        con = self.txt_console
        con.configure(state="normal")
        con.insert(END, data + "\n")

        # format of this list of tuples is (tag, highlight color)
        if self.__app.frm_settings.colortagging:
            self._tag_line(data, self.__app.colortags)
            if self._halt != "":
                self.__app.stream_handler.stop_read_thread()
                self.__app.set_status(f"Halted on user tag match: {self._halt}", "red")

        idx = float(con.index("end"))  # Lazy but it works
        if idx > self.__app.frm_settings.maxlines:
            # Remember these tcl indices look like floats but they're not!
            # ("1.0:, "2.0") signifies "from the first character in
            # line 1 (inclusive) to the first character in line 2 (exclusive)"
            # i.e. delete the first line
            con.delete("1.0", "2.0")

        # con.update_idletasks()
        if self.__app.frm_settings.autoscroll:
            con.see("end")
        con.configure(state="disabled")

    def _tag_line(self, line, tags):
        """
        Highlights any occurrence of tags in line - each tag
        must be a tuple of (search term, highlight color)

        :param str line: line in console
        :param tuple tags: (search term, highlight color)

        """

        con = self.txt_console
        idx = con.index("end-1c")
        last = int(idx[0 : idx.find(".")]) - 1

        for count, tag in enumerate(tags):
            match, color = tag
            start = line.find(match)
            end = start + len(match)

            if start != -1:  # If search string found in line
                # "HALT" tag terminates stream
                if color == "HALT":
                    self._halt = match
                    color = "red"
                con.tag_add(count, f"{last}.{start}", f"{last}.{end}")
                con.tag_config(count, foreground=color)

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
        return (self.winfo_width(), self.winfo_height())
