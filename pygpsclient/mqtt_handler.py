"""
u-blox PointPerfect MQTT client with AssistNow v0.6

Based on pointperfect.assistnow-client-06.py

NB: MQTT certificate (*.crt) and key (*.pem) files must be placed in
the user's home directory.

The Client ID can be set as environment variable MQTTCLIENTID.

Created on 8 Feb 2023

:author: semuadmin
:copyright: SEMU Consulting © 2023
:license: BSD 3-Clause
"""

from os import getenv

from time import sleep
from queue import Queue
from threading import Thread, Event
import paho.mqtt.client as mqtt
from pyubx2 import (
    UBXReader,
    UBXParseError,
    protocol,
    UBX_PROTOCOL,
    GET,
)
from pygpsclient.globals import SPARTN_EVENT, SPARTN_PPSERVER


class MQTTHandler:
    """
    MQTT Handler Class.
    """

    def __init__(
        self,
        app,
        region: str,
        outqueue: Queue,
        **kwargs,
    ):
        """
        Constructor.

        :param str region: region eg. "uk"
        :param Queue outqueue: output queue to GNSS receiver
        """

        self.__app = app
        self.__master = self.__app.appmaster
        self._clientid = kwargs.get("clientid", getenv("MQTTCLIENTID", default=""))
        self._server = kwargs.get("server", SPARTN_PPSERVER)
        self._topics = kwargs.get(
            "mqtt_topics",
            [
                (f"/pp/ip/{region}", 0),
                ("/pp/ubx/mga", 0),
                ("/pp/ubx/0236/ip", 0),
            ],
        )
        # mqtt_topics = [(f"/pp/ip/{self._region}", 0), ("/pp/ubx/mga", 0), ("/pp/ubx/0236/Lp", 0)]
        self._tls = kwargs.get("tls")
        self._outqueue = outqueue
        self._stopevent = Event()
        self._mqtt_thread = None

    def start(self):
        """
        Start MQTT handler thread.
        """

        self._stopevent.clear()
        self._mqtt_thread = Thread(
            target=self._run,
            args=(
                self._clientid,
                self._topics,
                self._server,
                self._tls,
                self._stopevent,
                self._outqueue,
            ),
            daemon=True,
        )
        self._mqtt_thread.start()

    def stop(self):
        """
        Stop MQTT handler thread.
        """

        self._stopevent.set()
        self._mqtt_thread = None

    def _run(
        self,
        clientid: str,
        topics: list,
        server: str,
        tls: tuple,
        stopevent: Event,
        outqueue: Queue,
    ):
        """
        THREADED Run MQTT client thread.

        :param str clientid: MQTT Client ID
        :param list topics: list of MQTT topics to subscribe to
        :param str server: MQTT server URL e.g. "pp.services.u-blox.com"
        :param tuple tls: tuple of (certificate, key)
        :param event stopevent: stop event
        :param Queue outqueue: output queue to GNSS receiver
        """

        userdata = {
            "gnss": outqueue,
            "topics": topics,
            "master": self.__master,
            "readevent": SPARTN_EVENT,
        }
        client = mqtt.Client(client_id=clientid, userdata=userdata)
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        (certfile, keyfile) = tls
        client.tls_set(certfile=certfile, keyfile=keyfile)

        while not stopevent.is_set():
            try:
                client.connect(server, port=8883)
                break
            except Exception:  # pylint: disable=broad-exception-caught
                # print("Trying to connect ...")
                pass
            sleep(3)

        client.loop_start()
        while not stopevent.is_set():
            # run the client loop in the same thread, as callback access gnss
            # client.loop(timeout=0.1)
            sleep(0.1)
        client.loop_stop()

    @staticmethod
    def on_connect(client, userdata, flags, rcd):  # pylint: disable=unused-argument
        """
        The callback for when the client receives a CONNACK response from the server.
        """
        if rcd == 0:
            client.subscribe(userdata["topics"])
        else:
            print(f"PyPGSClient MQTT Client - Connection failed, rc: {rcd}!")

    @staticmethod
    def on_message(client, userdata, msg):  # pylint: disable=unused-argument
        """
        The callback for when a PUBLISH message is received from the server.
        """

        parsed = f"<MQTT(topic={msg.topic}, payload={msg.payload[0:10]}...)>"
        if protocol(msg.payload) == UBX_PROTOCOL:
            try:
                parsed = UBXReader.parse(msg.payload, msgmode=GET)
            except UBXParseError:
                pass
        userdata["gnss"].put((msg.payload, parsed))
        userdata["master"].event_generate(userdata["readevent"])