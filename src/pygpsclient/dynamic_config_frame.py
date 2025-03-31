"""
dynamic_config_frame.py

UBX and NMEA configuration widget for user-selected configuration commands.

When a configuration (SET) command is selected from the listbox, a POLL request
is sent to the device to retrieve the current configuration, which is then used
to populate a series of dynamically generated Entry widgets. The user can then
amend the values as required and send the updated configuration to the device.
NB: this mechanism is dependent on receiving timely POLL responses.

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
from pynmeagps import NMEA_PAYLOADS_POLL_PROP, NMEA_PAYLOADS_SET_PROP, NMEAMessage
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
)

from pygpsclient.globals import (
    ERRCOL,
    ICON_CONFIRMED,
    ICON_PENDING,
    ICON_REDRAW,
    ICON_SEND,
    ICON_UNKNOWN,
    ICON_WARNING,
    INFOCOL,
    NMEA_CFGOTHER,
    OKCOL,
    UBX_CFGOTHER,
)
from pygpsclient.helpers import stringvar2val
from pygpsclient.strings import LBLCFGGENERIC, LBLCFGGENERICNMEA

# dimensions of scrollable attribute window
SCROLLX = 300
SCROLLY = 300
NMEA = "NMEA"
UBX = "UBX"
ACK = "ACK-ACK"
NAK = "ACK-NAK"

# following CFG types excluded from selection...
CFG_EXCLUDED = (
    "CFG-DAT-NUM",  # deprecated
    "CFG-GEOFENCE",  # 'variable by size' groups not yet implemented - use pyubx2
    "CFG-NMEAv0",  # deprecated
    "CFG-NMEAvX",  # deprecated
    "CFG-RINV",  # 'variable by size' groups not yet implemented - use pyubx2
    "CFG-VALDEL",  # handled via existing CFG-VALGET/SET/DEL panel
    "CFG-VALSET",  # handled via existing CFG-VALGET/SET/DEL panel
)
# alternative POLL dictionary names for where POLL command
# doesn't correspond to SET (fudge for Quectel)
ALT_POLL_NAMES = {
    "QTMCFGGEOFENCE_DIS": "QTMCFGGEOFENCE",
    "QTMCFGGEOFENCE_POLY": "QTMCFGGEOFENCE",
    "QTMCFGPPS_DIS": "QTMCFGPPS",
    "QTMCFGSAT_LOW": "QTMCFGSAT",
    "QTMCFGSAT_MASKHIGH": "QTMCFGSAT",
    "QTMCFGUART_CURRBAUD": "QTMCFGUART_CURR",
    "QTMCFGUART_BAUD": "QTMCFGUART",
}
# default argument values for POLLS
NMEA_POLL_VALS = {
    "geofenceindex": 0,
    "index": 1,
    "msgname": "RMC",
    "msgver": 1,
    "porttype": 1,
    "portid": 1,
    "ppsindex": 1,
    "signalid": 1,
    "status": "R",
    "systemid": 1,
}
UBX_POLL_VALS = {
    "msgClass": 0x01,
    "msgID": 0x07,
    "portID": 0,
    "protocolID": 0,
}


class Dynamic_Config_Frame(Frame):
    """
    Dynamic configuration command panel.
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
        self._img_refresh = ImageTk.PhotoImage(Image.open(ICON_REDRAW))
        self._cfg_id = ""  # identity of selected CFG command
        self._cfg_atts = {}  # this holds the attributes of the selected CFG command
        self._expected_response = None

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
            command=self._on_set_cfg,
            font=self.__app.font_md,
        )
        self._btn_refresh = Button(
            self,
            image=self._img_refresh,
            width=50,
            command=self._on_refresh,
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
        self._btn_send_command.grid(column=3, row=1, ipadx=3, ipady=3, sticky=W)
        self._lbl_send_command.grid(column=3, row=2, ipadx=3, ipady=3, sticky=W)
        self._btn_refresh.grid(column=3, row=3, ipadx=3, ipady=3, sticky=W)
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
        if self._protocol == NMEA:
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

    def _on_refresh(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Handle refresh button.
        """

        self._do_poll_cfg()

    def _on_select_cfg(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Handle configuration command selection. Look up payload dictionary of command,
        dynamically add Entry widget for each payload attribute and poll for
        current configuration (if available) to pre-populate these Entry widgets.
        """

        self._expected_response = None
        idx = self._lbx_cfg_cmd.curselection()
        self._cfg_id = self._lbx_cfg_cmd.get(idx)
        self._lbl_command.config(text=self._cfg_id)
        if self._protocol == NMEA:
            pdic = NMEA_PAYLOADS_SET_PROP[self._cfg_id]
        else:  # UBX
            pdic = UBX_PAYLOADS_SET[self._cfg_id]
        self._clear_widgets()
        self._add_widgets(pdic, 1, 0)
        self.update()
        self._do_poll_cfg()

    def _on_set_cfg(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Populate CFG SET message from Entry fields on panel and send to device.
        """

        if self._cfg_id in ("", None):
            self.__container.set_status("Select command", ERRCOL)
            return

        nam = ""
        ent = StringVar().set("")
        try:
            # create dict of attribute keyword arguments from
            # Entry field string variables
            vals = {}
            for nam, (ent, att) in self._cfg_atts.items():
                val = ent.get()
                vals[nam] = stringvar2val(val, att)

            if self._protocol == NMEA:
                # create NMEAMessage using these keyword arguments
                # strip off any variant suffix from cfg_id
                # e.g. "QTMCFGUART_CURR" -> "QTMCFGUART"
                cfg_id = self._cfg_id.rsplit("_", 1)[0]
                msg = NMEAMessage("P", cfg_id, SET, **vals)
                penddlg = NMEA_CFGOTHER
                pendcfg = ("P" + cfg_id,)
            else:
                # create UBXMessage using these keyword arguments
                msg = UBXMessage("CFG", self._cfg_id, SET, **vals)
                penddlg = UBX_CFGOTHER
                pendcfg = (ACK, NAK)

            # send message, update status and await response
            self.__container.send_command(msg)
            # self.logger.debug(f"command {msg.serialize()}")
            self._lbl_send_command.config(image=self._img_pending)
            self.__container.set_status(
                f"{self._cfg_id} SET message sent",
            )
            for msgid in pendcfg:
                self.__container.set_pending(msgid, penddlg)
            self._expected_response = SET

        except ValueError as err:
            self.__container.set_status(
                f"INVALID! {nam}, {att}: {err}",
                ERRCOL,
            )

    def _do_poll_cfg(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        Send configuration POLL request (if supported) and set pending response status.

        Some POLL requests require arguments (e.g. portid or msgname) - these
        will be taken from the relevant Entry field or, if null, from a
        table of default values.
        """

        if self._cfg_id in ("", None):
            self.__container.set_status("Select command", ERRCOL)
            return

        msg = penddlg = pendcfg = None
        # use alternate names for some NMEA PQTM POLL commands
        cfg_id = ALT_POLL_NAMES.get(self._cfg_id, self._cfg_id)
        # set any POLL arguments to specified or default values
        # e.g. portid = "1", msgname="RMC"
        args = self._do_poll_args(cfg_id)
        if self._protocol == NMEA:
            if cfg_id in NMEA_PAYLOADS_POLL_PROP:  # CFG is POLLable
                # strip off any variant suffix from cfg_id
                # e.g. "QTMCFGUART_CURR" -> "QTMCFGUART"
                msg = NMEAMessage("P", cfg_id.rsplit("_", 1)[0], POLL, **args)
                penddlg = NMEA_CFGOTHER
                pendcfg = (msg.identity,)
        else:  # UBX
            if cfg_id in UBX_PAYLOADS_POLL:  # CFG is POLLable
                msg = UBXMessage("CFG", cfg_id, POLL, **args)
                penddlg = UBX_CFGOTHER
                pendcfg = (msg.identity, NAK)

        if msg is not None:
            self.__container.send_command(msg)
            # self.logger.debug(f"poll {msg.serialize()}")
            self.__container.set_status(f"{cfg_id} POLL message sent", INFOCOL)
            self._lbl_send_command.config(image=self._img_pending)
            for msgid in pendcfg:
                self.__container.set_pending(msgid, penddlg)
            self._expected_response = POLL
        else:  # CFG cannot be POLLed
            self.__container.set_status(
                f"{cfg_id} No POLL available",
            )
            self._lbl_send_command.config(image=self._img_unknown)

    def _do_poll_args(self, cfg_id: str) -> dict:
        """
        Set any poll arguments to default or entered values.

        :param str cfg_id: config command name
        :return: dictionary of poll arguments
        :rtype: dict
        """

        args = {}
        try:
            if self._protocol == NMEA:
                dic = NMEA_PAYLOADS_POLL_PROP[cfg_id]
                for attn in dic:
                    pval = self._cfg_atts.get(attn, None)
                    if pval is not None:
                        pval = pval[0].get()
                    if pval != "" and attn != "status":
                        val = pval
                    else:
                        val = NMEA_POLL_VALS.get(attn, "")
                        self._cfg_atts[attn][0].set(val)
                    args[attn] = val
            else:  # UBX
                dic = UBX_PAYLOADS_POLL[cfg_id]
                for attn in dic:
                    pval = self._cfg_atts.get(attn, None)
                    if pval is not None:
                        pval = pval[0].get()
                    if pval != "":
                        val = pval
                        if val.isnumeric():
                            val = int(val)
                    else:
                        val = UBX_POLL_VALS.get(attn, "")
                        self._cfg_atts[attn][0].set(val)
                    args[attn] = val
        except KeyError:
            pass
        return args

    def update_status(self, msg: object):
        """
        UBXHandler or NMEAHandler module has received expected command response
        and forwarded it to this module, entry widgets are pre-populated with
        current configuration values and confirmation status is updated.

        :param object msg: UBXMessage or NMEAMessage response
        """

        ok = False
        # self.logger.debug(f"incoming status msg: {msg}")
        # strip off any variant suffix from cfg_id
        # e.g. "QTMCFGUART_CURR" -> "PQTMCFGUART"
        cfg_id = (
            "P" + self._cfg_id.rsplit("_", 1)[0]
            if self._protocol == NMEA
            else self._cfg_id
        )

        # if this message identity matches an expected response
        if msg.identity in (cfg_id, ACK, NAK):
            if self._protocol == NMEA:
                if getattr(msg, "status", "OK") == "OK":
                    ok = True
                    if self._expected_response == POLL:
                        self._update_widgets(msg)
            else:  # UBX
                if msg.identity != NAK:
                    ok = True
                if msg.identity == cfg_id and self._expected_response == POLL:
                    self._update_widgets(msg)

            if ok:
                self.__container.set_status(f"{cfg_id} message acknowledged", OKCOL)
                self._lbl_send_command.config(image=self._img_confirmed)
            else:
                self.__container.set_status(f"{cfg_id} message rejected", ERRCOL)
                self._lbl_send_command.config(image=self._img_warn)
            self.update()

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

    def _add_widgets(self, pdict: dict, row: int, index: int) -> int:
        """
        Recursive routine to dynamically add Entry widgets to panel.

        :param object msg: UBXMessage or NMEAMessage response to POLL (if available)
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
                    row = self._add_widgets(attd, row, index)
                else:  # repeating group
                    if isinstance(numr, int):  # fixed length group
                        nr = numr
                    else:
                        nr = 1
                    for idx in range(nr):
                        row = self._add_widgets_group(att, row, idx + 1)
            else:  # single attribute
                row = self._add_widgets_single(nam, att, row, index)

        return row

    def _add_widgets_group(self, att: object, row: int, index: int) -> int:
        """
        Add widgets for group header label.

        :param object msg: UBXMessage or NMEAMessage response to CFG POLL (if available)
        :param object att: attribute type
        :param int row: current row in frame
        :param int index: grouped item index
        :return: last row used
        :rtype: int
        """

        numr, attd = att

        if index == 1:
            Label(self._frm_attrs, text="Group Size:").grid(
                column=0, row=row, sticky=(E)
            )
            Label(self._frm_attrs, text=numr).grid(column=1, row=row, sticky=W)
            row += 1

        row = self._add_widgets(attd, row, index)

        return row

    def _add_widgets_single(
        self,
        nam: str,
        att: object,
        row: int,
        index: int,
    ) -> int:
        """
        Add Entry widget for single attribute.

        If a configuration POLL response is available, the Entry widget is
        pre-populated with the current value.

        :param object msg: UBXMessage or NMEAMessage response to POLL (if available)
        :param str nam: attribute name e.g. "lat"
        :param object att: attribute type e.g. "U004"
        :param int row: current row in frame
        :param int index: grouped item index
        :return: last row used
        :rtype: int
        """

        if index > 0:  # if part of group, add index suffix e.g. '_02'
            nam += f"_{index:02d}"
        if isinstance(att, list):  # (type, scale factor)
            att = att[0]
        self._cfg_atts[nam] = (StringVar(), att)
        Label(self._frm_attrs, text=nam).grid(column=0, row=row, sticky=E)
        ent = Entry(
            self._frm_attrs,
            textvariable=self._cfg_atts[nam][0],
            relief="sunken",
            highlightthickness=2,
        )
        ent.grid(column=1, row=row, sticky=W)
        # check if poll argument
        self._check_pollarg(nam, ent)
        Label(self._frm_attrs, text=att).grid(column=2, row=row, sticky=W)
        row += 1

        return row

    def _check_pollarg(self, nam: str, wdg: Entry):
        """
        Highlight this Entry widget if it represents a POLL argument.

        :param str nam: attribute name e.g. "portid"
        :param Entry wdg: Entry widget
        """

        cfg = self._cfg_id.split("_")[0]
        if (
            self._protocol == NMEA
            and (cfg[:3] == "QTM" and nam != "status")  # ignore Quectel status
            and nam in NMEA_PAYLOADS_POLL_PROP.get(cfg, {})
        ) or (self._protocol == UBX and nam in UBX_PAYLOADS_POLL.get(cfg, {})):
            wdg.configure(highlightbackground=INFOCOL, highlightcolor=INFOCOL)

    def _update_widgets(self, msg: object):
        """
        Update Entry widgets with attribute values from poll response.

        :param object msg: UBXMessage or NMEAMessage poll response
        """

        # add any grouped attributes that aren't already listed (index > 1)
        row = len(self._cfg_atts) + 1
        for att in msg.__dict__:
            if att[0] != "_" and len(att) > 3:
                # only add public grouped attributes
                if att not in self._cfg_atts and att[-3] == "_":
                    # get added attribute type by reference to first in group
                    atn = att.rsplit("_", 1)[0] + "_01"
                    typ = self._cfg_atts[atn][1]
                    # add Entry widget for this attribute
                    self._add_widgets_single(att, typ, row, 0)
                    row += 1

        # update Entry values
        for att in self._cfg_atts:  # pylint: disable=consider-using-dict-items
            val = getattr(msg, att, 0)
            # change NMEA 'OK' status to 'W' (write)
            if self._protocol == NMEA and att == "status" and val == "OK":
                val = "W"
            self._cfg_atts[att][0].set(val)
