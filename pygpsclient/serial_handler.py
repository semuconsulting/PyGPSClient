"""
SerialHandler class for PyGPSClient application

This handles all the serial i/o , threaded read process and direction to
the appropriate protocol handler

Created on 16 Sep 2020

@author: semuadmin
"""

from io import BufferedReader
from threading import Thread

from serial import Serial, SerialException, SerialTimeoutException

import pyubx2.ubxtypes_core as ubt

from .globals import (
    CONNECTED,
    CONNECTED_FILE,
    DISCONNECTED,
    SERIAL_TIMEOUT,
    NMEA_PROTOCOL,
    MIXED_PROTOCOL,
    UBX_PROTOCOL,
    PARITIES,
)
from .strings import STOPDATA, NOTCONN, SEROPENERROR, ENDOFFILE


class SerialHandler:
    """
    Serial handler class.
    """

    def __init__(self, app):
        """
        Constructor.

        :param object app: reference to main tkinter application
        """

        self.__app = app  # Reference to main application class
        self.__master = self.__app.get_master()  # Reference to root class (Tk)

        self._serial_object = None
        self._serial_buffer = None
        self._serial_thread = None
        self._file_thread = None
        self._connected = False
        self._logpath = None
        self._datalogging = False
        self._recordtrack = False
        self._port = None
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

        settings = self.__app.frm_settings.get_settings()

        self._port = settings["port"]
        port_desc = settings["port_desc"]
        baudrate = settings["baudrate"]
        databits = settings["databits"]
        stopbits = settings["stopbits"]
        parity = PARITIES[settings["parity"]]
        xonxoff = settings["xonxoff"]
        rtscts = settings["rtscts"]
        self._datalogging = settings["datalogging"]
        self._recordtrack = settings["recordtrack"]

        try:
            self._serial_object = Serial(
                self._port,
                baudrate,
                bytesize=databits,
                stopbits=stopbits,
                parity=parity,
                xonxoff=xonxoff,
                rtscts=rtscts,
                timeout=SERIAL_TIMEOUT,
            )
            self._serial_buffer = BufferedReader(self._serial_object)
            self.__app.frm_banner.update_conn_status(CONNECTED)
            self.__app.set_connection(
                f"{self._port}:{port_desc} @ {str(baudrate)}", "green"
            )
            self.__app.frm_settings.set_controls(CONNECTED)
            self._connected = True
            self.start_read_thread()

            if self._datalogging:
                self.__app.file_handler.open_logfile_output()

            if self._recordtrack:
                self.__app.file_handler.open_trackfile()

        except (IOError, SerialException, SerialTimeoutException) as err:
            self._connected = False
            self.__app.set_connection(
                f"{self._port}:{port_desc} @ {str(baudrate)}", "red"
            )
            self.__app.set_status(SEROPENERROR.format(err), "red")
            self.__app.frm_banner.update_conn_status(DISCONNECTED)
            self.__app.frm_settings.set_controls(DISCONNECTED)

    def connect_file(self):
        """
        Open binary data file connection.
        """

        settings = self.__app.frm_settings.get_settings()
        self._datalogging = False
        self._logpath = settings["logpath"]
        self._recordtrack = settings["recordtrack"]

        try:
            self._serial_object = open(self._logpath, "rb")
            self._serial_buffer = BufferedReader(self._serial_object)
            self.__app.frm_banner.update_conn_status(CONNECTED_FILE)
            self.__app.set_connection(f"{self._logpath}", "blue")
            self.__app.frm_settings.set_controls(CONNECTED_FILE)
            self._connected = True
            self.start_readfile_thread()

            if self._recordtrack:
                self.__app.file_handler.open_trackfile()

        except (IOError, SerialException, SerialTimeoutException) as err:
            self._connected = False
            self.__app.set_connection(f"{self._logpath}", "red")
            self.__app.set_status(SEROPENERROR.format(err), "red")
            self.__app.frm_banner.update_conn_status(DISCONNECTED)
            self.__app.frm_settings.set_controls(DISCONNECTED)

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

                if self._datalogging:
                    self.__app.file_handler.close_logfile()

                if self._recordtrack:
                    self.__app.file_handler.close_trackfile()

            except (SerialException, SerialTimeoutException):
                pass

        self._connected = False
        self.__app.frm_settings.set_controls(self._connected)

    @property
    def port(self):
        """
        Getter for port
        """

        return self._port

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

        :param bytes data
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
            self.__app.set_status(STOPDATA, "red")

    def stop_readfile_thread(self):
        """
        Stop file reader thread.
        """

        if self._file_thread is not None:
            self._reading = False
            self._file_thread = None
            self.__app.set_status(STOPDATA, "red")

    def _read_thread(self):
        """
        THREADED PROCESS
        Reads binary data from serial port and generates virtual event to
        trigger data parsing and widget updates.
        """

        try:
            #         print("doing serial_handler._read_thread")
            while self._reading and self._serial_object:
                #             print("doing serial_handler._read_thread while loop")
                if self._serial_object.in_waiting:
                    #                 print(f"Bytes in buffer: {self._serial_object.in_waiting}")
                    #                 print("doing serial_handler._read_thread in_waiting")
                    self.__master.event_generate("<<ubx_read>>")
        except SerialException as err:
            self.__app.set_status(f"Error in read thread {err}", "red")

    def _readfile_thread(self):
        """
        THREADED PROCESS
        Reads binary data from datalog file and generates virtual event to
        trigger data parsing and widget updates.
        """

        #         print("doing serial_handler._readfile_thread")
        while self._reading and self._serial_object:
            #             print("doing serial_handler._readfile_thread while loop")
            self.__master.event_generate("<<ubx_readfile>>")

    def on_read(self, event):  # pylint: disable=unused-argument
        """
        Action on <<ubx_read>> event - read any data in the buffer.

        :param event
        """

        #         print("doing serial_handler.on_read")
        if self._reading and self._serial_object is not None:
            try:
                self._parse_data(self._serial_buffer)
            except SerialException as err:
                self.__app.set_status(f"Error {err}", "red")

    def on_eof(self, event):  # pylint: disable=unused-argument
        """
        Action on end of file

        :param event
        """

        #         print("doing serial_handler.on_eof")
        self.disconnect()
        self.__app.set_status(ENDOFFILE, "blue")

    def _parse_data(self, ser: Serial):
        """
        Read the binary data and direct to the appropriate
        UBX and/or NMEA protocol handler, depending on which protocols
        are filtered.

        :param Serial ser: serial port
        """

        #         print("doing serial_handler_parse_data")
        parsing = True
        raw_data = None
        byte1 = ser.read(1)  # read first two bytes to determine protocol
        if len(byte1) < 1:
            self.__master.event_generate("<<ubx_eof>>")
            return

        while parsing:
            filt = self.__app.frm_settings.get_settings()["protocol"]
            byte2 = ser.read(1)
            if len(byte2) < 1:
                self.__master.event_generate("<<ubx_eof>>")
                return
            # if it's a UBX message (b'\b5\x62')
            if (
                byte1 == b"\xb5"
                and byte2 == b"\x62"
                and filt in (UBX_PROTOCOL, MIXED_PROTOCOL)
            ):
                #                 print(f"doing serial_handler._parse_data if ubx {ser.peek()}")
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
                self.__app.ubx_handler.process_data(raw_data)
                parsing = False
            # if it's an NMEA message ('$G' or '$P')
            elif (
                byte1 == b"\x24"
                and byte2 in (b"\x47", b"\x50")
                and filt
                in (
                    NMEA_PROTOCOL,
                    MIXED_PROTOCOL,
                )
            ):
                #                 print(f"doing serial_handler._parse_data if nmea {ser.peek()}")
                try:
                    raw_data = byte1 + byte2 + ser.readline()
                    self.__app.nmea_handler.process_data(raw_data.decode("utf-8"))
                except UnicodeDecodeError:
                    continue
                parsing = False
            # else drop it like it's hot
            else:
                #                 print(f"dropping {ser.peek()}")
                parsing = False

        # if datalogging, write to log file
        if self._datalogging and raw_data is not None:
            self.__app.file_handler.write_logfile(raw_data)

    def flush(self):
        """
        Flush input buffer
        """

        if self._serial_buffer is not None:
            self._serial_buffer.flush()
        if self._serial_object is not None:
            self._serial_object.flushInput()
