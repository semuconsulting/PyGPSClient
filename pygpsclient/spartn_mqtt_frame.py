"""
SPARTN configuration dialog

This is the pop-up dialog containing the various
SPARTN configuration functions.

This dialog maintains its own threaded serial
stream handler for incoming and outgoing Correction
receiver (D9S) data (RXM-PMP), and must remain open for
SPARTN passthrough to work.

Created on 26 Jan 2023

:author: semuadmin
:copyright: SEMU Consulting © 2023
:license: BSD 3-Clause
"""
# pylint: disable=invalid-name, too-many-locals, too-many-instance-attributes

from os import path, getenv
from pathlib import Path
from tkinter import (
    ttk,
    Frame,
    Button,
    Checkbutton,
    Spinbox,
    Label,
    Entry,
    StringVar,
    IntVar,
    E,
    W,
    NORMAL,
    DISABLED,
)
from PIL import ImageTk, Image
from pyubx2 import UBXMessage
from pygpsclient.mqtt_handler import MQTTHandler
from pygpsclient.globals import (
    ICON_EXIT,
    ICON_SEND,
    ICON_CONFIRMED,
    ICON_PENDING,
    ICON_WARNING,
    ICON_SERIAL,
    ICON_DISCONN,
    ICON_BLANK,
    ICON_SOCKET,
    ICON_LOAD,
    ENTCOL,
    CONNECTED_SPARTNIP,
    DISCONNECTED,
    READONLY,
    SPARTN_PPSERVER,
    SPARTN_PPREGIONS,
    SPARTN_GNSS,
    RXMMSG,
    TOPIC_IP,
    TOPIC_MGA,
    TOPIC_RXM,
)
from pygpsclient.strings import LBLSPARTNIP
from pygpsclient.helpers import valid_entry, VALLEN


class SPARTNMQTTDialog(Frame):
    """,
    SPARTNConfigDialog class.
    """

    def __init__(
        self, app, container, *args, **kwargs
    ):  # pylint: disable=unused-argument
        """
        Constructor.

        :param Frame app: reference to main tkinter application
        :param Frame container: reference to container frame
        :param args: optional args to pass to parent class (not currently used)
        :param kwargs: optional kwargs to pass to parent class (not currently used)
        """

        self.__app = app  # Reference to main application class
        self.__master = self.__app.appmaster  # Reference to root class (Tk)
        self.__container = container  # container frame

        Frame.__init__(self, self.__container.container, *args, **kwargs)

        self._img_blank = ImageTk.PhotoImage(Image.open(ICON_BLANK))
        self._img_pending = ImageTk.PhotoImage(Image.open(ICON_PENDING))
        self._img_confirmed = ImageTk.PhotoImage(Image.open(ICON_CONFIRMED))
        self._img_warn = ImageTk.PhotoImage(Image.open(ICON_WARNING))
        self._img_exit = ImageTk.PhotoImage(Image.open(ICON_EXIT))
        self._img_send = ImageTk.PhotoImage(Image.open(ICON_SEND))
        self._img_serial = ImageTk.PhotoImage(Image.open(ICON_SERIAL))
        self._img_socket = ImageTk.PhotoImage(Image.open(ICON_SOCKET))
        self._img_disconn = ImageTk.PhotoImage(Image.open(ICON_DISCONN))
        self._img_load = ImageTk.PhotoImage(Image.open(ICON_LOAD))
        self._stream_handler = None
        self._status = StringVar()
        self._mqtt_server = StringVar()
        self._mqtt_region = StringVar()
        self._mqtt_clientid = StringVar()
        self._mqtt_crt = StringVar()
        self._mqtt_pem = StringVar()
        self._mqtt_iptopic = IntVar()
        self._mqtt_mgatopic = IntVar()
        self._mqtt_keytopic = IntVar()

        self._body()
        self._do_layout()
        self._reset()

    def _body(self):
        """
        Set up frame and widgets.
        """
        # pylint: disable=unnecessary-lambda

        self._lbl_corrip = Label(self, text=LBLSPARTNIP)
        self._lbl_mqttserver = Label(self, text="Server")
        self._ent_mqttserver = Entry(
            self,
            textvariable=self._mqtt_server,
            bg=ENTCOL,
            state=NORMAL,
            relief="sunken",
            width=25,
        )
        self._lbl_mqttregion = Label(self, text="Region")
        self._spn_mqttregion = Spinbox(
            self,
            values=SPARTN_PPREGIONS,
            textvariable=self._mqtt_region,
            readonlybackground=ENTCOL,
            state=READONLY,
            width=4,
            wrap=True,
        )
        self._lbl_mqttclientid = Label(self, text="Client ID")
        self._ent_mqttclientid = Entry(
            self,
            textvariable=self._mqtt_clientid,
            bg=ENTCOL,
            state=NORMAL,
            relief="sunken",
            width=35,
        )
        self._lbl_topics = Label(self, text="Topics")
        self._chk_mqtt_iptopic = Checkbutton(
            self,
            text="IP",
            variable=self._mqtt_iptopic,
        )
        self._chk_mqtt_mgatopic = Checkbutton(
            self,
            text="MGA",
            variable=self._mqtt_mgatopic,
        )
        self._chk_mqtt_keytopic = Checkbutton(
            self,
            text="SPARTNKEY",
            variable=self._mqtt_keytopic,
        )
        self._btn_opencrt = Button(
            self,
            width=45,
            image=self._img_load,
            command=lambda: self._get_spartnkeys("crt"),
        )
        self._lbl_mqttcrt = Label(self, text="CRT File")
        self._ent_mqttcrt = Entry(
            self,
            textvariable=self._mqtt_crt,
            bg=ENTCOL,
            state=NORMAL,
            relief="sunken",
            width=32,
        )
        self._btn_openpem = Button(
            self,
            width=45,
            image=self._img_load,
            command=lambda: self._get_spartnkeys("pem"),
        )
        self._lbl_mqttpem = Label(self, text="PEM File")
        self._ent_mqttpem = Entry(
            self,
            textvariable=self._mqtt_pem,
            bg=ENTCOL,
            state=NORMAL,
            relief="sunken",
            width=32,
        )
        self._btn_connect = Button(
            self,
            width=45,
            image=self._img_socket,
            command=lambda: self.on_connect(),
        )
        self._btn_disconnect = Button(
            self,
            width=45,
            image=self._img_disconn,
            command=lambda: self.on_disconnect(),
            state=DISABLED,
        )

    def _do_layout(self):
        """
        Position widgets in frame.
        """

        self._lbl_corrip.grid(column=0, row=0, columnspan=6, padx=3, pady=2, sticky=W)
        self._lbl_mqttserver.grid(column=0, row=1, padx=3, pady=2, sticky=W)
        self._ent_mqttserver.grid(
            column=1, row=1, columnspan=5, padx=3, pady=2, sticky=W
        )
        self._lbl_mqttregion.grid(column=0, row=2, padx=3, pady=2, sticky=W)
        self._spn_mqttregion.grid(
            column=1, row=2, columnspan=5, padx=3, pady=2, sticky=W
        )
        self._lbl_mqttclientid.grid(column=0, row=3, padx=3, pady=2, sticky=W)
        self._ent_mqttclientid.grid(
            column=1, row=3, columnspan=5, padx=3, pady=2, sticky=W
        )
        self._lbl_topics.grid(column=0, row=4, padx=3, pady=2, sticky=W)
        self._chk_mqtt_iptopic.grid(column=1, row=4, padx=3, pady=2, sticky=W)
        self._chk_mqtt_mgatopic.grid(column=2, row=4, padx=3, pady=2, sticky=W)
        self._chk_mqtt_keytopic.grid(column=3, row=4, padx=3, pady=2, sticky=W)
        self._lbl_mqttcrt.grid(column=0, row=5, padx=3, columnspan=5, pady=2, sticky=W)
        self._ent_mqttcrt.grid(
            column=1, row=5, padx=3, columnspan=4, pady=2, sticky=(W, E)
        )
        self._btn_opencrt.grid(column=5, row=5, padx=3, pady=2, sticky=E)
        self._lbl_mqttpem.grid(column=0, row=6, columnspan=3, padx=3, pady=2, sticky=W)
        self._ent_mqttpem.grid(
            column=1, row=6, columnspan=4, padx=3, pady=2, sticky=(W, E)
        )
        self._btn_openpem.grid(column=5, row=6, padx=3, pady=2, sticky=E)
        ttk.Separator(self).grid(
            column=0, row=7, columnspan=6, padx=2, pady=3, sticky=(W, E)
        )
        self._btn_connect.grid(column=0, row=8, padx=3, pady=2, sticky=W)
        self._btn_disconnect.grid(column=2, row=8, padx=3, pady=2, sticky=W)

    def _reset(self):
        """
        Reset configuration widgets.
        """

        self._mqtt_server.set(SPARTN_PPSERVER)
        self._mqtt_region.set(SPARTN_PPREGIONS[0])
        self._mqtt_iptopic.set(1)
        self._mqtt_mgatopic.set(1)
        self._mqtt_keytopic.set(1)
        self._mqtt_clientid.set(getenv("MQTTCLIENTID", default="enter-client-id"))

        # Thingstream > Location Services > PointPerfect Thing > Credentials
        # Default location for key files is user's HOME directory
        self._spartn_crt = path.join(
            Path.home(), f"device-{self._mqtt_clientid.get()}-pp-cert.crt"
        )
        self._spartn_pem = path.join(
            Path.home(), f"device-{self._mqtt_clientid.get()}-pp-key.pem"
        )
        self._mqtt_crt.set(self._spartn_crt)
        self._mqtt_pem.set(self._spartn_pem)

        self.__container.set_status("", "blue")

        if self.__app.rtk_conn_status == CONNECTED_SPARTNIP:
            self.set_controls(CONNECTED_SPARTNIP)
        else:
            self.set_controls(DISCONNECTED)

    def set_controls(self, status: int):
        """
        Enable or disable MQTT Correction widgets depending on
        connection status.

        :param int status: connection status (0 = disconnected, 1 = connected)
        """

        stat = NORMAL if status == CONNECTED_SPARTNIP else DISABLED
        for wdg in (self._btn_disconnect,):
            wdg.config(state=stat)
        stat = DISABLED if status == CONNECTED_SPARTNIP else NORMAL
        for wdg in (
            self._ent_mqttserver,
            self._btn_connect,
            self._ent_mqttclientid,
            self._ent_mqttcrt,
            self._ent_mqttpem,
            self._chk_mqtt_iptopic,
            self._chk_mqtt_mgatopic,
            self._chk_mqtt_keytopic,
            self._btn_opencrt,
            self._btn_openpem,
        ):
            wdg.config(state=stat)
        stat = DISABLED if status == CONNECTED_SPARTNIP else READONLY
        for wdg in (self._spn_mqttregion,):
            wdg.config(state=stat)

    def _valid_settings(self) -> bool:
        """
        Validate settings.

        :return: valid True/False
        :rtype: bool
        """

        valid = True
        valid = valid & valid_entry(self._ent_mqttserver, VALLEN, 1, 50)
        valid = valid & valid_entry(self._ent_mqttclientid, VALLEN, 1, 30)
        valid = valid & valid_entry(self._ent_mqttcrt, VALLEN, 1, 254)
        valid = valid & valid_entry(self._ent_mqttpem, VALLEN, 1, 254)
        return valid

    def _get_spartnkeys(self, ext: str):
        """
        Get SPARTN key (*.pem) and cert (*.crt) files

        :param str ext: file extension ("crt" or "pem")
        """

        spfile = self.__app.file_handler.open_spartnfile(ext)
        if ext == "crt":
            self._mqtt_crt.set(spfile)
        elif ext == "pem":
            self._mqtt_pem.set(spfile)

    def on_connect(self):
        """
        Connect to MQTT client.
        """

        self.__app.rtk_conn_status = CONNECTED_SPARTNIP
        server = SPARTN_PPSERVER
        region = self._mqtt_region.get()
        topics = []
        if self._mqtt_iptopic.get():
            topics.append((TOPIC_IP.format(region), 0))
        if self._mqtt_mgatopic.get():
            topics.append((TOPIC_MGA, 0))
        if self._mqtt_keytopic.get():
            topics.append((TOPIC_RXM, 0))
            self.__container.set_pending(RXMMSG, SPARTN_GNSS)

        self._stream_handler = MQTTHandler(
            self.__app,
            "eu",
            self.__app.spartn_inqueue,
            clientid=self._mqtt_clientid.get(),
            mqtt_topics=topics,
            server=server,
            tls=(self._mqtt_crt.get(), self._mqtt_pem.get()),
        )
        self._stream_handler.start()
        self.__container.set_status(
            f"Connected to MQTT server {server}",
            "green",
        )
        self.set_controls(CONNECTED_SPARTNIP)

    def on_disconnect(self):
        """
        Disconnect from MQTT client.
        """

        if self.__app.rtk_conn_status == CONNECTED_SPARTNIP:
            if self._stream_handler is not None:
                self.__app.rtk_conn_status = DISCONNECTED
                self._stream_handler.stop()
                self._stream_handler = None
                self.__container.set_status(
                    "Disconnected",
                    "red",
                )
        self.set_controls(DISCONNECTED)

    def update_status(self, msg: UBXMessage):
        """
        Update pending confirmation status.
        :param UBXMessage msg: UBX config message
        """
