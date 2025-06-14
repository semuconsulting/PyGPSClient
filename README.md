
# PyGPSClient

[Current Status](#currentstatus) |
[Installation](#installation) |
[Instructions](#instructions) |
[UBX Configuration](#ubxconfig) |
[NMEA Configuration](#nmeaconfig) |
[NTRIP Client](#ntripconfig) |
[SPARTN Client](#spartnconfig) |
[Socket Server / NTRIP Caster](#socketserver) |
[GPX Track Viewer](#gpxviewer) |
[Mapquest API Key](#mapquestapi) |
[User-defined Presets](#userdefined) |
[TTY Commands](#ttycommands) |
[CLI Utilities](#cli) |
[Known Issues](#knownissues) |
[License](#license) |
[Author Information](#author)

PyGPSClient is a free, open-source, multi-platform graphical GNSS/GPS testing, diagnostic and configuration application written entirely in Python and tkinter. 
* Runs on any platform which supports a Python 3 interpreter (>=3.9) and tkinter (>=8.6) GUI framework, including Windows, MacOS, Linux and Raspberry Pi OS.
* Supports NMEA, UBX, SBF, RTCM3, NTRIP, SPARTN, MQTT and TTY (ASCII) protocols.
* Capable of reading from a variety of GNSS data streams: Serial (USB / UART), Socket (TCP / UDP), binary data stream (terminal or file capture) and u-center (*.ubx) recording.
* Provides [NTRIP](#ntripconfig) and [SPARTN](#spartnconfig) client facilities.
* Can serve as an [NTRIP base station](#basestation) with an RTK-compatible receiver (e.g. u-blox ZED-F9P/X20P, Quectel LG290P or Septentrio Mosaic X5).
* While not intended to be a direct replacement, the application supports most of the UBX configuration functionality in u-blox's Windows-only [u-center &copy;](https://www.u-blox.com/en/product/u-center) tool (*only public-domain features are supported*).
* Also supports GNSS (*and related*) device configuration via proprietary NMEA sentences (e.g. Quectel LG290P PQTM*) and ASCII TTY commands (e.g. Septentrio Mosaic X5, Feyman IM19).

![full app screenshot ubx](https://github.com/semuconsulting/PyGPSClient/blob/master/images/app.png?raw=true)

*Screenshot showing mixed-protocol stream from u-blox ZED-F9P receiver, using PyGPSClient's [NTRIP Client](#ntripconfig) with a base station 26 km to the west to achieve better than 2 cm accuracy*

The application can be installed using the standard `pip` Python package manager - see [installation instructions](#installation) below.

This is an independent project and we have no affiliation whatsoever with any GNSS manufacturer or distributor.

---
## <a name="currentstatus">Current Status</a>

![Status](https://img.shields.io/pypi/status/PyGPSClient) 
![Release](https://img.shields.io/github/v/release/semuconsulting/PyGPSClient)
![Build](https://img.shields.io/github/actions/workflow/status/semuconsulting/PyGPSClient/main.yml?branch=master)
![Release Date](https://img.shields.io/github/release-date/semuconsulting/PyGPSClient)
![Last Commit](https://img.shields.io/github/last-commit/semuconsulting/PyGPSClient)
![Contributors](https://img.shields.io/github/contributors/semuconsulting/PyGPSClient.svg)
![Open Issues](https://img.shields.io/github/issues-raw/semuconsulting/PyGPSClient)

The PyGPSClient home page is at [PyGPSClient](https://github.com/semuconsulting/PyGPSClient). The following references may be useful:
1. [Glossary of GNSS Terms and Abbreviations](https://www.semuconsulting.com/gnsswiki/glossary/).
1. [GNSS Positioning - A Reviser](https://www.semuconsulting.com/gnsswiki/) - a general overview of GNSS, OSR, SSR, RTK, NTRIP and SPARTN positioning and error correction technologies and terminology.
1. [Achieving cm Level GNSS Accuracy using RTK](https://www.semuconsulting.com/gnsswiki/rtktips/) - practical tips on high precision RTK using PyGPSClient.
1. [Sphinx API Documentation](https://www.semuconsulting.com/pygpsclient) in HTML format.

Contributions welcome - please refer to [CONTRIBUTING.MD](https://github.com/semuconsulting/PyGPSClient/blob/master/CONTRIBUTING.md).

For [Bug reports](https://github.com/semuconsulting/PyGPSClient/blob/master/.github/ISSUE_TEMPLATE/bug_report.md), please use the template provided. For feature requests and general queries and advice, post a message to one of the [PyGPSClient Discussions](https://github.com/semuconsulting/PyGPSClient/discussions) channels in the first instance.

---
## <a name="installation">Installation</a>

## The Quick Version

If you have an [official Python]([Python.org](https://www.python.org/downloads/)) >=3.9 with tkinter >=8.6 installed and the Python [binaries](#binaries) folder is in your PATH, you can install PyGPSClient using pip:
```shell
python3 -m pip install --upgrade pygpsclient
```

and then run it by typing:
```shell
pygpsclient
```

**NB** If you get `error: externally-managed-environment`, refer to the longer installation guidelines for **virtual environments** using [pip](#pip) or [pipx](#pipx) below.

## The Longer Version

In the following, `python3` & `pip` refer to the Python 3 executables. You may need to substitute `python` for `python3`, depending on your particular environment (*on Windows it's generally `python`*). 

### Platform Dependencies

- Python 3.9 - 3.13
- Tk (tkinter) >= 8.6*¹*
- Screen resolution >= 800 x 600; Ideally >= 1920 x 1080, though the main application window is resizeable and reconfigurable.

**All platforms**

- **NB** It is highly recommended to use the latest official [Python.org](https://www.python.org/downloads/) installation package for your platform, rather than any pre-installed version.
- **NB** It is highly recommended that the Python 3 [binaries](#binaries) and site_packages directories are included in your PATH (*most standard Python 3 installation packages will do this automatically if you select the 'Add to PATH' option during installation*).

**Windows 10 or later:**

Normally installs without any additional steps.

**MacOS 13 or later:**

(See also [Installation Script](#installscript) below)

*¹* The version of Python supplied with some Apple MacOS platforms includes a [deprecated version of tkinter](https://www.python.org/download/mac/tcltk/) (8.5). Use an official [Python.org](https://www.python.org/downloads/) installation package instead. 

**NB:** PyGPSClient does *NOT* require Homebrew or MacPorts to be installed on MacOS.

**Linux (including Raspberry Pi OS):**

(See also [Installation Script](#installscript) below)

Some Linux distributions may not include the necessary pip, tkinter or Pillow imaging libraries by default. They may need to be installed separately, e.g.:

```shell
sudo apt install python3-pip python3-tk python3-pil python3-pil.imagetk libjpeg-dev zlib1g-dev
```

If you're [compiling the latest version of Python 3 from source](https://github.com/semuconsulting/PyGPSClient/blob/master/examples/python_compile.sh), you may also need to install tk-dev (or a similarly named package e.g. tk-devel) first. Refer to http://wiki.python.org/moin/TkInter for further details:

```shell
sudo apt install tk-dev
```

On some 32-bit Linux platforms (e.g. Raspberry Pi OS 32), it may be necessary to [install Rust compiler support](https://www.rust-lang.org/tools/install) and some [additional build dependencies](https://cryptography.io/en/latest/installation/) in order to install the `cryptography` library which PyGPSClient depends on to decrypt SPARTN messages (see  [pyspartn cryptography installation notes](https://github.com/semuconsulting/pyspartn/tree/main/cryptography_installation#readme)):

```shell
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
sudo apt-get install build-essential libssl-dev libffi-dev python3-dev pkg-config
```

**Import Custom Map dependency - rasterio**

To enable automatic extent detection in the Import Custom Map facility, the `rasterio` Python library must be installed. This in turn requires the [GDAL (Geospatial Data Abstration Layer)](https://gdal.org/en/stable/) library:

```shell
python3 -m pip install rasterio
```

... or on some Linux distributions:

```shell
sudo apt install python3-rasterio
```

*FYI* GDAL can also be installed as part of a [QGIS](https://qgis.org/download/) installation.

### User Privileges

To access the serial port on most Linux platforms, you will need to be a member of the 
`tty` and/or `dialout` groups. Other than this, no special privileges are required.

```shell
usermod -a -G tty myuser
```

### <a name="pip">Install using pip</a>

![Python version](https://img.shields.io/pypi/pyversions/PyGPSClient.svg?style=flat)
[![PyPI version](https://img.shields.io/pypi/v/PyGPSClient.svg?style=flat)](https://pypi.org/project/PyGPSClient/)
![PyPI downloads](https://img.shields.io/pypi/dm/PyGPSClient.svg?style=flat)

The recommended way to install the latest version of `PyGPSClient` is with [pip](http://pypi.python.org/pypi/pip/):

```shell
python3 -m pip install --upgrade pygpsclient
```

If required, `PyGPSClient` can also be installed and run in a [virtual environment](https://www.geeksforgeeks.org/python-virtual-environment/) - this may be necessary if you have an `externally-managed-environment`, e.g.:
```shell
python3 -m venv pygpsclient
source pygpsclient/bin/activate # (or pygpsclient\Scripts\activate on Windows)
python3 -m pip install --upgrade pygpsclient
pygpsclient
```

To deactivate the virtual environment:

```shell
deactivate
```

To reactivate and run from the virtual environment:
```shell
source pygpsclient/bin/activate # (or pygpsclient\Scripts\activate on Windows)
pygpsclient
```

To upgrade PyGPSClient to the latest version from the virtual environment:
```shell
source pygpsclient/bin/activate # (or pygpsclient\Scripts\activate on Windows)
python3 -m pip install --upgrade pygpsclient
```

The pip installation process places an executable file `pygpsclient` in the Python binaries folder (`../bin` on Linux & MacOS, `..\Scripts` on Windows). The PyGPSClient application may be started by double-clicking on this executable file from your file manager or, if the binaries folder is in your PATH, by opening a terminal and typing (all lowercase):
```shell
pygpsclient
````

`pygpsclient` accepts optional command line arguments for a variety of configurable parameters. These will override any saved configuration file settings. Type the following for help:
```shell
pygpsclient -h
```

**NB:** If the Python 3 binaries folder is *not* in your PATH, you will need to add the fully-qualified path to the `pygpsclient` executable in the command above.

<a name="binaries">**Tip:**</a> The location of the relevant binaries folder can usually be found by executing one of the following commands:

Global installation:
```shell
python3 -c "import os,sysconfig;print(sysconfig.get_path('scripts'))"
```

User installation:
```shell
python3 -c "import os,sysconfig;print(sysconfig.get_path('scripts',f'{os.name}_user'))"
```

Typically:

1. Windows: `C:\Users\myuser\AppData\Roaming\Python\Python3**\Scripts\pygpsclient.exe`
2. MacOS: `/Library/Frameworks/Python.framework/Versions/3.**/bin/pygpsclient`
3. Linux: `/home/myuser/.local/bin/pygpsclient`
4. Virtual Env: `$ENV/bin/pygpsclient` (or `$ENV\Scripts\pygpsclient.exe` on Windows), where `$ENV` is the full path to your virtual environment.

where `**` signifies the Python version e.g. `3.12`.

**NB** The pip installation process does not automatically create a desktop application launcher, but this can be done manually - see [APPLAUNCH](https://github.com/semuconsulting/PyGPSClient/blob/master/APPLAUNCH.md).

### <a name="pipx">Install using pipx</a>

You can also use [pipx](https://pipx.pypa.io/latest/installation/) (_if available_) to install `pygpsclient` into a virtual environment - use the `pipx ensurepath` command to add the relevant Python binaries folder to your PATH.

```shell
pipx ensurepath
pipx install pygpsclient
```

`pipx` will typically create a virtual environment in the user's local shared folder e.g. `/home/user/.local/share/pipx/venvs/pygpsclient`.

### <a name="installscript">Install Using Installation Script - MacOS & 64-bit Debian-based Linux Only</a>

An example [installation shell script](https://github.com/semuconsulting/PyGPSClient/blob/master/examples/pygpsclient_debian_install.sh) is available for use on most vanilla 64-bit Debian-based environments with Python>=3.9, including Raspberry Pi and Ubuntu. To run this installation script, download it to your Raspberry Pi or other Debian-based workstation and - from the download folder - type:

```shell
chmod +x pygpsclient_debian_install.sh
./pygpsclient_debian_install.sh
```

A similar [installation shell script](https://github.com/semuconsulting/PyGPSClient/blob/master/examples/pygpsclient_macos_install.sh) is available for MacOS 13 or later running a ZSH shell (*Homebrew or MacPorts are NOT required*). This will also install the latest official version of Python 3 with tkinter 8.6. Download the script to your Mac and - from the download folder - type:

```shell
./pygpsclient_macos_install.sh
```

In both cases you will be prompted to enter your sudo (admin) password.

---
## <a name="instructions">Instructions</a>

1. To connect to a GNSS receiver via USB or UART port, select the device from the listbox, set the appropriate serial connection parameters and click 
![connect icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/usbport-1-24.png?raw=true). The application will endeavour to pre-select a recognised GNSS/GPS device but this is platform and device dependent. Press the ![refresh](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/iconmonstr-refresh-6-16.png?raw=true) button to refresh the list of connected devices at any point. `Rate bps` (baud rate) is typically the only setting that might need adjusting, but tweaking the `timeout` setting may improve performance on certain platforms. The `Msg Mode` parameter defaults to `GET` i.e., periodic or poll response messages *from* a receiver. If you wish to parse streams of command or poll messages being sent *to* a receiver, set the `Msg Mode` to `SET` or `POLL`. An optional serial or socket stream inactivity timeout can also be set (in seconds; 0 = no timeout).
1. A custom user-defined serial port can also be passed via the json configuration file setting `"userport_s":`, via environment variable `PYGPSCLIENT_USERPORT` or as a command line argument `--userport`. A special userport value of "ubxsimulator" invokes the experimental [`pyubxutils.UBXSimulator`](https://github.com/semuconsulting/pyubxutils/blob/main/src/pyubxutils/ubxsimulator.py) utility to emulate a GNSS NMEA/UBX serial stream. 
1. To connect to a TCP or UDP socket, enter the server URL and port, select the protocol (defaults to TCP) and click 
![connect socket icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/ethernet-1-24.png?raw=true).
1. To stream from a previously-saved <a name="filestream">binary datalog file</a>, click 
![connect-file icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/binary-1-24.png?raw=true) and select the file type (`*.log, *.ubx, *.*`) and path. PyGPSClient datalog files will be named e.g. `pygpsdata-20220427114802.log`, but any binary dump of an GNSS receiver output is acceptable, including `*.ubx` files produced by u-center.
1. To disconnect from the data stream, click
![disconnect icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/iconmonstr-media-control-50-24.png?raw=true).
1. Protocols Shown - Select which protocols to display; NMEA, UBX, SBF, RTCM3, SPARTN or TTY (NB: this only changes the displayed protocols - to change the actual protocols output by the receiver, use the [UBX Configuration Dialog](#ubxconfig)).
   - **NB:** Serial connection must be stopped before changing between SBF, UBX or TTY (terminal) protocols.
   - **NB:** Enabling TTY (terminal) mode will disable all other protocols.
1. Console Display - Select console display format (Parsed, Binary, Hex Tabular, Hex String, Parsed+Hex Tabular - see Console Widget below).
1. Tags - enable color tags in console (see Console Widget below).
1. Position Format and Units - Change the displayed position (D.DD / D.M.S / D.M.MM / ECEF) and unit (metric/imperial) formats.
1. Map Type - Select from "world", "map", "sat" or "custom". "map" and "sat" types require an Internet connection and free [Mapquest API Key](#mapquestapi). "custom" offline map images can be imported and georeferenced using the [Menu..Options..Import Custom Map](#custommap) facility.
1. Show Track - Tick to show track in map view. Map track will only be recorded while this checkbox is ticked.
1. Show Unused Satellites - Include or exclude satellites that are not used in the navigation solution (e.g. because their signal level is too low) from the graph and sky view panels.
1. DataLogging - Turn Data logging in the selected format on or off. You will be prompted to select the directory into which timestamped log files are saved.
1. GPX Track - Turn track recording (in GPX format) on or off. You will be prompted to select the directory into which timestamped GPX track files are saved.
1. To save the current configuration to a file, go to File..Save Configuration.
1. To load a saved configuration file, go to File..Load Configuration. The default configuration file location is `$HOME/pygpsclient.json`. **NB** Any active serial or RTK connection must be stopped before loading a new configuration.

1. [Socket Server / NTRIP Caster](#socketserver) facility with two modes of operation: (a) open, unauthenticated Socket Server or (b) NTRIP Caster (mountpoint = `pygnssutils`).
1. [UBX Configuration Dialog](#ubxconfig), with the ability to send a variety of UBX CFG configuration commands to u-blox GNSS devices. This includes the facility to add **user-defined commands or command sequences** - see instructions under [user-defined presets](#userdefined) below. To display the UBX Configuration Dialog (*only functional when connected to a UBX GNSS device via serial port*), click
![gear icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/iconmonstr-gear-2-24.png?raw=true), or go to Menu..Options..UBX Configuration Dialog.
1. [NMEA Configuration Dialog](#nmeaconfig), with the ability to send a variety of NMEA configuration commands to GNSS devices (e.g. Quectel LG290P). This includes the facility to add **user-defined commands or command sequences** - see instructions under [user-defined presets](#userdefined) below. To display the NMEA Configuration Dialog (*only functional when connected to a compatible GNSS device via serial port*), click
![gear icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/iconmonstr-gear-2-24-brown.png?raw=true), or go to Menu..Options..NMEA Configuration Dialog.
1. [NTRIP Client](#ntripconfig) facility with the ability to connect to a specified NTRIP caster, parse the incoming RTCM3 or SPARTN data and feed this data to a compatible GNSS receiver (*requires an Internet connection and access to an NTRIP caster and local mountpoint*). To display the NTRIP Client Configuration Dialog, click
![ntrip icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/iconmonstr-antenna-4-24.png?raw=true), or go to Menu..Options..NTRIP Configuration Dialog.
1. [SPARTN Client](#spartnconfig) facility with the ability to configure an IP or L-Band SPARTN Correction source and SPARTN-compatible GNSS receiver (e.g. ZED-F9P) and pass the incoming correction data to the GNSS receiver (*requires an Internet connection and access to a SPARTN location service*). To display the SPARTN Client Configuration Dialog, click ![spartn icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/iconmonstr-antenna-3-24.png?raw=true), or go to Menu..Options..SPARTN Configuration Dialog.
1. [GPX Track Viewer](#gpxviewer) utility with elevation and speed profiles and track metadata. To display the GPX Track viewer, go to Menu..Options..GPX Track Viewer.

FYI: By default, the GUI refresh interval is 0.5 seconds. This can be configured via the `guiupdateinterval_f` setting in the json configuration file. **NB:** PyGPSClient may become unresponsive on slower platforms (e.g. Raspberry Pi) if the GUI update interval is less than 0.1 seconds, though much lower intervals (<= 0.1 secs) can be accommodated on more powerful platforms.

| User-selectable 'widgets' | To show or hide the various widgets, go to Menu..View and click on the relevant hide/show option. |
|---------------------------|---------------------------------------------------------------------------------------------------|
|![banner widget](https://github.com/semuconsulting/PyGPSClient/blob/master/images/banner_widget.png?raw=true)| Expandable banner showing key navigation status information based on messages received from receiver. To expand or collapse the banner or serial port configuration widgets, click the ![expand icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/iconmonstr-arrow-80-16.png?raw=true)/![expand icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/iconmonstr-triangle-1-16.png?raw=true) buttons. **NB**: some fields (e.g. hdop/vdop, hacc/vacc) are only available from proprietary NMEA or UBX messages and may not be output by default. The minimum messages required to populate all available fields are: NMEA: GGA, GSA, GSV, RMC, UBX00 (proprietary); UBX: NAV-DOP, NAV-PVT, NAV_SAT |
|![console widget](https://github.com/semuconsulting/PyGPSClient/blob/master/images/console_widget.png?raw=true)| Configurable serial console widget showing incoming GNSS data streams in either parsed, binary or tabular hexadecimal formats. Double-right-click to copy contents of console to clipboard. The scroll behaviour and number of lines retained in the console can be configured via the settings panel. Supports user-configurable color tagging of selected strings for easy identification. Color tags are loaded from the `"colortag_b":` value (`0` = disable, `1` = enable) and `"colortags_l":` list (`[string, color]` pairs) in your json configuration file (see example provided). If color is set to "HALT", streaming will halt on any match and a warning displayed. NB: color tagging does impose a small performance overhead - turning it off will improve console response times at very high transaction rates.|
|![skyview widget](https://github.com/semuconsulting/PyGPSClient/blob/master/images/skyview_widget.png?raw=true)| Skyview widget showing current satellite visibility and position (elevation / azimuth). Satellite icon borders are colour-coded to distinguish between different GNSS constellations. For consistency between NMEA and UBX data sources, will display GLONASS NMEA SVID (65-96) rather than slot (1-24). |
|![graphview widget](https://github.com/semuconsulting/PyGPSClient/blob/master/images/graphview_widget.png?raw=true)| Graphview widget showing current satellite reception (carrier-to-noise ratio or cnr). Double-click to toggle legend. |
|![static map](https://github.com/semuconsulting/PyGPSClient/blob/master/images/staticmap.png?raw=true)| Map widget with various modes of display. Map Type = 'world': a static offline Mercator world map showing current global location.
|![webmap widget](https://github.com/semuconsulting/PyGPSClient/blob/master/images/webmap_widget.png?raw=true)| Map Type = 'map' or 'sat': Dynamic, online web map or satellite image via MapQuest API (*requires an Internet connection and free [Mapquest API Key](#mapquestapi)*). Left Click +/- to zoom in or out. Right click +/- to zoom in or out to maximum extent. By default, the web map will automatically refresh every 60 seconds (*indicated by a small timer icon at the top left*). The default refresh rate can be amended by changing the `"mapupdateinterval_n":` value in your json configuration file, but **NB** the facility is not intended to be used for real-time navigation. Double-click anywhere in the map to immediately refresh. |
|![custom map](https://github.com/semuconsulting/PyGPSClient/blob/master/images/custommap.png?raw=true)| Map Type = 'custom': One or more user-defined custom offline maps can be imported using the Menu..Options..Import Custom Map facility, or by manually setting the `usermaps_l` field in the json configuration file. The `usermaps_l` setting represents a list of map paths and bounding boxes in the format ["path to map image", [minlat, minlon, maxlat, maxlon]] - see [example configuration file](https://github.com/semuconsulting/PyGPSClient/blob/master/pygpsclient.json#L268). Map images must be a [supported format](https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html) and use a standard WGS84 Web Mercator projection e.g. EPSG:4326.|
|![import custom map](https://github.com/semuconsulting/PyGPSClient/blob/master/images/importcustommap.png?raw=true)| <a name="custommap">Import Custom Map dialog</a>. Click ![load icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/iconmonstr-folder-18-24.png?raw=true) to open the custom map image location (*the default file suffix is `*.tif` - select Show Options to select any file suffix `*.*`*). If the `rasterio` library is installed and the image is georeferenced (e.g. using [QGIS](https://qgis.org/)), the map extent will be automatically extracted - otherwise it must be entered manually. Import the custom map path anad extent settings by clicking ![play icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/iconmonstr-arrow-12-24.png?raw=true). See [Creating Custom Maps for PyGPSClient](https://www.semuconsulting.com/gnsswiki/custommapwiki/) for tips on how to create a suitable georeferenced map image.|
|![spectrum widget](https://github.com/semuconsulting/PyGPSClient/blob/master/images/spectrum_widget.png?raw=true)| Spectrum widget showing a spectrum analysis chart (*GNSS receiver must be capable of outputting UBX MON-SPAN messages*). Clicking anywhere in the spectrum chart will display the frequency and decibel reading at that point. Double-clicking anywhere in the chart will toggle the GNSS frequency band markers (L1, G2, etc.) on or off. Right-click anywhere in the chart to capture a snapshot of the spectrum data, which will then be superimposed on the live data. Double-right-click to clear snapshot. **NB:** Some receivers (e.g. NEO-F10N) will not output the requisite MON-SPAN messages unless the port baud rate is at least 57,600. |
|![sysmon widget](https://github.com/semuconsulting/PyGPSClient/blob/master/images/sysmon_widget.png?raw=true)| System Monitor widget showing device cpu, memory and I/O utilisation (*GNSS receiver must be capable of outputting UBX MON-SYS and/or MON-COMMS messages*). Tick checkbox to toggle between actual (cumulative) I/O stats and pending I/O. |
|![scatterplot widget](https://github.com/semuconsulting/PyGPSClient/blob/master/images/scatterplot_widget.png?raw=true)| Scatterplot widget showing variability in position reporting over time. (Optional) Enter fixed reference position. Select Average to center plot on dynamic average position (*displayed at top left*), or Fixed to center on fixed reference position (*if entered*). Check Autorange to set plot range automatically. Set the update interval (e.g. 4 = every 4th navigation solution). Use the range slider or mouse wheel to adjust plot range. Right-click to set fixed reference point to the current mouse cursor position. Double-click to clear the existing data. Settings may be saved to a json configuration file. |
|![rover widget](https://github.com/semuconsulting/PyGPSClient/blob/master/images/rover_widget.png?raw=true) | Rover widget plots the relative 2D position, track and status information for the roving receiver in a fixed or moving base / rover RTK configuration. Can also display relative position of NTRIP mountpoint and receiver in a static RTK configuration. Double-click to clear existing plot. (*GNSS rover receiver must be capable of outputting UBX NAV-RELPOSNED messages.*) |
|![chart view](https://github.com/semuconsulting/PyGPSClient/blob/master/images/chart_widget.png?raw=true) | Chart widget acts as a multi-channel "plotter", allowing the user to plot a series of named numeric data attributes from any NMEA, UBX, SBF, RTCM or SPARTN data source, with configurable y (value) and x (time) axes. By default, the number of channels is set to 4, but this can be manually edited by the user via the json configuration file setting `chartsettings_d["numchn_n"]`. For each channel, user can select: (*optional*) identity of message source e.g. `NAV-PVT`; attribute name e.g. `hAcc`; scaling factor (divisor) e.g. 1000; y axis range e.g. 0 - 5. Wildcards are available for attribute groups - "\*" (average of group values), "+" (maximum of group values), "-" (minimum of group values) e.g. `cno*` will plot the average `cno` value for a group of satellites. Double-click to clear the existing data. Double-right-click to save the current chart data to the clipboard in CSV format which can be directly pasted into a spreadsheet application. Settings may be saved to a json configuration file. |
|![IMU widget](https://github.com/semuconsulting/PyGPSClient/blob/master/images/imu_widget.png?raw=true) |  IMU (Inertial Management Unit) Monitor widget showing current orientation/attitude (roll, pitch, yaw) and status of IMU from a specified NMEA or UBX message source. Enter the identity of the UBX or NMEA message source (e.g. ESF-ALG, HNR-ATT, NAV-ATT, NAV-PVAT, GPFMI). Select range in degrees (from ±1 to ±180 degrees). Settings may be saved to a json configuration file. |

---
## <a name="ubxconfig">UBX Configuration Facilities</a>

![ubxconfig widget screenshot](https://github.com/semuconsulting/PyGPSClient/blob/master/images/ubxconfig_widget.png?raw=true)

**Pre-Requisites:**

- u-blox GNSS receiver e.g. u-blox NEO-M8S, ZED-F9P, etc. connected to the workstation via USB or UART port.

**Instructions:**

The UBX Configuration Dialog currently provides the following UBX configuration panels:
1. Version panel shows current device hardware/firmware versions (*via MON-VER and MON-HW polls*).
1. CFG Configuration Load/Save/Record facility. This allows users to record ![record icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/iconmonstr-record-24.png?raw=true) a sequence of UBX CFG configuration commands, and to save ![save icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/iconmonstr-save-14-24.png?raw=true) this recording to a file (as binary CFG-* messages). Saved files can be reloaded ![load icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/iconmonstr-folder-18-24.png?raw=true) and the configuration commands replayed ![play icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/iconmonstr-arrow-12-24.png?raw=true). This provides a means to easily reproduce a given sequence of configuration commands, or copy a saved configuration between compatible devices. The Configuration Load/Save/Record facility can accept configuration files in either binary UBX format (\*.ubx) or u-center text format (\*.txt). Files saved using the [ubxsave](#ubxsave) CLI utility (*installed via the `pygnssutils` library*) can also be reloaded and replayed. **Tip:** The contents of a binary config file can be reviewed using PyGPSClient's [file streaming facility](#filestream), *BUT* remember to set the `Msg Mode` in the Settings panel to `SET` rather than the default `GET` ![msgmode capture](https://github.com/semuconsulting/PyGPSClient/blob/master/images/msgmode.png?raw=true).
1. Protocol Configuration panel (CFG-PRT) sets baud rate and inbound/outbound protocols across all available ports.
1. Solution Rate panel (CFG-RATE) sets navigation solution interval in ms (e.g. 1000 = 1/second) and measurement ratio (ratio between the number of measurements and the number of navigation solutions, e.g. 5 = five measurements per navigation solution).
1. For each of the panels above, clicking anywhere in the panel background will refresh the displayed information with the current configuration.
1. Message Rate panel (CFG-MSG) sets message rates per port for UBX and NMEA messages. Message rate is relative to navigation solution frequency e.g. a message rate of '4' means 'every 4th navigation solution' (higher = less frequent).
1. Dynamic configuration panel providing structured updates for a range of legacy CFG-* configuration commands for pre-Generation 9+ devices. Note: 'X' (byte) type attributes can be entered as integers or hexadecimal strings e.g. 522125312 or 0x1f1f0000. Once a command is selected, the configuration is polled and the current values displayed. The user can then amend these values as required and send the updated configuration. Some polls require input arguments (e.g. portID) - these are highlighted and will be set at default values initially (e.g. portID = 0), but can be amended by the user and re-polled using the ![refresh](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/iconmonstr-refresh-lined-24.png?raw=true) button.
1. Configuration Interface widget (CFG-VALSET, CFG-VALDEL and CFG-VALGET) queries and sets configuration for [Generation 9+ devices](https://github.com/semuconsulting/pyubx2#configinterface) e.g. NEO-M9, ZED-F9P, etc.
1. Preset Commands widget supports a variety of preset and user-defined commands - see [user defined presets](#userdefined). The port checkboxes (USB, UART1, etc.) determine which device port(s) any preset message rate commands apply to (_assuming the selected ports are physically implemented on the device_). The selected port(s) may be saved as configuration parameter `defaultport_s` e.g. "USB,UART1".

An icon to the right of each 'SEND' 
![send icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/iconmonstr-arrow-12-24.png?raw=true) button indicates the confirmation status of the configuration command; 
(pending i.e. awaiting confirmation ![pending icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/iconmonstr-time-6-24.png?raw=true), 
confirmed ![confirmed icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/iconmonstr-check-mark-8-24.png?raw=true) or 
warning ![warning icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/iconmonstr-warning-1-24.png?raw=true)). 

**Note:**
* The UBX protocol does not support synchronous command acknowledgement or unique confirmation IDs. Asynchronous command and poll acknowledgements and responses can take several seconds at high message transmission rates, or be discarded altogether if the device's transmit buffer is full (*txbuff-alloc error*). To ensure timely responses, try increasing the baud rate and/or temporarily reducing transmitted message rates using the configuration commands provided.
* A warning icon (typically accompanied by an ACK-NAK response) is usually an indication that one or more of the commands sent is not supported by your receiver.
---
## <a name="nmeaconfig">NMEA Configuration Facilities</a>

![nmeaconfig widget screenshot](https://github.com/semuconsulting/PyGPSClient/blob/master/images/nmeaconfig_widget.png?raw=true)

**Pre-Requisites:**

- Receiver capable of being configured via proprietary NMEA sentences, connected to the workstation via USB or UART port. At time of writing, the only supported GNSS receiver type is the Quectel LG290P, via PQTM* sentences, but additional types may be supported in the underlying NMEA parser library [pynmeagps](https://github.com/semuconsulting/pynmeagps) in later releases.

**Instructions:**

The NMEA Configuration Dialog currently provides the following NMEA configuration panels:
1. Version panel shows current device hardware/firmware versions (*via PQTMVERNO polls*).
1. Dynamic configuration panel providing structured updates for supported receivers e.g. the Quectel LG290P via PQTM* sentences. Once a command is selected, the configuration is polled and the current values displayed. The user can then amend these values as required and send the updated configuration. Some polls require input arguments (e.g. portid or msgname) - these are highlighted and will be set at default values initially (e.g. portid = 1), but can be amended by the user and re-polled using the ![refresh](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/iconmonstr-refresh-lined-24.png?raw=true) button.
1. Preset Commands widget supports a variety of preset and user-defined commands - see [user defined presets](#userdefined).

An icon to the right of each 'SEND' 
![send icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/iconmonstr-arrow-12-24.png?raw=true) button indicates the confirmation status of the configuration command; 
(pending i.e. awaiting confirmation ![pending icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/iconmonstr-time-6-24.png?raw=true), 
confirmed ![confirmed icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/iconmonstr-check-mark-8-24.png?raw=true) or 
warning ![warning icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/iconmonstr-warning-1-24.png?raw=true)).

**NB:** Several Quectel LG290P commands require a Hot Restart (PQTMHOT) before taking effect, including PQTMCFGCNST (Enable/Disable Constellations), PQTMCFGFIX (Configure Fix Rate), PQTMCFGSAT (Configure Satellite Masks) and PQTMCFGSIGNAL (Configure Signal Masks). This is a Quectel protocol constraint, not a PyGPSClient issue.

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

1. Enter the required NTRIP server URL (or IP address), port (defaults to 2101) and HTTPS flag (defaults to 'yes' for ports 443/2102, 'no' for all else). For services which require authorisation, enter your login username and password.
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

![spartn config widget screenshot](https://github.com/semuconsulting/PyGPSClient/blob/master/images/spartnconfig_widget.png?raw=true)

The SPARTN Configuration utility allows users to receive and process SPARTN RTK Correction data from an IP or L-Band source to achieve cm level location accuracy. It provides three independent configuration sections, one for IP Correction (MQTT), one for L-Band Correction (e.g. NEO-D9S) and a third for the GNSS receiver (e.g. ZED-F9P). 

The facility can be accessed by clicking ![SPARTN Client button](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/iconmonstr-antenna-3-24.png?raw=true) or selecting Menu..Options..SPARTN Configuration Dialog.

**Pre-Requisites:**

**NB:** SPARTN data from proprietary subscription services like Thingstream PointPerfect (MQTT or L-Band) is encrypted. While it is not necessary for PyGPSClient to decrypt the data prior to sending it to the GNSS receiver (*the receiver's own firmware will perform the necessary decryption provided the relevant keys have been uploaded*), if you wish to see the decrypted data in the PyGPSClient console it will be necessary to provide current decryption keys via the `spartndecode_b` and `spartnkey_s` settings in the json configuration file. Note that these keys are typically only valid for a 4 week period and will require regular updating. See [pyspartn Encrypted Payloads](https://github.com/semuconsulting/pyspartn#encrypted-payloads) for further details.

1. IP Correction (MQTT Client):

    - Internet access
    - Subscription to a suitable MQTT SPARTN location service e.g. u-blox / Thingstream PointPerfect IP or L-band, which should provide the following details:
      - Server URL e.g. `pp.services.u-blox.com`
      - Client ID (which can be stored in the `"mqttclientid_s":` json configuration file setting or via environment variable `MQTTCLIENTID`)
      - Client Certificate (`*.crt`) and Client Key (`*.pem`) files required to access the SPARTN service via an encrypted HTTPS connection. These files can be downloaded from the Thingstream..PointPerfect..Location Things..Credentials web page. If these are placed in the user's HOME directory using the location service's standard naming convention, PyGPSClient will find them automatically.
      - Region code - select from `us`, `eu`, `jp`, `kr` or `au`.
	  - Source - select from either `IP` or `L-Band` (*NB: the 'L-Band' MQTT mode provides decryption keys, Assist Now (ephemerides) data and L-Band frequency information, but the correction data itself arrives via the L-Band receiver below*).
      - A list of published topics. These typically include:
	  	- `/pp/ip/region` - binary SPARTN correction data (SPARTN-1X-HPAC* / OCB* / GAD*) for the selected region, for IP sources only.
		- `/pp/ubx/mga` - UBX MGA AssistNow ephemera data for each constellation.
		- `/pp/ubx/0236/ip` or `/pp/ubx/0236/Lb` - UBX RXM-SPARTNKEY messages containing the IP or L-band decryption keys to be uploaded to the GNSS receiver.
		- `/pp/frequencies/Lb` - json message containing each region's L-band transmission frequency - currently `us` or `eu` (this is automatically enabled when `L-Band` is selected).

2. L-BAND Correction (D9* Receiver):

    - SPARTN L-Band correction receiver e.g. u-blox NEO-D9S.
    - [Suitable Inmarsat L-band antenna](https://www.amazon.com/RTL-SDR-Blog-1525-1637-Inmarsat-Iridium/dp/B07WGWZS1D) and good satellite reception on regional frequency (NB: standard GNSS antenna may not be suitable).
    - Subscription to L-Band location service e.g. u-blox / Thingstream PointPerfect, which should provide the following details:
      - L-Band frequency (*also available via `/pp/frequencies/Lb` MQTT topic*)
	  - Search window
	  - Use Service ID?
	  - Use Descrambling?
	  - Use Prescrambling?
	  - Service ID
	  - Data Rate
	  - Descrambler Init
	  - Unique Word

3. GNSS Receiver:

    - SPARTN-compatible GNSS receiver e.g. u-blox ZED-F9P
    - Subscription to either IP and/or L-Band location service(s) e.g. e.g. u-blox / Thingstream PointPerfect, which should provide the following details:
      - Current and Next IP or L-band decryption Keys in hexadecimal format. These allow the receiver to decrypt the SPARTN message payloads.
	  - Valid From dates in YYYYMMDD format (keys normally valid for 4 week period).

**Instructions:**

### IP Correction Configuration (MQTT)

1. Enter your MQTT Client ID (or set it up beforehand as *.json configuration setting `"mqttclientid_s":` or via environment variable `MQTTCLIENTID`).
1. Select the path to the MQTT `*.crt` and `*.pem` files provided by the location service (PyGPSClient will use the user's HOME directory by default).
1. Select the required region and subscription mode (`IP` or `L-Band`).
1. Select the required topics:
    - IP - this is the raw SPARTN correction data as SPARTN-1X-HPAC* / OCB* / GAD* messages (required for IP; must be unchecked for L-Band).
    - Assist - this is Assist Now data as UBX MGA-* messages.
    - Key - this is the SPARTN IP or L-band decryption keys as a UBX RXM-SPARTNKEY message.
1. To connect to the MQTT server, click ![connect icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/ethernet-1-24.png?raw=true). To disconnect, click ![disconnect icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/iconmonstr-media-control-50-24.png?raw=true).

### L-Band Correction Configuration (D9*)

1. To connect to the Correction receiver, select the receiver's port from the SPARTN dialog's Serial Port listbox and click ![connect icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/usbport-1-24.png?raw=true). To disconnect, click ![disconnect icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/iconmonstr-media-control-50-24.png?raw=true).
1. Select the required Output Port - this is the port used to connect the Correction receiver to the GNSS receiver e.g. UART2 or I2C.
1. If both Correction and GNSS receivers are connected to the same PyGPSClient workstation (e.g. via separate USB ports), it is possible to run the utility in Output Port = 'Passthough' mode, whereby the output data from the Correction receiver (UBX `RXM-PMP` messages) will be automatically passed through to the GNSS receiver by PyGPSClient, without the need to connect the two externally.
1. To enable INF-DEBUG messages, which give diagnostic information about current L-Band reception, click 'Enable Debug?'.
1. To save the configuration to the device's persistent storage (Battery-backed RAM, Flash or EEPROM), click 'Save Config?'. This only has to be done once for a given region.
1. Once connected, click ![send button](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/iconmonstr-arrow-12-24.png?raw=true) to upload the configuration. The utility will send the relevant configuration command(s) to the Correction receiver and poll for an acknowledgement.

### GNSS Receiver Configuration (F9*)

1. Connect to the GNSS receiver first by clicking ![connect icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/usbport-1-24.png?raw=true) on the main PyGPSClient settings panel.
1. If you are subscribing to the MQTT SPARTNKEY (`/pp/ubx/0236/ip` or `/pp/ubx/0236/Lb`) topic, the decryption key and validity date details will be entered automatically on receipt of a UBX RXM-SPARTNKEY message (which may take a few seconds after connecting). Alternatively, they can be uploaded from the service provider's JSON file, or entered manually as follows:
1. Enter the current and next decryption keys in hexadecimal format e.g. `0102030405060708090a0b0c0d0e0f10`. The keys are normally 16 bytes long, or 32 hexadecimal characters.
1. Enter the supplied Valid From dates in `YYYYMMDD` format. **NB:** These are *Valid From* dates rather than *Expiry* dates. If the location service provides Expiry dates, subtract 4 weeks from these to get the Valid From dates.
1. Select 'DGPS Timeout', 'Upload keys', 'Configure receiver' and 'Disable NMEA' options as required.
1. Select the SPARTN correction source - either `IP` or `L-Band`.
1. To reduce traffic volumes, you can choose to disable NMEA messages from the receiver. A minimal set of UBX NAV messages will be enabled in their place.
1. Click ![send button](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/iconmonstr-arrow-12-24.png?raw=true) to upload the configuration. The utility will send the relevant configuration command(s) to the receiver and poll for an acknowledgement.


Below is a illustrative SPARTN DGPS data log, showing:
* Incoming SPARTN correction messages (SPARTN-1X-HPAC* high-precision atmosphere corrections; SPARTN-OCB* orbit / clock / bias corrections; SPARTN-1X-GAD geographic area definitions). 
* Outgoing UBX RXM-COR confirmation messages from receiver showing that the SPARTN data has been received and decrypted OK.

![spartn console screenshot](https://github.com/semuconsulting/PyGPSClient/blob/master/images/spartn_consolelog.png?raw=true)
---
## <a name="socketserver">Socket Server / NTRIP Caster Facilities</a>

The Socket Server / NTRIP Caster facility is capable of operating in either of two modes;
1. SOCKET SERVER - an open, unauthenticated TCP socket server available to any socket client including, for example, another instance of PyGPSClient or the [`gnssstreamer` CLI utility](https://github.com/semuconsulting/pygnssutils#gnssstreamer). In this mode it will broadcast the host's currently connected GNSS data stream (NMEA, UBX, SBF, RTCM3). The default port is 50012.
2. NTRIP CASTER - a simple implementation of an authenticated NTRIP caster available to any NTRIP client including, for example, PyGPSClient's NTRIP Client facility, [`gnssntripclient`](https://github.com/semuconsulting/pygnssutils#gnssntripclient) or BKG's [NTRIP Client (BNC)](https://igs.bkg.bund.de/ntrip/download). Login credentials for the NTRIP caster are set via the `"ntripcasteruser_s":` and `"ntripcasterpassword_s":` settings in the *.json confirmation file (they can also be set via PyGPSClient command line arguments `--ntripcasteruser`, `--ntripcasterpassword`, or by setting environment variables `NTRIPCASTER_USER`, `NTRIPCASTER_PASSWORD`). Default settings are as follows: bind address: 0.0.0.0, port: 2101, mountpoint: pygnssutils, user: anon, password: password.

By default, the server/caster binds to the host address '0.0.0.0' (IPv4) or '::' (IPv6) i.e. all available IP addresses on the host machine. This can be overridden via the settings panel or a host environment variable `PYGPSCLIENT_BINDADDRESS`. A label on the settings panel indicates the number of connected clients, and the server/caster status is indicated in the topmost banner: running with no clients: ![transmit icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/iconmonstr-noclient-10-24.png?raw=true), running with clients: ![transmit icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/iconmonstr-transmit-10-24.png?raw=true).

**Pre-Requisites:**

1. Running in NTRIP CASTER mode is predicated on the host being connected to an RTK-compatible GNSS receiver (e.g. u-blox ZED-F9P/X20P, Quectel LG290P or Septentrio Mosaic X5) **operating in Base Station mode** (either `FIXED` or `SURVEY_IN`) and outputting the requisite RTCM3 message types (1006, 1077, 1087, 1097, etc.). 
1. It may be necessary to add a firewall rule and/or enable port-forwarding on the host machine or router to allow remote traffic on the specified address:port.

**Instructions:**

**SOCKET SERVER MODE**

1. Select SOCKET SERVER mode and (if necessary) enter the host IP address and port.
1. Check the Socket Server/NTRIP Caster checkbox to activate the server.
1. To stop the server, uncheck the checkbox.

**NTRIP CASTER MODE**

1. Select NTRIP CASTER mode and (if necessary) enter the host IP address and port.
1. An additional expandable panel is made available to allow the user to configure a connected RTK-compatible receiver to operate in either `FIXED` or `SURVEY-IN` Base Station mode (*NB: parameters can only be amended while the caster is stopped*).
1. Select the receiver type (currently u-blox ZED-F9*, u-blox ZED-X20*, Quectel LG290P and Septentrio Mosaic X5 receivers are supported) and click the Send button to send the appropriate configuration commands to the receiver. 
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

The GPX Track Viewer can display any valid GPX file containing trackpoints (`<trkpt>..</trkpt>` elements) against either an ["custom" offline map image](#custommap), or an online MapQuest "map" or "sat" view. The "map" and "sat" options require a free [MapQuest API key](#mapquestapi). The Y axis scales will reflect the current choice of units (metric or imperial). Click ![refresh icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/iconmonstr-refresh-lined-24.png?raw=true) to refresh the display after any changes (e.g. resizing, zooming or change of units). In "custom" view, zoom is not functional, and mouse right-click will show the position at the mouse cursor.

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

The UBX and NMEA Configuration Dialogs include the facility to send user-defined configuration messages or message sequences to a compatible receiver. These can be set up by adding
appropriate comma- or semicolon-delimited message descriptions and payload definitions to the `"ubxpresets_l":`or `"nmeapresets_l":` lists in your json configuration file (see [example provided](https://github.com/semuconsulting/PyGPSClient/blob/master/pygpsclient.json#L158)). The message definition comprises a free-format text description (*avoid embedded commas or semi-colons*) followed by one or more pyubx2 (UBX) or pynmeagps (NMEA) message constructors, e,g. 

- UBX - `<description>, <message class>, <message id>, <payload as hexadecimal string>, <msgmode>`
- NMEA - `<description>; <talker>; <message id>; <payload as comma-separated string>; <msgmode>`

If the command description contains the term `CONFIRM`, a pop-up confirmation box will appear before the command is actioned.

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

Multiple commands can be concatenated on a single line. Illustrative examples are shown in the sample [pygpsclient.json](https://github.com/semuconsulting/PyGPSClient/blob/master/pygpsclient.json#L158) file.

---
## <a name="ttycommands">TTY Commands and Presets</a>

![ttydialog screenshot](https://github.com/semuconsulting/PyGPSClient/blob/master/images/tty_dialog.png?raw=true)

The TTY Commands dialog provides a facility to send user-defined ASCII TTY commands (e.g. `AT+` style commands) to the connected serial device. Commands can be entered manually or selected from a list of user-defined presets. The dialog can be accessed via menu bar Options...TTY Commands. 
- CRLF checkbox - if ticked, a CRLF (`b"\x0d\x0a"`) terminator will be added to the command string. 
- Echo checkbox - if ticked, outgoing TTY commands will be echoed on the console with the marker `"TTY<<"`.
- Delay checkbox - if ticked, a small delay will be added between each outgoing command to allow time for the receiving device to process the command.

Preset commands can be set up by adding appropriate semicolon-delimited message descriptions and payload definitions to the `"ttypresets_l":` list in your json configuration file (see [example provided](https://github.com/semuconsulting/PyGPSClient/blob/master/pygpsclient.json#L246)). The message definition comprises a free-format text description (*avoid embedded semi-colons*) followed by one or more ASCII TTY commands, e,g. 

- `<description>; <tty command>`

The following example illustrates a series of ASCII configuration commands being sent to a Septentrio Mosaic X5 receiver, followed by successful acknowledgements:

![ttyconsole screenshot](https://github.com/semuconsulting/PyGPSClient/blob/master/images/tty_console.png?raw=true)

---
## <a name="cli">Command Line Utilities</a>

The `pygnssutils` and `pyubxutils` libraries which underpin many of the functions in `PyGPSClient` also incorporate command line versions of these functions:

1. `gnssstreamer` CLI utility. This is essentially a configurable input/output wrapper around the [`pyubx2.UBXReader`](https://github.com/semuconsulting/pyubx2#reading) class with flexible message formatting and filtering options for NMEA, UBX and RTCM3 protocols.
1. `gnssserver` CLI utility. This implements a TCP Socket Server for GNSS data streams which is also capable of being run as a simple NTRIP Server.
1. `gnssntripclient` CLI utility. This implements a simple NTRIP Client which receives RTCM3 correction data from an NTRIP Server and (optionally) sends this to a
designated output stream.
1. `gnssmqttclient` CLI utility. This implements a simple SPARTN IP (MQTT) Client which receives SPARTN and UBX correction data from a SPARTN IP location service (e.g. u-blox / Thingstream PointPerfect) and (optionally) sends this to a designated output stream.
1. <a name="ubxsave">`ubxsave` CLI utility</a>. This saves a complete set of configuration data from any Generation 9+ u-blox device (e.g. NEO-M9N or ZED-F9P) to a file. The file can then be reloaded to any compatible device using the `ubxload` utility.
1. `ubxload` CLI utility. This reads a file containing binary configuration data and loads it into any compatible Generation 9+ u-blox device (e.g. NEO-M9N or ZED-F9P).
1. `ubxsetrate` CLI utility. A simple utility which sets NMEA or UBX message rates on u-blox GNSS receivers.
1. `ubxbase` CLI utility. This configures an RTK-compatible UBX receiver (e.g. the ZED-F9P) to operate in Base Station mode.

For further details, refer to the `pygnssutils` homepage at [https://github.com/semuconsulting/pygnssutils](https://github.com/semuconsulting/pygnssutils) or `pyubxutils` homepage at [https://github.com/semuconsulting/pyubxutils](https://github.com/semuconsulting/pyubxutils).

--
## <a name="knownissues">Known Issues</a>

None

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

`PyGPSClient` is maintained entirely by unpaid volunteers. It receives no funding from advertising or corporate sponsorship. If you find the utility useful, please consider sponsoring the project with the price of a coffee...

[![Sponsor](https://github.com/semuconsulting/pyubx2/blob/master/images/sponsor.png?raw=true)](https://buymeacoffee.com/semuconsulting)

[![Freedom for Ukraine](https://github.com/semuadmin/sandpit/blob/main/src/sandpit/resources/ukraine200.jpg?raw=true)](https://u24.gov.ua/)
