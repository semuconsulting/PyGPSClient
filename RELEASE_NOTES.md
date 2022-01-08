# PyGPSClient Release Notes

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

