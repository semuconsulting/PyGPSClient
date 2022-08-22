"""
UBX Configuration widget for user-selected CFG command

Allows user to receive and update configuration for any legacy CFG-*
command supported by the device which is not already supported by
another UBX configuration widget.

When a CFG command is selected from the listbox, a POLL request is sent to
the device to retrieve current attribute values, which are then used to populate
a series of dynamically generated entry widgets. The user can then amend the
values as required and send the updated set of values as a SET message to the
device. After sending, the current values will be polled again to confirm the
update has taken place. NB: this mechanism is dependent on receiving timely
POLL responses.

Created on 17 Aug 2022

:author: semuadmin
:copyright: SEMU Consulting © 2022
:license: BSD 3-Clause
"""
# pylint: disable=invalid-name, too-many-instance-attributes, too-many-ancestors

from tkinter import (
    Frame,
    Canvas,
    Listbox,
    Scrollbar,
    Entry,
    Button,
    Label,
    StringVar,
    LEFT,
    VERTICAL,
    N,
    S,
    E,
    W,
    END,
)
from PIL import ImageTk, Image
from pyubx2 import (
    UBXMessage,
    POLL,
    SET,
    UBX_PAYLOADS_SET,
    UBX_PAYLOADS_POLL,
    atttyp,
    nomval,
    X1,
    X2,
    X4,
    X6,
    X8,
    X24,
    U1,
)
from .globals import (
    ENTCOL,
    ICON_SEND,
    ICON_WARNING,
    ICON_PENDING,
    ICON_CONFIRMED,
    UBX_CFGOTHER,
)
from .strings import LBLCFGDYN

# dimensions of scrollable attribute window
SCROLLX = 300
SCROLLY = 300
# following CFG types exluded from selection, mainly because they're deprecated
# or catered for in other UBX config widgets.
CFG_EXCLUDED = (
    "CFG-DAT-NUM",
    "CFG-MSG",
    "CFG-NMEAv0",
    "CFG-NMEAvX",
    "CFG-PRT",
    "CFG-RATE",
    "CFG-VALDEL",
    "CFG-VALSET",
)


class UBX_Dynamic_Frame(Frame):
    """
    UBX dynamic configuration command panel.
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

        self._img_send = ImageTk.PhotoImage(Image.open(ICON_SEND))
        self._img_pending = ImageTk.PhotoImage(Image.open(ICON_PENDING))
        self._img_confirmed = ImageTk.PhotoImage(Image.open(ICON_CONFIRMED))
        self._img_warn = ImageTk.PhotoImage(Image.open(ICON_WARNING))
        self._cfg_id = ""  # identity of selected CFG command
        self._cfg_atts = {}  # this holds the attributes of the selected CFG command

        self._body()
        self._do_layout()
        self._attach_events()
        self.reset()

    def _body(self):
        """
        Set up frame and widgets.
        """

        self._lbl_cfg_dyn = Label(self, text=LBLCFGDYN, anchor="w")
        self._lbx_cfg_cmd = Listbox(
            self,
            border=2,
            relief="sunken",
            bg=ENTCOL,
            height=6,
            justify=LEFT,
            exportselection=False,
        )
        self._scr_cfg_cmd = Scrollbar(
            self, orient=VERTICAL, command=self._lbx_cfg_cmd.yview
        )
        self._lbx_cfg_cmd.config(yscrollcommand=self._scr_cfg_cmd.set)
        self._lbl_send_command = Label(self, image=self._img_pending)
        self._btn_send_command = Button(
            self,
            image=self._img_send,
            width=50,
            command=self._on_send_cfg,
            font=self.__app.font_md,
        )
        self._lbl_command = Label(self, text="", anchor="w")
        self._frm_container = Frame(self)
        self._can_container = Canvas(self._frm_container)
        self._frm_attrs = Frame(self._can_container)
        self._scr_container_ver = Scrollbar(
            self._frm_container, orient="vertical", command=self._can_container.yview
        )
        self._scr_container_hor = Scrollbar(
            self._frm_container, orient="horizontal", command=self._can_container.xview
        )
        self._can_container.config(
            yscrollcommand=self._scr_container_ver.set,
            xscrollcommand=self._scr_container_hor.set,
        )
        self._can_container.create_window(0, 0, window=self._frm_attrs, anchor="nw")

    def _do_layout(self):
        """
        Layout widgets.
        """

        self._lbl_cfg_dyn.grid(column=0, row=0, columnspan=4, padx=3, sticky=(W, E))
        self._lbx_cfg_cmd.grid(
            column=0, row=1, columnspan=2, rowspan=6, padx=3, pady=3, sticky=(W, E)
        )
        self._scr_cfg_cmd.grid(column=1, row=1, rowspan=6, sticky=(N, S, E))
        self._btn_send_command.grid(
            column=3, row=1, rowspan=3, ipadx=3, ipady=3, sticky=(W)
        )
        self._lbl_send_command.grid(
            column=3, row=4, rowspan=3, ipadx=3, ipady=3, sticky=(W)
        )
        self._lbl_command.grid(column=0, row=7, columnspan=4, padx=3, sticky=(W, E))
        self._frm_container.grid(
            column=0, row=8, columnspan=4, rowspan=15, padx=3, sticky=(N, S, W, E)
        )
        self._can_container.grid(
            column=0, row=0, columnspan=3, rowspan=15, padx=3, sticky=(N, S, W, E)
        )
        self._scr_container_ver.grid(column=3, row=0, rowspan=15, sticky=(N, S, E))
        self._scr_container_hor.grid(
            column=0, row=15, columnspan=4, rowspan=15, sticky=(W, E)
        )

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

        self._lbx_cfg_cmd.bind("<<ListboxSelect>>", self._on_select_cfg)
        self._frm_attrs.bind("<Configure>", self._setscroll)

    def reset(self):
        """
        Reset panel to initial settings
        """

        # populate CFG listbox with range of CFG message types
        self._lbx_cfg_cmd.delete(0, END)
        for i, cmd in enumerate(UBX_PAYLOADS_SET):
            if cmd[0:3] == "CFG" and cmd not in CFG_EXCLUDED:
                self._lbx_cfg_cmd.insert(i, cmd)

        self._clear_widgets()

    def _setscroll(self, event):  # pylint: disable=unused-argument
        """
        Set dynamic scroll region.
        """

        self._can_container.configure(
            scrollregion=self._can_container.bbox("all"),
            width=SCROLLX,
            height=SCROLLY,
        )

    def _on_select_cfg(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Handle CFG command selection - populate listbox with entry widgets
        corresponding to each attribute in CFG payload definition.
        """

        idx = self._lbx_cfg_cmd.curselection()
        self._cfg_id = self._lbx_cfg_cmd.get(idx)
        self._do_poll_cfg()
        self._lbl_command.config(text=self._cfg_id)

        self._clear_widgets()
        self._add_widgets(None, UBX_PAYLOADS_SET[self._cfg_id], 1, 0)
        self.update()

    def update_status(self, cfgtype, **kwargs):
        """
        Update dynamic entry fields from response to CFG POLL.

        TODO needs more work for repeating groups

        :param str cfgtype: identity of UBX CFG message
        :param kwargs: status keywords and values from UBX config message
        """

        if cfgtype == self._cfg_id:
            self._lbl_send_command.config(image=self._img_confirmed)
            self.__container.set_status(f"{cfgtype} GET message received", "green")
            msg = kwargs.get("msg", None)  # CFG POLL response message
            self._clear_widgets()
            self._add_widgets(msg, UBX_PAYLOADS_SET[self._cfg_id], 1, 0)
            self.update()
        elif cfgtype == "ACK-NAK":
            self.__container.set_status(f"{cfgtype} POLL message rejected", "red")
            self._lbl_send_command.config(image=self._img_warn)

    def _clear_widgets(self):
        """
        Clear dynamically generated widgets from listbox.
        """

        self._cfg_atts = {}
        wdgs = self._frm_attrs.grid_slaves()
        for wdg in wdgs:
            wdg.destroy()
        Label(self._frm_attrs, text="Attribute", width=12, anchor="w").grid(
            column=0, row=0, padx=3, sticky=(W)
        )
        Label(self._frm_attrs, text="Value", width=20, anchor="w").grid(
            column=1, row=0, padx=3, sticky=(W)
        )
        Label(self._frm_attrs, text="Type", width=5, anchor="w").grid(
            column=2, row=0, padx=3, sticky=(W)
        )

    def _add_widgets(self, msg: UBXMessage, pdict: dict, row: int, index: int) -> int:
        """
        Recursive routine to add entry widgets to listbox.

        :param UBXMessage msg: response to CFG POLL (if available)
        :param dict pdict: dict representing CFG SET payload definition
        :param int row: current row of listbox
        :returns: last row used
        :param int index: grouped item index
        :rtype: int
        """

        for nam, att in pdict.items():  # process each attribute in dict

            if isinstance(att, tuple):  # repeating group or bitfield
                numr, attd = att
                if numr in (
                    X1,
                    X2,
                    X4,
                    X6,
                    X8,
                    X24,
                ):  # bitfield
                    row = self._add_widgets(msg, attd, row, index)
                else:  # repeating group
                    if isinstance(numr, int):  # fixed length group
                        nr = numr
                    elif msg is None:  # no poll response => unknown length
                        nr = 1
                    else:  # variable length group, length known
                        nr = getattr(msg, numr, 1)
                    for idx in range(nr):
                        row = self._add_widgets_group(msg, nam, att, row, idx + 1)
            else:  # single attribute
                row = self._add_widgets_single(msg, nam, att, row, index)

        return row

    def _add_widgets_group(
        self, msg: UBXMessage, nam: str, att: object, row: int, index: int
    ) -> int:
        """
        Add widgets for group header.

        TODO needs more work for variable length repeating groups

        :param UBXMessage msg: response to CFG POLL (if available)
        :param str nam: attribute name
        :param object att: attribute type
        :param int row: current row in listbox
        :param int index: grouped item index
        :returns: last row used
        :rtype: int
        """

        numr, attd = att

        if index == 1:
            # if 'variable by size' group, add entry field to
            # allow user to specify size of group
            if numr == "None":
                self._cfg_atts[nam] = (StringVar(), U1)
                Label(self._frm_attrs, text="Group Size:").grid(
                    column=0, row=row, sticky=(E)
                )
                Entry(
                    self._frm_attrs,
                    readonlybackground=ENTCOL,
                    textvariable=self._cfg_atts[nam],
                    relief="sunken",
                    bg=ENTCOL,
                ).grid(column=1, row=row, sticky=(W))
                Label(self._frm_attrs, text=U1).grid(column=2, row=row, sticky=(W))
                row += 1
            # otherwise add label indicating the integer or existing attribute
            # which represents the group size
            else:
                Label(self._frm_attrs, text="Group Size:").grid(
                    column=0, row=row, sticky=(E)
                )
                Label(self._frm_attrs, text=numr).grid(column=1, row=row, sticky=(W))
                row += 1

            # # add spinbox to allow user to select which item
            # # within group is being updated
            # Label(self._frm_attrs, text="Group Index:").grid(
            #     column=0, row=row, sticky=(E)
            # )
            # Spinbox(
            #     self._frm_attrs,
            #     from_=0,
            #     to=numa,
            #     width=10,
            #     state=READONLY,
            #     readonlybackground=ENTCOL,
            # ).grid(column=1, row=row, sticky=(W))
            # row += 1
        row = self._add_widgets(msg, attd, row, index)

        return row

    def _add_widgets_single(
        self,
        msg: UBXMessage,
        nam: str,
        att: object,
        row: int,
        index: int,
    ) -> int:
        """
        Add Entry widget for single attribute.

        If a CFG POLL response is available, the Entry widget is
        prepopulated with the current value. If not, it's
        prepopulated with the nominal value for that attribute
        type e.g. 0, 0.0 or " ".

        :param UBXMessage msg: response to CFG POLL (if available)
        :param str nam: attribute name
        :param object att: attribute type
        :param int row: current row in listbox
        :param int index: grouped item index
        :returns: last row used
        :rtype: int
        """

        if nam[0:8] == "reserved":  # ignore reserved attributes
            return row

        if index > 0:
            nam += f"_{index:02d}"
        if isinstance(att, list):  # (type, scale factor)
            att = att[0]
        self._cfg_atts[nam] = (StringVar(), att)
        val = nomval(att)
        if msg is None:  # no poll response available
            self._cfg_atts[nam][0].set(val)
        else:  # set initial value from POLL response
            self._cfg_atts[nam][0].set(getattr(msg, nam, val))
        Label(self._frm_attrs, text=nam).grid(column=0, row=row, sticky=(E))
        Entry(
            self._frm_attrs,
            readonlybackground=ENTCOL,
            textvariable=self._cfg_atts[nam][0],
            relief="sunken",
            bg=ENTCOL,
        ).grid(column=1, row=row, sticky=(W))
        Label(self._frm_attrs, text=att).grid(column=2, row=row, sticky=(W))
        row += 1

        return row

    def _on_send_cfg(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Populate CFG SET message from entry fields on panel, send to device,
        then send CFG POLL to confirm update.
        """

        nam = ""
        ent = StringVar().set("")
        try:

            # create dict of attribute keyword arguments from
            # Entry fields
            vals = {}
            for (nam, (ent, att)) in self._cfg_atts.items():
                vals[nam] = self._get_val(ent, att)

            # create UBXMessage using these keyword arguments
            msg = UBXMessage("CFG", self._cfg_id, SET, **vals)

            # send message, update status and await response
            self.__app.stream_handler.serial_write(msg.serialize())
            self._lbl_send_command.config(image=self._img_pending)
            self.__container.set_status(f"{self._cfg_id} SET message sent", "blue")
            self.__container.set_pending(UBX_CFGOTHER, ("ACK-ACK", "ACK-NAK"))

            # POLL to confirm update
            self._do_poll_cfg()

        except ValueError:
            self.__container.set_status(
                f"ERROR! Invalid entry {nam}: {ent.get()}, {att}", "red"
            )

    def _do_poll_cfg(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Send CFG POLL request (if supported).
        """

        if self._cfg_id not in UBX_PAYLOADS_POLL:
            return

        msg = UBXMessage("CFG", self._cfg_id, POLL)
        self.__app.stream_handler.serial_write(msg.serialize())
        self._lbl_send_command.config(image=self._img_pending)
        self.__container.set_status(f"{self._cfg_id} POLL message sent", "blue")
        self.__container.set_pending(UBX_CFGOTHER, (self._cfg_id, "ACK-NAK"))

    def _get_val(self, ent: StringVar, att: str):
        """
        Convert Entry field to appropriate value.

        :param StringVar ent: entry string variable
        :param str att: attribute type e.g. 'U004'
        """

        val = ent.get()
        if atttyp(att) in ("E", "I", "L", "U", "X"):  # integer
            if val.find(".") != -1:  # ignore scaling decimals
                val = val[0 : val.find(".")]
            if val[0:2] == "0b":
                mod = 2
            elif val[0:2] == "0x":
                mod = 16
            else:
                mod = 10
            val = int(val, mod)
        elif atttyp(att) == "R":  # float
            val = float(val)

        return val
