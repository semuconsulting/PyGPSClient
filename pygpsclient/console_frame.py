"""
Console frame class for PyGPSClient application.

This handles a scrollable text box into which the serial data is printed.

Created on 12 Sep 2020

@author: semuadmin
"""
# pylint: disable=invalid-name, too-many-instance-attributes, too-many-ancestors

from tkinter import Frame, Text, Scrollbar, S, E, W, END, HORIZONTAL, VERTICAL, N

from .globals import TAGS, BGCOL, FGCOL


class ConsoleFrame(Frame):
    """
    Frame inheritance class for plotting area.
    """

    def __init__(self, app, *args, **kwargs):
        """
        Constructor.

        :param object app: reference to main tkinter application
        """

        self.__app = app  # Reference to main application class
        self.__master = self.__app.get_master()  # Reference to root class (Tk)

        Frame.__init__(self, self.__master, *args, **kwargs)

        self.width, self.height = self.get_size()
        self._body()
        self._do_layout()
        self._attach_events()

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
        # Making the textbox read only
        self.txt_console.configure(state="disabled")

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

    def update_console(self, data):
        """
        Print the latest data stream to the console in raw (NMEA) or
        parsed (key,value pair) format.

        'maxlines' defines the maximum number of scrollable lines that are
        retained in the text box on a FIFO basis.

        :param str data
        """

        settings = self.__app.frm_settings.get_settings()
        con = self.txt_console
        con.configure(state="normal")
        con.insert(END, data + "\n")

        # format of this array of tuples is (tag, highlight color)
        self._tag_line(data, TAGS)

        idx = float(con.index("end"))  # Lazy but it works
        if idx > settings["maxlines"]:
            con.delete("1.0", "2.0")  # Remember these look like floats but they're not!

        con.update()
        if settings["autoscroll"]:
            con.see("end")
        con.configure(state="disabled")

    def _tag_line(self, line, tags):
        """
        Highlights any occurrence of tags in line - each tag
        must be a tuple of (search term, highlight color)

        :param str line
        :param tuple tags: (search term, highlight color)
        """

        con = self.txt_console
        idx = con.index("end-1c")
        last = int(idx[0 : idx.find(".")]) - 1

        for count, tag in enumerate(tags):
            match, color = tag
            connect = line.find(match)
            end = connect + len(match)

            if connect != -1:  # If search string found in line
                con.tag_add(count, f"{last}.{connect}", f"{last}.{end}")
                con.tag_config(count, foreground=color)

    def _on_resize(self, event):  # pylint: disable=unused-argument
        """
        Resize frame

        :param event
        """

        self.width, self.height = self.get_size()

    def get_size(self):
        """
        Get current object size.
        """

        self.update_idletasks()  # Make sure we know about any resizing
        return (self.winfo_width(), self.winfo_height())
