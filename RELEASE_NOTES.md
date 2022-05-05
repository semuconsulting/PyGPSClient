# PyGPSClient Release Notes

### RELEASE v1.3.1

ENHANCEMENTS:

1. Console color tagging is now user-configurable. The fixed color tags that were in `globals.py` are instead loaded from a file named 'colortags' in the user's home directory (see example in project root directory). A special color tag of 'HALT' allows the user to terminate streaming when a specified string match is found - this could for example be a particular message identity or a particular attribute value.
2. Add optional manual GGA settings (lat, lon, alt. sep) to NTRIP configuration dialog. If GGA sentence transmission is enabled, GGA sentence can either be constructed from live GNSS readings (if a receiver is connected) or from the four manual settings. If a GNSS receiver is not connected, the manual GGA settings must be used to send a GGA sentence.
3. Internal refactoring to use consistent message queuing technique for all incoming data streams (eliminates code duplication & offers moderate performance improvement). 

FIXES:

1. Enhanced error handling in serial and socket handlers - Fixes #22

### RELEASE v1.3.0

ENHANCEMENTS:

1. New BETA feature supports reading from TCP or UDP socket in addition to USB/UART and Binary File stream. At present, only open (i.e. unauthenticated, unencrypted) sockets are supported, and the connection is input only (i.e. you can't send UBX config polls or updates via the socket), but this may be enhanced in future versions.
2. Datalogging enhanced to record incoming NTRIP data stream.
3. Minor enhancements to NTRIP client exception handling.

### RELEASE v.1.2.1

CHANGES:

1. Minimum versions of `pyubx2` and `pyrtcm` updated to 1.2.7 and 0.2.5 respectively.

### RELEASE v.1.2.0

ENHANCEMENTS:

1. Various performance enhancements via internal refactoring, including updating the GUI widgets on a minimum interval basis (rather than on receipt of each NMEA or UBX message), streamlining and centralising GNSS status updates, and eliminating redundant tkinter `update()` and `update_idletasks()` operations. Note, however, that some [tkinter performance issues](https://github.com/semuconsulting/PyGPSClient#knownissues) remain on MacOS Monterey.
2. DGPS status added to information banner. **NB** this indicates the successful reception of DGPS correction data (e.g. RTCM3 or SBAS) based on information from NMEA (GGA, GNS) or UBX (NAV-PVT, NAV-STATUS, RXM-RTCM) messages. It does *not* necessarily indicate that a DGPS correction has been applied. Note that a) NMEA and UBX messages do not always give consistent indications of DGPS receipt status, and b) DGPS status *cannot* be reliably inferred from other NMEA message types (e.g. RMC, VTG) earlier than NMEA 4.10. 
3. UBX Configuration dialog can now be opened regardless of whether a device is connected (*but commands will only take effect when connected!*). The dialog is also now resizeable. (*These enhancements afford a workaround for current MacOS Monterey performance issues.*)
4. GPX Track recording now enabled for all NMEA and UBX message types which contain relevant position data, and trackpoints now include dgps data where available.


### RELEASE v1.1.9

ENHANCEMENTS:

1. Add Beta NTRIP Client facility. Connects to specified NTRIP server (caster) and feeds received RTCM3 messages through to connected RTCM3-compatible GNSS receiver. Tested with a variety of public and private NTRIP casters and u-blox GNSS receivers but additional testing and feedback welcome.

### RELEASE v1.1.8

ENHANCEMENTS:

1. Min version of `pyrtcm` updated to 0.2.4 (fixes a few RTCM parsing issues).
2. `pyrtcm` version added to About dialog.

### RELEASE v1.1.7

ENHANCEMENTS:

1. Added provision for RTCM3 message decoding via `pyrtcm` library. **NB** `pyrtcm` is still in Alpha
and provides basic decoding of RTCM3 messages to their constituent data fields. To revert to the 
'stub' RTCM3 decoding as used in v1.1.6, set the `USE_PYRTCM` constant in `globals.py` to `False`.
2. Min `pyubx2` version updated to v1.2.6.
3. Banner will now display high precision lat/lon where available.

### RELEASE v1.1.6

ENHANCEMENTS:

1. Added provision for RTCM3 messages following enhancements in `pyubx2` v1.2.5. **NB** `pygpsclient`
does not currently decode RTCM3 data - it simply indicates the presence of an RTCM3 message (with message
type) in the input stream.
2. Min `pyubx2` version updated to v1.2.5.

### RELEASE v1.1.5

FIXES:

1. Fix issue #9 where app becomes unresponsive with a null data stream. 

### RELEASE v1.1.4

ENHANCEMENTS:

1. Added tabular hex format to console display and datalogging format options.
2. Internal refactoring of serial handler to use `pyubx2.UBXReader.read()` function. 
3. Min pynmeagps version updated to 1.0.7
4. Min pyubx2 version updated to 1.2.4
5. Python 3.6 dropped from list of supported versions (if should still run fine, but 3.6 is now end of life)
6. Python 3.10 added to list of supported versions *BUT* note there still appear to be some teething performance issues with the version of tkinter embedded in Python 3.10 on MacOS Monterey. See installation notes for futher details.

FIXES:

1. Fix issue where first few seconds of datalogging or gpx tracking would fail on serial connections

### RELEASE v1.1.3

ENHANCEMENTS:

1. Additional configdb key categories added to CFG-VALGET/SET/DEL panel (CFG-HW-RF*, CFG-SPARTN*).
2. Minimum pyubx2 version updated to >=1.2.3.
3. Version checker added to Help panel.

### RELEASE v1.1.2

ENHANCEMENTS:

1. UBX handler scaling factors removed as pyubx2 >=1.2.0 now applies these internally.
2. Minimum pyubx2 version updated to >=1.2.0.


### RELEASE v1.1.1

ENHANCEMENTS:

1. Minor enhancements to UBX config configuration database dialog to aid category selection.
2. Minimum pyubx2 and pynmeagps versions updated to 1.1.6 and 1.0.6 respectively.

### RELEASE v1.1.0

ENHANCEMENTS:

1. Updated to handle changes in pyubx2 v1.1.0 - parsing of individvual bits in bitfield (type 'X') message attributes. For example, the NAV-PVT attribute valid (X1) is now parsed as four individual bit flags: validDate (U1), validTime (U1), fullyResolved (U1) and validMag (U1).

### RELEASE v1.0.11

FIXES:

1. Fix hidden confirmation box issue on UBX config dialog.
2. Various other minor fixes to dialog handling and positioning

### RELEASE v1.0.10

ENHANCEMENTS:

1. Console and datalogging enhanced to display either parsed, binary or hexadecimal formats.
2. Minimum pyubx2 version updated to 1.0.16.
3. Minimum pynmeagps version updated to 1.0.4.

### RELEASE v1.0.9

ENHANCEMENTS:

1. Additional CFG-VAL categories added for NEO-D9S, ZED-F9K, ZED-F9P & ZED-F9R Receivers.
2. Minimum pyubx2 version updated to 1.0.14.

### RELEASE v1.0.8

FIXES:

1. Updated to use pynmeagps v 1.0.3.

### RELEASE v1.0.7

FIXES:

1. Fixed distribution packaging glitch in 1.0.6 - CFG-BDS category should now appear in UBX CFG-VALSET dialog.


### RELEASE v1.0.6

CHANGES:

1. Entry point added to setup.py to allow app installed via pip to be invoked via simple command `pygpsclient`.
2. Minimum pynmeagps version updated to v1.0.1.
3. SUpport for BDS messages added to UBX CFG-VALSET config dialog.
4. Minor build script and documentation updates.


### RELEASE v1.0.5

CHANGES:

1. Helper methods moved from globals.py to new module helpers.py
2. Minimum pynmeagps version updated to v1.0.0

### RELEASE v1.0.4

FIXES:

1. Display position fix from HNR-PVT message.
2. Fix error on cancelling/quitting input filepath dialog on Linux.


### RELEASE v1.0.3

FIXES:

1. Fix 'flashing map' issue with mixed NMEA / UBX streams and no satellite fix. NB: 'flashing' (alternating between map and 'no fix' warning) may still occur if you have mixed streams and one outputs a valid position while the other doesn't, which can happen (e.g. position solutions are often reported in UBX messages slightly before they appear in NMEA messages).
2. Fix error on cancelling/quitting filepath dialog on Linux.
3. Fix highlighting of pre-selected serial port.
4. Other minor UI fixes.

ENHANCEMENTS:

1. Add facility to write data log in raw, parsed or both formats.
2. Add ability to refresh list of connected serial devices at run time. An existing connection must be terminated before connecting to a different device.
3. Allow datalogging from file input as well as serial port input.

INTERNAL CHANGES:

1. Generic serial port dialog moved to pygpsclient package; common package removed.

### RELEASE v1.0.2

FIX:

1. Fix failure to update vacc and hacc in banner from NMEA PUBX00 message

### RELEASE v1.0.1

ENHANCEMENTS:

1. NMEA handler updated to use new pynmeagps library (>=0.1.7) rather than pynmea2. This lightweight library obviates the need to perform NMEA lat/lon and other format conversions and makes the parsed NMEA representation more consistent with UBX.

### RELEASE v1.0.0

Version and status updated to v1.0.0 Production/Stable

ENHANCEMENTS:

1. Timeout setting added to common Serial port control dialog. 
2. Serial port baudrate configuration settings range extended to 921600.

