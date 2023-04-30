"""
FOR TESTING ONLY

TCP socket client test harness.

Receives and parses arbitrary UBX messages from TCP server.

Created on 26 Apr 2022

:author: semuadmin
:copyright: SEMU Consulting © 2022
:license: BSD 3-Clause
"""

import socket

import pyubx2.ubxtypes_core as ubt
from pynmeagps import NMEAReader
from pyrtcm import RTCMReader
from pyubx2 import UBXReader

HOST = "localhost"  # The remote host
PORT = 50007  # The same port as used by the server
BUFLEN = 4096


class TCPClient:
    """
    TCP Client class.
    """

    def __init__(self, host, port):
        """
        Constructor.
        """

        self._host = host
        self._port = port

    def run(self):
        """
        Start client connection.
        """

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((self._host, self._port))
            buf = bytearray()
            data = "init"
            try:
                while data:
                    data = sock.recv(BUFLEN)
                    print(f"Bytes received {len(data)}")
                    buf += data
                    while True:
                        raw, buf = self.parse_buffer(buf)
                        if raw is None:
                            break
            except KeyboardInterrupt:
                print("TCP Client terminated by user")

    def parse_buffer(self, buf: bytearray) -> tuple:
        """
        Read buffer and parse the first complete UBX, NMEA or RTCM2 message.

        :param bytearray buf: buffer
        :return: tuple of (raw_data, buf_remain)
        :rtype: tuple
        """

        raw_data = None
        parsed_data = None
        buf_remain = buf
        start = 0

        while start < len(buf):
            try:
                byte1 = self._read_bytes(buf, start, 1)
                # if not NMEA, UBX or RTCM3, skip and continue
                if byte1 not in (b"\x24", b"\xb5", b"\xd3"):
                    start += 1
                    continue
                byte2 = self._read_bytes(buf, start + 1, 1)
                bytehdr = byte1 + byte2
                if bytehdr == ubt.UBX_HDR:  # UBX
                    raw_data, parsed_data = self.parse_ubx(buf, start, bytehdr)
                elif bytehdr in ubt.NMEA_HDR:  # NMEA
                    raw_data, parsed_data = self.parse_nmea(buf, start, bytehdr)
                elif byte1 == b"\xd3" and (byte2[0] & ~0x03) == 0:  # RTCM3
                    raw_data, parsed_data = self.parse_rtcm(buf, start, bytehdr)
                else:
                    start += 2
                    continue

                print(parsed_data)
                lnr = len(raw_data)
                buf_remain = buf[start + lnr :]
                break

            except EOFError:
                break

        return (raw_data, buf_remain)

    def parse_ubx(self, buf: bytearray, start: int, hdr: bytes) -> bytes:
        """
        Parse UBX Message.
        """

        byten = self._read_bytes(buf, start + 2, 4)
        lenb = int.from_bytes(byten[2:4], "little", signed=False)
        byten += self._read_bytes(buf, start + 6, lenb + 2)
        raw_data = bytes(hdr + byten)
        parsed_data = UBXReader.parse(raw_data)

        return raw_data, parsed_data

    def parse_nmea(self, buf: bytearray, start: int, hdr: bytes) -> bytes:
        """
        Parse NMEA Message.
        """

        i = 1
        # read buffer until CRLF - equivalent to readline()
        while True:
            byten = self._read_bytes(buf, start + 2, i)
            if byten[-2:] == b"\x0d\x0a":  # CRLF
                raw_data = bytes(hdr + byten)
                parsed_data = NMEAReader.parse(raw_data)
                break
            i += 1

        return raw_data, parsed_data

    def parse_rtcm(self, buf: bytearray, start: int, hdr: bytes) -> bytes:
        """
        Parse RTCM3 Message.
        """

        hdr3 = self._read_bytes(buf, start + 2, 1)
        lenb = hdr3[0] | (hdr[1] << 8)
        byten = self._read_bytes(buf, start + 3, lenb + 3)
        raw_data = bytes(hdr + hdr3 + byten)
        parsed_data = RTCMReader.parse(raw_data)

        return raw_data, parsed_data

    @staticmethod
    def _read_bytes(buf: bytearray, start: int, num: int) -> bytes:
        """
        Read specified number of bytes from buffer.

        :param bytearray buf: buffer
        :param int start: start index
        :param int num: number of bytes to read
        :return: bytes read
        :rtype: bytes
        :raises: EOFError
        """

        if len(buf) < start + num:
            raise EOFError
        return buf[start : start + num]


if __name__ == "__main__":
    print(f"Creating TCP client on {HOST}:{PORT}")
    client = TCPClient(HOST, PORT)

    print("Starting TCP client ...")
    client.run()
