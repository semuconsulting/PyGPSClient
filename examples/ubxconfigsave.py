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

> python3 ubxconfigsave.py outfile=ubxconfig.ubx port=/dev/ttyACM1 baud=9600 timeout=0.02 verbose=1

Created on 06 Jan 2023

:author: semuadmin
:copyright: SEMU Consulting © 2023
:license: BSD 3-Clause
"""

from os import getenv
import sys
from threading import Thread, Event, Lock
from queue import Queue
from time import sleep, strftime
from serial import Serial
from pyubx2 import (
    UBXReader,
    UBXMessage,
    UBX_PROTOCOL,
    UBX_CONFIG_DATABASE,
    POLL_LAYER_RAM,
    SET_LAYER_RAM,
    TXN_START,
    TXN_ONGOING,
    TXN_COMMIT,
)

# try increasing these values if device response is too slow:
DELAY = 0.02  # delay between polls
WRAPUP = 5  # delay for final responses


def progbar(i: int, lim: int, inc: int = 20):
    """
    Display progress bar on console.
    """

    i = min(i, lim)
    pct = int(i * inc / lim)
    if not i % int(lim / inc):
        print("\u2593" * pct + "\u2591" * (inc - pct), end="\r")


class UBXSaver:
    """UBX Configuration Saver Class."""

    def __init__(self, file: object, stream: object, **kwargs):
        """Constructor."""

        self.file = file
        self.stream = stream
        self.verbose = int(kwargs.get("verbose", 0))

        ubxreader = UBXReader(stream, protfilter=UBX_PROTOCOL)

        self.serial_lock = Lock()
        self.read_queue = Queue()
        self.send_queue = Queue()
        self.stop_event = Event()

        self.read_thread = Thread(
            target=self.read_data,
            daemon=True,
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
            daemon=True,
            args=(
                stream,
                self.send_queue,
                self.serial_lock,
            ),
        )
        self.save_thread = Thread(
            target=self.save_data,
            daemon=True,
            args=(
                self.file,
                self.read_queue,
            ),
        )

        self.msg_sent = 0
        self.msg_rcvd = 0
        self.msg_save = 0
        self.cfgkeys = 0

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
                    if not stop.is_set():
                        print(f"\n\nSomething went wrong {err}\n\n")
                    continue

    def write_data(self, stream: object, queue: Queue, lock: Lock):
        """
        Read send queue and send UBX message to device
        """

        while True:

            if queue.empty() is False:
                message = queue.get()
                lock.acquire()
                stream.write(message.serialize())
                lock.release()

    def save_data(self, file: object, queue: Queue):
        """
        Get CFG-VALGET data from read queue, convert to CFG-VALSET commands
        and save to binary file.
        """

        i = 0
        while True:

            cfgdata = []
            while queue.qsize() > 0:
                (_, parsed) = queue.get()
                if parsed.identity == "CFG-VALGET":
                    for keyname in dir(parsed):
                        if keyname[0:3] == "CFG":
                            cfgdata.append((keyname, getattr(parsed, keyname)))
                queue.task_done()
                if len(cfgdata) >= 64:  # up to 64 keys in each CFG-VALSET
                    txn = TXN_ONGOING if i else TXN_START
                    self.file_write(file, txn, cfgdata)
                    cfgdata = []
                    i += 1
            if len(cfgdata) > 0:
                self.file_write(file, TXN_COMMIT, cfgdata)

    def file_write(self, file: object, txn: int, cfgdata: list):
        """
        Write binary CFG-VALSET message data to output file.
        """

        if len(cfgdata) == 0:
            return
        self.msg_save += 1
        self.cfgkeys += len(cfgdata)
        data = UBXMessage.config_set(
            layers=SET_LAYER_RAM, transaction=txn, cfgData=cfgdata
        )
        if self.verbose:
            print(f"SAVE {self.msg_save} - {data}")
        file.write(data.serialize())

    def run(self):
        """
        Main save routine.
        """

        print("\nStarting configuration poll. Press Ctrl-C to terminate early...")

        self.read_thread.start()
        self.write_thread.start()

        # loop until all commands sent or user presses Ctrl-C
        try:
            layer = POLL_LAYER_RAM
            position = 0
            keys = []
            for i, key in enumerate(UBX_CONFIG_DATABASE):
                if not self.verbose:
                    progbar(i, len(UBX_CONFIG_DATABASE), 50)
                keys.append(key)
                msg = UBXMessage.config_poll(layer, position, keys)
                self.send_queue.put(msg)
                self.msg_sent += 1
                if self.verbose:
                    print(f"POLL {i} - {msg}")
                keys = []
                sleep(DELAY)

            print(
                "\n\nAll keys in configuration database polled. Waiting for final responses..."
            )
            sleep(WRAPUP)
            self.stop_event.set()
            self.save_thread.start()

        except KeyboardInterrupt:  # capture Ctrl-C
            print("\n\nTerminated by user. WARNING! Configuration may be incomplete.")

        print("Responses processed. Waiting for data to be written to file...")

        self.read_queue.join()

        print("Processing complete.")
        print(f"{self.msg_sent} CFG-VALGET polls sent to {self.stream.port}")
        print(f"{self.msg_rcvd} CFG-VALGET responses received")
        print(
            f"{self.msg_save} CFG-VALSET messages containing {self.cfgkeys} keys",
            f"({self.cfgkeys*100/self.msg_rcvd:.1f}%) written to {self.file.name}",
        )


if __name__ == "__main__":

    home = f"{getenv('HOME')}/Downloads/"

    kwgs = dict(arg.split("=") for arg in sys.argv[1:])

    outfile = kwgs.get("outfile", f"{home}ubxconfig-{strftime('%Y%m%d%H%M%S')}.ubx")
    port = kwgs.get("port", "/dev/tty.usbmodem101")
    baud = kwgs.get("baud", 9600)
    timeout = kwgs.get("timeout", 0.02)
    verbose = int(kwgs.get("verbose", 0))

    with open(outfile, "wb") as outfile:
        with Serial(port, baud, timeout=timeout) as serial_stream:
            ubs = UBXSaver(outfile, serial_stream, verbose=verbose)
            ubs.run()
