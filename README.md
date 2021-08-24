# PyGPSClient

PyGPSClient is a graphical GNSS/GPS testing, diagnostic and UBX &copy; (u-blox &trade;) device configuration application written entirely in Python and tkinter.

![full app screenshot ubx](/images/all_widgets.png)

The application runs on any platform which supports a Python3 interpreter (>=3.6) and tkinter (>=8.6) GUI framework, 
including Windows, MacOS, Linux and Raspberry Pi OS. It displays location and diagnostic data from any NMEA or UBX compatible GNSS/GPS device over a standard serial (UART) or USB port, or from a previously-saved datalog file, *in addition to* providing a useful subset of the UBX configuration functionality in u-blox's Windows-only [u-center &copy;](https://www.u-blox.com/en/product/u-center) tool.

This is an independent project and we have no affiliation whatsoever with u-blox.

### Current Status

![Status](https://img.shields.io/pypi/status/PyGPSClient)
![Release](https://img.shields.io/github/v/release/semuconsulting/PyGPSClient)
![Build](https://img.shields.io/github/workflow/status/semuconsulting/pygpsclient/pygpsclient)
![Release Date](https://img.shields.io/github/release-date/semuconsulting/PyGPSClient)
![Last Commit](https://img.shields.io/github/last-commit/semuconsulting/PyGPSClient)
![Contributors](https://img.shields.io/github/contributors/semuconsulting/PyGPSClient.svg)
![Open Issues](https://img.shields.io/github/issues-raw/semuconsulting/PyGPSClient)

Sphinx API Documentation in HTML format is available at [https://www.semuconsulting.com/pygpsclient](https://www.semuconsulting.com/pygpsclient).

Contributions welcome - please refer to [CONTRIBUTING.MD](https://github.com/semuconsulting/PyGPSClient/blob/master/CONTRIBUTING.md).

[Bug reports](https://github.com/semuconsulting/PyGPSClient/blob/master/.github/ISSUE_TEMPLATE/bug_report.md) and [Feature requests](https://github.com/semuconsulting/PyGPSClient/blob/master/.github/ISSUE_TEMPLATE/feature_request.md) - please use the templates provided.

## Features

1. Supports both NMEA and UBX protocols. It uses the [pynmeagps library](https://pypi.org/project/pynmeagps/) for NMEA parsing and the [pyubx2 library](https://pypi.org/project/pyubx2/) for UBX parsing.
1. Capable of reading from serial/USB port or previously-saved binary datalog file. 
1. Configurable GUI with selectable and resizeable widgets.
1. Expandable banner widget showing key navigation information.
1. Serial console widget showing data stream in either parsed, binary or hexadecimal format.
1. Skyview widget showing current satellite visibility and position (elevation / azimuth). Satellite icon borders are colour-coded to distinguish between different GNSS constellations.
1. Graphview widget showing current satellite reception (signal-to-noise ratio).
1. Mapview widget with location marker, showing either a static Mercator world map, or an optional dynamic web-based map downloaded via a MapQuest API (requires an Internet connection and free 
[MapQuest API Key](https://developer.mapquest.com/plan_purchase/steps/business_edition/business_edition_free/register)).
1. Data logging in parsed, binary and hexadecimal formats.
1. Track recording in GPX format.
1. UBX Configuration Dialog, with the ability to send a variety of UBX configuration commands to u-blox GNSS devices. This includes the facility to add **user-defined commands or command sequences** - see instructions under [installation](#installation) below.

![compact view screenshot](/images/min_widgets.png)

## How to Use

* To connect to a listed serial device, select the device from the listbox, set the appropriate serial connection parameters and click 
![connect icon](/pygpsclient/resources/iconmonstr-link-8-24.png). The application will endeavour to pre-select a recognised GNSS/GPS device but this is platform and device dependent. Press the ![refresh](/pygpsclient/resources/iconmonstr-refresh-6-16.png) button to refresh the list of connected devices at any point. *Rate bps is typically the only setting that might need adjusting, but tweaking the timeout setting may improve performance on certain platforms*.
* To stream from a previously-saved binary datalog file (pygpsdata-*.log, or any binary dump of an NMEA or UBX GNSS device output), click 
![connect-file icon](/pygpsclient/resources/iconmonstr-note-37-24.png) and select the file.
* To disconnect from a serial device or datalog file, click
![disconnect icon](/pygpsclient/resources/iconmonstr-link-10-24.png).
* To display the UBX Configuration Dialog (*only available when connected to a UBX serial device*), click
![gear icon](/pygpsclient/resources/iconmonstr-gear-2-24.png), or go to Menu..Options.
* To expand or collapse the banner or serial port configuration widgets, click the ![expand icon](/pygpsclient/resources/iconmonstr-arrow-80-16.png)/![expand icon](/pygpsclient/resources/iconmonstr-triangle-1-16.png) buttons.
* To show or hide the various widgets, go to Menu..View and click on the relevant hide/show option.
* Protocols Displayed - Select which protocols to display (NB: this only changes the displayed protocols - to change the actual protocols output by the receiver, use the CFG-PRT command).
* Console Display - Select from parsed, binary or hexadecimal formats.
* Degrees Format and Units - Change the displayed degree and unit formats.
* Zoom - Change the web map scale (any change will take effect at the next map refresh, indicated by a small timer icon at the top left of the panel).
* Show Legend - Turn the graph legend on or off.
* Show Zero Signal - Include or exclude satellites with zero signal level in the graph and sky view panels.
* Enable Data Logging - Turn Data logging on or off. You will be prompted to select the directory into which timestamped log files are saved. Data logs can be saved in parsed, binary or hexadecimal formats (or all three together).
* Record Track - Turn track recording (in GPX format) on or off. You will be prompted to select the directory into which timestamped track files are saved.
* Widgets (and their associated fonts) are fully resizeable.

### UBX Configuration Facilities
![ubxconfig widget screenshot](/images/ubxconfig_widget.png)

The UBX Configuration Dialog currently supports the following UBX configuration 'widgets':
1. Shows current device hardware/firmware versions via MON-VER and MON-HW polls. Clicking anywhere in the widget background will refresh the displayed information with the current configuration.
1. CFG-PRT sets baud rate and inbound/outbound protocols across all available ports.
1. CFG-RATE sets navigation solution interval in ms (e.g. 1000 = 1/second) and measurement ratio (ratio between the number of
measurements and the number of navigation solutions, e.g. 5 = five measurements per navigation solution).
1. CFG-MSG sets message rates per port for UBX and NMEA messages. Message rate is relative to navigation solution frequency e.g. a message rate of '4' means 'every 4th navigation solution'.
1. CFG-VALSET, CFG-VALDEL and CFG-VALGET configuration (for [Generation 9+ devices](https://github.com/semuconsulting/pyubx2#configinterface)).
1. PRESET commands support a variety of preset and user-defined commands - see [user defined presets](#userdefined)

An icon to the right of each 'SEND' 
![send icon](/pygpsclient/resources/iconmonstr-arrow-12-24.png) button indicates the confirmation status of the configuration command; 
(pending i.e. awaiting confirmation ![pending icon](/pygpsclient/resources/iconmonstr-time-6-24.png), 
confirmed ![confirmed icon](/pygpsclient/resources/iconmonstr-check-mark-8-24.png) or 
warning ![warning icon](/pygpsclient/resources/iconmonstr-warning-1-24.png)). 

**Note:**
* Confirmation responses can take several seconds at high message transmission rates, or be discarded altogether if the device's transmit buffer is full (*txbuff-alloc error* - not uncommon with budget receivers at high message rates). To ensure timely confirmation responses, try increasing the baud rate and/or temporarily reducing transmitted message rates using the configuration commands provided.
* A warning icon (typically accompanied by an ACK-NAK response) is usually an indication that one or more of the commands sent is not supported by your receiver. 

## <a name="installation">Installation</a>

In the following, `python` & `pip` refer to the Python 3 executables. You may need to type 
`python3` or `pip3`, depending on your particular environment. It is also recommended that 
the Python 3 scripts (bin) and site_packages directories are included in your PATH 
(*most standard Python 3 installation packages will do this automatically*).

### Dependencies

On Windows and MacOS, pip, tkinter and the necessary imaging libraries are generally packaged with Python 3.  On some Linux distributions like Ubuntu 18+ and Raspberry Pi OS, they may need to be installed separately, e.g.:

```shell
sudo apt install python3-pip python3-tk python3-pil python3-pil.imagetk
```

### User Privileges

To access the serial port on most Linux platforms, you will need to be a member of the 
`tty` and `dialout` groups. Other than this, no special privileges are required.

### 1. Install using pip

![Python version](https://img.shields.io/pypi/pyversions/PyGPSClient.svg?style=flat)
[![PyPI version](https://img.shields.io/pypi/v/PyGPSClient.svg?style=flat)](https://pypi.org/project/PyGPSClient/)
![PyPI downloads](https://img.shields.io/pypi/dm/PyGPSClient.svg?style=flat)

The easiest way to install the latest version of `PyGPSClient` is with
[pip](http://pypi.python.org/pypi/pip/):

```shell
python -m pip install --upgrade PyGPSClient
```

If required, `PyGPSClient` can also be installed into a virtual environment, e.g.:

```shell
python -m pip install --user --upgrade virtualenv
python -m virtualenv env
source env/bin/activate (or env\Scripts\activate on Windows)
(env) python -m pip install --upgrade PyGPSClient
...
deactivate
```

To run the application, if the Python 3 scripts (bin) directory is in your PATH, simply type (all lowercase): 
```shell
pygpsclient
```

If desired, you can add a shortcut to this command to your desktop or favourites menu.

Alternatively, if the Python 3 site_packages are in your PATH, you can type (all lowercase): 
```shell
python -m pygpsclient
```

**NB:** If the Python 3 scripts (bin) or site_packages directories are *not* in your PATH, you will need to add the fully-qualified path to `pygpsclient` in the commands above.

**Tip:** to find the site_packages location, type:
```shell
python -m pip show PyGPSClient
``` 
and look for the `Location:` entry in the response, e.g.

- Linux: `Location: /home/username/.local/lib/python3.9/site-packages`
- MacOS: `Location: /Library/Frameworks/Python.framework/Versions/3.9/lib/python3.9/site-packages`
- Windows: `Location: c:\users\username\appdata\roaming\python\python39\lib\site-packages`

**Tip:** To create an application launcher for linux distributions like Ubuntu, create a text file named `pygpsclient.desktop` with the following content (*edited for your particular environment*) and copy this to the `/home/user/.local/share/applications` folder, e.g.

```
[Desktop Entry]
Type=Application
Terminal=false
Name=PyGPSClient
Icon=/home/user/.local/lib/python3.9/site-packages/pygpsclient/resources/pygpsclient.ico
Exec=/home/user/.local/bin/pygpsclient
```

### 2. Manual installation

See [requirements.txt](requirements.txt).

The following Python libraries are required (these will be installed automatically if using pip to install PyGPSClient):

```shell
python -m pip install --upgrade pyubx2 pynmeagps pyserial Pillow requests
```

To install PyGPSClient manually, download and unzip this repository and run:

```shell
python -m /path_to_folder/foldername/pygpsclient
```

e.g. if you downloaded and unzipped to a folder named `PyGPSClient-1.0.5`, run: 

```shell
python -m /path_to_folder/PyGPSClient-1.0.5/pygpsclient
```

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
1. message class as a string e.g. `CFG` (must be a valid class from pyubx2.UBX_CLASSES)
2. message id as a string e.g. `CFG-MSG` (must be a valid id from pyubx2.UBX_MSGIDS)
3. payload as a hexadecimal string e.g. `f004010100010100` (leave blank for null payloads e.g. most POLL messages)
4. mode as an integer (`1` = SET, `2` = POLL)

Multiple commands can be concatenated on a single line. Illustrative examples are shown below:

```
Stop GNSS, CFG, CFG-RST, 00000800, 1
Start GNSS, CFG, CFG-RST, 00000900, 1
Enable NMEA UBX00 & UBX03 sentences (legacy), CFG, CFG-MSG, f100010100010100, 1, CFG, CFG-MSG, f103010100010100, 1
Poll UART1/2 baud rates (modern), CFG, CFG-VALGET, 000000000100524001005340, 2
Poll Message Rates (modern), CFG, CFG-VALGET, 00000000ffff9120, 2, CFG, CFG-VALGET, 00004000ffff9120, 2, CFG, CFG-VALGET, 00008000ffff9120, 2
Use Extended NMEA SV Numbering (modern), CFG, CFG-VALSET, 000000000700932001, 1
Set NAV Solution Rate to 5 Hz (modern), CFG, CFG-VALSET, 0001000001002130c800, 1
Set NAV Solution Rate to 10 Hz (legacy), CFG, CFG-RATE, 640001000000, 1
Poll Receiver Software Version, MON, MON-VER, , 2
Poll Datum, CFG, CFG-DAT, , 2
Poll GNSS config, CFG, CFG-GNSS, , 2
Poll NMEA config, CFG, CFG-NMEA, , 2
Poll Satellite-based Augmentation, CFG, CFG-SBAS, , 2
Poll Receiver Management, CFG, CFG-RXM, , 2
Poll Navigation Mode, CFG, CFG-NAV5, , 2
Poll Expert Navigation mode, CFG, CFG-NAVX5, , 2
Poll Geofencing, CFG, CFG-GEOFENCE, , 2
Limit NMEA GNSS to GPS only (legacy), CFG, CFG-NMEA, 0040000272000000000000010000000000000000, 1
Limit NMEA GNSS to GLONASS only (legacy), CFG, CFG-NMEA, 0040000253000000000000010000000000000000, 1
Set NMEA GNSS to ALL (legacy), CFG, CFG-NMEA, 0040000200000000000000010000000000000000, 1
Limit UBX GNSS to GPS only (legacy), CFG, CFG-GNSS, 0020200700081000010001010101030000000101020408000000010103081000000001010400080000000103050003000000010506080E0000000101, 1
Limit UBX GNSS to GLONASS only (legacy), CFG, CFG-GNSS, 0020200700081000000001010101030000000101020408000000010103081000000001010400080000000103050003000000010506080E0001000101, 1
Set UBX GNSS to ALL (legacy), CFG, CFG-GNSS, 0020200700081000010001010101030001000101020408000000010103081000000001010400080000000103050003000100010506080E0001000101, 1
FORCE COLD RESTART !*** Expect ClearCommError ***!, CFG, CFG-RST, ffff0100, 1
```

#### Glossary of Terms

* ACC - accuracy of location in real units (hacc - horizontal, vacc - vertical). Note that location accuracy is not directly provided via the standard NMEA message set, but is available via some proprietary NMEA messages e.g. UBX00.
* BEI - [BeiDou Navigation Satellite System](https://en.wikipedia.org/wiki/BeiDou).
* DOP - [dilution of precision](https://gisgeography.com/gps-accuracy-hdop-pdop-gdop-multipath/) (pdop - overall position, hdop - horizontal, vdop - vertical).
* GAL - [Galileo Satellite Navigation](https://en.wikipedia.org/wiki/Galileo_(satellite_navigation)).
* GLO - [GLONASS, Global Navigation Satellite System](https://en.wikipedia.org/wiki/GLONASS).
* GNSS - [global navigation satellite system](https://en.wikipedia.org/wiki/Satellite_navigation).
* GPS - [Global Positioning System](https://en.wikipedia.org/wiki/Global_Positioning_System).
* IME - [IMES, Indoor MEssaging System](https://www.gpsworld.com/wirelessindoor-positioningopening-up-indoors-11603/)
* PRN - [pseudo-random noise number](https://www.gps.gov/technical/prn-codes/) (code that each satellite transmits to differentiate itself from other satellites in the active constellation).
* QZS - [QZSS, Quasi-Zenith Satellite System](https://en.wikipedia.org/wiki/Quasi-Zenith_Satellite_System).
* SBA - [SBAS, Satellite-based Augmentation System](https://en.wikipedia.org/wiki/GNSS_augmentation#Satellite-based_augmentation_system).
* SIP - satellites used in position solution.
* SIV - satellites in view.
* SV(N) - [space vehicle number](https://en.wikipedia.org/wiki/List_of_GPS_satellites) (serial number assigned to each satellite).
* UTC - coordinated universal time.

## License

![License](https://img.shields.io/github/license/semuconsulting/PyGPSClient.svg)

BSD 3-Clause License

Copyright &copy; 2020, SEMU Consulting
All rights reserved.

Application icons from [iconmonstr](https://iconmonstr.com/license/) &copy;.

## Author Information

semuadmin@semuconsulting.com


