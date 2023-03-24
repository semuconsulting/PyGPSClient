"""
spartn_json_config.py

Utility class to load SPARTN decryption configuration from 
JSON file provided by ThingStream PointPerfect location service.
Requires paid subscription.

JSON file normally named "device-{Client ID}-ucenter-config.json"

Created on 12 Feb 2023

:author: semuadmin
:copyright: SEMU Consulting © 2023
:license: BSD 3-Clause
"""

import json
from datetime import datetime, timedelta


class SpartnJsonConfig:
    """
    SpartnJsonConfig class.
    """

    def __init__(self, filename):
        """
        Constructor.

        :param str filename: Fully qualified path to JSON file
        """

        if filename in (None, ""):
            raise AttributeError("Filename must be provided")

        self._loadconfig(filename)

    def _loadconfig(self, filename: str):
        """
        Import config from JSON file.

        :param str filename: filename
        """

        with open(filename, "r", encoding="utf-8") as jsonfile:
            jsondict = json.load(jsonfile)
            connection = jsondict["MQTT"]["Connectivity"]
            subscriptions = jsondict["MQTT"]["Subscriptions"]
            dynamic = jsondict["MQTT"]["dynamickeys"]

            self._clientid = connection["ClientID"]
            self._server = connection["ServerURI"]
            self._key = connection["ClientCredentials"]["Key"]
            self._cert = connection["ClientCredentials"]["Cert"]
            self._rootca = connection["ClientCredentials"]["RootCA"]

            self._topics = {}
            self._topics["Key"] = tuple(subscriptions["Key"]["KeyTopics"])
            self._topics["AssistNow"] = tuple(
                subscriptions["AssistNow"]["AssistNowTopics"]
            )
            self._topics["Data"] = tuple(subscriptions["Data"]["DataTopics"])

            current_ts = dynamic["current"]["start"]
            current_dur = dynamic["current"]["duration"]
            next_ts = dynamic["next"]["start"]
            next_dur = dynamic["next"]["duration"]
            self._curr_key = dynamic["current"]["value"]
            self._curr_start = datetime.fromtimestamp(current_ts / 1000)
            self._curr_end = self._curr_start + timedelta(milliseconds=current_dur)
            self._next_key = dynamic["next"]["value"]
            self._next_start = datetime.fromtimestamp(next_ts / 1000)
            self._next_end = self._next_start + timedelta(milliseconds=next_dur)

    @property
    def clientid(self) -> str:
        """
        Getter for ClientID.

        :return: clientID
        :rtype: str
        """

        return self._clientid

    @property
    def server(self) -> str:
        """
        Getter for Server URI.

        :return: Server UIR
        :rtype: str
        """

        return self._server

    @property
    def topics(self) -> list:
        """
        Getter for topics.

        :return: list of topics
        :rtype: list
        """

        return self._topics

    @property
    def key(self) -> str:
        """
        Getter for Key.

        :return: Key
        :rtype: str
        """

        return self._key

    @property
    def cert(self) -> str:
        """
        Getter for Certificate.

        :return: Certificate
        :rtype: str
        """

        return self._cert

    @property
    def rootca(self) -> str:
        """
        Getter for RootCA.

        :return: RootCA
        :rtype: str
        """

        return self._rootca

    @property
    def current_key(self) -> tuple:
        """
        Getter for current key.

        :return: tuple of (key, start date, end date)
        :rtype: tuple
        """

        return (self._curr_key, self._curr_start, self._curr_end)

    @property
    def next_key(self) -> tuple:
        """
        Getter for next key.

        :return: tuple of (key, start date, end date)
        :rtype: tuple
        """

        return (self._next_key, self._next_start, self._next_end)
