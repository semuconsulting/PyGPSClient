
# PyGPSClient

[Current Status](#currentstatus) |
[Installation](#installation) |
[Instructions](#instructions) |
[UBX Configuration](#ubxconfig) |
[NTRIP Client](#ntripconfig) |
[SPARTN Client](#spartnconfig) |
[Socket Server / NTRIP Caster](#socketserver) |
[GPX Track Viewer](#gpxviewer) |
[Mapquest API Key](#mapquestapi) |
[User-defined Presets](#userdefined) |
[CLI Utilities](#cli) |
[License](#license) |
[Author Information](#author)

PyGPSClient is a free, open-source, multi-platform graphical GNSS/GPS testing, diagnostic and UBX &copy; (u-blox &trade;) device configuration application written entirely in Python and tkinter. 
* Runs on any platform which supports a Python 3 interpreter (>=3.8) and tkinter (>=8.6) GUI framework, including Windows, MacOS, Linux and Raspberry Pi OS.
* Supports NMEA, UBX, RTCM3, NTRIP and SPARTN protocols.
* Capable of reading from a variety of GNSS data streams: Serial (USB / UART), Socket (TCP / UDP), binary datalog file/terminal capture and u-center recording.
* Configurable GUI with user-selectable and resizable widgets.
* Supports data logging in parsed, binary and hexadecimal formats.
* Supports track recording and display in GPX format.
* Can serve as an [NTRIP base station](#basestation) with a compatible receiver (e.g. ZED-F9P).
* While not intended to be a direct replacement, the application supports most of the UBX monitoring and configuration functionality in u-blox's Windows-only [u-center &copy;](https://www.u-blox.com/en/product/u-center) tool.

![full app screenshot ubx](https://github.com/semuconsulting/PyGPSClient/blob/master/images/app.png?raw=true)

*Screenshot showing mixed-protocol stream from u-blox ZED-F9P receiver, using PyGPSClient's [NTRIP Client](#ntripconfig) with a base station 26km to the west to achieve better than 2cm accuracy*

The application can be installed using the standard `pip` Python package manager - see [installation instructions](#installation) below.

---
## <a name="currentstatus">Current Status</a>

![Status](https://img.shields.io/pypi/status/PyGPSClient) 
![Release](https://img.shields.io/github/v/release/semuconsulting/PyGPSClient)
![Build](https://img.shields.io/github/actions/workflow/status/semuconsulting/PyGPSClient/main.yml?branch=master)
![Release Date](https://img.shields.io/github/release-date/semuconsulting/PyGPSClient)
![Last Commit](https://img.shields.io/github/last-commit/semuconsulting/PyGPSClient)
![Contributors](https://img.shields.io/github/contributors/semuconsulting/PyGPSClient.svg)
![Open Issues](https://img.shields.io/github/issues-raw/semuconsulting/PyGPSClient)

The PyGPSClient home page is at [PyGPSClient](https://github.com/semuconsulting/PyGPSClient). For a general overview of GNSS, DGPS, RTK, NTRIP and SPARTN technologies and terminology, refer to [GNSS Positioning - A Reviser](https://www.semuconsulting.com/gnsswiki/).

Sphinx API Documentation in HTML format is available at [https://www.semuconsulting.com/pygpsclient](https://www.semuconsulting.com/pygpsclient).

Contributions welcome - please refer to [CONTRIBUTING.MD](https://github.com/semuconsulting/PyGPSClient/blob/master/CONTRIBUTING.md).

[Bug reports](https://github.com/semuconsulting/PyGPSClient/blob/master/.github/ISSUE_TEMPLATE/bug_report.md) and [Feature requests](https://github.com/semuconsulting/PyGPSClient/blob/master/.github/ISSUE_TEMPLATE/feature_request.md) - please use the templates provided. For general queries and advice, post a message to one of the [PyGPSClient Discussions](https://github.com/semuconsulting/PyGPSClient/discussions) channels.

This is an independent project and we have no affiliation whatsoever with u-blox.

---
## <a name="instructions">Instructions</a>

1. To connect to a GNSS receiver via USB or UART port, select the device from the listbox, set the appropriate serial connection parameters and click 
![connect icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/usbport-1-24.png?raw=true). The application will endeavour to pre-select a recognised GNSS/GPS device but this is platform and device dependent. Press the ![refresh](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/iconmonstr-refresh-6-16.png?raw=true) button to refresh the list of connected devices at any point. `Rate bps` (baud rate) is typically the only setting that might need adjusting, but tweaking the `timeout` setting may improve performance on certain platforms. The `Msg Mode` parameter defaults to `GET` i.e., periodic or poll response messages *from* a receiver. If you wish to parse streams of command or poll messages being sent *to* a receiver, set the `Msg Mode` to `SET` or `POLL`. A default user-defined serial port can also be passed via the json configuration file setting `"userport_s":`, via environment variable `PYGPSCLIENT_USERPORT` or as a command line argument `--userport`.
1. To connect to a TCP or UDP socket, enter the server URL and port, select the protocol (defaults to TCP) and click 
![connect socket icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/ethernet-1-24.png?raw=true).
1. To stream from a previously-saved <a name="filestream">binary datalog file</a>, click 
![connect-file icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/binary-1-24.png?raw=true) and select the file type (`*.log, *.ubx, *.*`) and path. PyGPSClient datalog files will be named e.g. `pygpsdata-20220427114802.log`, but any binary dump of an GNSS receiver output is acceptable, including `*.ubx` files produced by u-center.
1. To disconnect from the data stream, click
![disconnect icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/iconmonstr-media-control-50-24.png?raw=true).
1. Protocols Shown - Select which protocols to display; NMEA, UBX and/or RTCM3 (NB: this only changes the displayed protocols - to change the actual protocols output by the receiver, use the [UBX Configuration Dialog](#ubxconfig)).
1. Position Format and Units - Change the displayed position (D.DD / D.M.S / D.M.MM / ECEF) and unit (metric/imperial) formats.
1. Map Type - Select from "world", "map" or "sat" (*"map" and "sat" types require an Internet connection and free [Mapquest API Key](#mapquestapi)*).
1. Show Unused Satellites - Include or exclude satellites that are not used in the navigation solution (e.g. because their signal level is too low) from the graph and sky view panels.
1. DataLogging - Turn Data logging in the selected format on or off. You will be prompted to select the directory into which timestamped log files are saved.
1. GPX Track - Turn track recording (in GPX format) on or off. You will be prompted to select the directory into which timestamped track files are saved.
1. To save the current configuration to a file, go to File..Save Configuration. **NB:** NTRIP and SPARTN client settings must be uploaded to the client handler (by clicking connect) before saving.
1. To load a saved configuration file, go to File..Load Configuration. The default configuration file location is `$HOME/pygpsclient.json`. **NB** Any active serial or RTK connection must be stopped before loading a new configuration.

1. [Socket Server / NTRIP Caster](#socketserver) facility with two modes of operation: (a) open, unauthenticated Socket Server or (b) NTRIP Caster (mountpoint = `pygnssutils`).
1. [UBX Configuration Dialog](#ubxconfig), with the ability to send a variety of UBX CFG configuration commands to u-blox GNSS devices. This includes the facility to add **user-defined commands or command sequences** - see instructions under [user-defined presets](#userdefined) below. To display the UBX Configuration Dialog (*only functional when connected to a UBX GNSS device via serial port*), click
![gear icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/iconmonstr-gear-2-24.png?raw=true), or go to Menu..Options..UBX Configuration Dialog.
1. [NTRIP Client](#ntripconfig) facility with the ability to connect to a specified NTRIP caster, parse the incoming RTCM3 data and feed this data to a compatible GNSS receiver (*requires an Internet connection and access to an NTRIP caster and local mountpoint*). To display the NTRIP Client Configuration Dialog (*requires Internet connection*), click
![ntrip icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/iconmonstr-antenna-4-24.png?raw=true), or go to Menu..Options..NTRIP Configuration Dialog.
1. [SPARTN Client](#spartnconfig) facility with the ability to configure an IP or L-Band SPARTN Correction source and SPARTN-compatible GNSS receiver (e.g. ZED-F9P) and pass the incoming correction data to the GNSS receiver (*requires an Internet connection and access to a SPARTN location service*). To display the SPARTN Client Configuration Dialog (*may require Internet connection*), click ![spartn icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/iconmonstr-antenna-3-24.png?raw=true), or go to Menu..Options..SPARTN Configuration Dialog.
1. [GPX Track Viewer](#gpxviewer) utility with elevation and speed profiles and track metadata (*requires an Internet connection and free 
[MapQuest API Key](https://developer.mapquest.com/user/login/sign-up)*). To display the GPX Track viewer, go to Menu..Options..GPX Track Viewer.


| User-selectable 'widgets' | To show or hide the various widgets, go to Menu..View and click on the relevant hide/show option. |
|---------------------------|---------------------------------------------------------------------------------------------------|
|![banner widget](https://github.com/semuconsulting/PyGPSClient/blob/master/images/banner_widget.png?raw=true)| Expandable banner showing key navigation status information based on messages received from receiver. To expand or collapse the banner or serial port configuration widgets, click the ![expand icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/iconmonstr-arrow-80-16.png?raw=true)/![expand icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/iconmonstr-triangle-1-16.png?raw=true) buttons. **NB**: some fields (e.g. hdop/vdop, hacc/vacc) are only available from proprietary NMEA or UBX messages and may not be output by default. The minumum messages required to populate all available fields are: NMEA: GGA, GSA, GSV, RMC, UBX00 (proprietary); UBX: NAV-DOP, NAV-PVT, NAV_SAT |
|![console widget](https://github.com/semuconsulting/PyGPSClient/blob/master/images/console_widget.png?raw=true)| Configurable serial console widget showing incoming GNSS, NTRIP and SPARTN data streams in either parsed, binary or tabular hexadecimal formats. Supports user-configurable color tagging of selected strings for easy identification. Color tags are loaded from the `"colortag_b":` value (`0` = disable, `1` = enable) and `"colortags_l":` list (`[string, color]` pairs) in your json configuration file (see example provided). NB: color tagging does impose a small performance overhead - turning it off will improve console response times at very high transaction rates.|
|![skyview widget](https://github.com/semuconsulting/PyGPSClient/blob/master/images/skyview_widget.png?raw=true)| Skyview widget showing current satellite visibility and position (elevation / azimuth). Satellite icon borders are colour-coded to distinguish between different GNSS constellations. For consistency between NMEA and UBX data sources, will display GLONASS NMEA SVID (65-96) rather than slot (1-24). |
|![graphview widget](https://github.com/semuconsulting/PyGPSClient/blob/master/images/graphview_widget.png?raw=true)| Graphview widget showing current satellite reception (carrier-to-noise ratio or cnr). Double-click to toggle legend. |
|![static map](https://github.com/semuconsulting/PyGPSClient/blob/master/images/staticmap.png?raw=true)| Static Mercator world map showing current global location. |
|![webmap widget](https://github.com/semuconsulting/PyGPSClient/blob/master/images/webmap_widget.png?raw=true)| Dynamic, scalable web map via MapQuest API (*requires an Internet connection and free [Mapquest API Key](#mapquestapi)*). Left Click +/- to zoom in or out. Right click +/- to zoom in or out to maximum extent. By default, the web map will automatically refresh every 60 seconds (*indicated by a small timer icon at the top left*). The default refresh rate can be amended by changing the `"mapupdateinterval":` value in your json configuration file, but **NB** the facility is not intended to be used for real-time navigation. Double-click anywhere in the map to immediately refresh. |
|![spectrum widget](https://github.com/semuconsulting/PyGPSClient/blob/master/images/spectrum_widget.png?raw=true)| Spectrum widget showing a spectrum analysis chart (*GNSS receiver must be capable of outputting UBX MON-SPAN messages*). Clicking anywhere in the spectrum chart will display the frequency and decibel reading at that point. Double-clicking anywhere in the chart will toggle the GNSS frequency band markers (L1, G2, etc.) on or off. |
|![sysmon widget](https://github.com/semuconsulting/PyGPSClient/blob/master/images/sysmon_widget.png?raw=true)| System Monitor widget showing device cpu, memory and I/O utilisation (*GNSS receiver must be capable of outputting UBX MON-SYS and/or MON-COMMS messages*). Tick checkbox to toggle between actual (cumulative) I/O stats and pending I/O. |
|![scatterplot widget](https://github.com/semuconsulting/PyGPSClient/blob/master/images/scatterplot_widget.png?raw=true)| Scatterplot widget showing variability in position reporting over time. Double-click to clear existing plot. |
|![rover widget](https://github.com/semuconsulting/PyGPSClient/blob/master/images/rover_widget.png?raw=true) | Rover widget plots the relative 2D position, track and status information for the roving receiver in a fixed or moving base / rover RTK configuration. Double-click to clear existing plot. (*GNSS rover receiver must be capable of outputting UBX NAV-RELPOSNED messages.*) |
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
1. Generic configuration panel (CFG-*) providing structured updates for a range of legacy CFG- configuration commands for pre-Generation 9+ devices. Note: 'X' (byte) type attributes can be entered as integers or hexadecimal strings e.g. 522125312 or 0x1f1f0000.
1. Configuration Interface widget (CFG-VALSET, CFG-VALDEL and CFG-VALGET) queries and sets configuration for [Generation 9+ devices](https://github.com/semuconsulting/pyubx2#configinterface) e.g. NEO-M9, ZED-F9P, etc.
1. Preset Commands widget supports a variety of preset and user-defined commands - see [user defined presets](#userdefined)

An icon to the right of each 'SEND' 
![send icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/iconmonstr-arrow-12-24.png?raw=true) button indicates the confirmation status of the configuration command; 
(pending i.e. awaiting confirmation ![pending icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/iconmonstr-time-6-24.png?raw=true), 
confirmed ![confirmed icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/iconmonstr-check-mark-8-24.png?raw=true) or 
warning ![warning icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/iconmonstr-warning-1-24.png?raw=true)). 

**Note:**
* The UBX protocol does not support synchronous command acknowledgement or unique confirmation IDs. Asynchronous command and poll acknowledgements and responses can take several seconds at high message transmission rates, or be discarded altogether if the device's transmit buffer is full (*txbuff-alloc error*). To ensure timely responses, try increasing the baud rate and/or temporarily reducing transmitted message rates using the configuration commands provided.
* A warning icon (typically accompanied by an ACK-NAK response) is usually an indication that one or more of the commands sent is not supported by your receiver.
* For presets that invoke a CFG-MSG command to set message rates, the port(s) to which the rate applies can be set via the `defaultport_s` configuration setting, which supports a comma-separated list of ports e.g. "USB", "USB,UART1" or "USB,I2C".

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

**Instructions:**

1. Enter the required NTRIP server URL (or IP address) and port (defaults to 2101). For services which require authorisation, enter your login username and password.
1. To retrieve the sourcetable, leave the mountpoint field blank and click connect (*response may take a few seconds*). The required mountpoint may then be selected from the list, or entered manually. Where possible, `PyGPSClient` will automatically identify the closest mountpoint to the current location.
1. For NTRIP services which require client position data via NMEA GGA sentences, select the appropriate sentence transmission interval in seconds. The default is 'None' (no GGA sentences sent). A value of 10 or 60 seconds is typical.
1. If GGA sentence transmission is enabled, GGA sentences can either be populated from live navigation data (*assuming a receiver is connected and outputting valid position data*) or from fixed reference settings entered in the NTRIP configuration panel (latitude, longitude, elevation and geoid separation - all four reference settings must be provided).
1. To connect to the NTRIP server, click ![connect icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/iconmonstr-media-control-48-24.png?raw=true). To disconnect, click ![disconnect icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/iconmonstr-media-control-50-24.png?raw=true).
1. If NTRIP data is being successfully received, the banner '**dgps:**' status indicator should change to 'YES' and indicate the age and reference station of the correction data (where available) ![dgps status](https://github.com/semuconsulting/PyGPSClient/blob/master/images/dgps_status.png?raw=true). Note that DGPS status is typically maintained for up to 60 seconds after loss of correction signal.
1. Some NTRIP services may output RTCM3 correction messages at a high rate, flooding the GUI console display. To suppress these messages in the console, de-select the 'RTCM' option in 'Protocols Shown' - the RTCM3 messages will continue to be processed in the background.

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

**FYI:** the SPARTN client utilises a new [`pyspartn`](https://github.com/semuconsulting/pyspartn) library. The `pyspartn.SPARTNReader` class will parse individual SPARTN messages from any binary stream containing *solely* SPARTN data e.g. an MQTT `/pp/ip` topic. The `pyspartn.SPARTNMessage` class is in Alpha and does not currently perform a full decode of all SPARTN protocol messages; it basically decodes just enough information to identify message type/subtype, payload length and other key metadata.

**Pre-Requisites:**

1. IP Correction (MQTT Client):

    - Internet access
    - Subscription to a suitable MQTT SPARTN location service e.g. u-blox / Thingstream PointPerfect IP or L-band, which should provide the following details:
      - Server URL e.g. `pp.services.u-blox.com`
      - Client ID (which can be stored in the `"mqttclientid_s":` json configuration file setting or via environment variable `MQTTCLIENTID`)
      - Encryption certificate (`*.crt`) and key (`*.pem`) files. If these are placed in the user's HOME directory using the location service's standard naming convention, PyGPSClient will find them automatically.
      - Region code - select from `us`, `eu`, `jp`, `kr` or `au`.
	  - Source - select from either `IP` or `L-Band` (*NB: the 'L-Band' MQTT mode provides decryption keys, Assist Now data and L-Band frequency information, but the correction data itself arrives via the L-Band receiver below*).
      - A list of published topics. These typically include:
	  	- `/pp/ip/region` - binary SPARTN correction data (SPARTN-1X-HPAC* / OCB* / GAD*) for the selected region, for IP sources only.
		- `/pp/ubx/mga` - UBX MGA AssistNow ephemera data for each constellation.
		- `/pp/ubx/0236/ip` or `/pp/ubx/0236/Lb` - UBX RXM-SPARTNKEY messages containing the IP or L-band decryption keys to be uploaded to the GNSS receiver.
		- `/pp/frequencies/Lb` - json message containing each region's L-band transmission frequency - currently `us` or `eu` (this is automatically enabled when `L-Band` is selected).
      - Python version <= 3.11. The [`paho-mqtt-python`](https://github.com/eclipse/paho.mqtt.python) library on which this function depends is not currently fully compatible with Python 3.12.beta releases.

2. L-BAND Correction (D9* Receiver):

    - SPARTN L-Band correction receiver e.g. u-blox NEO-D9S.
    - [Suitable Inmarsat L-band antenna](https://www.amazon.com/RTL-SDR-Blog-1525-1637-Inmarsat-Iridium/dp/B07WGWZS1D) and good satellite reception on regional frequency (NB: standard GNSS antenna may not be suitable).
    - Subscription to L-Band location service e.g. u-blox / Thingstream PointPerfect, which should provide the following details:
      - L-Band frequency
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
      - Current and Next IP or L-band decryption Keys in hexadecimal format.
	  - Valid From dates in YYYYMMDD format (keys normally valid for 4 week period).

**Instructions:**

### IP Correction Configuration (MQTT)

1. Enter your MQTT Client ID (or set it up beforehand as *.json configuration setting `"mqttclientid_s":` or via environment variable `MQTTCLIENTID`).
1. Select the path to the MQTT `*.crt` and `*.pem` files provided by the location service (PyGPSClient will use the user's HOME directory by default).
1. Select the required region and subscription mode (`IP` or `L-Band`).
1. Select the required topics:
    - IP - this is the raw SPARTN correction data as SPARTN-1X-HPAC* / OCB* / GAD* messages (required for IP; must be unchecked for L-band).
    - Assist - this is Assist Now data as UBX MGA-* messages.
    - Key - this is the SPARTN IP or L-band decryption keys as a UBX RXM-SPARTNKEY message.
1. To connect to the MQTT server, click ![connect icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/ethernet-1-24.png?raw=true). To disconnect, click ![disconnect icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/iconmonstr-media-control-50-24.png?raw=true).

### L-Band Correction Configuration (D9*)

1. To connect to the Correction receiver, select the receiver's port from the SPARTN dialog's Serial Port listbox and click ![connect icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/usbport-1-24.png?raw=true). To disconnect, click ![disconnect icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/iconmonstr-media-control-50-24.png?raw=true).
1. Select the required Output Port - this is the port used to connect the Correction receiver to the GNSS receiver e.g. UART2 or I2C.
1. If both Correction and GNSS receivers are connected to the same PyGPSClient workstation (e.g. via separate USB ports), it is possible to run the utility in Output Port = 'Passthough' mode, whereby the output data from the Correction receiver (UBX `RXM-PMP` messages) will be automatically passed through to the GNSS receiver by PyGPSClient, without the need to connect the two externally.
1. To enable INF-DEBUG messages, which give diagnostic information about current L-Band reception, click 'Enable Debug?'.
1. To save the configuration to the device's persistent storage (Battery-backed RAM, Flash or EEPROM), click 'Save Config?'.
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
1. SOCKET SERVER - an open, unauthenticated TCP socket server available to any socket client including, for example, another instance of PyGPSClient or the [`gnssdump` CLI utility](https://github.com/semuconsulting/pygnssutils#gnssdump). In this mode it will broadcast the host's currently connected GNSS data stream (NMEA, UBX, RTCM3). The default port is 50012.
2. NTRIP CASTER - a simple implementation of an authenticated NTRIP caster available to any NTRIP client including, for example, the PyGPSClient NTRIP Client facility or the [`gnssntripclient` CLI utility](https://github.com/semuconsulting/pygnssutils#gnssntripclient). Login credentials for the NTRIP caster are set via the `"ntripclientuser_s":` and `"ntripclientpassword_s":` settings in the *.json confirmation file (they can also be set via PyGPSClient command line arguments `--ntripuser`, `--ntrippassword`, or by setting environment variables `PYGPSCLIENT_USER`, `PYGPSCLIENT_PASSWORD`). Default settings are as follows: bind address: 0.0.0.0, port: 2101, mountpoint: pygnssutils, user: anon, password: password.

By default, the server/caster binds to the host address '0.0.0.0' (IPv4) or '::' (IPv6) i.e. all available IP addresses on the host machine. This can be overridden via the settings panel or a host environment variable `PYGPSCLIENT_BINDADDRESS`. A label on the settings panel indicates the number of connected clients, and the server/caster status is indicated in the topmost banner: open with no clients: ![transmit icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/iconmonstr-noclient-10-24.png?raw=true), open with clients: ![transmit icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/iconmonstr-transmit-10-24.png?raw=true).

**Pre-Requisites:**

1. Running in NTRIP CASTER mode is predicated on the host being connected to an RTK-compatible GNSS receiver (e.g. u-blox ZED-F9P) **operating in Base Station mode** (either `FIXED` or `SURVEY_IN`) and outputting the requisite RTCM3 message types (1005, 1077, 1087, 1097, 1127 and 1230). 
1. It may be necessary to add a firewall rule on the host and/or client machine to allow remote traffic on the specified address:port.

**Instructions:**

**SOCKET SERVER MODE**

1. Select SOCKET SERVER mode and (if necessary) enter the host IP address and port.
1. Check the Socket Server/NTRIP Caster checkbox to activate the server.
1. To stop the server, uncheck the checkbox.

**NTRIP CASTER MODE**

1. Select NTRIP CASTER mode and (if necessary) enter the host IP address and port.
1. An additional expandable panel is made available to allow the user to configure a connected RTK-compatible u-blox receiver (e.g. ZED-F9P) to operate in either `FIXED` or `SURVEY-IN` Base Station mode (*NB: parameters can only be amended while the caster is stopped*). If 'Configure Base Station' is checked, the selected configuration will be applied to the connected receiver once the caster is activated. 
1. NMEA messages can be suppressed by checking 'Disable NMEA'. A minimum set of UBX messages will be output in their place.
1. NTRIP client login credentials are set via the user and password fields. 
1. Check the Socket Server/NTRIP Caster checkbox to activate the caster.
1. To stop the caster, uncheck the checkbox.

### <a name="basestation">Base Station Configuration</a>

| Configuration Settings | Base Station Mode    |
|------------------------------------------------------|---------------------------------------------------------|
| ![basestation config](https://github.com/semuconsulting/PyGPSClient/blob/master/images/basestation_fixed.png?raw=true) | **FIXED**. In this mode, the known base station coordinates (*Antenna Reference Point or ARP*) are specified in either LLH or ECEF (X,Y,Z) format. The coordinates are pre-populated with the receiver's current navigation solution (if available), but these can (and normally should) be overridden with accurately surveyed values. If the coordinates are accepted, the UBX Fix status will change to `TIME ONLY` and the receiver will start outputting RTCM `1005` (*ARP location*) messages. |
| ![basestation config](https://github.com/semuconsulting/PyGPSClient/blob/master/images/basestation_svin.png?raw=true)  | **SURVEY-IN**. In this mode, the base station coordinates are derived from the receiver's current navigation solution, provided the prescribed level of accuracy is met within the specified survey duration. If the survey is successful, the UBX NAV-SVIN monitoring message will indicate `valid=1, active=0`, the UBX Fix status will change to `TIME ONLY` and the receiver will start outputting RTCM `1005` (*ARP location*) messages. |
| ![basestation config](https://github.com/semuconsulting/PyGPSClient/blob/master/images/basestation_off.png?raw=true)  | **DISABLED**. Disable base station operation. |

**NB:** To operate effectively as an RTK Base Station, antenna positioning is of paramount importance. Refer to the following links for advice:
- [u-blox GNSS Antennas Paper](https://www.ardusimple.com/wp-content/uploads/2022/04/GNSS-Antennas_AppNote_UBX-15030289.pdf)
- [Ardusimple GNSS Antenna Installation Guide](https://www.ardusimple.com/gps-gnss-antenna-installation-guide/)


---
## <a name="gpxviewer">GPX Track Viewer</a>

![gpxviewer screenshot](https://github.com/semuconsulting/PyGPSClient/blob/master/images/gpxviewer.png?raw=true)

*GPX Track Viewer screenshot*

The GPX Track Viewer can display any valid GPX file containing trackpoints (`<trkpt>..</trkpt>` elements). The map display requires a free [MapQuest API key](#mapquestapi). The Y axis scales will reflect the current choice of units (metric or imperial). Click ![refresh icon](https://github.com/semuconsulting/PyGPSClient/blob/master/src/pygpsclient/resources/iconmonstr-refresh-lined-24.png?raw=true) to refresh the display after any changes (e.g. resizing, zooming or change of units).

---
## <a name="installation">Installation</a>

In the following, `python3` & `pip` refer to the Python 3 executables. You may need to type 
`python` or `pip3`, depending on your particular environment. It is recommended that 
the Python 3 scripts (bin) and site_packages directories are included in your PATH 
(*most standard Python 3 installation packages will do this automatically if you select the 'Add to PATH' option during installation*).

NB: if you're installing onto a 32-bit Linux platform (e.g. Raspberry Pi OS 32), there may be additional installation steps - see note*⁵* below.

### Platform Dependencies

- Python >= 3.8*¹*
- Tk (tkinter) >= 8.6*²*
- Screen resolution >= 800 x 600; Ideally >= 1920 x 1080, though the main application window is resizeable and reconfigurable.

**All platforms**

*¹* It is highly recommended to use the latest official [Python.org](https://www.python.org/downloads/) installation package for your platform, rather than any pre-installed version.

**Windows 10 or later:**

Normally installs without any additional steps.

**MacOS 11 or later:**

*²* The version of Python supplied with most Apple MacOS platforms includes a [deprecated version of tkinter](https://www.python.org/download/mac/tcltk/) (8.5). Use an official [Python.org](https://www.python.org/downloads/) installation package instead.

**Linux (including Raspberry Pi OS):**

*³* Some Linux distributions may not include the necessary pip, tkinter or Pillow imaging libraries by default. They may need to be installed separately, e.g.:

```shell
sudo apt install python3-pip python3-tk python3-pil python3-pil.imagetk
```

*⁴* If you're compiling the latest version of Python 3 from source, you may also need to install tk-dev (or a similarly named package e.g. tk-devel) first. Refer to http://wiki.python.org/moin/TkInter for further details:

```shell
sudo apt install tk-dev
```

*⁵* On some 32-bit Linux platforms (e.g. Raspberry Pi OS 32), it may be necessary to [install Rust compiler support](https://www.rust-lang.org/tools/install) and some [additional build dependencies](https://cryptography.io/en/latest/installation/) in order to install the `cryptography` library which PyGPSClient depends on to decrypt SPARTN messages (see [Discussion](https://github.com/semuconsulting/PyGPSClient/discussions/83) and also [pyspartn cryptography installation notes](https://github.com/semuconsulting/pyspartn/tree/main/cryptography_installation#readme)):

```shell
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
sudo apt-get install build-essential libssl-dev libffi-dev python3-dev pkg-config
```

### User Privileges

To access the serial port on most Linux platforms, you will need to be a member of the 
`tty` and/or `dialout` groups. Other than this, no special privileges are required.

```shell
usermod -a -G tty myuser
```

### 1. Install using pip

![Python version](https://img.shields.io/pypi/pyversions/PyGPSClient.svg?style=flat)
[![PyPI version](https://img.shields.io/pypi/v/PyGPSClient.svg?style=flat)](https://pypi.org/project/PyGPSClient/)
![PyPI downloads](https://img.shields.io/pypi/dm/PyGPSClient.svg?style=flat)

The easiest way to install the latest version of `PyGPSClient` is with
[pip](http://pypi.python.org/pypi/pip/):

```shell
python3 -m pip install --upgrade pygpsclient
```

If required, `PyGPSClient` can also be installed into a virtual environment, e.g.:

```shell
python3 -m pip install --user --upgrade virtualenv
python3 -m virtualenv env
source env/bin/activate (or env\Scripts\activate on Windows)
(env) python3 -m pip install --upgrade pygpsclient
(env) ./env/bin/pygpsclient
...
deactivate
```

To run the application, if the Python 3 scripts (bin) directory is in your PATH, simply type (all lowercase): 
```shell
pygpsclient
```

`pygpsclient` also accepts optional command line arguments for a variety of configurable parameters. Type the following for help:
```shell
pygpsclient -h
```

If desired, you can add a shortcut to this command to your desktop or favourites menu.

Alternatively, if the Python 3 site_packages are in your PATH, you can type (all lowercase): 
```shell
python3 -m pygpsclient
```

**NB:** If the Python 3 scripts (bin) or site_packages directories are *not* in your PATH, you will need to add the fully-qualified path to `pygpsclient` in the commands above.

**Tip:** to find the site_packages location, type:
```shell
python3 -m pip show pygpsclient
``` 
and look for the `Location:` entry in the response, e.g.

- Linux: `Location: /home/username/.local/lib/python3.11/site-packages`
- MacOS: `Location: /Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages`
- Windows: `Location: c:\users\username\appdata\roaming\python\python311\lib\site-packages`

**Tip:** To create an application launcher for Linux distributions like Ubuntu, create a text file named `pygpsclient.desktop` with the following content (*edited for your particular environment*) and copy this to the `/home/user/.local/share/applications` folder, e.g.

```
[Desktop Entry]
Type=Application
Terminal=false
Name=PyGPSClient
Icon=/home/user/.local/lib/python3.11/site-packages/pygpsclient/resources/pygpsclient.ico
Exec=/home/user/.local/bin/pygpsclient
```

**Tip:** To create an application launcher for MacOS, use MacOS's Automator tool to create a "Run Shell Script" application and save this as `PyGPSClient.app`, e.g.

Shell: /bin/zsh
```
/Library/Frameworks/Python.framework/Versions/3.11/bin/pygpsclient
```

To assign an icon to this application, right-click on the `PyGPSClient` entry in the Applications folder, select "Get Info" and drag-and-drop the pygpsclient.ico image file from the site-packages folder (e.g. "/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages/pygpsclient/resources/pygpsclient.ico") to the default application icon at the top left.


### 2. Manual installation

The following Python libraries are required (these will be installed automatically if using pip to install PyGPSClient):

```shell
python3 -m pip install --upgrade Pillow pygnssutils pyserial pyspartn requests 
```

To install PyGPSClient manually, download and unzip this repository and run:

```shell
python3 -m /path_to_folder/foldername/pygpsclient
```

e.g. if you downloaded and unzipped to a folder named `PyGPSClient-1.3.26`, run: 

```shell
python3 -m /path_to_folder/PyGPSClient-1.3.26/pygpsclient
```

---
## <a name="mapquestapi">MapQuest API Key</a>

**Pre-Requisites:**

To use the optional dynamic web-based mapview or GPX Track Viewer facilities, you need to request and install a 
free [MapQuest API key](https://developer.mapquest.com/user/login/sign-up) (*no payment details required*).
The free edition of this API allows for up to 15,000 transactions/month (roughly 500/day) on a non-commercial basis.
For this reason, the map refresh rate is intentionally limited to 1/minute* to avoid exceeding the free transaction
limit under normal use. **NB:** this facility is *not* intended to be used for real time navigational purposes.

**Instructions:**

Once you have received the API key (a 32-character alphanumeric string), you can (in order of precedence):

1. Copy it to the `"mqapikey_s":` value in your json configuration file (see example provided).
2. Create an environment variable named `MQAPIKEY` (all upper case) and set this to the API key value. It is recommended 
that this is a User variable rather than a System/Global variable.
3. Pass it via command line argument `--mqapikey`.

*The web map refresh rate can be amended if required by changing the `mapupdateinterval_n:` value in your json configuration file.

---
## <a name="userdefined">User Defined Presets</a>

The UBX Configuration Dialog includes the facility to send user-defined UBX configuration messages or message sequences to the receiver. These can be set up by adding
appropriate comma-delimited message descriptions and payload definitions to the `"ubxpresets_l":` list in your json configuration file (see example provided). The message definition comprises a free-format text description (*avoid embedded commas*) 
followed by one or more [pyubx2 UBXMessage constructors](https://pypi.org/project/pyubx2/), i.e. 
1. message class as a string e.g. `CFG` (must be a valid class from pyubx2.UBX_CLASSES)
2. message id as a string e.g. `CFG-MSG` (must be a valid id from pyubx2.UBX_MSGIDS)
3. payload as a hexadecimal string e.g. `f004010100010100` (leave blank for null payloads e.g. most POLL messages)
4. mode as an integer (`1` = SET, `2` = POLL)

(payload as hex string can be obtained from a `UBXMessage` created using the [pyubx2 library](https://pypi.org/project/pyubx2/) thus: ```msg.payload.hex()```)

Multiple commands can be concatenated on a single line. Illustrative examples are shown below:

```
	"ubxpresets_l": [
		"Force HOT Reset (!!! Will require reconnection !!!), CFG, CFG-RST, 00000000, 1",
		"Force WARM Reset (!!! Will require reconnection !!!), CFG, CFG-RST, 00010000, 1",
		"Force COLD Reset (!!! Will require reconnection !!!), CFG, CFG-RST, ffff0000, 1",
		"Stop GNSS, CFG, CFG-RST, 00000800, 1",
		"Start GNSS, CFG, CFG-RST, 00000900, 1",
		"Enable NMEA UBX00 & UBX03 sentences, CFG, CFG-MSG, f100010100010100, 1, CFG, CFG-MSG, f103010100010100, 1",
		"Poll NEO-9 UART1/2 baud rates, CFG, CFG-VALGET, 000000000100524001005340, 2",
		"Poll NEO-9 Message Rates, CFG, CFG-VALGET, 00000000ffff9120, 2, CFG, CFG-VALGET, 00004000ffff9120, 2, CFG, CFG-VALGET, 00008000ffff9120, 2",
		"Set ZED-F9P RTCM3 MSGOUT Basestation, CFG, CFG-VALSET, 00010000c002912001cf02912001d4029120011b03912001d902912001060391200101039120018403912001, 1",
		"Set ZED-F9P to Survey-In Timing Mode Basestation, CFG, CFG-VALSET, 0001000001000320011100034070110100100003405a0000008b00912001, 1",
		"Poll Receiver Software Version, MON, MON-VER, , 2",
		"Poll Datum, CFG, CFG-DAT, , 2",
		"Poll GNSS config, CFG, CFG-GNSS, , 2",
		"Poll NMEA config, CFG, CFG-NMEA, , 2",
		"Poll Satellite-based Augmentation, CFG, CFG-SBAS, , 2",
		"Poll Receiver Management, CFG, CFG-RXM, , 2",
		"Poll RXM-SPARTN-KEY, RXM, RXM-SPARTN-KEY, , 2",
		"Poll RXM-COR, RXM, RXM-COR, , 2",
		"Poll Navigation Mode, CFG, CFG-NAV5, , 2",
		"Poll Expert Navigation mode, CFG, CFG-NAVX5, , 2",
		"Poll Geofencing, CFG, CFG-GEOFENCE, , 2",
		"Poll Timepulse, CFG, CFG-TP5, , 2",
		"Set NEO-M8T Timepulse to 8 MHz, CFG, CFG-TP5, 000100003200000000127a0000127a003200000032000000000000006f000000, 1",
	]
```

---
## <a name="cli">Command Line Utilities</a>

The `pygnssutils` library which underpins many of the functions in `PyGPSClient` also incorporates command line versions of these functions:

1. `gnssdump` CLI utility. This is essentially a configurable input/output wrapper around the [`pyubx2.UBXReader`](https://github.com/semuconsulting/pyubx2#reading) class with flexible message formatting and filtering options for NMEA, UBX and RTCM3 protocols.
1. `gnssserver` CLI utility. This implements a TCP Socket Server for GNSS data streams which is also capable of being run as a simple NTRIP Server.
1. `gnssntripclient` CLI utility. This implements a simple NTRIP Client which receives RTCM3 correction data from an NTRIP Server and (optionally) sends this to a
designated output stream.
1. `gnssmqttclient` CLI utility. This implements a simple SPARTN IP (MQTT) Client which receives SPARTN and UBX correction data from a SPARTN IP location service (e.g. u-blox / Thingstream PointPerfect) and (optionally) sends this to a designated output stream.
1. <a name="ubxsave">`ubxsave` CLI utility</a>. This saves a complete set of configuration data from any Generation 9+ u-blox device (e.g. NEO-M9N or ZED-F9P) to a file. The file can then be reloaded to any compatible device using the `ubxload` utility.
1. `ubxload` CLI utility. This reads a file containing binary configuration data and loads it into any compatible Generation 9+ u-blox device (e.g. NEO-M9N or ZED-F9P).
1. `ubxsetrate` CLI utility. A simple utility which sets NMEA or UBX message rates on u-blox GNSS receivers.

For further details, refer to the `pygnssutils` homepage at [https://github.com/semuconsulting/pygnssutils](https://github.com/semuconsulting/pygnssutils).

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

[![Discord general channel](https://img.shields.io/badge/contact-me-blue?logo=discord&logoColor=white)](https://discord.gg/BNKjSbYAmr)

`PyGPSClient` is maintained entirely by unpaid volunteers. It receives no funding from advertising or corporate sponsorship. If you find the utility useful, a small donation would be greatly appreciated!

[![Donations](https://www.paypalobjects.com/en_GB/i/btn/btn_donate_LG.gif)](https://www.paypal.com/donate/?business=UL24WUA4XHNRY&no_recurring=0&item_name=The+SEMU+GNSS+Python+libraries+are+maintained+entirely+by+unpaid+volunteers.+All+donations+are+greatly+appreciated.&currency_code=GBP)
