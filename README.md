# PyGPSClient

[Current Status](#currentstatus) |
[Features](#features) |
[How to Use](#howtouse) |
[UBX Configuration](#ubxconfig) |
[NTRIP Client](#ntripconfig) |
[Installation](#installation) |
[Mapquest API Key](#mapquestapi) |
[User-defined Presets](#userdefined) |
[Known Issues](#knownissues) |
[Glossary of Terms](#glossary) |
[License](#license) |
[Author Information](#author)

PyGPSClient is a multi-platform graphical GNSS/GPS testing, diagnostic and UBX &copy; (u-blox &trade;) device configuration application written entirely in Python and tkinter.

![full app screenshot ubx](/images/all_widgets.png)

The application runs on any platform which supports a Python interpreter (>=3.7) and tkinter (>=8.6) GUI framework, including Windows, MacOS, Linux and Raspberry Pi OS. It displays navigation and diagnostic data from any NMEA, UBX or RTCM3 compatible GNSS/GPS device *in addition to* providing a useful subset of the UBX configuration functionality in u-blox's Windows-only [u-center &copy;](https://www.u-blox.com/en/product/u-center) tool.

The application can be installed using the standard `pip` Python package manager - see [installation instructions](#installation) below.

This is an independent project and we have no affiliation whatsoever with u-blox.

---
## <a name="currentstatus">Current Status</a>

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

---
## <a name="features">Features</a>

1. Supports NMEA, UBX and RTCM3 protocols.
1. Capable of reading from a variety of data streams: Serial (USB / UART), Socket (TCP / UDP) and binary datalog file. 
1. Configurable GUI with selectable and resizeable widgets.
1. Expandable banner widget showing key navigation information.
1. Serial console widget showing data stream in either parsed, binary or hexadecimal format.
1. User-configurable color tagging of selected console entries.
1. Skyview widget showing current satellite visibility and position (elevation / azimuth). Satellite icon borders are colour-coded to distinguish between different GNSS constellations.
1. Graphview widget showing current satellite reception (signal-to-noise ratio).
1. Mapview widget with location marker, showing either a static Mercator world map, or an optional dynamic web-based map downloaded via a MapQuest API (*requires an Internet connection and free 
[MapQuest API Key](https://developer.mapquest.com/user/login/sign-up)*).
1. Data logging in parsed, binary, hexadecimal string and tabulated hexadecimal formats (NB. only binary datalogs can be re-read by `PyGPSClient`'s parser).
1. Track recording in GPX format.
1. UBX Configuration Dialog, with the ability to send a variety of UBX configuration commands to u-blox GNSS devices. This includes the facility to add **user-defined commands or command sequences** - see instructions under [installation](#installation) below.
1. [NTRIP](https://en.wikipedia.org/wiki/Networked_Transport_of_RTCM_via_Internet_Protocol) Client ([differential GPS enhancement](https://en.wikipedia.org/wiki/Differential_GPS)) facility with the ability to connect to a specified NTRIP server (caster), parse the incoming RTCM3 data and feed this data to a compatible GNSS device (*requires an Internet connection and access to a suitable NTRIP caster*).

---
## <a name="howtouse">How to Use</a>

* To connect to a listed serial device, select the device from the listbox, set the appropriate serial connection parameters and click 
![connect icon](/pygpsclient/resources/usbport-1-24.png). The application will endeavour to pre-select a recognised GNSS/GPS device but this is platform and device dependent. Press the ![refresh](/pygpsclient/resources/iconmonstr-refresh-6-16.png) button to refresh the list of connected devices at any point. *Rate bps is typically the only setting that might need adjusting, but tweaking the timeout setting may improve performance on certain platforms*.
* **BETA FEATURE** To connect to a TCP or UDP socket, enter the server URL and port, select the protocol (defaults to TCP) and click 
![connect socket icon](/pygpsclient/resources/ethernet-1-24.png).
* To stream from a previously-saved binary datalog file, click 
![connect-file icon](/pygpsclient/resources/binary-1-24.png) and select the file. PyGPSClient datalog files will be named e.g. `pygpsdata-20220427114802.log`, but any binary dump of an GNSS receiver output is acceptable.
* To disconnect from the data stream, click
![disconnect icon](/pygpsclient/resources/iconmonstr-media-control-50-24.png).
* To display the UBX Configuration Dialog (*only available when connected to a UBX serial device*), click
![gear icon](/pygpsclient/resources/iconmonstr-gear-2-24.png), or go to Menu..Options.
* To display the NTRIP Client Configuration Dialog (*requires internet connection*), click
![gear icon](/pygpsclient/resources/iconmonstr-antenna-6-24.png), or go to Menu..Options.
* To expand or collapse the banner or serial port configuration widgets, click the ![expand icon](/pygpsclient/resources/iconmonstr-arrow-80-16.png)/![expand icon](/pygpsclient/resources/iconmonstr-triangle-1-16.png) buttons.
* To show or hide the various widgets, go to Menu..View and click on the relevant hide/show option.
* Protocols Shown - Select which protocols to display; NMEA, UBX and/or RTCM3 (NB: this only changes the displayed protocols - to change the actual protocols output by the receiver, use the CFG-PRT command).
* Console Display - Select from parsed, binary or hexadecimal formats.
* Tags - Turn console color tagging on or off. User-configurable color tags are loaded from a file "colortags" (lower case, no extension) in the user's home directory - see example provided. NB: color tagging does impose a small performance overhead - turning it off will improve console response times at very high transaction rates.
* Degrees Format and Units - Change the displayed degree and unit formats.
* Zoom - Change the web map scale (any change will take effect at the next map refresh, indicated by a small timer icon at the top left of the panel).
* Show Legend - Turn the graph legend on or off.
* Show Unused Satellites - Include or exclude satellites that are not used in the navigation solution (e.g. because their signal level is too low) from the graph and sky view panels.
* DataLogging - Turn Data logging in the selected format on or off. You will be prompted to select the directory into which timestamped log files are saved (NB. only binary datalogs can be re-read by `pygpsclient`'s parser).
* GPX Track - Turn track recording (in GPX format) on or off. You will be prompted to select the directory into which timestamped track files are saved.

---
### <a name="ubxconfig">UBX Configuration Facilities</a>

![ubxconfig widget screenshot](/images/ubxconfig_widget.png)

The UBX Configuration Dialog currently supports the following UBX configuration 'widgets':
1. Version widget shows current device hardware/firmware versions (*via MON-VER and MON-HW polls*).
1. Protocol Configuration widget (CFG-PRT) sets baud rate and inbound/outbound protocols across all available ports.
1. Solution Rate widget (CFG-RATE) sets navigation solution interval in ms (e.g. 1000 = 1/second) and measurement ratio (ratio between the number of measurements and the number of navigation solutions, e.g. 5 = five measurements per navigation solution).
1. For each of the widgets above, clicking anywhere in the widget background will refresh the displayed information with the current configuration.
1. Message Rate widget (CFG-MSG) sets message rates per port for UBX and NMEA messages. Message rate is relative to navigation solution frequency e.g. a message rate of '4' means 'every 4th navigation solution'.
1. Configuration Interface widget (CFG-VALSET, CFG-VALDEL and CFG-VALGET) queries and sets configuration for [Generation 9+ devices](https://github.com/semuconsulting/pyubx2#configinterface) e.g. NEO-M9, ZED-F9P, etc.
1. Preset Commands widget supports a variety of preset and user-defined commands - see [user defined presets](#userdefined)

An icon to the right of each 'SEND' 
![send icon](/pygpsclient/resources/iconmonstr-arrow-12-24.png) button indicates the confirmation status of the configuration command; 
(pending i.e. awaiting confirmation ![pending icon](/pygpsclient/resources/iconmonstr-time-6-24.png), 
confirmed ![confirmed icon](/pygpsclient/resources/iconmonstr-check-mark-8-24.png) or 
warning ![warning icon](/pygpsclient/resources/iconmonstr-warning-1-24.png)). 

**Note:**
* Confirmation responses can take several seconds at high message transmission rates, or be discarded altogether if the device's transmit buffer is full (*txbuff-alloc error*). To ensure timely confirmation responses, try increasing the baud rate and/or temporarily reducing transmitted message rates using the configuration commands provided.
* A warning icon (typically accompanied by an ACK-NAK response) is usually an indication that one or more of the commands sent is not supported by your receiver. 

---
### <a name="ntripconfig">NTRIP Client Facilities</a>

**BETA FEATURE**

![ntrip config widget screenshot](/images/ntripconfig_widget.png)

To use:
1. Enter the required NTRIP server URL (or IP address) and port (defaults to 2101). For services which require authorisation, enter your login username and password.
1. To retrieve the sourcetable, leave the mountpoint field blank and click connect (*response may take a few seconds*). The required mountpoint may then be selected from the list, or entered manually.
1. For NTRIP services which require client position data via NMEA GGA sentences, select the appropriate sentence transmission interval in seconds (*only available when a GNSS receiver is connected*). The default is 'None' (no GGA sentences sent). A value of 10 or 60 seconds is typical.
1. If GGA sentence transmission is enabled, GGA sentences can either be populated from live navigation data (*assuming a receiver is connected and outputting valid position data*) or from manual settings entered in the NTRIP configuration panel (latitude, longitude, elevation and separation - all four manual settings must be provided).
1. To connect to the NTRIP server, click ![connect icon](/pygpsclient/resources/iconmonstr-media-control-48-24.png). To disconnect, click ![disconnect icon](/pygpsclient/resources/iconmonstr-media-control-50-24.png).
1. If NTRIP data is being successfully received, the banner '**dgps:**' status indicator should change to 'YES' and indicate the age and reference station of the correction data (where available) ![dgps status](/images/dgps_status.png). Note that DGPS status is typically maintained for up to 60 seconds after loss of correction signal.
1. Some NTRIP services may output RTCM3 correction messages at a high rate, flooding the GUI console display. To suppress these messages in the console, de-select the 'RTCM' option in 'Protocols Shown' - the RTCM3 messages will continue to be processed in the background.

Below is a illustrative NTRIP DGPS data log, showing:
* Outgoing NMEA GPGGA (client position) sentence.
* Incoming RTCM3 correction messages; in this case - 1006 (Ref station ARP (*DF003=2690*) with antenna height), 1008 (Antenna descriptor), 1033 (Receiver descriptor), 1075 (GPS MSM5), 1085 (GLONASS MSM5), 1095 (Galileo MSM5), 1125 (BeiDou MSM5) and 1230 (GLONASS Code-Phase Biases)
* Corresponding UBX RXM-RTCM acknowledgements generated by the u-blox ZED-F9P receiver, confirming message type, valid checksum (*crcFailed=0*), successful use (*msgUsed=2*) and reference station ARP (*refStation=2690*). 
* The incoming DGPS correction status can also be verified by reference to e.g. NMEA GGA (*diffAge=1.0, diffStation=2690*), UBX NAV-PVT (*difSoln=1, lastCorrectionAge=2*) or UBX NAV-STATUS (*diffSoln=1, diffCorr=1*) messages. NB. Some of the DGPS status attributes are only available in the latest UBX firmware versions e.g. HPG 1.30.

![ntrip console screenshot](/images/ntrip_consolelog.png)

**NB:** Please respect the terms and conditions of any remote NTRIP service used with this facility. For testing or evaluation purposes, consider deploying a local [SNIP LITE](https://www.use-snip.com/download/) server. *Inappropriate use of an NTRIP service may result in your account being blocked*.

---
## <a name="installation">Installation</a>

In the following, `python` & `pip` refer to the Python 3 executables. You may need to type 
`python3` or `pip3`, depending on your particular environment. It is also recommended that 
the Python 3 scripts (bin) and site_packages directories are included in your PATH 
(*most standard Python 3 installation packages will do this automatically*).

### Platform Dependencies

On Windows and MacOS, pip, tkinter and the necessary imaging libraries are generally packaged with Python 3.  On some Linux distributions like Ubuntu 18+ and Raspberry Pi OS, they may need to be installed separately, e.g.:

```shell
sudo apt install python3-pip python3-tk python3-pil python3-pil.imagetk
```

*NB:* If you're compiling the latest version of Python 3 from source, you may also need to install tk-dev (or a similarly named package e.g. tk-devel) first. Refer to http://wiki.python.org/moin/TkInter for further details.

```shell
sudo apt install tk-dev
```

### User Privileges

To access the serial port on most Linux platforms, you will need to be a member of the 
`tty` and/or `dialout` groups. Other than this, no special privileges are required.

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
python -m pip install --upgrade pyubx2 pynmeagps pyrtcm pyserial Pillow requests
```

To install PyGPSClient manually, download and unzip this repository and run:

```shell
python -m /path_to_folder/foldername/pygpsclient
```

e.g. if you downloaded and unzipped to a folder named `PyGPSClient-1.1.9`, run: 

```shell
python -m /path_to_folder/PyGPSClient-1.1.9/pygpsclient
```

---
## <a name="mapquestapi">MapQuest API Key</a>

To use the optional dynamic web-based mapview facility, you need to request and install a 
[MapQuest API key](https://developer.mapquest.com/user/login/sign-up).
The free edition of this API allows for up to 15,000 transactions/month (roughly 500/day) on a non-commercial basis.
For this reason, the map refresh rate is intentionally limited to 1/minute* to avoid exceeding the free transaction
limit under normal use. **NB:** this facility is *not* intended to be used for real time navigational purposes.

Once you have received the API key (a 32-character alphanumeric string), you can either:

1. create an environment variable named `MQAPIKEY` (all upper case) and set this to the API key value. It is recommended 
that this is a User variable rather than a System/Global variable.
2. copy it to a file named `mqapikey` (lower case, no extension) and place this file in the user's home directory.

*The web map refresh rate can be amended if required by changing the MAP_UPDATE_INTERVAL constant in `globals.py`.

---
## <a name="userdefined">User Defined Presets</a>

The UBX Configuration Dialog includes the facility to send user-defined UBX configuration messages or message sequences to the receiver. These can be set up by adding
appropriate comma-delimited message descriptions and payload definitions to a file named `ubxpresets` (lower case, no extension), and then placing this file in the user's home directory. The message definition comprises a free-format text description (*avoid embedded commas*) 
followed by one or more [pyubx2 UBXMessage constructors](https://pypi.org/project/pyubx2/), i.e. 
1. message class as a string e.g. `CFG` (must be a valid class from pyubx2.UBX_CLASSES)
2. message id as a string e.g. `CFG-MSG` (must be a valid id from pyubx2.UBX_MSGIDS)
3. payload as a hexadecimal string e.g. `f004010100010100` (leave blank for null payloads e.g. most POLL messages)
4. mode as an integer (`1` = SET, `2` = POLL)

(payload as hex string can be obtained from a `UBXMessage` created using the [pyubx2 library](https://pypi.org/project/pyubx2/) thus: ```msg.payload.hex()```)

Multiple commands can be concatenated on a single line. Illustrative examples are shown below:

```
Stop GNSS, CFG, CFG-RST, 00000800, 1
Start GNSS, CFG, CFG-RST, 00000900, 1
Enable NMEA UBX00 & UBX03 sentences, CFG, CFG-MSG, f100010100010100, 1, CFG, CFG-MSG, f103010100010100, 1
Poll NEO-9 UART1/2 baud rates, CFG, CFG-VALGET, 000000000100524001005340, 2
Poll NEO-9 Message Rates, CFG, CFG-VALGET, 00000000ffff9120, 2, CFG, CFG-VALGET, 00004000ffff9120, 2, CFG, CFG-VALGET, 00008000ffff9120, 2
Set ZED-F9P to Base Station Survey-In Mode (1m accuracy), CFG, CFG-VALSET, 000100008b00912001c002912001cf02912001d4029120011b03912001d902912001060391200111000340e8030000100003405a0000000100032001, 1
Set ZED-F9P to Base Station Survey-In Mode (1cm accuracy), CFG, CFG-VALSET, 000100008b00912001c002912001cf02912001d4029120011b03912001d9029120010603912001110003400a000000100003405a0000000100032001, 1
Poll Receiver Software Version, MON, MON-VER, , 2
Poll Datum, CFG, CFG-DAT, , 2
Poll GNSS config, CFG, CFG-GNSS, , 2
Poll NMEA config, CFG, CFG-NMEA, , 2
Poll Satellite-based Augmentation, CFG, CFG-SBAS, , 2
Poll Receiver Management, CFG, CFG-RXM, , 2
Poll Navigation Mode, CFG, CFG-NAV5, , 2
Poll Expert Navigation mode, CFG, CFG-NAVX5, , 2
Poll Geofencing, CFG, CFG-GEOFENCE, , 2
Limit NMEA GNSS to GPS only, CFG, CFG-NMEA, 0040000276000000000000010000000000000000, 1
Limit NMEA GNSS to GLONASS only, CFG, CFG-NMEA, 0040000257000000000000010000000000000000, 1
Set NMEA GNSS to ALL, CFG, CFG-NMEA, 0040000200000000000000010000000000000000, 1
Limit UBX GNSS to GPS only, CFG, CFG-GNSS, 0020200700081000010001010101030000000101020408000000010103081000000001010400080000000103050003000000010506080E0000000101, 1
Limit UBX GNSS to GLONASS only, CFG, CFG-GNSS, 0020200700081000000001010101030000000101020408000000010103081000000001010400080000000103050003000000010506080E0001000101, 1
Set UBX GNSS to ALL, CFG, CFG-GNSS, 0020200700081000010001010101030001000101020408000000010103081000000001010400080000000103050003000100010506080E0001000101, 1
FORCE COLD RESTART !*** Expect ClearCommError ***!, CFG, CFG-RST, ffff0100, 1
```

---
## <a name="knownissues">Known Issues</a>

As of April 2022 there appear to be some performance issues with the version of tkinter embedded with Python >=3.9 on MacOS Monterey.

Windows and Linux (including Raspberry Pi OS) users are unaffected.

The application is fully functional on MacOS Monterey but you may find dialog frame load/resizing operations are relatively slow, particularly on newer Apple M1 platforms e.g. some dialogs may take a while to load and may require manual resizing when first opened. This will hopefully be resolved in a subsequent MacOS update, but in the meantime the impact can be minimised by:
1. Opening and closing the UBX or NTRIP configuration dialogs while the serial connection is closed.
1. Minimising incoming message rates while using the configuration facilities. The [UBX Configuration](#ubxconfig) facility offers presets for 'minimum NMEA messages' or 'minimum UBX messages'.
1. Temporarily disabling the console display of certain message protocols using the 'Protocols Displayed' checkboxes.

---
## <a name="glossary">Glossary of Terms</a>

* ACC - accuracy of location in real units (hacc - horizontal, vacc - vertical). Note that location accuracy is not directly provided via the standard NMEA message set, but is available via some proprietary NMEA messages e.g. UBX00.
* BEI - [BeiDou Navigation Satellite System](https://en.wikipedia.org/wiki/BeiDou).
* DOP - [dilution of precision](https://gisgeography.com/gps-accuracy-hdop-pdop-gdop-multipath/) (pdop - overall position, hdop - horizontal, vdop - vertical).
* GAL - [Galileo Satellite Navigation](https://en.wikipedia.org/wiki/Galileo_(satellite_navigation)).
* GLO - [GLONASS, Global Navigation Satellite System](https://en.wikipedia.org/wiki/GLONASS).
* GNSS - [global navigation satellite system](https://en.wikipedia.org/wiki/Satellite_navigation).
* GPS - [Global Positioning System](https://en.wikipedia.org/wiki/Global_Positioning_System).
* IME - [IMES, Indoor MEssaging System](https://www.gpsworld.com/wirelessindoor-positioningopening-up-indoors-11603/)
* NTRIP - [Networked Transport of RTCM via Internet Protocol](https://en.wikipedia.org/wiki/Networked_Transport_of_RTCM_via_Internet_Protocol)
* PRN - [pseudo-random noise number](https://www.gps.gov/technical/prn-codes/) (code that each satellite transmits to differentiate itself from other satellites in the active constellation).
* QZS - [QZSS, Quasi-Zenith Satellite System](https://en.wikipedia.org/wiki/Quasi-Zenith_Satellite_System).
* RTCM(3) - [RTCM 10403.n Differential GNSS Services standard](https://rtcm.myshopify.com/collections/differential-global-navigation-satellite-dgnss-standards/products/rtcm-10403-2-differential-gnss-global-navigation-satellite-systems-services-version-3-february-1-2013).
* SBA - [SBAS, Satellite-based Augmentation System](https://en.wikipedia.org/wiki/GNSS_augmentation#Satellite-based_augmentation_system).
* SIP - satellites used in position solution.
* SIV - satellites in view.
* SV(N) - [space vehicle number](https://en.wikipedia.org/wiki/List_of_GPS_satellites) (serial number assigned to each satellite).
* UTC - coordinated universal time.

---
## <a name="license">License</a>

![License](https://img.shields.io/github/license/semuconsulting/PyGPSClient.svg)

BSD 3-Clause License

Copyright &copy; 2020, SEMU Consulting
All rights reserved.

Application icons from [iconmonstr](https://iconmonstr.com/license/) &copy;.

---
## <a name="author">Author Information</a>

semuadmin@semuconsulting.com

`PyGPSClient` is maintained entirely by volunteers. If you find it useful, a small donation would be greatly appreciated!

[![Donations](https://www.paypalobjects.com/en_GB/i/btn/btn_donate_LG.gif)](https://www.paypal.com/donate/?hosted_button_id=4TG5HGBNAM7YJ)
