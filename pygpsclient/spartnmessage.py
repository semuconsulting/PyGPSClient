"""
Skeleton SPARTNMessage and SPARTNReader classes.

The SPARTNReader class will parse individual SPARTN messages
from any binary stream containing *solely* SPARTN data e.g. an
MQTT `/pp/ip` topic.

The SPARTNMessage class does not currently perform a full decode
of SPARTN protocol messages; it basically decodes just enough
information to identify message type/subtype, payload length and
other key metadata.

Sourced from https://www.spartnformat.org/download/
(available in the public domain)
© 2021 u-blox AG. All rights reserved.

If anyone wants to contribute a full SPARTN message decode, be my guest :-)

SPARTN 1X transport layer bit format:
+-----------+------------+-------------+------------+-----------+----------+
| preamble  | framestart |   payload   |  payload   | embedded  |   crc    |
| 0x73  's' |            |  descriptor |            | auth data |          |
+-----------+------------+-------------+------------+-----------+----------+
|<--- 8 --->|<--- 24 --->|<-- 32-64 -->|<- 8-8192 ->|<- 0-512 ->|<- 8-32 ->|


Created on 11 Feb 2023

:author: semuadmin
:copyright: SEMU Consulting © 2022
:license: BSD 3-Clause
"""
# pylint: disable=invalid-name too-many-instance-attributes

from socket import socket
from pyubx2.socket_stream import SocketStream
from pygpsclient.helpers import getbits

SPARTN_PRE = 0x73
SPARTN_MSGIDS = {
    0: "SPARTN-1X-OCB",  # Orbit, Clock, Bias
    (0, 0): "SPARTN-1X-OCB-GPS",
    (0, 1): "SPARTN-1X-OCB-GLO",
    (0, 2): "SPARTN-1X-OCB-GAL",
    (0, 3): "SPARTN-1X-OCB-BEI",
    (0, 4): "SPARTN-1X-OCB-QZS",
    1: "SPARTN-1X-HPAC",  # High-precision atmosphere correction
    (1, 0): "SPARTN-1X-HPAC-GPS",
    (1, 1): "SPARTN-1X-HPAC-GLO",
    (1, 2): "SPARTN-1X-HPAC-GAL",
    (1, 3): "SPARTN-1X-HPAC-BEI",
    (1, 4): "SPARTN-1X-HPAC-QZS",
    2: "SPARTN-1X-GAD",  # Geographic Area Definition
    (2, 0): "SPARTN-1X-GAD",
    3: "SPARTN-1X-BPAC",  # Basic-precision atmosphere correction
    (3, 0): "SPARTN-1X-BPAC",
    4: "SPARTN-1X-EAS",  # Encryption and Authentication Support
    (4, 0): "SPARTN-1X-EAS-DYN",
    (4, 1): "SPARTN-1X-EAS-GRP",  # deprecated
    120: "SPARTN_1X-PROP",  # Proprietary messages
    (120, 0): "SPARTN-1X-PROP-TEST",
    (120, 1): "SPARTN-1X-PROP-UBLOX",
    (120, 2): "SPARTN-1X-PROP-SWIFT",
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
            raise SPARTNMessageError("Payload must be provided")

        self._preamble = getbits(self._payload, 0, 8)
        if self._preamble != SPARTN_PRE:  # not SPARTN
            raise SPARTNParseError(f"Unknown message preamble {self._preamble}")

        self.msgType = getbits(self._payload, 8, 7)
        self.msgSubtype = getbits(self._payload, 32, 4)
        self.nData = getbits(self._payload, 15, 10)
        self.eaf = getbits(self._payload, 25, 1)
        self.crcType = getbits(self._payload, 26, 2)
        self.frameCrc = getbits(self._payload, 28, 4)
        self.timeTagtype = getbits(self._payload, 36, 1)
        timl = 16 if self.timeTagtype == 0 else 32
        self.gnssTimeTag = getbits(self._payload, 37, timl)
        self.solutionId = getbits(self._payload, 37 + timl, 7)
        self.solutionProcId = getbits(self._payload, 44 + timl, 4)

        self._do_attributes(**kwargs)

    def _do_attributes(self, **kwargs):
        """
        TODO this is where to do a full decode of a SPARTN message...
        """

    @property
    def identity(self) -> str:
        """
        Return message identity.
        """

        return SPARTN_MSGIDS.get((self.msgType, self.msgSubtype), "UNKNOWN")

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

        stg = f"<SPARTN({self.identity}, "
        for i, att in enumerate(self.__dict__):
            if att[0] != "_":  # only show public attributes
                val = self.__dict__[att]

                stg += att + "=" + str(val)
                if i < len(self.__dict__) - 1:
                    stg += ", "
        if self.identity == "UNKNOWN":
            stg += ", Not_Yet_Implemented"
        stg += ")>"

        return stg

    def __repr__(self) -> str:
        """
        Machine readable representation.
        eval(repr(obj)) = obj

        :return: machine readable representation
        :rtype: str
        """

        return f"SPARTNMessage(payload={self._payload})"


class SPARTNReader:
    """
    SPARTNReader class.
    """

    def __init__(self, datastream, **kwargs):
        """Constructor.
        :param datastream stream: input data stream
        :param int quitonerror: (kwarg) 0 = ignore,  1 = log and continue, 2 = (re)raise (1)
        :param int validate: (kwarg) 0 = ignore invalid checksum, 1 = validate checksum (1)
        :param bool scaling: (kwarg) apply attribute scaling True/False (True)
        :param int bufsize: (kwarg) socket recv buffer size (4096)
        :raises: SPARTNStreamError (if mode is invalid)
        """

        bufsize = int(kwargs.get("bufsize", 4096))
        if isinstance(datastream, socket):
            self._stream = SocketStream(datastream, bufsize=bufsize)
        else:
            self._stream = datastream
        self._quitonerror = int(kwargs.get("quitonerror", 1))

    def __iter__(self):
        """Iterator."""

        return self

    def __next__(self) -> tuple:
        """
        Return next item in iteration.
        :return: tuple of (raw_data as bytes, parsed_data as rtcmMessage)
        :rtype: tuple
        :raises: StopIteration
        """

        (raw_data, parsed_data) = self.read()
        if raw_data is not None:
            return (raw_data, parsed_data)
        raise StopIteration

    def read(self) -> tuple:
        """
        Read a single SPARTN message from the stream buffer
        and return both raw and parsed data.
        'quitonerror' determines whether to raise, log or ignore parsing errors.
        :return: tuple of (raw_data as bytes, parsed_data as SPARTNMessage)
        :rtype: tuple
        :raises: SPARTNStreamError (if unrecognised protocol in data stream)
        """

        parsing = True

        try:
            while parsing:  # loop until end of valid message or EOF
                raw_data = None
                parsed_data = None
                byte1 = self._read_bytes(1)  # read the first byte
                # if not SPARTN, discard and continue
                if byte1 == b"s":
                    (raw_data, parsed_data) = self._parse_spartn(byte1)
                    parsing = False
                # unrecognised protocol header
                else:
                    if self._quitonerror == 2:
                        raise SPARTNStreamError(f"Unknown protocol {byte1}.")
                    if self._quitonerror == 1:
                        return (byte1, f"<UNKNOWN PROTOCOL(header={byte1})>")
                    continue

        except EOFError:
            return (None, None)

        return (raw_data, parsed_data)

    def _parse_spartn(self, preamble: bytes) -> tuple:
        """
        Parse any SPARTN data in the stream.

        :param preamble hdr: preamble of SPARTN message
        :return: tuple of (raw_data as bytes, parsed_stub as SPARTNMessage)
        :rtype: tuple
        """
        # pylint: disable=unused-variable

        framestart = self._read_bytes(3)
        msgType = getbits(framestart, 0, 7)
        nData = getbits(framestart, 7, 10)
        eaf = getbits(framestart, 17, 1)
        crcType = getbits(framestart, 18, 2)
        frameCrc = getbits(framestart, 20, 4)

        if eaf:
            payDesc = self._read_bytes(6)
        else:
            payDesc = self._read_bytes(4)
        msgSubtype = getbits(payDesc, 0, 4)
        timeTagtype = getbits(payDesc, 4, 1)
        if timeTagtype:
            payDesc += self._read_bytes(2)
            gtlen = 32
            pos = 37
        else:
            gtlen = 16
            pos = 21
        gnssTimeTag = getbits(payDesc, 5, gtlen)
        if eaf:
            authInd = getbits(payDesc, pos + 21, 3)
            embAuthLen = getbits(payDesc, pos + 24, 3)
        # print(
        #     f"DEBUG parse_spartn len paydesc {len(payDesc)*8} msgtype:",
        #     f"{msgType} eaf: {eaf} crctype: {crcType} subtype: {msgSubtype}",
        #     f"gnsstime: {gnssTimeTag} timetag: {timeTagtype} authind: {authInd}",
        # )
        payload = self._read_bytes(nData)
        embAuth = b""
        if eaf and authInd > 1:
            if embAuthLen == 0:
                aln = 8
            elif embAuthLen == 1:
                aln = 12
            elif embAuthLen == 2:
                aln = 16
            elif embAuthLen == 3:
                aln = 32
            elif embAuthLen == 4:
                aln = 64
            embAuth = self._read_bytes(aln)
        crc = self._read_bytes(crcType + 1)
        raw_data = preamble + framestart + payDesc + payload + embAuth + crc
        parsed_data = self.parse(raw_data)

        return (raw_data, parsed_data)

    def _read_bytes(self, size: int) -> bytes:
        """
        Read a specified number of bytes from stream.
        :param int size: number of bytes to read
        :return: bytes
        :rtype: bytes
        :raises: EOFError if stream ends prematurely
        """

        data = self._stream.read(size)
        if len(data) < size:  # EOF
            raise EOFError()
        return data

    def iterate(self, **kwargs) -> tuple:
        """
        Invoke the iterator within an exception handling framework.
        :param int quitonerror: (kwarg) 0 = ignore,  1 = log and continue, 2 = (re)raise (1)
        :param object errorhandler: (kwarg) Optional error handler (None)
        :return: tuple of (raw_data as bytes, parsed_data as RTCMMessage)
        :rtype: tuple
        :raises: SPARTN...Error (if quitonerror is set and stream is invalid)
        """

        quitonerror = kwargs.get("quitonerror", self._quitonerror)
        errorhandler = kwargs.get("errorhandler", None)

        while True:
            try:
                yield next(self)  # invoke the iterator
            except StopIteration:
                break
            except (
                SPARTNMessageError,
                SPARTNParseError,
                SPARTNStreamError,
            ) as err:
                # raise, log or ignore any error depending
                # on the quitonerror setting
                if quitonerror == 2:
                    raise err
                if quitonerror == 1:
                    # pass to error handler if there is one
                    if errorhandler is None:
                        print(err)
                    else:
                        errorhandler(err)
                # continue

    @property
    def datastream(self) -> object:
        """
        Getter for stream.
        :return: data stream
        :rtype: object
        """

        return self._stream

    @staticmethod
    def parse(message: bytes, **kwargs) -> SPARTNMessage:
        """
        Parse SPARTN message to SPARTNMessage object.
        :param bytes message: SPARTN raw message bytes
        :return: SPARTNMessage object
        :rtype: SPARTNMessage
        :raises: SPARTN...Error (if data stream contains invalid data or unknown message type)
        """
        # pylint: disable=unused-argument

        return SPARTNMessage(payload=message)
