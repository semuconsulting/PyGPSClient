# PyGPSClient Release Notes

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

