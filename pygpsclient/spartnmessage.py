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
from pygpsclient.helpers import bitsval

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


class SPARTNTypeError(Exception):
    """
    SPARTN Type error.
    """


class SPARTNMessage:
    """
    SPARTNMessage class.
    """

    def __init__(self, **kwargs):
        """
        Constructor.
        """

        # object is mutable during initialisation only
        super().__setattr__("_immutable", False)

        self._transport = kwargs.get("transport", None)
        if self._transport is None:
            raise SPARTNMessageError("Transport must be provided")

        self._preamble = bitsval(self._transport, 0, 8)
        if self._preamble != SPARTN_PRE:  # not SPARTN
            raise SPARTNParseError(f"Unknown message preamble {self._preamble}")

        self._scaling = kwargs.get("scaling", False)

        self._do_attributes()

        self._immutable = True  # once initialised, object is immutable

    def _do_attributes(self):
        """
        Populate SPARTNMessage attributes from transport.
        :param bytes self._transport: SPARTN message transport
        :raises: SPARTNTypeError
        """

        # start of framestart
        self.msgType = bitsval(self._transport, 8, 7)
        self.nData = bitsval(self._transport, 15, 10)
        self.eaf = bitsval(self._transport, 25, 1)
        self.crcType = bitsval(self._transport, 26, 2)
        self.frameCrc = bitsval(self._transport, 28, 4)

        # start of payDesc
        self.msgSubtype = bitsval(self._transport, 32, 4)
        self.timeTagtype = bitsval(self._transport, 36, 1)
        gln = 32 if self.timeTagtype else 16
        self.gnssTimeTag = bitsval(self._transport, 37, gln)
        pos = 37 + gln
        self.solutionId = bitsval(self._transport, pos, 7)
        self.solutionProcId = bitsval(self._transport, pos + 7, 4)
        pos += 11
        if self.eaf:  # encrypted payload
            self.encryptionId = bitsval(self._transport, pos, 4)
            self.encryptionSeq = bitsval(self._transport, pos + 4, 6)
            self.authInd = bitsval(self._transport, pos + 10, 3)
            self.embAuthLen = bitsval(self._transport, pos + 13, 3)
            pos += 16

        # start of payload
        self._payload = self._transport[int(pos / 8) : int(pos / 8) + self.nData]

        # start of embAuth
        pos += self.nData * 8
        aln = 0
        if self.authInd > 1:
            if self.embAuthLen == 0:
                aln = 64
            elif self.embAuthLen == 1:
                aln = 94
            elif self.embAuthLen == 2:
                aln = 128
            elif self.embAuthLen == 3:
                aln = 256
            elif self.embAuthLen == 4:
                aln = 512
            self.embAuth = bitsval(self._transport, pos, aln)

        # start of CRC
        pos += aln
        self.crc = bitsval(self._transport, pos, (self.crcType + 1) * 8)

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

        return f"SPARTNMessage(transport={self._transport})"

    def __setattr__(self, name, value):
        """
        Override setattr to make object immutable after instantiation.
        :param str name: attribute name
        :param object value: attribute value
        :raises: SPARTNMessageError
        """

        if self._immutable:
            raise SPARTNMessageError(
                f"Object is immutable. Updates to {name} not permitted after initialisation."
            )

        super().__setattr__(name, value)

    def serialize(self) -> bytes:
        """
        Serialize message.
        :return: serialized output
        :rtype: bytes
        """

        return self._transport

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
        Parse any SPARTN data in the stream. The structure of the transport layer
        depends on encryption type, GNSS timetag format and CRC format.

        :param preamble hdr: preamble of SPARTN message
        :return: tuple of (raw_data as bytes, parsed_stub as SPARTNMessage)
        :rtype: tuple
        :raises: EOFError if premature end of file
        """
        # pylint: disable=unused-variable

        framestart = self._read_bytes(3)
        msgType = bitsval(framestart, 0, 7)
        nData = bitsval(framestart, 7, 10)
        eaf = bitsval(framestart, 17, 1)
        crcType = bitsval(framestart, 18, 2)
        # frameCrc = bitsval(framestart, 20, 4)

        payDesc = self._read_bytes(4)
        msgSubtype = bitsval(payDesc, 0, 4)
        timeTagtype = bitsval(payDesc, 4, 1)
        if timeTagtype:
            payDesc += self._read_bytes(2)
        gtlen = 32 if timeTagtype else 16
        gnssTimeTag = bitsval(payDesc, 5, gtlen)
        # solutionId = bitsval(payDesc, gtlen + 5, 7)
        # solutionProcId = bitsval(payDesc, gtlen + 12, 4)
        authInd = 0
        if eaf:
            payDesc += self._read_bytes(2)
            # encryptionId = bitsval(payDesc, gtlen + 16, 4)
            # encryptionSeq = bitsval(payDesc, gtlen + 20, 6)
            authInd = bitsval(payDesc, gtlen + 26, 3)
            embAuthLen = bitsval(payDesc, gtlen + 29, 3)
        payload = self._read_bytes(nData)
        embAuth = b""
        if authInd > 1:
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
            else:
                aln = 0
            embAuth = self._read_bytes(aln)
        crc = self._read_bytes(crcType + 1)
        raw_data = preamble + framestart + payDesc + payload + embAuth + crc
        parsed_data = self.parse(raw_data)
        # print(
        #     f"DEBUG parse_spartn len paydesc {len(payDesc)*8} msgType: {msgType} msgSubtype: {msgSubtype}",
        #     f"gnssTimeTag: {gnssTimeTag} timeTagtype: {timeTagtype} eaf: {eaf} authind: {authInd}",
        #     f"embAuthLen {embAuthLen} crcType: {crcType} crc {int.from_bytes(crc,'little')}",
        # )

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

        return SPARTNMessage(transport=message)
