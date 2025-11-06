"""
socketconfig_ntrip_frame.py

NTRIP socket configuration frame.
Inherited from generic SocketConfigFrame class.

Created on 27 Apr 2022

:author: semuadmin (Steve Smith)
:copyright: 2020 semuadmin
:license: BSD 3-Clause
"""

# pylint: disable=unused-argument

from tkinter import TclError

from pygpsclient.globals import DEFAULT_TLS_PORTS, VALINT, VALURL
from pygpsclient.helpers import MAXPORT
from pygpsclient.socketconfig_frame import SocketConfigFrame


class SocketConfigNtripFrame(SocketConfigFrame):
    """
    Socket configuration frame class.
    """

    def __init__(self, app, container, *args, **kwargs):
        """
        Constructor.

        :param tkinter.Frame container: reference to container frame
        :param args: optional args to pass to Frame parent class
        :param kwargs: optional kwargs for value ranges, or to pass to Frame parent class
        """

        self.__app = app
        super().__init__(app, container, *args, **kwargs)

    def _on_update_server(self, var, index, mode):
        """
        Server updated.
        """

        if not self.ent_server.validate(VALURL):
            return

        # also invokes _on_server() callback method in NTRIP
        # client panel to set data mode to SPARTN or RTCM
        if self._server_callback is not None:
            self._server_callback(var, index, mode)
        self.__app.configuration.set("ntripclientserver_s", self.server.get())

    def _on_update_port(self, var, index, mode):
        """
        Port updated.
        """

        if not self.ent_port.validate(VALINT, 0, MAXPORT):
            return

        try:
            if self.port.get() in DEFAULT_TLS_PORTS:
                self.https.set(1)
            else:
                self.https.set(0)
            self.__app.configuration.set("ntripclientport_n", int(self.port.get()))
        except TclError:
            pass

    def _on_update_https(self, var, index, mode):
        """
        Action on updating TLS flag.
        """

        self.__app.configuration.set("ntripclienthttps_b", int(self.https.get()))

    def _on_update_protocol(self, var, index, mode):
        """
        Action on updating TCP/UDP protocol.
        """

        try:
            self.__app.configuration.set("ntripclientprotocol_s", self.protocol.get())
        except TclError:
            pass

    def _on_update_selfsign(self, var, index, mode):
        """
        Action on updating self-sign flag.
        """

        self.__app.configuration.set("ntripclientselfsign_b", int(self.selfsign.get()))

    def reset(self):
        """
        Reset settings to saved configuration.
        """

        self._attach_events(False)
        cfg = self.__app.configuration
        self.server.set(cfg.get("ntripclientserver_s"))
        self.port.set(cfg.get("ntripclientport_n"))
        self.https.set(cfg.get("ntripclienthttps_b"))
        self.selfsign.set(cfg.get("ntripclientselfsign_b"))
        self.protocol.set(cfg.get("ntripclientprotocol_s"))
        self._attach_events(True)
