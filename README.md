# PyGPSClient

PyGPSClient is a graphical GNSS/GPS testing and diagnostic client application written entirely in Python and tkinter.

![full app screenshot ubx](/images/all_widgets.png)

The application runs on any platform which supports a Python3 interpreter (>=3.6) and tkinter (>=8.6) GUI framework, 
including Windows, MacOS, Linux and Raspberry Pi OS. It displays location and diagnostic data from any NMEA or UBX (u-blox &copy;) 
compatible GNSS/GPS device over a standard serial (UART) or USB port, or from a previously-saved datalog file, *in addition to* providing a small but useful subset of the configuration functionality in u-blox's Windows-only [u-center](https://www.u-blox.com/en/product/u-center) tool.

This is an independent project and we have no affiliation whatsoever with u-blox &copy;.

### Current Status

![Status](https://img.shields.io/pypi/status/pyubx2)
![Release](https://img.shields.io/github/v/release/semuconsulting/PyGPSClient?include_prereleases)
![Build](https://img.shields.io/travis/semuconsulting/PyGPSClient)
![Release Date](https://img.shields.io/github/release-date-pre/semuconsulting/PyGPSClient)
![Last Commit](https://img.shields.io/github/last-commit/semuconsulting/PyGPSClient)
![Contributors](https://img.shields.io/github/contributors/semuconsulting/PyGPSClient.svg)
![Open Issues](https://img.shields.io/github/issues-raw/semuconsulting/PyGPSClient)

Contributions and constructive feedback welcome.

## Features

1. Supports both NMEA and UBX protocols. It uses the existing pynmea2 library for NMEA parsing and 
implements a **[new pyubx2 library](https://github.com/semuconsulting/pyubx2)** for UBX parsing.
1. Capable of reading from serial/USB port or previously-saved binary datalog file. 
1. Configurable GUI with selectable and resizeable widgets.
1. Expandable banner widget showing key navigation information.
1. Serial console widget showing either raw or parsed data stream.
1. Skyview widget showing current satellite visibility and position (elevation / azimuth).
1. Graphview widget showing current satellite reception (signal-to-noise ratio).
1. Mapview widget with location marker, showing either a static Mercator world map, or an optional dynamic web-based map downloaded via a MapQuest API (requires an Internet connection and free 
[MapQuest API Key](https://developer.mapquest.com/plan_purchase/steps/business_edition/business_edition_free/register)).
1. Data logging.
1. Track recording in GPX format.
1. UBX Configuration Dialog, with the ability to send a variety of UBX configuration messages to u-blox GNSS devices. This includes the facility to add **user-defined messages or message sequences** - see instructions under [installation](#installation) below.

![compact view screenshot](/images/min_widgets.png)

## How to Use

* To connect to a listed serial device, select the device from the listbox and click 
![connect icon](/pygpsclient/resources/iconmonstr-link-8-24.png). The application will endeavour to pre-select a recognised GNSS/GPS device but this is platform and device dependent.
* To stream from a previously-saved binary datalog file (pygpsdata-*.log, or any binary dump of an NMEA or UBX GNSS device output), click 
![connect-file icon](/pygpsclient/resources/iconmonstr-note-37-24.png) and select the file.
* To disconnect from a serial device or datalog file, click
![disconnect icon](/pygpsclient/resources/iconmonstr-link-10-24.png).
* To display the UBX Configuration Dialog (*only available when connected to a UBX serial device*), click
![gear icon](/pygpsclient/resources/iconmonstr-gear-2-24.png), or go to Menu..Options.
* To show or hide the various widgets, go to Menu..View and click on the relevant hide/show option.
* Protocols Displayed - Select which protocols to display (NB: this only changes the displayed protocols - to change the actual protocols output by the receiver, use the CFG-PRT command).
* Console Display - Change the console display from parsed to raw (hexadecimal) format.
* Degrees Format and Units - Change the displayed degree and unit formats.
* Zoom - Change the web map scale (any change will take effect at the next map refresh, indicated by a small timer icon at the top left of the panel).
* Show Legend - Turn the graph legend on or off.
* Show Zero Signal - Include or exclude satellites with zero signal level in the graph and sky view panels.
* Enable Data Logging - Turn Data logging (in binary format) on or off. You will be prompted to select the directory into which timestamped log files are saved.
* Record Track - Turn track recording (in GPX format) on or off. You will be prompted to select the directory into which timestamped track files are saved.
* Widgets (and their associated fonts) are fully resizeable.

### UBX Configuration Facilities
![ubxconfig widget screenshot](/images/ubxconfig_widget.png)

The UBX Configuration Dialog currently supports the following UBX configuration commands:
1. CFG-PRT sets baud rate and inbound/outbound protocols across all available ports 
(*note that* an active USB port may report a baud rate of 0 on some platforms).
1. CFG-MSG sets message rates per port for NMEA protocol messages (standard & proprietary) and UBX protocol messages.
1. PRESET commands support a variety of preset and user-defined commands - see [user defined presets](#userdefined)

An icon to the right of each 'SEND' 
![send icon](/pygpsclient/resources/iconmonstr-arrow-12-24.png) button indicates the latest polled state of the displayed configuration 
(pending i.e. awaiting confirmation ![pending icon](/pygpsclient/resources/iconmonstr-time-6-24.png), 
confirmed ![confirmed icon](/pygpsclient/resources/iconmonstr-check-mark-8-24.png) or 
warning ![warning icon](/pygpsclient/resources/iconmonstr-warning-1-24.png)). 

**Note:**
* Command confirmation is not always 100% reliable as the UBX protocol does not support explicit command handshaking, and confirmation responses can occasionally get discarded or delayed at low baud rates. To ensure timely confirmation responses, try increasing the baud rate and/or temporarily minimising periodic inbound traffic using the preset commands provided.
* A warning icon (typically accompanied by an ACK-NAK response) is usually an indication that one or more of the messages sent is not supported by your receiver. 


#### Glossary of Terms

* utc - coordinated universal time.
* siv - satellites in view.
* sip - satellites used in position solution.
* dop - [dilution of precision](https://gisgeography.com/gps-accuracy-hdop-pdop-gdop-multipath/) (pdop - position, hdop - horizontal, vdop - vertical).
* acc - accuracy of location in real units (hacc - horizontal, vacc - vertical). Note that location accuracy is not directly provided via the standard NMEA message set, but is available via some proprietary NMEA messages e.g. UBX00.
* SV - space vehicle number
* PRN - pseudo-random noise number

## <a name="installation">Installation</a>

In the following, `python` & `pip` refer to the python3 executables. You may need to type 
`python3` or `pip3`, depending on your particular environment.

### Dependencies

See [requirements.txt](requirements.txt).

On Windows and MacOS, pip, tkinter and the necessary imaging libraries are generally packaged with Python.  On some Linux distributions like Ubuntu 18+ and Raspberry Pi OS, they may need to be installed separately, e.g.:

`sudo apt-get install python3-pip python3-tk python3-pil python3-pil.imagetk`

The following python libraries are required (these will be installed automatically if using pip to install PyGPSClient):

`python -m pip install pyubx2 pyserial pynmea2 Pillow requests`

### User Privileges

To access the serial port on most linux platforms, you will need to be a member of the 
`tty` and `dialout` groups. Other than this, no special privileges are required.

### 1. Install using pip

![Python version](https://img.shields.io/pypi/pyversions/PyGPSClient.svg?style=flat)
[![PyPI version](https://img.shields.io/pypi/v/PyGPSClient.svg?style=flat)](https://pypi.org/project/PyGPSClient/)
![PyPI downloads](https://img.shields.io/pypi/dm/PyGPSClient.svg?style=flat)

The easiest way to install the latest version of PyGPSClient is via [pip](http://pypi.python.org/pypi/pip/):

`python -m pip install --upgrade PyGPSClient`

To run the application, if the python3 site_packages are in your PATH, simply type `python -m pygpsclient`.

If not, type `python -m \full_path_to_site_packages\pygpsclient`.

**Tip**: to find the site_packages location, type `pip show PyGPSClient` and look for the `Location:` entry in the response, e.g.

- Linux: `Location: /home/username/.local/lib/python3.8/site-packages`
- MacOS: `Location: /Library/Frameworks/Python.framework/Versions/3.8/lib/python3.8/site-packages`
- Windows: `Location: c:\users\username\appdata\local\programs\python\python38\lib\site-packages`

### 2. Manual installation

To install manually, download and unzip this repository and run:

`python -m /path_to_folder/foldername/pygpsclient`

e.g. if you downloaded and unzipped to a folder named `PyGPSClient-0.2.0`, run: 

`python -m /path_to_folder/PyGPSClient-0.2.0/pygpsclient`.

### MapQuest API Key

To use the optional dynamic web-based mapview facility, you need to request and install a 
[MapQuest API key](https://developer.mapquest.com/plan_purchase/steps/business_edition/business_edition_free/register).
The free edition of this API allows for up to 15,000 transactions/month (roughly 500/day) on a non-commercial basis.
For this reason, the map refresh rate is intentionally limited to 1/minute* to avoid exceeding the free transaction
limit under normal use. **NB:** this facility is *not* intended to be used for real time navigational purposes.

Once you have received the API key (a 32-character alphanumeric string), copy it to a file named `mqapikey` (lower case, 
no extension) and place this file in the user's home directory.

*The web map refresh rate can be amended if required by changing the MAP_UPDATE_INTERVAL constant in `globals.py`.

### <a name="userdefined">User Defined Presets</a>

The UBX Configuration Dialog includes the facility to send user-defined UBX configuration messages or message sequences to the receiver. These can be set up by adding
appropriate comma-delimited message descriptions and payload definitions to a file named `ubxpresets` (lower case, no extension), and then placing this file in the user's home directory. The message definition comprises a free-format text description (*avoid embedded commas*) 
followed by one or more [pyubx2 UBXMessage constructors](https://pypi.org/project/pyubx2/), i.e. 
1. ubx_class as a string e.g. `CFG` (must be a valid class from pyubx2.UBX_CONFIG_CATEGORIES)
2. ubx_id as a string e.g. `CFG-MSG` (must be a valid id from pyubx2.UBX_CONFIG_MESSAGES)
3. payload as a hexadecimal string e.g. `f004010100010100` (leave blank for null payloads e.g. most POLL messages)
4. mode as an integer (`1` = SET, `2` = POLL)

Multiple commands can be concatenated on a single line. Illustrative examples are shown below:

```
Enable NMEA RMC sentence, CFG, CFG-MSG, f004010100010100, 1
Enable NMEA VTG sentence, CFG, CFG-MSG, f005010100010100, 1
Enable NMEA UBX00 & UBX03 sentences, CFG, CFG-MSG, f100010100010100, 1, CFG, CFG-MSG, f103010100010100, 1
Poll UART1/2 baud rates, CFG, CFG-VALGET, 000000000100524001005340, 2
Poll Message Rates, CFG, CFG-VALGET, 00000000ffff9120, 2, CFG, CFG-VALGET, 00004000ffff9120, 2, CFG, CFG-VALGET, 00008000ffff9120, 2
Use Extended NMEA SV Numbering, CFG, CFG-VALSET, 000000000700932001, 1
Poll Receiver Software Version, MON, MON-VER, , 2
Poll Datum, CFG, CFG-DAT, , 2
Poll GNSS config, CFG, CFG-GNSS, , 2
Poll NMEA config, CFG, CFG-NMEA, , 2
Poll Satellite-based Augmentation, CFG, CFG-SBAS, , 2
Poll Receiver Management, CFG, CFG-RXM, , 2
Poll Navigation Mode, CFG, CFG-NAV5, , 2
Poll Expert Navigation mode, CFG, CFG-NAVX5, , 2
Poll Geofencing, CFG, CFG-GEOFENCE, , 2
Limit NMEA GNSS to GPS only, CFG, CFG-NMEA, 0040000272000000000000010000000000000000, 1
Limit NMEA GNSS to GLONASS only, CFG, CFG-NMEA, 0040000253000000000000010000000000000000, 1
Set NMEA GNSS to ALL, CFG, CFG-NMEA, 0040000200000000000000010000000000000000, 1
Limit UBX GNSS to GPS only, CFG, CFG-GNSS, 0020200700081000010001010101030000000101020408000000010103081000000001010400080000000103050003000000010506080E0000000101, 1
Limit UBX GNSS to GLONASS only, CFG, CFG-GNSS, 0020200700081000000001010101030000000101020408000000010103081000000001010400080000000103050003000000010506080E0001000101, 1
Set UBX GNSS to ALL, CFG, CFG-GNSS, 0020200700081000010001010101030001000101020408000000010103081000000001010400080000000103050003000100010506080E0001000101, 1
FORCE COLD RESTART !*** Expect ClearCommError ***!, CFG, CFG-RST, ffff0100, 1
```

## License

![License](https://img.shields.io/github/license/semuconsulting/PyGPSClient.svg)

BSD 3-Clause License

Copyright (c) 2020, SEMU Consulting
All rights reserved.

Application icons from [iconmonstr](https://iconmonstr.com/license/) &copy;.

## Author Information

semuadmin@semuconsulting.com
