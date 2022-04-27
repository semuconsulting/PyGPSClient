"""
SocketHandler class for PyGPSClient application

This handles all the TCP/UDP socket comms and direction to the
appropriate protocol handler.

Created on 27 Apr 2022

:author: semuadmin
:copyright: SEMU Consulting © 2022
:license: BSD 3-Clause
"""

from io import BufferedReader
from threading import Thread
from datetime import datetime, timedelta
import socket
from pynmeagps import NMEAReader, NMEAParseError
from pyrtcm import RTCMReader
from pyubx2 import UBXReader, UBXParseError
import pyubx2.ubxtypes_core as ubt
from pygpsclient.globals import (
    CONNECTED_SOCKET,
    DISCONNECTED,
    CRLF,
)
from pygpsclient.strings import NOTCONN, ENDOFFILE, SEROPENERROR

BUFLEN = 4096


class SocketHandler:
    """
    Socket handler class.
    """

    def __init__(self, app):
        """
        Constructor.

        :param Frame app: reference to main tkinter application

        """

        self.__app = app  # Reference to main application class
        self.__master = self.__app.get_master()  # Reference to root class (Tk)

        self._socket = None
        self._socket_thread = None
        self._server = None
        self._port = None
        self._connected = False
        self._reading = False

    def __del__(self):
        """
        Destructor.
        """

        if self._socket_thread is not None:
            self._reading = False
            self._socket_thread = None
            self.disconnect()

    def connect(self):
        """
        Open socket connection.
        """

        socket_settings = self.__app.frm_settings.socket_settings()
        self._server = socket_settings.server
        self._port = socket_settings.port
        if self._server == "" or self._port in ("", 0):
            self.__app.set_status("ERROR - please enter server and port", "red")
            return

        try:
            self.__app.conn_status = CONNECTED_SOCKET
            self.__app.set_connection(f"{self._server}:{self._port}", "green")
            self._connected = True
            self.start_read_thread()

            if self.__app.frm_settings.datalogging:
                self.__app.file_handler.open_logfile()

            if self.__app.frm_settings.record_track:
                self.__app.file_handler.open_trackfile()
            self.__app.set_status("Connected", "blue")

        except Exception as err:
            self._connected = False
            self.__app.set_connection(f"{self._server}:{self._port} ", "red")
            self.__app.set_status(SEROPENERROR.format(err), "red")
            self.__app.frm_banner.update_conn_status(DISCONNECTED)
            self.__app.frm_settings.enable_controls(DISCONNECTED)

    def disconnect(self):
        """
        Close socket connection.
        """

        if self._connected:
            try:
                self._socket.close()
                self._socket = None
                self._reading = False
                self.__app.conn_status = DISCONNECTED

            except Exception:
                pass

        self._connected = False
        self.__app.frm_settings.enable_controls(self._connected)

    @property
    def server(self):
        """
        Getter for server
        """

        return self.__app.frm_settings.socket_settings().server

    @property
    def port(self):
        """
        Getter for port
        """

        return self.__app.frm_settings.socket_settings().port

    @property
    def connected(self):
        """
        Getter for serial connection status
        """

        return self._connected

    @property
    def socket(self):
        """
        Getter for serial object
        """

        return self._socket

    @property
    def thread(self):
        """
        Getter for serial thread
        """

        return self._socket_thread

    def socket_write(self, data: bytes):
        """
        Write binary data to socket.

        :param bytes data: data to write to socket
        """

        if self._connected and self._socket is not None:
            try:
                self._socket.sendall(data)
            except Exception as err:
                print(f"Error writing to socket {err}")

    def start_read_thread(self):
        """
        Start the socket reader thread.
        """

        if self._connected:
            self._reading = True
            self.__app.frm_mapview.reset_map_refresh()
            self._socket_thread = Thread(target=self._read_thread, daemon=True)
            self._socket_thread.start()

    def stop_read_thread(self):
        """
        Stop socket reader thread.
        """

        if self._socket_thread is not None:
            self._reading = False
            self._socket_thread = None

    # def _read_thread(self):
    #     """
    #     THREADED PROCESS
    #     Reads binary data from socket and generates virtual event to
    #     trigger data parsing and widget updates.
    #     """

    #     try:
    #         while self._reading and self._serial_object:
    #             if self._socket_object.in_waiting:
    #                 self.__master.event_generate("<<socket_read>>")
    #     except SerialException as err:
    #         self.__app.set_status(f"Error in read thread {err}", "red")
    #     # spurious errors as thread shuts down after serial disconnection
    #     except (TypeError, OSError):
    #         pass

    def on_read(self, event):  # pylint: disable=unused-argument
        """
        EVENT TRIGGERED
        Action on <<socket_read>> event - read any data in the buffer.

        :param event event: read event
        """

        if self._reading and self._socket is not None:
            pass
            # try:
            #     self._parse_data(self._serial_buffer)
            # except SerialException as err:
            #     self.__app.set_status(f"Error {err}", "red")

    # def on_eof(self, event):  # pylint: disable=unused-argument
    #     """
    #     EVENT TRIGGERED
    #     Action on end of file

    #     :param event event: eof event
    #     """

    #     self.disconnect()
    #     self.__app.set_status(ENDOFFILE, "blue")

    def _read_thread(self):
        """
        THREADED PROCESS
        Start socket client connection.
        """

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self._socket:
            self._socket.connect((self._server, self._port))
            buf = bytearray()
            data = "init"
            try:
                while data:
                    data = self._socket.recv(BUFLEN)
                    print(f"Bytes received {len(data)}")
                    buf += data
                    while True:
                        raw, buf = self.parse_buffer(buf)
                        if raw is None:
                            break
            except (OSError,) as err:
                self.__app.set_status(f"Error in socket {err}", "red")

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
                self.__app.process_data(raw_data, parsed_data)
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
