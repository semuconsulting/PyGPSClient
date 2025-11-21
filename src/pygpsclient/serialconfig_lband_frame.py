"""
serialconfig_lband_frame.py

For L-Band modem configuration (e.g. u-blox NEO-D9S).
Inherited from generic SerialConfigFrame class.

Created on 24 Dec 2020

:author: semuadmin (Steve Smith)
:copyright: 2020 semuadmin
:license: BSD 3-Clause
"""

# pylint: disable=unused-argument

from pygpsclient.serialconfig_frame import MSGMODED, PARITIES, SerialConfigFrame


class SerialConfigLbandFrame(SerialConfigFrame):
    """
    L-BAND Serial port configuration frame class.
    """

    def __init__(self, app, container, *args, **kwargs):
        """
        Constructor.

        :param Frame app: reference to main tkinter application
        :param tkinter.Frame container: reference to container frame
        :param args: optional args to pass to Frame parent class
        :param kwargs: optional kwargs for value ranges, or to pass to Frame parent class
        """

        self.__app = app
        super().__init__(app, container, *args, **kwargs)

    def reset(self):
        """
        Reset settings to saved configuration.
        """

        self._attach_events(False)
        cfg = self.__app.configuration
        self._port.set(cfg.get("lbandclientserialport_s"))
        self._bpsrate.set(cfg.get("lbandclientbpsrate_n"))
        self._databits.set(cfg.get("lbandclientdatabits_n"))
        self._stopbits.set(cfg.get("lbandclientstopbits_f"))
        self._parity_name.set(PARITIES[cfg.get("lbandclientparity_s")])
        self._rtscts.set(cfg.get("lbandclientrtscts_b"))
        self._xonxoff.set(cfg.get("lbandclientxonxoff_b"))
        self._timeout.set(cfg.get("lbandclienttimeout_f"))
        self._msgmode_name.set(MSGMODED[cfg.get("lbandclientmsgmode_n")])
        self._inactivity_timeout.set(cfg.get("lbandclientinactivity_timeout_n"))
        self.user_defined_port.set(cfg.get("spartnport_s"))
        self._on_refresh_ports()
        self._attach_events(True)

    def _on_update_port(self, var, index, mode):
        """
        Action on update port.
        """

        self.__app.configuration.set("lbandclientserialport_s", self.port)

    def _on_update_bpsrate(self, var, index, mode):
        """
        Action on update baud rate.
        """

        self.__app.configuration.set("lbandclientbpsrate_n", int(self.bpsrate))

    def _on_update_databits(self, var, index, mode):
        """
        Action on update databits.
        """

        self.__app.configuration.set("lbandclientdatabits_n", int(self.databits))

    def _on_update_stopbits(self, var, index, mode):
        """
        Action on update stopbits.
        """

        self.__app.configuration.set("lbandclientstopbits_f", float(self.stopbits))

    def _on_update_parity_name(self, var, index, mode):
        """
        Action on update parity.
        """

        self.__app.configuration.set("lbandclientparity_s", self.parity)

    def _on_update_rtscts(self, var, index, mode):
        """
        Action on update RTS/CTS.
        """

        self.__app.configuration.set("lbandclientrtscts_b", int(self.rtscts))

    def _on_update_xonxoff(self, var, index, mode):
        """
        Action on update XON/XOFF.
        """

        self.__app.configuration.set("lbandclientxonxoff_b", int(self.xonxoff))

    def _on_update_timeout(self, var, index, mode):
        """
        Action on update serial read timeout.
        """

        self.__app.configuration.set("lbandclienttimeout_f", float(self.timeout))

    def _on_update_msgmode_name(self, var, index, mode):
        """
        Action on update msgmode.
        """

        self.__app.configuration.set("lbandclientmsgmode_n", int(self.msgmode))

    def _on_update_inactivity_timeout(self, var, index, mode):
        """
        Action on update inactivity timeout.
        """

        self.__app.configuration.set(
            "lbandclientinactivity_timeout_n", int(self.inactivity_timeout)
        )

    def _on_update_user_defined_port(self, var, index, mode):
        """
        Action on update user-defined port.
        """

        self.__app.configuration.set("spartnport_s", self.userport)
