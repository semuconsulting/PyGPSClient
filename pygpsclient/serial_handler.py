"""
SerialHandler class for PyGPSClient application

This handles all the serial i/o , threaded read process and direction to
the appropriate protocol handler

Created on 16 Sep 2020

:author: semuadmin
:copyright: SEMU Consulting © 2020
:license: BSD 3-Clause
"""

from io import BufferedReader
from threading import Thread
from datetime import datetime, timedelta
from serial import Serial, SerialException, SerialTimeoutException
from pynmeagps import NMEAReader, NMEAParseError
from pyrtcm import RTCMReader
from pyubx2 import UBXReader, UBXParseError, RTCMMessage as RTCMStub
import pyubx2.ubxtypes_core as ubt
from pygpsclient.globals import (
    CONNECTED,
    CONNECTED_FILE,
    DISCONNECTED,
    CRLF,
    USE_PYRTCM,
    FILEREAD_INTERVAL,
)
from pygpsclient.strings import NOTCONN, SEROPENERROR, ENDOFFILE


class SerialHandler:
    """
    Serial handler class.
    """

    def __init__(self, app):
        """
        Constructor.

        :param Frame app: reference to main tkinter application

        """

        self.__app = app  # Reference to main application class
        self.__master = self.__app.get_master()  # Reference to root class (Tk)

        self._serial_object = None
        self._serial_buffer = None
        self._serial_thread = None
        self._file_thread = None
        self._connected = False
        self._connectedfile = False
        self._reading = False
        self._lastfileread = datetime.now()

    def __del__(self):
        """
        Destructor.
        """

        if self._serial_thread is not None:
            self._reading = False
            self._serial_thread = None
            self.disconnect()

    def connect(self):
        """
        Open serial connection.
        """
        # pylint: disable=consider-using-with

        serial_settings = self.__app.frm_settings.serial_settings()
        if serial_settings.status == 3:  # NOPORTS
            return

        try:
            self._serial_object = Serial(
                serial_settings.port,
                serial_settings.bpsrate,
                bytesize=serial_settings.databits,
                stopbits=serial_settings.stopbits,
                parity=serial_settings.parity,
                xonxoff=serial_settings.xonxoff,
                rtscts=serial_settings.rtscts,
                timeout=serial_settings.timeout,
            )
            self._serial_buffer = BufferedReader(self._serial_object)
            self.__app.frm_banner.update_conn_status(CONNECTED)
            self.__app.set_connection(
                (
                    f"{serial_settings.port}:{serial_settings.port_desc} "
                    + f"@ {str(serial_settings.bpsrate)}"
                ),
                "green",
            )
            self.__app.frm_settings.enable_controls(CONNECTED)
            self._connected = True
            self.start_read_thread()

            if self.__app.frm_settings.datalogging:
                self.__app.file_handler.open_logfile()

            if self.__app.frm_settings.record_track:
                self.__app.file_handler.open_trackfile()
            self.__app.set_status("Connected", "blue")

        except (IOError, SerialException, SerialTimeoutException) as err:
            self._connected = False
            self.__app.set_connection(
                (
                    f"{serial_settings.port}:{serial_settings.port_desc} "
                    + f"@ {str(serial_settings.bpsrate)}"
                ),
                "red",
            )
            self.__app.set_status(SEROPENERROR.format(err), "red")
            self.__app.frm_banner.update_conn_status(DISCONNECTED)
            self.__app.frm_settings.enable_controls(DISCONNECTED)

    def connect_file(self):
        """
        Open binary data file connection.
        """
        # pylint: disable=consider-using-with

        in_filepath = self.__app.frm_settings.infilepath
        if in_filepath is None:
            return

        try:
            self._serial_object = open(in_filepath, "rb")
            self._serial_buffer = BufferedReader(self._serial_object)
            self.__app.frm_banner.update_conn_status(CONNECTED_FILE)
            self.__app.set_connection(f"{in_filepath}", "blue")
            self.__app.frm_settings.enable_controls(CONNECTED_FILE)
            self._connectedfile = True
            self.start_readfile_thread()

            if self.__app.frm_settings.datalogging:
                self.__app.file_handler.open_logfile()

            if self.__app.frm_settings.record_track:
                self.__app.file_handler.open_trackfile()

        except (IOError, SerialException, SerialTimeoutException) as err:
            self._connected = False
            self.__app.set_connection(f"{in_filepath}", "red")
            self.__app.set_status(SEROPENERROR.format(err), "red")
            self.__app.frm_banner.update_conn_status(DISCONNECTED)
            self.__app.frm_settings.enable_controls(DISCONNECTED)

    def disconnect(self):
        """
        Close serial connection.
        """

        if self._connected or self._connectedfile:
            try:
                self._reading = False
                self._serial_object.close()
                self.__app.frm_banner.update_conn_status(DISCONNECTED)
                self.__app.set_connection(NOTCONN, "red")
                self.__app.set_status("", "blue")

                if self.__app.frm_settings.datalogging:
                    self.__app.file_handler.close_logfile()

                if self.__app.frm_settings.record_track:
                    self.__app.file_handler.close_trackfile()

            except (SerialException, SerialTimeoutException):
                pass

        self._connected = False
        self._connectedfile = False
        self.__app.frm_settings.enable_controls(self._connected)

    @property
    def port(self):
        """
        Getter for port
        """

        return self.__app.frm_settings.serial_settings().port

    @property
    def connected(self):
        """
        Getter for serial connection status
        """

        return self._connected

    @property
    def connectedfile(self):
        """
        Getter for file connection status
        """

        return self._connectedfile

    @property
    def serial(self):
        """
        Getter for serial object
        """

        return self._serial_object

    @property
    def buffer(self):
        """
        Getter for serial buffer
        """

        return self._serial_buffer

    @property
    def thread(self):
        """
        Getter for serial thread
        """

        return self._serial_thread

    def serial_write(self, data: bytes):
        """
        Write binary data to serial port.

        :param bytes data: data to write to stream
        """

        if self._connected and self._serial_object is not None:
            try:
                self._serial_object.write(data)
            except (SerialException, SerialTimeoutException) as err:
                print(f"Error writing to serial port {err}")

    def start_read_thread(self):
        """
        Start the serial reader thread.
        """

        if self._connected:
            self._reading = True
            self.__app.frm_mapview.reset_map_refresh()
            self._serial_thread = Thread(target=self._read_thread, daemon=True)
            self._serial_thread.start()

    def start_readfile_thread(self):
        """
        Start the file reader thread.
        """

        if self._connectedfile:
            self._reading = True
            self.__app.frm_mapview.reset_map_refresh()
            self._file_thread = Thread(target=self._readfile_thread, daemon=True)
            self._file_thread.start()

    def stop_read_thread(self):
        """
        Stop serial reader thread.
        """

        if self._serial_thread is not None:
            self._reading = False
            self._serial_thread = None
            # self.__app.set_status(STOPDATA, "red")

    def stop_readfile_thread(self):
        """
        Stop file reader thread.
        """

        if self._file_thread is not None:
            self._reading = False
            self._file_thread = None
            # self.__app.set_status(STOPDATA, "red")

    def _read_thread(self):
        """
        THREADED PROCESS
        Reads binary data from serial port and generates virtual event to
        trigger data parsing and widget updates.
        """

        try:
            while self._reading and self._serial_object:
                if self._serial_object.in_waiting:
                    self.__master.event_generate("<<gnss_read>>")
        except SerialException as err:
            self.__app.set_status(f"Error in read thread {err}", "red")
        # spurious errors as thread shuts down after serial disconnection
        except (TypeError, OSError):
            pass

    def _readfile_thread(self):
        """
        THREADED PROCESS
        Reads binary data from datalog file and generates virtual event to
        trigger data parsing and widget updates. A delay loop is introduced
        to ensure the GUI remains responsive during file reads.
        """

        while self._reading and self._serial_object:
            if datetime.now() > self._lastfileread + timedelta(
                seconds=FILEREAD_INTERVAL
            ):
                # self.__app.update_idletasks()
                self.__master.event_generate("<<gnss_readfile>>")
                self._lastfileread = datetime.now()

    def on_read(self, event):  # pylint: disable=unused-argument
        """
        EVENT TRIGGERED
        Action on <<gnss_read>> event - read any data in the buffer.

        :param event event: read event
        """

        if self._reading and self._serial_object is not None:
            try:
                self._parse_data(self._serial_buffer)
            except SerialException as err:
                self.__app.set_status(f"Error {err}", "red")

    def on_readfile(self, event):  # pylint: disable=unused-argument
        """
        EVENT TRIGGERED
        Action on <<gnss_readfile>> event - read any data from file.

        :param event event: read event
        """

        if self._reading and self._serial_object is not None:
            try:
                self._parse_data(self._serial_buffer)
                # self.__app.update_idletasks()
            except SerialException as err:
                self.__app.set_status(f"Error {err}", "red")

    def on_eof(self, event):  # pylint: disable=unused-argument
        """
        EVENT TRIGGERED
        Action on end of file

        :param event event: eof event
        """

        self.disconnect()
        self.__app.set_status(ENDOFFILE, "blue")

    def _parse_data(self, stream: object):
        """
        Read the binary data and direct to the appropriate
        UBX, NMEA or RTCM protocol handler, depending on which protocols
        are filtered.

        :param Serial ser: serial port
        """

        parsing = True
        raw_data = None
        parsed_data = None

        try:
            while parsing:  # loop until end of valid UBX/NMEA message or EOF
                byte1 = self._read_bytes(
                    stream, 1
                )  # read first byte to determine protocol
                if byte1 not in (
                    b"\xb5",
                    b"\x24",
                    b"\xd3",
                ):  # not UBX, NMEA or RTCM3, discard and continue
                    continue
                byte2 = self._read_bytes(stream, 1)
                # if it's a UBX message (b'\b5\x62')
                bytehdr = byte1 + byte2
                if bytehdr == ubt.UBX_HDR:
                    byten = self._read_bytes(stream, 4)
                    clsid = byten[0:1]
                    msgid = byten[1:2]
                    lenb = byten[2:4]
                    leni = int.from_bytes(lenb, "little", signed=False)
                    byten = self._read_bytes(stream, leni + 2)
                    plb = byten[0:leni]
                    cksum = byten[leni : leni + 2]
                    raw_data = bytehdr + clsid + msgid + lenb + plb + cksum
                    parsed_data = UBXReader.parse(raw_data)
                    parsing = False
                # if it's an NMEA GNSS message ('$G' or '$P')
                elif bytehdr in ubt.NMEA_HDR:
                    byten = stream.readline()
                    if byten[-2:] != CRLF:
                        raise EOFError
                    raw_data = bytehdr + byten
                    parsed_data = NMEAReader.parse(raw_data)
                    parsing = False
                # if it's a RTCM3 GNSS message
                # (byte1 = 0xd3; byte2 = 0b000000**)
                elif byte1 == b"\xd3" and (byte2[0] & ~0x03) == 0:
                    bytehdr3 = self._read_bytes(stream, 1)
                    size = bytehdr3[0] | (bytehdr[1] << 8)
                    payload = self._read_bytes(stream, size)
                    crc = self._read_bytes(stream, 3)
                    raw_data = bytehdr + bytehdr3 + payload + crc
                    if USE_PYRTCM:
                        parsed_data = RTCMReader.parse(raw_data)
                    else:
                        parsed_data = RTCMStub(payload)
                    parsing = False
                # else drop it like it's hot
                else:
                    parsing = False

        except EOFError:
            self.__master.event_generate("<<gnss_eof>>")
            return
        except (UBXParseError, NMEAParseError) as err:
            # log errors to console, then continue
            self.__app.frm_console.update_console(bytes(str(err), "utf-8"), err)
            return

        # logging.debug("raw: %s parsed: %s", raw_data, parsed_data)
        if raw_data is None or parsed_data is None:
            return
        # update the GUI, datalog file and GPX track file
        self.__app.process_data(raw_data, parsed_data)

    def _read_bytes(self, stream: object, size: int) -> bytes:
        """
        Read a specified number of bytes from stream.

        :param object stream: input stream
        :param int size: number of bytes to read
        :return: bytes
        :raises: EOFError if stream ends prematurely
        """

        data = stream.read(size)
        if len(data) < size:  # EOF
            raise EOFError()
        return data

    def flush(self):
        """
        Flush input buffer
        """

        if self._serial_buffer is not None:
            self._serial_buffer.flush()
        if self._serial_object is not None:
            self._serial_object.flushInput()
