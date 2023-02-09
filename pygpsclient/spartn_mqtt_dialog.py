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

from os import getenv
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
    ENTCOL,
    CONNECTED,
    DISCONNECTED,
    READONLY,
)
from pygpsclient.strings import (
    LBLSPARTNIP,
)
from pygpsclient.helpers import (
    valid_entry,
    get_gpswnotow,
    VALHEX,
    VALDMY,
    VALLEN,
    VALINT,
)

PPSERVER = "pp.services.u-blox.com"
PPREGIONS = ("eu", "us", "au")


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
        self.mqtt_stream_handler = None
        self._status = StringVar()
        self._mqtt_server = StringVar()
        self._mqtt_region = StringVar()
        self._mqtt_clientid = StringVar()
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
            width=20,
        )
        self._lbl_mqttregion = Label(self, text="Region")
        self._spn_mqttregion = Spinbox(
            self,
            values=PPREGIONS,
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
            width=32,
        )
        self._lbl_topics = Label(self, text="Topics:")
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
        self._btn_mqttconnect = Button(
            self,
            width=45,
            image=self._img_socket,
            command=lambda: self._on_connect(),
        )
        self._btn_mqttdisconnect = Button(
            self,
            width=45,
            image=self._img_disconn,
            command=lambda: self._on_disconnect(),
            state=DISABLED,
        )

    def _do_layout(self):
        """
        Position widgets in frame.
        """

        self._lbl_corrip.grid(column=0, row=0, columnspan=4, padx=3, pady=2, sticky=W)
        self._lbl_mqttserver.grid(column=0, row=1, padx=3, pady=2, sticky=W)
        self._ent_mqttserver.grid(
            column=1, row=1, columnspan=3, padx=3, pady=2, sticky=W
        )
        self._lbl_mqttregion.grid(column=0, row=2, padx=3, pady=2, sticky=W)
        self._spn_mqttregion.grid(
            column=1, row=2, columnspan=3, padx=3, pady=2, sticky=W
        )
        self._lbl_mqttclientid.grid(column=0, row=3, padx=3, pady=2, sticky=W)
        self._ent_mqttclientid.grid(
            column=1, row=3, columnspan=3, padx=3, pady=2, sticky=W
        )
        self._lbl_topics.grid(column=0, row=4, padx=3, pady=2, sticky=W)
        self._chk_mqtt_iptopic.grid(column=1, row=4, padx=3, pady=2, sticky=W)
        self._chk_mqtt_mgatopic.grid(column=2, row=4, padx=3, pady=2, sticky=W)
        self._chk_mqtt_keytopic.grid(column=3, row=4, padx=3, pady=2, sticky=W)
        ttk.Separator(self).grid(
            column=0, row=5, columnspan=4, padx=2, pady=3, sticky=(W, E)
        )
        self._btn_mqttconnect.grid(column=0, row=6, padx=3, pady=2, sticky=W)
        self._btn_mqttdisconnect.grid(column=1, row=6, padx=3, pady=2, sticky=W)

    def _reset(self):
        """
        Reset configuration widgets.
        """

        self._mqtt_server.set(PPSERVER)
        self._mqtt_region.set(PPREGIONS[0])
        self._mqtt_iptopic.set(1)
        self._mqtt_mgatopic.set(0)
        self._mqtt_keytopic.set(1)
        self._mqtt_clientid.set(getenv("MQTTCLIENTID", default=""))
        self.__container.set_status("", "blue")
        self.set_controls(DISCONNECTED)

    def set_controls(self, status: int):
        """
        Enable or disable MQTT Correction widgets depending on
        connection status.

        :param int status: connection status (0 = disconnected, 1 = connected)
        """

        stat = NORMAL if status == CONNECTED else DISABLED
        for wdg in (self._btn_mqttdisconnect,):
            wdg.config(state=stat)
        stat = DISABLED if status == CONNECTED else NORMAL
        for wdg in (
            self._ent_mqttserver,
            self._btn_mqttconnect,
            self._ent_mqttclientid,
            self._chk_mqtt_iptopic,
            self._chk_mqtt_mgatopic,
            self._chk_mqtt_keytopic,
        ):
            wdg.config(state=stat)
        stat = DISABLED if status == CONNECTED else READONLY
        for wdg in (self._spn_mqttregion,):
            wdg.config(state=stat)

    def _valid_settings(self) -> bool:
        """
        Validate settings.

        :return: valid True/False
        :rtype: bool
        """

        valid = True
        return valid

    def _on_connect(self):
        """
        Connect to MQTT client.
        """

        self.__app.spartn_conn_status = CONNECTED
        server = PPSERVER
        region = self._mqtt_region.get()
        topics = []
        if self._mqtt_iptopic.get():
            topics.append((f"/pp/ip/{region}", 0))
        if self._mqtt_mgatopic.get():
            topics.append(("/pp/ubx/mga", 0))
        if self._mqtt_keytopic.get():
            topics.append(("/pp/ubx/0236/ip", 0))

        self.mqtt_stream_handler = MQTTHandler(
            self.__app,
            "eu",
            self.__app.spartn_inqueue,
            clientid=self._mqtt_clientid.get(),
            mqtt_topics=topics,
            server=server,
        )
        self.mqtt_stream_handler.start()
        self.__container.set_status(
            f"Connected to MQTT server {server}",
            "green",
        )
        self.set_controls(CONNECTED)

    def _on_disconnect(self):
        """
        Disconnect from MQTT client.
        """

        if self.mqtt_stream_handler is not None:
            self.__app.spartn_conn_status = DISCONNECTED
            self.mqtt_stream_handler.stop()
            self.mqtt_stream_handler = None
            self.__container.set_status(
                "Disconnected",
                "red",
            )
        self.set_controls(DISCONNECTED)
