'''
SerialHandler class for PyGPSClient application

This handles all the serial i/o , threaded read process and data parsing

Created on 16 Sep 2020

@author: semuadmin
'''

from io import BufferedRWPair
from threading import Thread

from serial import Serial, SerialException, SerialTimeoutException

from .globals import CONNECTED, DISCONNECTED, SERIAL_TIMEOUT, \
                                NMEA_PROTOCOL, MIXED_PROTOCOL, UBX_PROTOCOL, PARITIES
from .nmea_handler import NMEAHandler
from .strings import WAITUBXDATA, STOPDATA, NOTCONN, SEROPENERROR
from .ubx_handler import UBXHandler
import pyubx2.ubxtypes_core as ubt


class SerialHandler():
    '''
    Serial handler class.
    '''

    def __init__(self, app):
        '''
        Constructor.
        '''

        self.__app = app  # Reference to main application class
        self.__master = self.__app.get_master()  # Reference to root class (Tk)

        self._nmea_handler = None
        self._ubx_handler = None
        self._serial_object = None
        self._serial_buffer = None
        self._serial_thread = None
        self._connected = False
        self._reading = False

    def connect(self):
        '''
        Open serial connection.
        '''

        settings = self.__app.frm_settings.get_settings()

        port = settings['port']
        port_desc = settings['port_desc']
        baudrate = settings['baudrate']
        databits = settings['databits']
        stopbits = settings['stopbits']
        parity = PARITIES[settings['parity']]
        xonxoff = settings['xonxoff']
        rtscts = settings['rtscts']

        try:
            self._serial_object = Serial(port,
                                         baudrate,
                                         bytesize=databits,
                                         stopbits=stopbits,
                                         parity=parity,
                                         xonxoff=xonxoff,
                                         rtscts=rtscts,
                                         timeout=SERIAL_TIMEOUT)
            self._serial_buffer = BufferedRWPair(self._serial_object, self._serial_object)
            self._nmea_handler = NMEAHandler(self.__app)
            self._ubx_handler = UBXHandler(self.__app)
            self.__app.frm_banner.update_banner(status=True)
            self.__app.set_connection(f"{port}:{port_desc} @ {str(baudrate)}", "green")
            self.__app.frm_settings.set_controls(CONNECTED)
            self._connected = True
            self.start_read_thread()
        except (SerialException, SerialTimeoutException) as err:
            self._connected = False
            self.__app.set_connection(f"{port}:{port_desc} @ {str(baudrate)}", "red")
            self.__app.set_status(SEROPENERROR.format(err), "red")
            self.__app.frm_banner.update_banner(status=False)
            self.__app.frm_settings.set_controls(DISCONNECTED)

    def disconnect(self):
        '''
        Close serial connection.
        '''

        if self._connected:
            try:
                self._reading = False
                self._serial_object.close()
                self.__app.frm_banner.update_banner(status=False)
                self.__app.set_connection(NOTCONN, "red")
                self.__app.set_status("", "blue")
            except (SerialException, SerialTimeoutException):
                pass

        self._connected = False
        self.__app.frm_settings.set_controls(self._connected)

    def serial_write(self, data: bytes):
        '''
        Write binary data to serial port.
        '''

        try:
            self._serial_object.write(data)
        except (SerialException, SerialTimeoutException) as err:
            print(f"Error writing to serial port {err}")

    def start_read_thread(self):
        '''
        Start the serial reader thread.
        '''

        if self._connected:
            self._reading = True
            self.__app.set_status(WAITUBXDATA, "blue")
            self.__app.frm_mapview.reset_map_refresh()
            self._serial_thread = Thread(target=self._read_thread, daemon=True)
            self._serial_thread.start()

    def stop_read_thread(self):
        '''
        Stop serial reader thread.
        '''

        if self._serial_thread is not None:
            self._reading = False
            self._serial_thread = None
            self.__app.set_status(STOPDATA, "red")

    def _read_thread(self):
        '''
        THREADED PROCESS
        Reads binary data from serial port and generates virtual event to
        trigger data parsing and widget updates.
        '''

        while self._reading and self._serial_object:
#             print(f"Bytes in buffer: {self._serial_object.in_waiting}")
            if self._serial_object.in_waiting:
                self.__master.event_generate('<<ubx_read>>')

    def on_read(self, event):  # pylint: disable=unused-argument
        '''
        Read any data in the buffer.
        '''

        self.__app.set_status("",)
        self._parse_data(self._serial_buffer)

    def _parse_data(self, ser: Serial) -> object:

        '''
        Parse the binary data.
        '''

        parsing = True
        raw_data = None

        byte1 = ser.read(1)

        while parsing:
            filt = self.__app.frm_settings.get_settings()['protocol']
            # if it's a UBX message
            if byte1 == ubt.UBX_HDR[0:1]:  # NB 'b1 == UBX_HDR[0]' doesn't work in python3
                # if we're not filtering out UBX messages
                # TODO MOVE THIS BLOCK TO UBX_HANDLER??
                if filt in (UBX_PROTOCOL, MIXED_PROTOCOL):
                    byte2 = ser.read(1)
                    if byte2 == ubt.UBX_HDR[1:2]:
                        byten = ser.read(4)
                        clsid = byten[0:1]
                        msgid = byten[1:2]
                        lenb = byten[2:4]
                        leni = int.from_bytes(lenb, 'little', signed=False)
                        byten = ser.read(leni + 2)
                        plb = byten[0:leni]
                        cksum = byten[leni:leni + 2]
                        raw_data = ubt.UBX_HDR + clsid + msgid + lenb + plb + cksum
                        self._ubx_handler.process_data(raw_data)
                    else:
                        parsing = False
            # if it's an NMEA message
            elif byte1 == ubt.NMEA_HDR[0:1]:
                # if we're not filtering out NMEA messages
                if filt in (NMEA_PROTOCOL, MIXED_PROTOCOL):
                    # TODO Decode errors can happen if
                    # mixed binary/text protocols get garbled
                    try:
                        raw_data = ser.readline().decode("utf-8")
                        # raw_data = '$' + ser.readline().decode("utf-8")
                        self._nmea_handler.process_data(raw_data)
                    except UnicodeDecodeError:
                        continue
                parsing = False
            # unrecognised message header
            else:
                parsing = False
