"""
ubx_dynamic_frame.py

UBX Configuration widget for user-selected CFG command.

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
:copyright: 2020 SEMU Consulting
:license: BSD 3-Clause
"""

import logging
from tkinter import (
    ALL,
    END,
    LEFT,
    NW,
    VERTICAL,
    Button,
    Canvas,
    E,
    Entry,
    Frame,
    Label,
    Listbox,
    N,
    S,
    Scrollbar,
    StringVar,
    W,
)

from PIL import Image, ImageTk
from pynmeagps import IN, NMEA_PAYLOADS_POLL_PROP, NMEA_PAYLOADS_SET_PROP, NMEAMessage
from pyubx2 import (
    POLL,
    SET,
    UBX_PAYLOADS_POLL,
    UBX_PAYLOADS_SET,
    X1,
    X2,
    X4,
    X6,
    X8,
    X24,
    UBXMessage,
    atttyp,
)

from pygpsclient.globals import (
    ICON_CONFIRMED,
    ICON_PENDING,
    ICON_SEND,
    ICON_UNKNOWN,
    ICON_WARNING,
    NMEA_CFGOTHER,
    UBX_CFGOTHER,
)
from pygpsclient.helpers import stringvar2val
from pygpsclient.strings import LBLCFGGENERIC, LBLCFGGENERICNMEA

# dimensions of scrollable attribute window
SCROLLX = 300
SCROLLY = 300
# following CFG types excluded from selection...
CFG_EXCLUDED = (
    "CFG-DAT-NUM",  # deprecated
    "CFG-GEOFENCE",  # 'variable by size' groups not yet implemented - use pyubx2
    "CFG-MSG",  # handled via existing CFG-MSG panel
    "CFG-NMEAv0",  # deprecated
    "CFG-NMEAvX",  # deprecated
    "CFG-PRT",  # handled via existing CFG-PRT panel
    "CFG-RATE",  # handled via existing CFG-RATE panel
    "CFG-RINV",  # 'variable by size' groups not yet implemented - use pyubx2
    "CFG-VALDEL",  # handled via existing CFG-VALGET/SET/DEL panel
    "CFG-VALSET",  # handled via existing CFG-VALGET/SET/DEL panel
)
# alternative POLL dictionary names for where POLL command
# doesn't correspond to SET
ALT_POLL_NAMES = {
    "QTMCFGGEOFENCE_DIS": "QTMCFGGEOFENCE",
    "QTMCFGGEOFENCE_POLY": "QTMCFGGEOFENCE",
    "QTMCFGPPS_DIS": "QTMCFGPPS",
    "QTMCFGUART_CURRBAUD": "QTMCFGUART_CURR",
    "QTMCFGUART_BAUD": "QTMCFGUART",
}
# default attribute values for POLLS
NMEA_POLL_VALS = {
    "index": 1,
    "porttype": 1,
    "portid": 1,
    "systemid": 1,
    "signalid": 1,
    "status": "R",
}
UBX_POLL_VALS = {"portID": 0}


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
        self.__master = self.__app.appmaster  # Reference to root class (Tk)
        self.__container = container
        self.logger = logging.getLogger(__name__)
        self._protocol = kwargs.pop("protocol", "UBX")

        Frame.__init__(self, self.__container.container, *args, **kwargs)

        self._img_send = ImageTk.PhotoImage(Image.open(ICON_SEND))
        self._img_pending = ImageTk.PhotoImage(Image.open(ICON_PENDING))
        self._img_confirmed = ImageTk.PhotoImage(Image.open(ICON_CONFIRMED))
        self._img_warn = ImageTk.PhotoImage(Image.open(ICON_WARNING))
        self._img_unknown = ImageTk.PhotoImage(Image.open(ICON_UNKNOWN))
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

        self._lbl_cfg_dyn = Label(
            self,
            text=LBLCFGGENERICNMEA if self._protocol == "NMEA" else LBLCFGGENERIC,
            anchor=W,
        )
        self._lbx_cfg_cmd = Listbox(
            self,
            border=2,
            relief="sunken",
            height=15,
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
        self._lbl_command = Label(self, text="", anchor=W)
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
        self._can_container.create_window(0, 0, window=self._frm_attrs, anchor=NW)

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
            column=3, row=1, rowspan=3, ipadx=3, ipady=3, sticky=W
        )
        self._lbl_send_command.grid(
            column=3, row=4, rowspan=3, ipadx=3, ipady=3, sticky=W
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

        self._lbx_cfg_cmd.delete(0, END)
        if self._protocol == "NMEA":
            for i, cmd in enumerate(NMEA_PAYLOADS_SET_PROP):
                if cmd[0:3] == "QTM" and cmd not in CFG_EXCLUDED:
                    self._lbx_cfg_cmd.insert(i, cmd)
        else:
            for i, cmd in enumerate(UBX_PAYLOADS_SET):
                if cmd[0:3] == "CFG" and cmd not in CFG_EXCLUDED:
                    self._lbx_cfg_cmd.insert(i, cmd)

        self._clear_widgets()
        self._lbl_send_command.config(image=self._img_unknown)

    def _setscroll(self, event):  # pylint: disable=unused-argument
        """
        Set dynamic scroll region.
        """

        self._can_container.configure(
            scrollregion=self._can_container.bbox(ALL),
            width=SCROLLX,
            height=SCROLLY,
        )

    def _on_select_cfg(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Handle CFG command selection - populate panel with Entry widgets
        corresponding to CFG payload attributes.
        """

        idx = self._lbx_cfg_cmd.curselection()
        self._cfg_id = self._lbx_cfg_cmd.get(idx)
        self._do_poll_cfg()
        self._lbl_command.config(text=self._cfg_id)

        self._clear_widgets()
        if self._protocol == "NMEA":
            self._add_widgets(None, NMEA_PAYLOADS_SET_PROP[self._cfg_id], 1, 0)
        else:
            self._add_widgets(None, UBX_PAYLOADS_SET[self._cfg_id], 1, 0)
        self.update()

    def update_status(self, msg: object):
        """
        UBXHandler or NMEAHandler module receives CFG SET/POLL response and forwards it
        on to this module; confirmation status updated accordingly.

        :param object msg: UBXMessage or NMEAMessage response
        """

        cfg_id = (
            "P" + self._cfg_id.rsplit("_", 1)[0]
            if self._protocol == "NMEA"
            else self._cfg_id
        )
        if (
            msg.identity == cfg_id
        ):  # if this message identity matches the expected response
            self._lbl_send_command.config(image=self._img_confirmed)
            self.__container.set_status(f"{msg.identity} GET message received", "green")
            self._clear_widgets()
            if self._protocol == "NMEA":
                status = getattr(msg, "status", "OK")
                if status == "OK":
                    self._lbl_send_command.config(image=self._img_confirmed)
                    self.__container.set_status(
                        f"{cfg_id} message acknowledged", "green"
                    )
                    self._add_widgets(msg, NMEA_PAYLOADS_SET_PROP[self._cfg_id], 1, 0)
                elif status == "ERROR":
                    self._lbl_send_command.config(image=self._img_warn)
                    self.__container.set_status(f"{cfg_id} message rejected", "red")
            else:  # UBX
                self._add_widgets(msg, UBX_PAYLOADS_SET[self._cfg_id], 1, 0)
            self.update()
        elif msg.identity == "ACK-NAK":  # UBX
            self.__container.set_status(f"{cfg_id} message rejected", "red")
            self._lbl_send_command.config(image=self._img_warn)
        elif msg.identity == "ACK-ACK":  # UBX
            self.__container.set_status(f"{cfg_id} message acknowledged", "green")
            self._lbl_send_command.config(image=self._img_confirmed)

    def _clear_widgets(self):
        """
        Clear dynamically generated Entry widgets from panel.
        """

        self._cfg_atts = {}
        wdgs = self._frm_attrs.grid_slaves()
        for wdg in wdgs:
            wdg.destroy()
        Label(self._frm_attrs, text="Attribute", width=12, anchor=W).grid(
            column=0, row=0, padx=3, sticky=(W)
        )
        Label(self._frm_attrs, text="Value", width=20, anchor=W).grid(
            column=1, row=0, padx=3, sticky=(W)
        )
        Label(self._frm_attrs, text="Type", width=5, anchor=W).grid(
            column=2, row=0, padx=3, sticky=(W)
        )

    def _add_widgets(self, msg: UBXMessage, pdict: dict, row: int, index: int) -> int:
        """
        Recursive routine to add Entry widgets to panel.

        :param UBXMessage msg: response to CFG POLL (if available)
        :param dict pdict: dict representing CFG SET payload definition
        :param int row: current row in frame
        :param int index: grouped item index
        :return: last row used
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
        Add widgets for group header label.

        :param UBXMessage msg: response to CFG POLL (if available)
        :param str nam: attribute name
        :param object att: attribute type
        :param int row: current row in frame
        :param int index: grouped item index
        :return: last row used
        :rtype: int
        """

        numr, attd = att

        if index == 1:
            # TODO if 'variable by size' group, add entry field to
            # allow user to specify size of group
            # if numr == "None":
            #     self._cfg_atts[nam] = (StringVar(), U1)
            #     Label(self._frm_attrs, text="Group Size:").grid(
            #         column=0, row=row, sticky=(E)
            #     )
            #     Entry(
            #         self._frm_attrs,
            #
            #         textvariable=self._cfg_atts[nam],
            #         relief="sunken",
            #
            #     ).grid(column=1, row=row, sticky=(W))
            #     Label(self._frm_attrs, text=U1).grid(column=2, row=row, sticky=(W))
            #     row += 1
            #     otherwise add label indicating the integer or existing attribute
            #     which represents the group size
            # else:
            Label(self._frm_attrs, text="Group Size:").grid(
                column=0, row=row, sticky=(E)
            )
            Label(self._frm_attrs, text=numr).grid(column=1, row=row, sticky=W)
            row += 1

        row = self._add_widgets(msg, attd, row, index)

        return row

    def _add_widgets_single(
        self,
        msg: object,
        nam: str,
        att: object,
        row: int,
        index: int,
    ) -> int:
        """
        Add Entry widget for single attribute.

        If a CFG POLL response is available, the Entry widget is
        prepopulated with the current value.

        :param object msg: response to CFG POLL (if available)
        :param str nam: attribute name e.g. "lat"
        :param object att: attribute type e.g. "U004"
        :param int row: current row in frame
        :param int index: grouped item index
        :return: last row used
        :rtype: int
        """

        # if nam[0:8] == "reserved":  # ignore reserved attributes
        #     return row

        if index > 0:  # if part of group, add index suffix e.g. '_02'
            nam += f"_{index:02d}"
        if isinstance(att, list):  # (type, scale factor)
            att = att[0]

        self._cfg_atts[nam] = (StringVar(), att)
        if msg is not None:  # set initial value from POLL response
            mval = getattr(msg, nam)
            if nam == "bdsTalkerId":  # fudge for default CFG-NMEA bdsTalkerId
                if mval == b"\x00\x00":
                    mval = ""
            if atttyp(att) == "X":
                mval = hex(int.from_bytes(mval, "big"))
            self._cfg_atts[nam][0].set(mval)

        Label(self._frm_attrs, text=nam).grid(column=0, row=row, sticky=E)
        Entry(
            self._frm_attrs,
            textvariable=self._cfg_atts[nam][0],
            relief="sunken",
        ).grid(column=1, row=row, sticky=W)
        Label(self._frm_attrs, text=att).grid(column=2, row=row, sticky=W)
        row += 1

        return row

    def _on_send_cfg(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Populate CFG SET message from Entry fields on panel and send to device.
        """

        nam = ""
        ent = StringVar().set("")
        try:
            # create dict of attribute keyword arguments from
            # Entry field string variables
            vals = {}
            for nam, (ent, att) in self._cfg_atts.items():
                val = ent.get()
                vals[nam] = stringvar2val(val, att)

            if self._protocol == "NMEA":
                # create NMEAMessage using these keyword arguments
                # strip off any variant suffix from cfg_id
                # e.g. "QTMCFGUART_CURR" -> "QTMCFGUART"
                msg = NMEAMessage("P", self._cfg_id.rsplit("_", 1)[0], SET, **vals)
                penddlg = NMEA_CFGOTHER
                pendcfg = ("P" + self._cfg_id,)
            else:
                # create UBXMessage using these keyword arguments
                msg = UBXMessage("CFG", self._cfg_id, SET, **vals)
                penddlg = UBX_CFGOTHER
                pendcfg = ("ACK-ACK", "ACK-NAK")

            # send message, update status and await response
            self.__container.send_command(msg)
            self.logger.debug(f"command {msg.serialize()}")
            self._lbl_send_command.config(image=self._img_pending)
            self.__container.set_status(
                f"{self._cfg_id} SET message sent",
            )
            for msgid in pendcfg:
                self.__container.set_pending(msgid, penddlg)

        except ValueError as err:
            self.__container.set_status(
                f"INVALID! {nam}, {att}: {err}",
                "red",
            )

    def _do_poll_cfg(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Send CFG POLL request (if supported) and set pending response status.
        """

        msg = penddlg = pendcfg = None
        # Some NMEA SET commands don't exist as POLLs
        cfg_id = ALT_POLL_NAMES.get(self._cfg_id, self._cfg_id)
        if self._protocol == "NMEA":
            if cfg_id in NMEA_PAYLOADS_POLL_PROP:  # CFG is POLLable
                # strip off any variant suffix from cfg_id
                # e.g. "QTMCFGUART_CURR" -> "QTMCFGUART"
                # set any POLL arguments to their default values
                # e.g. portid = 1
                dic = NMEA_PAYLOADS_POLL_PROP[cfg_id]
                vals = {}
                for attn in dic:
                    if attn in NMEA_POLL_VALS:
                        vals[attn] = NMEA_POLL_VALS[attn]
                msg = NMEAMessage("P", cfg_id.rsplit("_", 1)[0], POLL, **vals)
                penddlg = NMEA_CFGOTHER
                pendcfg = (msg.identity,)
        else:  # UBX
            if cfg_id in UBX_PAYLOADS_POLL:  # CFG is POLLable
                msg = UBXMessage("CFG", cfg_id, POLL)
                penddlg = UBX_CFGOTHER
                pendcfg = (msg.identity, "ACK-NAK")

        if msg is not None:
            self.__container.send_command(msg)
            self.logger.debug(f"poll {msg.serialize()}")
            self.__container.set_status(
                f"{cfg_id} POLL message sent",
            )
            self._lbl_send_command.config(image=self._img_pending)
            for msgid in pendcfg:
                self.__container.set_pending(msgid, penddlg)
        else:  # CFG cannot be POLLed
            self.__container.set_status(
                f"{cfg_id} No POLL available",
            )
            self._lbl_send_command.config(image=self._img_unknown)
