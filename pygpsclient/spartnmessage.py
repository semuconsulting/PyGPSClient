"""
SPARTNMessage class.

Skeleton SPARTN message class - just parses identity.

(If anyone wants to write a full SPARTN message parser, be my guest:
https://www.spartnformat.org/download/ )

Created on 11 Feb 2023

:author: semuadmin
:copyright: SEMU Consulting © 2022
:license: BSD 3-Clause
"""

# use pyrtcm library helpers for bit handling
from pyrtcm.rtcmhelpers import bits2val, get_bitarray

SPARTN_MSGIDS = {
    0: "SPARTN-1X-OCB",
    1: "SPARTN-1X-HPAC",
    2: "SPARTN-1X-GAD",
    3: "SPARTN-1X-BPAC",
    4: "SPARTN-1X-EAS",
    120: "SPARTN_1X-PROPRIETARY",
}


class SPARTNStreamError(Exception):
    """
    SPARTN Streaming error.
    """


class SPARTNParseError(Exception):
    """
    SPARTN Parsing error.
    """


class SPARTNMessageError(Exception):
    """
    SPARTN Message error.
    """


class SPARTNMessage:
    """
    SPARTNMessage class.
    """

    def __init__(self, **kwargs):
        """
        Constructor.
        """

        self._payload = kwargs.get("payload", None)
        if self._payload is None:
            raise SPARTNParseError

        bits = get_bitarray(self._payload)
        self._preamble = bits2val("CHA008", 0, bits[0:8])
        if self._preamble != "s":  # not SPARTN
            raise SPARTNParseError
        self._msg_type = bits2val("UINT007", 0, bits[8:15])

        self._do_attributes(**kwargs)

    def _do_attributes(self, **kwargs):
        """
        TODO populate individual attributes when I get round to it
        """

    @property
    def identity(self) -> str:
        """
        Return message identity.
        """

        return SPARTN_MSGIDS.get(self._msg_type, f"UNKNOWN {self._msg_type}")

    @property
    def payload(self) -> str:
        """
        Return message payload.
        """

        return self._payload

    def __str__(self) -> str:
        """
        Human readable representation.

        :return: human readable representation
        :rtype: str
        """

        return f"<SPARTN({self.identity})>"

    def __repr__(self) -> str:
        """
        Machine readable representation.
        eval(repr(obj)) = obj

        :return: machine readable representation
        :rtype: str
        """

        return f"SPARTNMessage(payload={self._payload})"
