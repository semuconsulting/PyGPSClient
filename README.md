
# PyGPSClient

[Current Status](#currentstatus) |
[Installation](#installation) |
[Instructions](#instructions) |
[UBX Configuration](#ubxconfig) |
[NMEA Configuration](#nmeaconfig) |
[TTY Commands](#ttycommands) |
[Load/Save/Record Commands](#recorder) |
[NTRIP Client](#ntripconfig) |
[SPARTN Client](#spartnconfig) |
[Socket Server / NTRIP Caster](#socketserver) |
[GPX Track Viewer](#gpxviewer) |
[Mapquest API Key](#mapquestapi) |
[User-defined Presets](#userdefined) |
[CLI Utilities](#cli) |
[Known Issues](#knownissues) |
[License](#license) |
[Author Information](#author)

PyGPSClient is a free, open-source, multi-platform graphical GNSS/GPS testing, diagnostic and configuration application written entirely by volunteers in Python and tkinter. 
* Runs on any platform which supports a Python 3 interpreter (>=3.10) and tkinter (>=8.6) GUI framework, including Windows, MacOS, Linux and Raspberry Pi OS.
* Supports NMEA, UBX, SBF, QGC, RTCM3, NTRIP, SPARTN, MQTT and TTY (ASCII) protocols¹.
* Capable of reading from a variety of GNSS data streams: Serial (USB / UART), Socket (TCP / UDP), binary data stream (terminal or file capture) and binary recording (e.g. u-center \*.ubx).
* Provides [NTRIP](#ntripconfig) and [SPARTN](#spartnconfig) client facilities.
* Can serve as an [NTRIP base station](#basestation) with an RTK-compatible receiver (e.g. u-blox ZED-F9P/ZED-X20P, Quectel LG290P/LG580P/LC29H and Septentrio Mosaic G5/X5).
* Supports GNSS (*and related*) device configuration via proprietary UBX, NMEA and ASCII TTY protocols, including most u-blox, Quectel, Septentrio and Feyman GNSS devices.
* Can be installed using the standard `pip` Python package manager - see [installation instructions](#installation) below.

This is an independent project and we have no affiliation whatsoever with any GNSS manufacturer or distributor.

¹ *specific message support subject to underlying parser implementation and open-source permissions*

![full app screenshot ubx](https://github.com/semuconsulting/PyGPSClient/blob/master/images/app.png?raw=true)

*Screenshot showing mixed-protocol stream from u-blox ZED-F9P receiver, using PyGPSClient's [NTRIP Client](#ntripconfig) with a base station 26 km to the west to achieve better than 2 cm accuracy*

#### References

1. [Glossary of GNSS Terms and Abbreviations](https://www.semuconsulting.com/gnsswiki/glossary/).
1. [GNSS Positioning - A Reviser](https://www.semuconsulting.com/gnsswiki/) - a general overview of GNSS, OSR, SSR, RTK, NTRIP and SPARTN positioning and error correction technologies and terminology.
1. [Achieving cm Level GNSS Accuracy using RTK](https://www.semuconsulting.com/gnsswiki/rtktips/) - practical tips on high precision RTK using PyGPSClient.
1. From time to time, instructional videos may be posted to the [semuadmin YouTube channel](https://www.youtube.com/@semuadmin).
1. [Sphinx API Documentation](https://www.semuconsulting.com/pygpsclient) in HTML format.

---
## <a name="currentstatus">Current Status</a>

![Status](https://img.shields.io/pypi/status/PyGPSClient) 
![Release](https://img.shields.io/github/v/release/semuconsulting/PyGPSClient)
![Build](https://img.shields.io/github/actions/workflow/status/semuconsulting/PyGPSClient/main.yml?branch=master)
[![Deploy](https://github.com/semuconsulting/pygpsclient/actions/workflows/deploy.yml/badge.svg)](https://github.com/semuconsulting/pygpsclient/actions/workflows/deploy.yml)
![Release Date](https://img.shields.io/github/release-date/semuconsulting/PyGPSClient)
![Last Commit](https://img.shields.io/github/last-commit/semuconsulting/PyGPSClient)
![Contributors](https://img.shields.io/github/contributors/semuconsulting/PyGPSClient.svg)
![Open Issues](https://img.shields.io/github/issues-raw/semuconsulting/PyGPSClient)

The PyGPSClient home page is at [PyGPSClient](https://github.com/semuconsulting/PyGPSClient). 

Contributions welcome - please refer to [CONTRIBUTING.MD](https://github.com/semuconsulting/PyGPSClient/blob/master/CONTRIBUTING.md).

For [Bug reports](https://github.com/semuconsulting/PyGPSClient/blob/master/.github/ISSUE_TEMPLATE/bug_report.md), please use the template provided. For feature requests and general queries and advice, post a message to one of the [PyGPSClient Discussions](https://github.com/semuconsulting/PyGPSClient/discussions) channels in the first instance.

![No Copilot](https://github.com/semuconsulting/PyGPSClient/blob/master/images/nocopilot75.png?raw=true)

---
## <a name="installation">Installation</a>

![Python version](https://img.shields.io/pypi/pyversions/PyGPSClient.svg?style=flat)
[![PyPI version](https://img.shields.io/pypi/v/PyGPSClient.svg?style=flat)](https://pypi.org/project/PyGPSClient/)
[![PyPI downloads](https://github.com/semuconsulting/PyGPSClient/blob/master/images/clickpy_top10.svg?raw=true)](https://clickpy.clickhouse.com/dashboard/pygpsclient)

## The Quick Version

If you have an [official Python](https://www.python.org/downloads/) >=3.10 with tkinter >=8.6 installed and the Python [binaries](https://github.com/semuconsulting/PyGPSClient/blob/master/INSTALLATION.md#binaries) folder is in your PATH, you can install PyGPSClient using pip:

```shell
python3 -m pip install --upgrade pygpsclient
```

and then run it by typing:
```shell
pygpsclient
```

To install into a virtual environment (*which may be necessary if you have an [`externally-managed-environment`](https://github.com/semuconsulting/PyGPSClient/blob/master/INSTALLATION.md#basics)*):

```shell
python3 -m venv pygpsclient
source pygpsclient/bin/activate # (or .\pygpsclient\Scripts\activate on Windows)
python3 -m pip install --upgrade pygpsclient
deactivate
```

## The Longer Version

For more comprehensive installation instructions, please refer to [INSTALLATION.md](https://github.com/semuconsulting/PyGPSClient/blob/master/INSTALLATION.md).

---
## <a name="instructions">Instructions</a>

1. To connect to a GNSS receiver via USB or UART port, select the device from the listbox, set the appropriate serial connection parameters and click 
![connect icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/usbport-1-24.png?raw=true). The application will endeavour to pre-select a recognised GNSS/GPS device but this is platform and device dependent. Press the ![refresh](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/iconmonstr-refresh-6-16.png?raw=true) button to refresh the list of connected devices at any point. `Rate bps` (baud rate) is typically the only setting that might need adjusting, but tweaking the `timeout` setting may improve performance on certain platforms. The `Msg Mode` parameter defaults to `GET` i.e., periodic or poll response messages *from* a receiver. If you wish to parse streams of command or poll messages being sent *to* a receiver, set the `Msg Mode` to `SET` or `POLL`. An optional serial or socket stream inactivity timeout can also be set (in seconds; 0 = no timeout).
1. A custom user-defined serial port can also be passed via the json configuration file setting `"userport_s":`, via environment variable `PYGPSCLIENT_USERPORT` or as a command line argument `--userport`. A special userport value of "ubxsimulator" invokes the experimental [`pyubxutils.UBXSimulator`](https://github.com/semuconsulting/pyubxutils/blob/main/src/pyubxutils/ubxsimulator.py) utility to emulate a GNSS NMEA/UBX serial stream. 
1. To connect to a TCP or UDP socket, enter the server URL and port, select the protocol (defaults to TCP) and click 
![connect socket icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/ethernet-1-24.png?raw=true). For encrypted TLS connections, tick the 'TLS' checkbox. Tick the 'Self Sign' checkbox to accommodate self-signed TLS certification (*typically for test or demonstration services*).
1. To stream from a previously-saved <a name="filestream">binary datalog file</a>, click 
![connect-file icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/binary-1-24.png?raw=true) and select the file type (`*.log, *.ubx, *.*`) and path. PyGPSClient datalog files will be named e.g. `pygpsdata-20220427114802.log`, but any binary dump of an GNSS receiver output is acceptable, including `*.ubx` files produced by u-center. The 'File Delay' spinbox sets the delay in milliseconds between individual file reads, acting as a throttle on file readback.
1. To disconnect from the data stream, click
![disconnect icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/iconmonstr-media-control-50-24.png?raw=true).
1. To exit the application, click
![exit icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/iconmonstr-door-6-24.png?raw=true), or press Ctrl-Q, or click the application window's close window icon.
1. To immediately disconnect and terminate all running threads, click Ctrl-K ("Kill Switch").
1. Protocols Shown - Select which protocols to display; NMEA, UBX, SBF, QGC, RTCM3, SPARTN or TTY (NB: this only changes the displayed protocols - to change the actual protocols output by the receiver, use the [UBX Configuration Dialog](#ubxconfig)).
   - **NB:** Serial connection must be stopped before changing to or from TTY (terminal) protocol.
   - **NB:** Enabling TTY (terminal) mode will disable all other protocols.
1. Console Display - Select console display format (Parsed, Binary, Hex Tabular, Hex String, Parsed+Hex Tabular - see Console Widget below).
1. Maxlines - Select number of scrollable lines retained in console.
1. File Delay - Select delay in milliseconds between individual reads when streaming from binary file (default 20 milliseconds).
1. Tags - Enable color tags in console (see Console Widget below).
1. Position Format and Units - Change the displayed position (D.DD / D.M.S / D.M.MM / ECEF) and unit (metric/imperial) formats.
1. Include C/No = 0 - Include or exclude satellites where carrier to noise ratio (C/No) = 0.
1. DataLogging - Turn Data logging in the selected format (Binary, Parsed, Hex Tabular, Hex String, Parsed+Hex Tabular) on or off. On first selection, you will be prompted to select the directory into which timestamped log files are saved. Log files are cycled when a maximum size is reached (default is 10 MB, manually configurable via `logsize_n` setting).
1. GPX Track - Turn track recording (in GPX format) on or off. On first selection, you will be prompted to select the directory into which timestamped GPX track files are saved.
1. Database - Turn spatialite database recording (*where available*) on or off. On first selection, you will be prompted to select the directory into which the `pygpsclient.sqlite` database is saved. Note that, when first created, the database's spatial metadata will take a few seconds to initialise (*up to a minute on Raspberry Pi and similar SBC*). **NB** This facility is dependent on your Python environment supporting the requisite [sqlite3 `mod_spatialite` extension](https://www.gaia-gis.it/fossil/libspatialite/index) - see [INSTALLATION.md](https://github.com/semuconsulting/PyGPSClient/blob/master/INSTALLATION.md#prereqs) for further details. If not supported, the option will be greyed out. Check the Menu..Help..About dialog for an indication of the current spatialite support status.

     *FYI* a helper method `retrieve_data()` is available to retrieve data from this database - see [Sphinx documentation](https://www.semuconsulting.com/pygpsclient/pygpsclient.html#pygpsclient.sqllite_handler.retrieve_data) and [retrieve_data.py](https://github.com/semuconsulting/PyGPSClient/blob/master/examples/retrieve_data.py) example for details.
1. To save the current configuration to a file, go to File..Save Configuration.
1. To load a saved configuration file, go to File..Load Configuration. The default configuration file location is `$HOME/pygpsclient.json`.
**NB** Any active serial or RTK connection must be stopped before loading a new configuration.
1. [Socket Server / NTRIP Caster](#socketserver) facility with two modes of operation: (a) open, unauthenticated Socket Server or (b) NTRIP Caster (mountpoint = `pygnssutils`).
1. [UBX Configuration Dialog](#ubxconfig), with the ability to send a variety of UBX CFG configuration commands to u-blox GNSS devices. This includes the facility to add **user-defined commands or command sequences** - see instructions under [user-defined presets](#userdefined) below. To display the UBX Configuration Dialog (*only functional when connected to a UBX GNSS device via serial port*), click
![gear icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/iconmonstr-gear-2-24-ubx.png?raw=true), or go to Menu..Options..UBX Configuration Dialog.
1. [NMEA Configuration Dialog](#nmeaconfig), with the ability to send a variety of NMEA configuration commands to GNSS devices (e.g. Quectel LG290P). This includes the facility to add **user-defined commands or command sequences** - see instructions under [user-defined presets](#userdefined) below. To display the NMEA Configuration Dialog (*only functional when connected to a compatible GNSS device via serial port*), click ![gear icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/iconmonstr-gear-2-24-nmea.png?raw=true), or go to Menu..Options..NMEA Configuration Dialog.
1. [TTY Config Dialog](#ttycommands), with the ability to send a variety of TTY (ASCII) configuration commands to GNSS and related devices (e.g. Septentrio X5, Feyman IM19). This includes the facility to add **user-defined commands or command sequences** - see instructions under [user-defined presets](#userdefined) below. To display the TTY Commands Dialog (*only functional when connected to a compatible GNSS device via serial port*), click
![gear icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/iconmonstr-gear-2-24-tty.png?raw=true), or go to Menu..Options..TTY Commands.
1. [NTRIP Client](#ntripconfig) facility with the ability to connect to a specified NTRIP caster, parse the incoming RTCM3 or SPARTN data and feed this data to a compatible GNSS receiver (*requires an Internet connection and access to an NTRIP caster and local mountpoint*). To display the NTRIP Client Configuration Dialog, click
![ntrip icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/iconmonstr-antenna-4-24.png?raw=true), or go to Menu..Options..NTRIP Configuration Dialog.
1. [SPARTN Client](#spartnconfig) facility with the ability to configure an IP or L-Band SPARTN Correction source and SPARTN-compatible GNSS receiver (e.g. ZED-F9P) and pass the incoming correction data to the GNSS receiver (*requires an Internet connection and access to a SPARTN location service*). To display the SPARTN Client Configuration Dialog, go to Menu..Options..SPARTN Configuration Dialog.
1. [GPX Track Viewer](#gpxviewer) utility with elevation and speed profiles and track metadata. To display the GPX Track viewer, go to Menu..Options..GPX Track Viewer.

#### <a name="config">Configuration settings</a>

- Configuration settings for PyGPSClient can be saved and recalled via the Menu..File..Save Configuration and Menu..File..Load Configuration options. By default, PyGPSClient will look for a file named `pygpsclient.json` in the user's home directory. Certain configuration settings require manual editing e.g. custom preset UBX, NMEA and TTY commands and tag colour schemes - see details below. It is recommended to re-save the configuration settings after each PyGPSClient version update, or if you see the warning "Consider re-saving" on startup.

#### <a name="updates">Checking for the latest version</a>

- The About dialog (Menu..Help..About) includes a facility to check the latest available versions of PyGPSClient and its subsidiary modules, and initiate an automatic update. Tick the 'Check on startup' box to perform this check on startup (*note that this requires internet access, which may result in slower startup times on platforms with low bandwidth / high latency internet connections*). The facility may be unavailable in certain Homebrew-installed Python environments due to technical constraints.

#### <a name="refreshrate">GUI refresh rate setting</a>

- PyGPSClient processes all incoming GNSS data in 'real time' but, by default, the GUI is only refreshed every 0.5 seconds. The refresh rate can be configured via the `guiupdateinterval_f` setting in the json configuration file. **NB:** PyGPSClient may become unresponsive on slower platforms (e.g. Raspberry Pi) at high message rates if the GUI update interval is less than 0.1 seconds, though lower intervals (<= 0.1 secs) can be accommodated on more powerful platforms.

#### <a name="transient">Transient dialog setting</a>

- A boolean configuration setting `transient_dialog_b` governs whether pop-up dialogs are 'transient' (i.e. always on top of main application dialog) or not. Changing this setting to `0` allows pop-up dialogs to be minimised independently of the main application window, but be mindful that some dialogs may end up hidden behind others e.g. "Open file/folder" dialogs. **If a file open button appears unresponsive, check that the "Open file/folder" panel isn't already open but obscured**. If you're accessing the desktop via a VNC session (e.g. to a headless Raspberry Pi) it is recommended to keep the setting at the default `1`, as VNC may not recognise keystrokes on overlaid transient windows.

---
| User-selectable 'widgets' | To show or hide the various widgets, go to Menu..View and click on the relevant hide/show option. |
|---------------------------|---------------------------------------------------------------------------------------------------|
|![banner widget](https://github.com/semuconsulting/PyGPSClient/blob/master/images/banner_widget.png?raw=true)| Expandable banner showing key navigation status information based on messages received from receiver. To expand or collapse the banner or serial port configuration widgets, click the ![expand icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/iconmonstr-arrow-80-16.png?raw=true)/![expand icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/iconmonstr-triangle-1-16.png?raw=true) buttons. **NB**: some fields (e.g. hdop/vdop, hacc/vacc) are only available from proprietary NMEA or UBX messages and may not be output by default. The minimum messages required to populate all available fields are: NMEA: GGA, GSA, GSV, RMC, UBX00 (proprietary); UBX: NAV-DOP, NAV-PVT, NAV-SAT |
|![console widget](https://github.com/semuconsulting/PyGPSClient/blob/master/images/console_widget.png?raw=true)| Configurable serial console widget showing incoming GNSS data streams in either parsed, binary or tabular hexadecimal formats. Double-right-click to copy contents of console to the clipboard. The scroll behaviour and number of lines retained in the console can be configured via the settings panel. Supports user-configurable color tagging of selected strings for easy identification. Color tags are loaded from the `"colortag_b":` value (`0` = disable, `1` = enable) and `"colortags_l":` list (`[string, color]` pairs) in your json configuration file (see example provided). If color is set to "HALT", streaming will halt on any match and a warning displayed. NB: color tagging does impose a small performance overhead - turning it off will improve console response times at very high transaction rates.|
|![skyview widget](https://github.com/semuconsulting/PyGPSClient/blob/master/images/skyview_widget.png?raw=true)| Skyview widget showing current satellite visibility and position (elevation / azimuth). Satellite icon borders are colour-coded to distinguish between different GNSS constellations. For consistency between NMEA and UBX data sources, will display GLONASS NMEA SVID (65-96) rather than slot (1-24). |
|![levelsview widget](https://github.com/semuconsulting/PyGPSClient/blob/master/images/graphview_widget.png?raw=true)| Levels view widget showing current satellite carrier-to-noise (C/No) levels for each GNSS constellation. Double-click to toggle legend. |
|![world map](https://github.com/semuconsulting/PyGPSClient/blob/master/images/staticmap.png?raw=true)| Map widget with various modes of display - select from "map" / "sat" (online) or "world" / "custom" (offline). Select zoom level 1 - 20. Double-click the zoom level label to reset the zoom to 10. Double-right-click the zoom label to maximise zoom to 20. Tick Track to show track (track will only be recorded while this box is checked). Double-Right-click will clear the map. Map Type = 'world': a static offline Mercator world map showing current global location.
|![online map](https://github.com/semuconsulting/PyGPSClient/blob/master/images/webmap_widget.png?raw=true)| Map Type = 'map', 'sat' or 'hyb' (hybrid): Dynamic, online web map or satellite image via MapQuest API (*requires an Internet connection and free [Mapquest API Key](#mapquestapi)*). By default, the web map will automatically refresh every 60 seconds (*indicated by a small timer icon at the top left*). The default refresh rate can be amended by changing the `"mapupdateinterval_n":` value in your json configuration file, but **NB** the facility is not intended to be used for real-time navigation. Double-click anywhere in the map to immediately refresh. |
|![offline map](https://github.com/semuconsulting/PyGPSClient/blob/master/images/custommap.png?raw=true)| Map Type = 'custom': One or more user-defined offline geo-referenced map images can be imported using the Menu..Options..Import Custom Map facility, or by manually setting the `usermaps_l` field in the json configuration file. The `usermaps_l` setting represents a list of map paths and extents in the format ["path to map image", [minlat, minlon, maxlat, maxlon]] - see [example configuration file](https://github.com/semuconsulting/PyGPSClient/blob/master/pygpsclient.json#L281). Map images must be a [supported format](https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html) and use a standard WGS84 Web Mercator projection e.g. EPSG:4326. PyGPSClient will automatically select the first map whose extents encompass the current location, based on the order in which the maps appear in `usermaps_l`. NB: The minimum and maximum viable 'zoom' levels depend on the resolution and extents of the imported image and the user's display - if the zoom bounds exceed the image extents, the Zoom spinbox will be highlighted. Offline and online zoom levels will not necessarily correspond. |
|![import custom map](https://github.com/semuconsulting/PyGPSClient/blob/master/images/importcustommap.png?raw=true)| <a name="custommap">Import Custom Map dialog</a>. Click ![load icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/iconmonstr-folder-18-24.png?raw=true) to open the custom map image location (*the default file suffix is `*.tif` - select Show Options to select any file suffix `*.*`*). If the `rasterio` library is installed and the image is geo-referenced (e.g. using [QGIS](https://qgis.org/)), the map extents will be automatically extracted - otherwise they must be entered manually. Import the custom map path and extent settings by clicking ![play icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/iconmonstr-arrow-12-24.png?raw=true). By default, the imported map will be appended to the existing list - click 'First?' to insert the map at the top of the list instead. See [Creating Custom Maps for PyGPSClient](https://www.semuconsulting.com/gnsswiki/custommapwiki/) for tips on how to create a suitable geo-referenced map image.|
|![spectrum widget](https://github.com/semuconsulting/PyGPSClient/blob/master/images/spectrum_widget.png?raw=true)| Spectrum widget showing a spectrum analysis chart (*GNSS receiver must be capable of outputting UBX MON-SPAN messages*). Clicking anywhere in the spectrum chart will display the frequency and decibel reading at that point. Double-clicking anywhere in the chart will toggle the GNSS frequency band markers (L1, G2, etc.) on or off. Right-click anywhere in the chart to capture a snapshot of the spectrum data, which will then be superimposed on the live data (*this can, for example, be used to compare reception with different antenna configurations*). Double-right-click to clear snapshot. **NB:** Some receivers (e.g. NEO-F10N) will not output the requisite MON-SPAN messages unless the port baud rate is at least 57,600. |
|![sysmon widget](https://github.com/semuconsulting/PyGPSClient/blob/master/images/sysmon_widget.png?raw=true)| System Monitor widget showing device cpu, memory and I/O utilisation (*GNSS receiver must be capable of outputting UBX MON-SYS/MON-COMMS or SBF ReceiverStatus messages*). Tick checkbox to toggle between actual (cumulative) I/O stats and pending I/O. Primarily intended for u-blox modules, but can display limited system information for other devices. |
|![scatterplot widget](https://github.com/semuconsulting/PyGPSClient/blob/master/images/scatterplot_widget.png?raw=true)| Scatterplot widget showing variability in position reporting over time. (Optional) Enter fixed reference position. Select Average to center plot on dynamic average position (*displayed at top left*), or Fixed to center on fixed reference position (*if entered*). Check Autorange to set plot range automatically. Set the update interval (e.g. 4 = every 4th navigation solution). Use the range slider or mouse wheel to adjust plot range. Right-click to set fixed reference point to the current mouse cursor position. Double-click to clear the existing data. |
|![rover widget](https://github.com/semuconsulting/PyGPSClient/blob/master/images/rover_widget.png?raw=true) | Rover widget plots the relative 2D position, track and status information for the roving receiver in a fixed or moving base / rover RTK configuration. Can also display relative position of NTRIP mountpoint and receiver in a static RTK configuration. Double-click to clear existing plot. |
|![chart view](https://github.com/semuconsulting/PyGPSClient/blob/master/images/chart_widget.png?raw=true) | Chart widget acts as a multi-channel "plotter", allowing the user to plot a series of named numeric data attributes from any parsed GNSS data source, with configurable y (value) and x (time) axes. By default, the number of channels is set to 4, but this can be manually edited by the user via the json configuration file setting `chartsettings_d["numchn_n"]`. For each channel, user can select: (*optional*) identity of message source e.g. `NAV-PVT`; attribute name e.g. `hAcc`; scaling factor (divisor) e.g. 1000; y axis range e.g. 0 - 5. Wildcards are available for attribute groups - "\*" (average of group values), "+" (maximum of group values), "-" (minimum of group values) e.g. `cno*` will plot the average `cno` value for a group of satellites. Double-click to clear the existing data. Double-right-click to save the current chart data to the clipboard in CSV format, which can be directly pasted into a spreadsheet application. |
|![IMU widget](https://github.com/semuconsulting/PyGPSClient/blob/master/images/imu_widget.png?raw=true) |  IMU (Inertial Management Unit) Monitor widget showing current orientation/attitude (roll, pitch, yaw) and status of IMU from any IMU/Dead Reckoning message source. Select range in degrees (from ±1 to ±180 degrees). |

---
## <a name="ubxconfig">UBX Configuration Facilities</a>

![ubxconfig widget screenshot](https://github.com/semuconsulting/PyGPSClient/blob/master/images/ubxconfig_widget.png?raw=true)

**Pre-Requisites and Caveats:**

- u-blox GNSS receiver connected to the workstation via USB or UART port¹².
- **NOTE:** u-blox introduced a [new configuration mechanism](https://github.com/semuconsulting/pyubx2#configinterface) in 9th generation devices (**ROM protocol >=23.01**). Some UBX configuration commands (e.g. `CFG-PRT`, `CFG-RATE`, `CFG-MSG`) will only work with legacy devices (e.g. NEO-M6S, NEO-M8P); others (e.g. `CFG-VALSET`, `CFG-VALDEL`) will only work with newer devices (e.g. NEO-M9, ZED-F9P, ZED-X20P).
- **NOTE:** The UBX protocol does not support synchronous command acknowledgement or unique confirmation IDs. Asynchronous command and poll acknowledgements and responses can take several seconds at high message transmission rates, or be discarded altogether if the device's transmit buffer is full (*txbuff-alloc error*). To ensure timely responses, try increasing the baud rate and/or temporarily reducing transmitted message rates using the configuration commands provided.
- A warning icon (typically accompanied by an ACK-NAK response) is usually an indication that one or more of the commands sent is not supported by your receiver (*e.g. mismatched protocol*).

¹ *Configuration commands can be sent via TCP socket, but a third-party or bespoke TCP-UART converter would be required at the receiving end.*

² *I2C (QWIIC) is not directly supported, but third-party I2C-UART adapters are available.*

**Instructions:**

The UBX Configuration Dialog currently provides the following UBX configuration panels:

1. Version panel shows current device hardware/firmware versions (*via MON-VER and MON-HW polls*).
1. Protocol Configuration panel (CFG-PRT) sets baud rate and inbound/outbound protocols across all available ports (*legacy protocols only*).
1. Solution Rate panel (CFG-RATE) sets navigation solution interval in ms (e.g. 1000 = 1/second) and measurement ratio (ratio between the number of measurements and the number of navigation solutions, e.g. 5 = five measurements per navigation solution) (*legacy protocols only*).
1. For each of the panels above, clicking anywhere in the panel background will refresh the displayed information with the current configuration.
1. Message Rate panel (CFG-MSG) sets message rates per port for UBX and NMEA messages (*legacy protocols only*). Message rate is relative to navigation solution frequency e.g. a message rate of '4' means 'every 4th navigation solution' (higher = less frequent).
1. Configuration Interface widget (CFG-VALSET, CFG-VALDEL and CFG-VALGET) queries and sets configuration for *modern protocols only*.
1. UBX Legacy Command configuration panel providing structured updates for a range of legacy CFG-* configuration commands (*legacy protocols only*). Note: 'X' (byte) type attributes can be entered as integers or hexadecimal strings e.g. 522125312 or 0x1f1f0000. Once a command is selected, the configuration is polled and the current values displayed. The user can then amend these values as required and send the updated configuration. Some polls require input arguments (e.g. portID) - these are highlighted and will be set at default values initially (e.g. portID = 0), but can be amended by the user and re-polled using the ![refresh](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/iconmonstr-refresh-lined-24.png?raw=true) button.
1. Preset Commands widget supports a variety of user-defined UBX commands and queries - see [user defined presets](#userdefined).

An icon to the right of each 'SEND' 
![send icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/iconmonstr-arrow-12-24.png?raw=true) button indicates the confirmation status of the configuration command; 
(pending i.e. awaiting confirmation ![pending icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/iconmonstr-time-6-24.png?raw=true), 
confirmed ![confirmed icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/iconmonstr-check-mark-8-24.png?raw=true) or 
warning ![warning icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/iconmonstr-warning-1-24.png?raw=true)). 

---
## <a name="nmeaconfig">NMEA Configuration Facilities</a>

![nmeaconfig widget screenshot](https://github.com/semuconsulting/PyGPSClient/blob/master/images/nmeaconfig_widget.png?raw=true)

**Pre-Requisites:**

- Receiver capable of being configured via proprietary NMEA sentences, connected to the workstation via USB or UART port.
- The facility includes support for several Quectel LG and LC series receivers via PQTM*, PSTM* and PAIR* sentences. Additional types may be supported in the underlying NMEA parser library [pynmeagps](https://github.com/semuconsulting/pynmeagps) in later releases (*contributions welcome*).

**Instructions:**

The NMEA Configuration Dialog currently provides the following NMEA configuration panels:
1. Version panel shows current device hardware/firmware versions (*via PQTMVERNO polls*).
1. Dynamic configuration panel providing structured updates for supported receivers e.g. Quectel LG290P via PQTM* sentences, or LC29H via PAIR* sentences. Once a command is selected, the configuration is polled and the current values displayed. The user can then amend these values as required and send the updated configuration. Some polls require input arguments (e.g. portid or msgname) - these are highlighted and will be set at default values initially (e.g. portid = 1), but can be amended by the user and re-polled using the ![refresh](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/iconmonstr-refresh-lined-24.png?raw=true) button.
1. Preset Commands widget supports a variety of user-defined NMEA commands and queries - see [user defined presets](#userdefined).

An icon to the right of each 'SEND' 
![send icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/iconmonstr-arrow-12-24.png?raw=true) button indicates the confirmation status of the configuration command; 
(pending i.e. awaiting confirmation ![pending icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/iconmonstr-time-6-24.png?raw=true), 
confirmed ![confirmed icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/iconmonstr-check-mark-8-24.png?raw=true) or 
warning ![warning icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/iconmonstr-warning-1-24.png?raw=true)).

**NB:** Several Quectel LG and LC series commands require a Hot Restart (PQTMHOT) before taking effect, including PQTMCFGCNST (Enable/Disable Constellations), PQTMCFGFIX (Configure Fix Rate), PQTMCFGSAT (Configure Satellite Masks) and PQTMCFGSIGNAL (Configure Signal Masks). This is a Quectel protocol constraint, not a PyGPSClient issue.

---
## <a name="ttycommands">TTY Configuration Facilities</a>

![ttydialog screenshot](https://github.com/semuconsulting/PyGPSClient/blob/master/images/tty_dialog.png?raw=true)

The TTY Commands dialog provides a facility to send user-defined ASCII TTY configuration commands (e.g. `AT+` style commands) to the connected serial device. Commands can be entered manually or selected from a list of user-defined presets. The dialog can be accessed via the TTY Config button or Menu..Options..TTY Commands. 
- CRLF checkbox - if ticked, a CRLF (`b"\x0d\x0a"`) terminator will be added to the command string. 
- Echo checkbox - if ticked, outgoing TTY commands will be echoed on the console with the marker `"TTY<<"`.
- Delay checkbox - if ticked, a small delay will be added between each outgoing command to allow time for the receiving device to process the command.

Preset commands can be set up by adding appropriate semicolon-delimited message descriptions and payload definitions to the `"ttypresets_l":` list in your json configuration file. See [User Defined Presets](#user-defined-presets) above and [example provided](https://github.com/semuconsulting/PyGPSClient/blob/master/pygpsclient.json#L302).

**NOTE:** Some GNSS devices (e.g. Septentrio X5) use separate UART ports for configuration and navigation/monitoring - ensure you are using the appropriate UART port when sending TTY commands. Septentrio devices also require an 'Initialise Command Mode' sequence (`SSSSSSSSSS`) to be sent before accepting TTY commands.

The following example illustrates a series of ASCII configuration commands being sent to a Septentrio Mosaic X5 receiver, followed by successful acknowledgements:

![ttyconsole screenshot](https://github.com/semuconsulting/PyGPSClient/blob/master/images/tty_console.png?raw=true)

---
## <a name="recorder">Configuration Command Load/Save/Record Facility</a>

![recorder screenshot](https://github.com/semuconsulting/PyGPSClient/blob/master/images/recorder_dialog.png?raw=true)

This allows users to record ![record icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/iconmonstr-record-24.png?raw=true) a sequence of UBX, NMEA or TTY configuration commands as they are sent to a device, and to save ![save icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/iconmonstr-save-14-24.png?raw=true) this recording to a file. Saved files can be reloaded ![load icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/iconmonstr-folder-18-24.png?raw=true) and the configuration commands replayed ![play icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/iconmonstr-arrow-12-24.png?raw=true). This provides a means to easily reproduce a given sequence of configuration commands, or copy a saved configuration between compatible devices. The Configuration Load facility can accept configuration files in either UBX/NMEA binary (\*.bin), TTY (\*.tty) or u-center UBX text format (\*.txt). Files saved using the [ubxsave](#ubxsave) CLI utility (*installed via the `pygnssutils` library*) can also be reloaded and replayed. **Tip:** The contents of a binary (\*.bin) config file can be reviewed using PyGPSClient's [file streaming facility](#filestream), *BUT* remember to set the `Msg Mode` in the Settings panel to `SET` rather than the default `GET` ![msgmode capture](https://github.com/semuconsulting/PyGPSClient/blob/master/images/msgmode.png?raw=true).

---
## <a name="ntripconfig">NTRIP Client Facilities</a>

![ntrip config widget screenshot](https://github.com/semuconsulting/PyGPSClient/blob/master/images/ntripconfig_widget.png?raw=true)

The NTRIP Configuration utility allows users to receive and process NTRIP RTK Correction data from an NTRIP caster to achieve cm level location accuracy. The facility can be accessed by clicking ![NTRIP Client button](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/iconmonstr-antenna-4-24.png?raw=true) or selecting Menu..Options..NTRIP Configuration Dialog. 

**Pre-Requisites:**

- NTRIP-compatible GNSS receiver e.g. u-blox ZED-F9P
- Internet access
- URL of NTRIP caster
- Login credentials for the NTRIP caster (where required)
- Name of local MOUNTPOINT (if not using PyGPSClient's automatic mountpoint locator)
- Data type (normally RTCM but some services output data in SPARTN format)

**Instructions:**

1. Enter the required NTRIP server URL (or IP address) and port (defaults to 2101). For SSL/TLS (HTTPS) connections (*typically on ports \*443 or 2102*), tick the TLS checkbox. Tick the Self-Sign checkbox to tolerate self-signed TLS certification (*typically for test or demonstration services*). For services which require authorisation, enter your assigned login username and password.
1. Select the Data Type (defaults to RTCM, but can be set to SPARTN).
1. To retrieve the sourcetable, leave the mountpoint field blank and click connect (*response may take a few seconds*). The required mountpoint may then be selected from the list, or entered manually. Where possible, `PyGPSClient` will automatically identify the closest mountpoint to the current location.
1. For NTRIP services which require client position data via NMEA GGA sentences, select the appropriate sentence transmission interval in seconds. The default is 'None' (no GGA sentences sent). A value of 10 or 60 seconds is typical.
1. If GGA sentence transmission is enabled, GGA sentences can either be populated from live navigation data (*assuming a receiver is connected and outputting valid position data*) or from fixed reference settings entered in the NTRIP configuration panel (latitude, longitude, elevation and geoid separation - all four reference settings must be provided).
1. To connect to the NTRIP server, click ![connect icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/iconmonstr-media-control-48-24.png?raw=true). To disconnect, click ![disconnect icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/iconmonstr-media-control-50-24.png?raw=true).
1. If NTRIP data is being successfully received, the banner '**dgps:**' status indicator should change to 'YES' and indicate the age and reference station of the correction data (where available) ![dgps status](https://github.com/semuconsulting/PyGPSClient/blob/master/images/dgps_status.png?raw=true). Note that DGPS status is typically maintained for up to 60 seconds after loss of correction signal.
1. Some NTRIP services may output RTCM3 or SPARTN correction messages at a high rate, flooding the GUI console display. To suppress these messages in the console, de-select the 'RTCM' or'SPARTN' options in 'Protocols Shown' - the RTCM3 or SPARTN messages will continue to be processed in the background.

Below is a illustrative NTRIP DGPS data log, showing:
* Outgoing NMEA GPGGA (client position) sentence.
* Incoming RTCM3 correction messages; in this case - 1006 (Ref station ARP (*DF003=2690*) with antenna height), 1008 (Antenna descriptor), 1033 (Receiver descriptor), 1075 (GPS MSM5), 1085 (GLONASS MSM5), 1095 (Galileo MSM5), 1125 (BeiDou MSM5) and 1230 (GLONASS Code-Phase Biases)
* Corresponding UBX RXM-RTCM acknowledgements generated by the u-blox ZED-F9P receiver, confirming message type, valid checksum (*crcFailed=0*), successful use (*msgUsed=2*) and reference station ARP (*refStation=2690*). 

![ntrip console screenshot](https://github.com/semuconsulting/PyGPSClient/blob/master/images/ntrip_consolelog.png?raw=true)

**NB:** Please respect the terms and conditions of any remote NTRIP service used with this facility. For testing or evaluation purposes, consider deploying a local [SNIP LITE](https://www.use-snip.com/download/) server. *Inappropriate use of an NTRIP service may result in your account being blocked*.

---
## <a name="spartnconfig">SPARTN Client Facilities</a>

  ### NB: As of October 2025, u-blox have discontinued both their L-Band and MQTT encrypted SPARTN correction services, so the SPARTN Client functionality is effectively redundant and may be removed in a subsequent version of PyGPSClient.

  The SPARTN MQTT and L-Band configuration panels are now disabled by default, though the L-Band panel can in theory still be used for other generic L-Band modem configuration purposes and can be re-enabled by setting json configuration parameter `lband_enabled_b` to `1`.

Please refer to [SPARTN.md](https://github.com/semuconsulting/PyGPSClient/blob/master/SPARTN.md) for instructions.

---
## <a name="socketserver">Socket Server / NTRIP Caster Facilities</a>

The Socket Server / NTRIP Caster facility is capable of operating in either of two modes;
1. SOCKET SERVER - an open, unauthenticated TCP socket server available to any socket client including, for example, another instance of PyGPSClient or the [`gnssstreamer` CLI utility](https://github.com/semuconsulting/pygnssutils#gnssstreamer). In this mode it will broadcast the host's currently connected GNSS data stream. The default port is 50012.
2. NTRIP CASTER - a simple implementation of an authenticated NTRIP caster available to any NTRIP client including, for example, PyGPSClient's NTRIP Client facility, [`gnssntripclient`](https://github.com/semuconsulting/pygnssutils#gnssntripclient) or BKG's [NTRIP Client (BNC)](https://igs.bkg.bund.de/ntrip/download). Login credentials for the NTRIP caster are set via the `"ntripcasteruser_s":` and `"ntripcasterpassword_s":` settings in the *.json confirmation file (they can also be set via PyGPSClient command line arguments `--ntripcasteruser`, `--ntripcasterpassword`, or by setting environment variables `NTRIPCASTER_USER`, `NTRIPCASTER_PASSWORD`). Default settings are as follows: bind address: 0.0.0.0, port: 2101, mountpoint: pygnssutils, user: anon, password: password.

By default, the server/caster binds to the host address '0.0.0.0' (IPv4) or '::' (IPv6) i.e. all available IP addresses on the host machine. This can be overridden via the settings panel or a host environment variable `PYGPSCLIENT_BINDADDRESS`. A label on the settings panel indicates the number of connected clients, and the server/caster status is indicated in the topmost banner: running with no clients: ![transmit icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/iconmonstr-noclient-10-24.png?raw=true), running with clients: ![transmit icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/iconmonstr-transmit-10-24.png?raw=true).

**Pre-Requisites:**

1. Running in NTRIP CASTER mode is predicated on the host being connected to an RTK-compatible GNSS receiver **operating in Base Station mode** (either `FIXED` or `SURVEY_IN`) and outputting the requisite RTCM3 message types (1005/6, 1077, 1087, 1097, etc.). 
1. It may be necessary to add a firewall rule and/or enable port-forwarding on the host machine or router to allow remote traffic on the specified address:port.
1. The server supports encrypted TLS (HTTPS) connections. The TLS certificate/key location can be set via environment variable `PYGNSSUTILS_PEMPATH`; the default is `$HOME/pygnssutils.pem`. A self-signed pem file suitable for test and demonstration purposes can be created interactively thus:
   ```shell
   openssl req -x509 -newkey rsa:4096 -keyout pygnssutils.pem -out pygnssutils.pem -sha256 -days 3650 -nodes
   ```

**Instructions:**

**SOCKET SERVER MODE**

1. Select SOCKET SERVER mode and (if necessary) enter the host IP address and port.
1. Select 'TLS' to enable an encrypted TLS connection.
1. Check the Socket Server/NTRIP Caster checkbox to activate the server.
1. To stop the server, uncheck the checkbox.

**NTRIP CASTER MODE**

1. Select NTRIP CASTER mode and (if necessary) enter the host IP address and port.
1. Select 'TLS' to enable an encrypted TLS (HTTPS) connection.
1. An additional expandable panel is made available to allow the user to configure a connected RTK-compatible receiver to operate in either `FIXED` or `SURVEY-IN` Base Station mode (*NB: parameters can only be amended while the caster is stopped*).
1. Select the receiver type (currently u-blox ZED-F9*, u-blox ZED-X20*, Quectel LG290P, Quectel LC29HBA and Septentrio Mosaic X5 receivers are supported) and click the Send button to send the appropriate configuration commands to the receiver. 
1. **NB** Septentrio Mosaic X5: These receivers are configured via ASCII TTY commands - to monitor the command responses, set the console protocol to "TTY" (*remember to set it back to RTCM when monitoring the RTCM3 output*). Note also that the input (ASCII command) UART port may be different to the output (RTCM3) UART port - make sure to select the appropriate port(s) when configuring the device and monitoring the RTCM3 output.
1. NMEA messages can be suppressed by checking 'Disable NMEA'.
1. NTRIP client login credentials are set via the user and password fields. 
1. Check the Socket Server/NTRIP Caster checkbox to activate the caster.
1. To stop the caster, uncheck the checkbox.

### <a name="basestation">Base Station Configuration</a>

| Configuration Settings | Base Station Mode    |
|------------------------------------------------------|---------------------------------------------------------|
| ![basestation config](https://github.com/semuconsulting/PyGPSClient/blob/master/images/basestation_fixed.png?raw=true) | **FIXED**. In this mode, the known base station coordinates (*Antenna Reference Point or ARP*) are specified in either LLH or ECEF (X,Y,Z) format. The coordinates are pre-populated with the receiver's current navigation solution (if available), but these can (and normally should) be overridden with accurately surveyed values. If the coordinates are accepted, the Fix status will change to `TIME ONLY` and the receiver will start outputting RTCM `1005` or `1006` (*Antenna Reference Point or ARP*) messages containing the base station location in ECEF (X,Y,Z) format. |
| ![basestation config](https://github.com/semuconsulting/PyGPSClient/blob/master/images/basestation_svin.png?raw=true)  | **SURVEY-IN**. In this mode, the base station coordinates are derived from the receiver's current navigation solution, provided the prescribed level of accuracy is met within the specified survey duration. If the survey is successful, the Fix status will change to `TIME ONLY` and the receiver will start outputting RTCM `1005` or `1006` messages containing the base station location in ECEF (X,Y,Z) format. The surveyed base station location will be updated from the position provided by these RTCM `1005` or `1006` messages.|
| ![basestation config](https://github.com/semuconsulting/PyGPSClient/blob/master/images/basestation_off.png?raw=true)  | **DISABLED**. Disable base station operation. |

**NB:** To operate effectively as an RTK Base Station, antenna positioning is of paramount importance. Refer to the following links for advice:
- [u-blox GNSS Antennas Paper](https://www.ardusimple.com/wp-content/uploads/2022/04/GNSS-Antennas_AppNote_UBX-15030289.pdf)
- [Ardusimple GNSS Antenna Installation Guide](https://www.ardusimple.com/gps-gnss-antenna-installation-guide/)


---
## <a name="gpxviewer">GPX Track Viewer</a>

![gpxviewer screenshot](https://github.com/semuconsulting/PyGPSClient/blob/master/images/gpxviewer.png?raw=true)

*GPX Track Viewer screenshot*

The GPX Track Viewer can display any valid GPX file containing track point (`trkpt`), route point (`rtept`) or waypoint (`wpt`) elements against either an ["custom" offline map image](#custommap), or an online MapQuest "map", "sat" or "hyb" view. The "map", "sat" and "hyb" options require a free [MapQuest API key](#mapquestapi). The Y axis scales will reflect the current choice of units (metric or imperial). If the GPX track omits a time element, the time and speed axes will be flagged as nominal. GPX track metadata, including min, max, average (mean) and median elevation and speed values, is displayed in the selected units. 
Click ![refresh icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/iconmonstr-refresh-lined-24.png?raw=true) to refresh the display after any changes (e.g. resizing, zooming or change of units). The location marker indicates the nominal center point of the track.

---
## <a name="mapquestapi">MapQuest API Key</a>

**Pre-Requisites:**

To use the optional dynamic web-based mapview or GPX Track Viewer facilities, you need to request and install a 
[MapQuest API key](https://developer.mapquest.com/user/login/sign-up).

Note that, from January 15th 2024, MapQuest require payment card details for the use of this API, but the
first 15,000 transactions/month remain free. Usage above 15,000 transactions/month is charged at $.0045 per transaction. See
[FAQ](https://developer.mapquest.com/faq) for further information.

For this reason, the map refresh rate is intentionally limited to 1/minute* to avoid exceeding the free transaction limit under normal use. **NB:** this
facility is *not* intended to be used for real time navigational purposes.

**Instructions:**

Once you have received the API key (a 32-character alphanumeric string), you can (in order of precedence):

1. Copy it to the `"mqapikey_s":` value in your json configuration file (see example provided).
2. Create an environment variable named `MQAPIKEY` (all upper case) and set this to the API key value. It is recommended 
that this is a User variable rather than a System/Global variable.
3. Pass it via command line argument `--mqapikey`.

*The web map refresh rate can be amended if required by changing the `mapupdateinterval_n:` value in your json configuration file.

---
## <a name="userdefined">User Defined Presets</a>

The UBX, NMEA and TTY Configuration Dialogs include the facility to send user-defined configuration messages or message sequences to a compatible receiver. These can be set up by adding appropriate comma- or semicolon-delimited message descriptions and payload definitions to the `"ubxpresets_l"`, `"nmeapresets_l"` or `"ttypresets_l"` settings in your json configuration file (see [example provided](https://github.com/semuconsulting/PyGPSClient/blob/master/pygpsclient.json#L186)). The message definition comprises a free-format text description (*avoid embedded commas or semi-colons*) followed by one or more pyubx2 (UBX), pynmeagps (NMEA) or tty (ASCII) message constructors, e,g. 

- UBX - `<description>, <message class>, <message id>, <payload as hexadecimal string>, <msgmode>`
- NMEA - `<description>; <talker>; <message id>; <payload as comma-separated string>; <msgmode>`
- TTY - `<description>; <tty command>`

If the command description contains the term `CONFIRM`, a pop-up confirmation box will appear before the command is actioned.

When PyGPSClient is first started, these settings are pre-populated with an initial set of preset commands, which can be saved to a \*.json configuration file and then manually removed, amended or supplemented in accordance with the user's preferences. To reinstate this initial set at a later date, insert the line `"INIT_PRESETS",` at the top of the relevant `"ubxpresets_l"`, `"nmeapresets_l"` or `"ttypresets_l"` configuration setting.

The `pygpsclient.ubx2preset()` and `pygpsclient.nmea2preset()` helper functions may be used to convert a `UBXMessage` or `NMEAMessage` object into a preset string suitable for copying and pasting into the `"ubxpresents_l":` or `"nmeapresets_l":` JSON configuration sections:

```python
from pygpsclient import ubx2preset, nmea2preset
from pyubx2 import UBXMessage
from pynmeagps import NMEAMessage, SET

ubx = UBXMessage("CFG", "CFG-MSG", SET, msgClass=0x01, msgID=0x03, rateUART1=1)
print(ubx2preset(ubx, "Configure NAV-STATUS Message Rate on ZED-F9P"))

nmea = NMEAMessage("P", "QTMCFGUART", SET, baudrate=460800)
print(nmea2preset(nmea, "Configure UART baud rate on LG290P"))
```
```
Configure NAV-STATUS Message Rate on ZED-F9P, CFG, CFG-MSG, 0103000100000000, 1
Configure UART baud rate on LG290P; P; QTMCFGUART; W,460800; 1
```

Multiple commands can be concatenated on a single line. Illustrative examples are shown in the sample [pygpsclient.json](https://github.com/semuconsulting/PyGPSClient/blob/master/pygpsclient.json#L188) file.

---
## <a name="cli">Command Line Utilities</a>

The `pygnssutils` and `pyubxutils` libraries which underpin many of the functions in `PyGPSClient` also incorporate command line versions of these functions.

For further details, refer to the `pygnssutils` homepage at [https://github.com/semuconsulting/pygnssutils](https://github.com/semuconsulting/pygnssutils) or `pyubxutils` homepage at [https://github.com/semuconsulting/pyubxutils](https://github.com/semuconsulting/pyubxutils).

--
## <a name="knownissues">Known Issues</a>

1. Most budget USB-UART adapters (e.g. FT232, CH345, CP2102) have a bandwidth limit of around 3MB/s and may not work reliably above 115200 baud, even if the receiver supports higher baud rates. If you're using an adapter and notice significant message corruption, try reducing the baud rate to a maximum 115200.

2. As of October 2025, u-blox have [discontinued their PointPerfect SPARTN L-Band and MQTT services](https://portal.u-blox.com/s/question/0D5Oj00000uB53GKAS/suspension-of-european-pointperfect-lband-spartn-service). As a result, PyGPSClient's [SPARTN Configuration](#spartnconfig) panel is largely redundant and is disabled by default in version>=1.5.17, though it can be re-enabled by manually setting the `lband_enabled_b` configuration setting to 1.

3. Some Homebrew-installed Python environments on MacOS can give rise to critical segmentation errors (*illegal memory access*)  when shell subprocesses are invoked, due to the way permissions are implemented. This may, for example, affect About..Update functionality; the workaround is to update via a standard CLI `pip install --upgrade` command.

4. Installing the optional `cryptography` package on some 32-bit Linux platforms (e.g. Raspberry Pi OS 32) may require [Rust compiler support](https://www.rust-lang.org/tools/install) and some [additional build dependencies](https://cryptography.io/en/latest/installation/) (see  [pyspartn cryptography installation notes](https://github.com/semuconsulting/pyspartn/tree/main/cryptography_installation#readme)):

   ```shell
   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
   sudo apt-get install build-essential libssl-dev libffi-dev python3-dev pkg-config
   ```

---
## <a name="license">License</a>

[![License](https://img.shields.io/github/license/semuconsulting/PyGPSClient.svg)](https://github.com/semuconsulting/PyGPSClient/blob/master/LICENSE)

[BSD 3-Clause License](https://github.com/semuconsulting/PyGPSClient/blob/master/LICENSE)

Copyright &copy; 2020, semuadmin (Steve Smith)

Application icons from [iconmonstr](https://iconmonstr.com/license/) &copy;.

---
## <a name="author">Author Information</a>

semuadmin@semuconsulting.com

`PyGPSClient` is maintained entirely by unpaid volunteers. It receives no funding from advertising or corporate sponsorship. If you find the utility useful, please consider sponsoring the project with the price of a coffee...

[![Sponsor](https://github.com/semuconsulting/pyubx2/blob/master/images/sponsor.png?raw=true)](https://buymeacoffee.com/semuconsulting)

[![Freedom for Ukraine](https://github.com/semuadmin/sandpit/blob/main/src/semuadmin_sandpit/resources/ukraine200.jpg?raw=true)](https://u24.gov.ua/)
