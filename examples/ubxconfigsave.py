"""
ubxconfigsave.py

ILLUSTRATION ONLY - NOT FOR PRODUCTION USE

This command line example illustrates how to poll every single
configuration database parameter for a Generation 9+ UBX device
and save the responses to a binary file. This file can be replayed
to a comparable device to reload the same configuration (using the
ubxconfigload.py example).

It can be used to copy configuration from one device to another.

Usage (all kwargs are optional):

> python3 ubxconfigsave.py outfile=ubxconfig-latest.ubx port=/dev/ttyACM1 baud=9600 timeout=0.02 verbose=1

Created on 06 Jan 2023

:author: semuadmin
:copyright: SEMU Consulting © 2023
:license: BSD 3-Clause
"""

from os import getenv
import sys
from threading import Thread, Event, Lock
from multiprocessing import Queue
from time import sleep, strftime
from serial import Serial
from pyubx2 import (
    UBXReader,
    UBXMessage,
    UBX_PROTOCOL,
    UBX_CONFIG_DATABASE,
    POLL_LAYER_RAM,
    SET_LAYER_RAM,
)

# try increasing these values if device response is too slow:
DELAY = 0.02  # delay between polls
WRAPUP = 5  # delay for final responses


class UBXSaver:
    """UBX Configuration Saver Class."""

    def __init__(self, file: object, stream: object, **kwargs):
        """Constructor."""

        self.file = file
        self.stream = stream
        self.verbose = kwargs.get("verbose", False)

        ubxreader = UBXReader(stream, protfilter=UBX_PROTOCOL)

        self.serial_lock = Lock()
        self.read_queue = Queue()
        self.send_queue = Queue()
        self.stop_event = Event()

        self.read_thread = Thread(
            target=self.read_data,
            args=(
                self.stream,
                ubxreader,
                self.read_queue,
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
        self.save_thread = Thread(
            target=self.save_data,
            args=(
                self.file,
                self.read_queue,
                self.stop_event,
            ),
        )

        self.msg_sent = 0
        self.msg_rcvd = 0
        self.msg_save = 0

    def read_data(
        self,
        stream: object,
        ubr: UBXReader,
        queue: Queue,
        lock: Lock,
        stop: Event,
    ):
        """
        Read and parse incoming UBX data and place
        raw and parsed data on read queue
        """
        # pylint: disable=broad-except

        while not stop.is_set():

            if stream.in_waiting:
                try:
                    lock.acquire()
                    (raw_data, parsed_data) = ubr.read()
                    lock.release()
                    if parsed_data is not None:
                        if parsed_data.identity == "CFG-VALGET":
                            queue.put((raw_data, parsed_data))
                            self.msg_rcvd += 1
                            if self.verbose:
                                print(f"RESPONSE {self.msg_rcvd} - {parsed_data}")
                except Exception as err:
                    print(f"\n\nSomething went wrong {err}\n\n")
                    continue

    def write_data(self, stream: object, queue: Queue, lock: Lock, stop: Event):
        """
        Read send queue and send UBX message to device
        """

        while not stop.is_set():

            if queue.empty() is False:
                message = queue.get()
                lock.acquire()
                stream.write(message.serialize())
                lock.release()

    def save_data(self, file: object, queue: Queue, stop: Event):
        """
        Get CFG-VALGET data from read queue, convert to CFG-VALSET commands
        and save to binary file.
        """

        while not stop.is_set():

            if queue.empty() is False:
                (_, parsed) = queue.get()
                if parsed.identity == "CFG-VALGET":
                    self.msg_save += 1
                    cfgdata = []
                    # convert to CFG-VALSET
                    for keyname, val in parsed.__dict__.items():
                        if keyname[0:3] == "CFG":
                            cfgdata.append((keyname, val))
                    data = UBXMessage.config_set(
                        layers=SET_LAYER_RAM, transaction=0, cfgData=cfgdata
                    )
                    if self.verbose:
                        print(f"SAVE {self.msg_save} - {data}")
                    file.write(data.serialize())

    def run(self):
        """
        Main save routine.
        """

        print("\nStarting processes. Press Ctrl-C to terminate early...")

        self.read_thread.start()
        self.write_thread.start()
        self.save_thread.start()

        # loop until all commands sent or user presses Ctrl-C
        while not self.stop_event.is_set():
            try:
                layer = POLL_LAYER_RAM
                position = 0
                keys = []
                for i, key in enumerate(UBX_CONFIG_DATABASE):
                    keys.append(key)
                    msg = UBXMessage.config_poll(layer, position, keys)
                    self.send_queue.put(msg)
                    self.msg_sent += 1
                    if self.verbose:
                        print(f"POLL {i} - {msg}")
                    keys = []
                    sleep(DELAY)

                print(
                    "\nAll keys in configuration database polled. Waiting for final responses..."
                )
                sleep(WRAPUP)
                self.stop_event.set()

            except KeyboardInterrupt:  # capture Ctrl-C
                print(
                    "\n\nTerminated by user. WARNING! Configuration may be incomplete."
                )
                self.stop_event.set()

        print("\nStop signal set. Waiting for threads to complete...")

        self.read_thread.join()
        self.write_thread.join()
        self.save_thread.join()

        print("\nProcessing complete.")
        print(f"{self.msg_sent} CFG-VALGET polls sent to {self.stream}")
        print(f"{self.msg_rcvd} CFG-VALGET responses received")
        print(f"{self.msg_save} CFG-VALSET messages saved to {self.file}")


if __name__ == "__main__":

    home = f"{getenv('HOME')}/Downloads/"

    kwargs = dict(arg.split("=") for arg in sys.argv[1:])

    outfile = kwargs.get("outfile", f"{home}ubxconfig-{strftime('%Y%m%d%H%M%S')}.ubx")
    port = kwargs.get("port", "/dev/tty.usbmodem101")
    baud = kwargs.get("baud", 9600)
    timeout = kwargs.get("timeout", 0.02)
    verbose = kwargs.get("verbose", False)

    with open(outfile, "wb") as outfile:
        with Serial(port, baud, timeout=timeout) as serial_stream:
            ubs = UBXSaver(outfile, serial_stream, verbose=verbose)
            ubs.run()
