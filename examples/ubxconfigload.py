"""
ubxconfigload.py

ILLUSTRATION ONLY - NOT FOR PRODUCTION USE

This command line example illustrates how to load a series of
CFG-VALSET configuration messages from a binary file (saved using
the ubxconfigsave.py example) and load these to a comparable Generation 9+
UBX device.

It can be used to copy configuration from one device to another.

Usage (all kwargs are optional):

> python3 ubxconfigload.py infile=ubxconfig-latest.ubx port=/dev/ttyACM1 baud=9600 timeout=0.05 verbose=1

Created on 06 Jan 2023

:author: semuadmin
:copyright: SEMU Consulting © 2023
:license: BSD 3-Clause
"""

from os import getenv
import sys
from threading import Thread, Event, Lock
from multiprocessing import Queue
from time import sleep
from serial import Serial
from pyubx2 import UBXReader, UBX_PROTOCOL, SET, UBXMessageError, UBXParseError

# try increasing these values if device response is too slow:
DELAY = 0.05  # delay between sends
WRAPUP = 5  # final wrap up delay


class UBXLoader:
    """UBX Configuration Loader Class."""

    def __init__(self, file, stream, **kwargs):
        """Constructor."""

        self.file = file
        self.stream = stream
        self.verbose = kwargs.get("verbose", False)
        ubxreader = UBXReader(self.stream, protfilter=UBX_PROTOCOL)
        ubxloader = UBXReader(self.file, protfilter=UBX_PROTOCOL, msgmode=SET)

        self.serial_lock = Lock()
        self.send_queue = Queue()
        self.stop_event = Event()

        self.read_thread = Thread(
            target=self.read_data,
            args=(
                stream,
                ubxreader,
                self.serial_lock,
                self.stop_event,
            ),
        )
        self.write_thread = Thread(
            target=self.write_data,
            args=(
                stream,
                self.send_queue,
                self.serial_lock,
                self.stop_event,
            ),
        )
        self.load_thread = Thread(
            target=self.load_data,
            args=(
                ubxloader,
                self.send_queue,
                self.stop_event,
            ),
        )

        self.msg_ack = self.msg_nak = self.msg_write = self.msg_load = 0

    def read_data(
        self,
        stream: object,
        ubr: UBXReader,
        lock: Lock,
        stop: Event,
    ):
        """
        Read and parse incoming UBX data
        """
        # pylint: disable=broad-except

        while not stop.is_set():

            if stream.in_waiting:
                try:
                    lock.acquire()
                    (_, parsed_data) = ubr.read()
                    lock.release()
                    if parsed_data is not None:
                        if (
                            parsed_data.identity == "ACK-ACK"
                            and parsed_data.clsID == 6
                            and parsed_data.msgID == 138
                        ):
                            self.msg_ack += 1
                            if self.verbose:
                                print(f"ACK {self.msg_ack} - {parsed_data}")

                        elif (
                            parsed_data.identity == "ACK-NAK"
                            and parsed_data.clsID == 6
                            and parsed_data.msgID == 138
                        ):
                            self.msg_nak += 1
                            if self.verbose:
                                print(f"ACK {self.msg_nak} - {parsed_data}")
                except (UBXMessageError, UBXParseError):
                    continue
                except Exception as err:
                    print(f"\n\nSomething went wrong {err}\n\n")
                    continue

    def write_data(self, stream: object, queue: Queue, lock: Lock, stop: Event):
        """
        Read send queue and send UBX message to device
        """

        while not stop.is_set():

            if queue.empty() is False:
                parsed_data = queue.get()
                if parsed_data is not None:
                    lock.acquire()
                    stream.write(parsed_data.serialize())
                    lock.release()
                    self.msg_write += 1
                    if self.verbose:
                        print(f"WRITE {self.msg_write} - {parsed_data}")

    def load_data(self, ubr: UBXReader, queue: Queue, stop: Event):
        """
        Get CFG-VALSET data from file and place it on send queue.
        """

        while not stop.is_set():

            (_, parsed_data) = ubr.read()
            if parsed_data is not None:
                self.msg_load += 1
                queue.put(parsed_data)
                if self.verbose:
                    print(f"LOAD {self.msg_load} - {parsed_data}")
                sleep(DELAY)
            else:
                print(
                    "\nLast message loaded from file. Waiting for final acknowledgements...\n"
                )
                sleep(WRAPUP)  # allow time for responses to arrive
                stop.set()

    def run(self):
        """
        Main save routine.
        """

        print("\nStarting processes. Press Ctrl-C to terminate early...")

        self.read_thread.start()
        self.write_thread.start()
        self.load_thread.start()

        # loop until all commands sent or user presses Ctrl-C
        while not self.stop_event.is_set():
            try:
                pass
            except KeyboardInterrupt:  # capture Ctrl-C
                print(
                    "\n\nTerminated by user. WARNING! Configuration may be incomplete."
                )
                self.stop_event.set()

        print("\nStop signal set. Waiting for threads to complete...")

        self.read_thread.join()
        self.write_thread.join()
        self.load_thread.join()

        print("\nProcessing complete.")
        print(f"{self.msg_load} CFG-VALSET messages loaded from {self.file}")
        print(f"{self.msg_write} CFG-VALSET messages sent to device {self.stream}")
        print(
            f"{self.msg_ack} CFG-VALSET messages acknowledged",
            f" - {self.msg_ack*100/self.msg_load:.1f}%",
        )
        print(
            f"{self.msg_nak} CFG-VALSET messages rejected",
            f" - {self.msg_nak*100/self.msg_load:.1f}%",
        )


if __name__ == "__main__":

    home = f"{getenv('HOME')}/Downloads/"
    kwargs = dict(arg.split("=") for arg in sys.argv[1:])

    infile = kwargs.get("infile", f"{home}ubxconfig.ubx")
    port = kwargs.get("port", "/dev/tty.usbmodem101")
    baud = kwargs.get("baud", 9600)
    timeout = kwargs.get("timeout", 0.05)
    verbose = kwargs.get("verbose", False)

    with open(infile, "rb") as infile:
        with Serial(port, baud, timeout=timeout) as serial_stream:
            ubl = UBXLoader(infile, serial_stream, verbose=verbose)
            ubl.run()
