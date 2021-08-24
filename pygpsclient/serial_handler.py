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
from serial import Serial, SerialException, SerialTimeoutException
import pyubx2.ubxtypes_core as ubt

from .globals import (
    CONNECTED,
    CONNECTED_FILE,
    DISCONNECTED,
    NMEA_PROTOCOL,
    MIXED_PROTOCOL,
    UBX_PROTOCOL,
)
from .strings import NOTCONN, SEROPENERROR, ENDOFFILE


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
        self._reading = False

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

        in_filepath = self.__app.frm_settings.infilepath
        if in_filepath is None:
            return

        try:
            self._serial_object = open(in_filepath, "rb")
            self._serial_buffer = BufferedReader(self._serial_object)
            self.__app.frm_banner.update_conn_status(CONNECTED_FILE)
            self.__app.set_connection(f"{in_filepath}", "blue")
            self.__app.frm_settings.enable_controls(CONNECTED_FILE)
            self._connected = True
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

        if self._connected:
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
        Getter for connection status
        """

        return self._connected

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

        if self._connected:
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
                    self.__master.event_generate("<<ubx_read>>")
        except SerialException as err:
            self.__app.set_status(f"Error in read thread {err}", "red")
        # spurious errors as thread shuts down after serial disconnection
        except (TypeError, OSError) as err:
            pass

    def _readfile_thread(self):
        """
        THREADED PROCESS
        Reads binary data from datalog file and generates virtual event to
        trigger data parsing and widget updates.
        """

        while self._reading and self._serial_object:
            self.__master.event_generate("<<ubx_readfile>>")

    def on_read(self, event):  # pylint: disable=unused-argument
        """
        Action on <<ubx_read>> event - read any data in the buffer.

        :param event event: read event
        """

        if self._reading and self._serial_object is not None:
            try:
                self._parse_data(self._serial_buffer)
            except SerialException as err:
                self.__app.set_status(f"Error {err}", "red")

    def on_eof(self, event):  # pylint: disable=unused-argument
        """
        Action on end of file

        :param event event: eof event
        """

        self.disconnect()
        self.__app.set_status(ENDOFFILE, "blue")

    def _parse_data(self, ser: Serial):
        """
        Read the binary data and direct to the appropriate
        UBX and/or NMEA protocol handler, depending on which protocols
        are filtered.

        :param Serial ser: serial port
        """

        parsing = True
        raw_data = None
        parsed_data = None
        byte1 = ser.read(1)  # read first byte to determine protocol
        if len(byte1) < 1:
            self.__master.event_generate("<<ubx_eof>>")
            return

        while parsing:
            filt = self.__app.frm_settings.protocol
            byte2 = ser.read(1)
            if len(byte2) < 1:
                self.__master.event_generate("<<ubx_eof>>")
                return
            # if it's a UBX message (b'\b5\x62')
            if byte1 == b"\xb5" and byte2 == b"\x62":
                byten = ser.read(4)
                if len(byten) < 4:
                    self.__master.event_generate("<<ubx_eof>>")
                    parsing = False
                    break
                clsid = byten[0:1]
                msgid = byten[1:2]
                lenb = byten[2:4]
                leni = int.from_bytes(lenb, "little", signed=False)
                byten = ser.read(leni + 2)
                if len(byten) < leni + 2:
                    self.__master.event_generate("<<ubx_eof>>")
                    parsing = False
                    break
                plb = byten[0:leni]
                cksum = byten[leni : leni + 2]
                raw_data = ubt.UBX_HDR + clsid + msgid + lenb + plb + cksum
                if filt in (UBX_PROTOCOL, MIXED_PROTOCOL):
                    parsed_data = self.__app.ubx_handler.process_data(raw_data)
                parsing = False
            # if it's an NMEA message ('$G' or '$P')
            elif byte1 == b"\x24" and byte2 in (b"\x47", b"\x50"):
                raw_data = byte1 + byte2 + ser.readline()
                if filt in (NMEA_PROTOCOL, MIXED_PROTOCOL):
                    parsed_data = self.__app.nmea_handler.process_data(raw_data)
                parsing = False
            # else drop it like it's hot
            else:
                parsing = False

        # if datalogging, write to log file
        if self.__app.frm_settings.datalogging:
            logformat = self.__app.frm_settings.logformat
            if logformat in ("Bin", "All") and raw_data is not None:
                self.__app.file_handler.write_logfile(raw_data)
            if logformat in ("Hex", "All") and raw_data is not None:
                self.__app.file_handler.write_logfile(raw_data.hex())
            if logformat in ("Parsed", "All") and parsed_data is not None:
                self.__app.file_handler.write_logfile(parsed_data)

    def flush(self):
        """
        Flush input buffer
        """

        if self._serial_buffer is not None:
            self._serial_buffer.flush()
        if self._serial_object is not None:
            self._serial_object.flushInput()
