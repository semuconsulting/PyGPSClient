# PyGPSClient Release Notes

### RELEASE 1.5.10

FIXES:

1. Fix issue with type formatting in banner_frame.py #202 - thanks to @davidtlascelles for contribution.
1. Fix issue which would cause console to flicker between fixed and dynamic fonts when filtering data.
1. Fix issue with reset widget layout menu option not updating stored configuration.

ENHANCEMENTS:

1. Add support for Septentrio Mosaic X5 Base Station configuration in NTRIP Caster mode (supplementing the existing u-blox ZED-F9P/X20P and Quectel LG290P options). Note that the Mosaic X5 is configured via ASCII TTY commands - to monitor the responses, set the console protocol to "TTY" (remember to set it back to "RTCM" to monitor the RTCM3 output). Note also that the input (ASCII command) UART port may be different to the output (RTCM3) port - ensure you select the appropriate port(s) when configuring the receiver and monitoring the RTCM3 output.
1. Add base station location update - automatically updates NTRIP CASTER Survey-in base station location from RTCM 1005/6 message.
1. Chart Plot widget streamlined to reduce memory footprint and simplify CSV cut-and-paste (double-right-click) function.
1. Minor enhancements to ubx2preset() and nmea2preset() helper functions; added \examples\convert_ubx_preset.py example.
1. Dependency versions updated to incorporate latest fixes and enhancements.


### RELEASE 1.5.9

FIXES:

1. Fixes [#193](https://github.com/semuconsulting/PyGPSClient/issues/193)

ENHANCEMENTS:

1. Add support for Septentrio SBF binary GNSS protocol (*via the underlying `pysbf2` library*). If SBF protocol is selected, the console can now display parsed SBF data e.g. from Septentrio Mosaic X5. 
   - **NB:** At present, *either* UBX *or* SBF protocols can be selected, but not both at the same time.
   - **NB:** At present, with the exception of the SBF PVTGeodetic message, SBF data is not used to update the various user-selectable PyGPSClient widgets. This functionality may be enhanced in future releases.
   - **NB:** Serial connection must be disconnected before switching between SBF, UBX or TTY protocols.
1. Enhancements to TTY Command mode - will now work with a wider variety of TTY-configured devices, including Septentrio Mosaic X5 Receiver and Feyman IM19 IMU.
   - See [/examples/ttypresets_examples.py](https://github.com/semuconsulting/PyGPSClient/blob/master/examples/ttypresets_examples.py) for examples of ASCII TTY commands for a variety of GNSS and related devices.
   - **NB:** For Septentrio devices, send an 'Initialise Command Mode' string (`"SSSSSSSSSS\r\n"`) before sending further commands.
1. Delay checkbox added to TTY Preset Commands dialog - if checked, inserts small delay between individual TTY commands.

### RELEASE 1.5.8

FIXES:

1. Fix incorrect default value for "lbandclientunqword_s" - Fixes [#189](https://github.com/semuconsulting/PyGPSClient/issues/189)
1. Fix issue where datalog path was not being updated if datalogging was enabled at runtime.
1. Fix issue where settings frame was not updated after reloading configuration file at runtime.

ENHANCEMENTS:

1. Add receiver type option to NTRIP Caster mode - can now utilise either u-blox ZED-F9* or Quectel LG290P as Base Station receiver. NOTE THAT due to quirks in the LG290P firmware, setting Base Station mode with RTCM MSM 7 messages requires two successive restarts - you may see `WARNING - connection error` in the console during those restarts.
1. Add new IMU Monitor widget, capable of displaying IMU orientation (roll, pitch, yaw) and status from a variety of NMEA or UBX IMU data sources (e.g. ESF-ALG, HNR-ATT, NAV-ATT, NAV-PVAT, GPFMI).
1. Add TTY Command Dialog, allowing user to enter/select ASCII TTY commands to the connected serial device. Access via menu bar Options...TTY Commands.
1. RTCM3 messages types 1002 (GPS L1 observables) & 1010 (GLONASS L1 observables) added to NTRIP Caster configuration.
1. Make GUI update interval configurable via configuration setting "guiupdateinterval_f" - default is 0.5 seconds. NB: PyGPSClient may struggle on slower platforms (e.g. Raspberry Pi) if the GUI update interval is less than 0.2 seconds, though much lower intervals (<= 0.1 secs) can be accommodated on high-spec platforms.

### RELEASE 1.5.7

FIXES:

1. Fixes some typos in MQTT configuration settings (mqtt rather than mgtt) **NB:** recommend saving a new json configuration file for this version.

ENHANCEMENTS:

1. Refactor configuration settings - new `Configuration` class in `configuration.py`.
1. Streamline command line argument handling.
1. Add 'Decode SPARTN in console' checkbox to SPARTN config dialog.

### RELEASE 1.5.6

1. Enhancements to Dynamic Configuration Panel to allow POLL arguments to be entered for those poll commands that require them.
1. Enhancements to Preset Command Configuration Panel to allow user to specify CONFIRM option.
1. Improved error handling in Preset and Dynamic Configuration panels.
1. Minor improvements to color choices to improve contrast in Dark Mode.

### RELEASE 1.5.5

1. Add new NMEA Configuration panel, complementing and (partly) mirroring the existing UBX Configuration panel. The NMEA configuration panel supports GNSS receivers which can be configured via proprietary NMEA sentences. Currently the only supported receiver is the Quectel LG290P (or other command-compatible Quectel receivers). See [README](https://github.com/semuconsulting/PyGPSClient?tab=readme-ov-file#nmeaconfig) for details. User-defined preset NMEA commands may be added via the `nmeapresets_l` section of the PyGPSClient *.json configuration file.
1. Two new helper functions added `ubx2preset()` and `nmea2preset()`, to assist users in converting `UBXMessage` or `NMEAMessage` objects into strings which can be copied-and-pasted into the relevant sections of the *.json configuration file (`ubxpresets_l` and `nmeapresets_l`). See [README](https://github.com/semuconsulting/PyGPSClient?tab=readme-ov-file#userdefined) for details.

### RELEASE 1.5.4

1. Fix issue with GUI update facility not working for virtual environments.

### RELEASE 1.5.3

1. Fix issue with displaying final content of file in console after EOF condition.

### RELEASE 1.5.2

1. Fix logpath setting in config file - Fixes [#171](https://github.com/semuconsulting/PyGPSClient/issues/171)
1. Add support for pyubxutils.
1. Minor updates to vscode task configurations.

### RELEASE 1.5.1

1. Add new user-selectable and configurable "Chart" widget:
   - The Chart widget broadly emulates a multi-channel "oscilloscope", allowing the user to plot designated numeric data attribute values over time. By default, the number of channels is set to 4, but this can be manually edited by the user via the json configuration file setting `chartsettings_d["numchn_n"]`.
   - Any numeric attribute from any incoming NMEA, UBX, RTCM or SPARTN message can be plotted.
   - For each channel, user must specify the parsed data attribute name e.g. "hAcc" or "numSV".
   - User can optionally specify a message identity e.g. "GNGGA" or "NAV-PVT", in which case only the attribute from that message identity will be plotted.
   - Nested group attributes must include the full group index e.g. "cno_04". Alternatively, one of three wildcard characters '*', '+' or '-' can be appended, representing the average, minimum or maximum of the nested group values e.g. "cno\*" = (cno_01 + cno_02 + ... + cno_0n) / n ; "cno+" = max(cno_01, cno_02, ..., cno_0n).
   - X (time) and Y (value) axes are fully configurable.
   - Double-right-click will save the current chart data to the clipboard in CSV format.
   - The maximum number of datapoints per channel is configurable, though **NB** the practical maximum will be dependent on available platform memory and performance. 100,000 datapoints per channel is roughly equivalent to 3 MB in-memory data.
   - Chart settings will be saved to the json configuration file when "Save Configuration" is invoked.
   - Principally intended to provide a real-time view of incoming data trends over relatively short periods (minutes or hours).  *Analyses of much long time-series data (days or weeks) can probably be done more efficiently by saving a binary log of the incoming data and processing the data offline through a standard Python graphing tool like `matplotlib`*.
1. Add Check (for updates) on startup option to About dialog (NB: check requires internet connectivity)

### RELEASE 1.5.0

FIXES:

1. Fix NAV-SVINFO TypeError in ubx_hnadler.

ENHANCEMENTS:

1. Enhancements to spectrum widget:
   - Add snapshot facilty. Right-click anywhere in spectrum plot to capture current spectrum data, which will then be superimposed on the live spectrum data in a different color. Double-right-click to clear the snapshot. Intention is to help compare RF reception at different times and/or with different antenna configurations.
   - Add pgaoffset option. If selected, adds receiver PGA (programmable gain amplifier) gain to spectrum db axis.
   - vertical (db) axis range is now fixed - fixes previous vertical axis 'jumping'.
1. Enhance console color tagging.
1. Add baseline (where available) to banner dgps display.
1. Selected receiver serial port now included in saved json configuration file (NB: obviously won't work if the saved device is no longer available on the same port).
1. Minor interval enhancments to SPARTM data stream handling to reflect pyspartn>=1.05



### RELEASE 1.4.27

ENHANCEMENTS:

1. Further enhancements to scatterplot widget; add autorange, update interval, right-click to set fixed ref position, standard deviation in addition to average lat/lon, improved font scaling
1. Add Height Above Ellipsoid (HAE) to banner. 'sep' = HAE - hMSL.
1. Add double-click to copy contents of console to clipboard.

### RELEASE 1.4.26

ENHANCEMENTS:

1. Enhance scatterplot widget dynamic/fixed display options.

### RELEASE 1.4.25

ENHANCEMENTS:

1. Enhance scatterplot widget to extend zoom range to 0.01m and add optional fixed reference position. Delivers #160 and #161.
1. Minor improvements to datalogging and track recording.

### RELEASE 1.4.24

FIXES:

1. Fix NMEA GSV SV range handling - was omitting certain SVIDs.

### RELEASE 1.4.23

CHANGES:

1. Update minimum pgnssutils version to 1.1.4 - includes fix for https://github.com/semuconsulting/pygnssutils/issues/93.
1. Drop active support for Python 3.8 - now End of Life as at October 2024.
1. Add active support for Python 3.13 - now General Release as at October 2024.

### RELEASE 1.4.22

ENHANCEMENTS:

1. Add guided custom offline map import facility to Menu..Options..Import Custom Map. If the Python `rasterio` library is installed, the map bounding box can be automatically extracted from any georeferenced image (e.g. GeoTIFF - the default custom map image format). If the image is not georeferenced, or if `rasterio` is not installed, the bounding box must be entered manually. Invoke 'File..Save Configuration' to save the imported custom map settings to disk. **NB**: the `rasterio` library is *not* a mandatatory dependency for PyGPSClient and is not automatically installed with PyGPSClient.
1. Add preset commands for SEC message types.

### RELEASE 1.4.21

CHANGES:

1. Add support for chunked transfer-encoded NTRIP datastreams (requires `pygnssutils>=1.1.0`).
1. Add sponsorship link to About dialog.
1. Add "Enable UBX, Suppress NMEA' preset in UBX Configuration Dialog (enables UBX NAV-PVT, NAV-SAT and NAV-DOP and disables all NMEA messages).

FIXES:

1. Fix issue with mountpoint selection sometimes not showing information in NTRIP configuration dialog.
1. Fix issue with live coordinates not being presented properly in FIXED NTRIP caster dialog.

### RELEASE 1.4.20

FIXES:

1. Fixes typo in ubx_handler which affects NAV2-STATUS messages [#142](https://github.com/semuconsulting/PyGPSClient/issues/142)

CHANGES:

1. Minor improvements to settings frame appearance.
1. Add support for logging in underlying `pygnssutils` utilities (`gnssntripclient`, `gnssmqttclient`, `gnssserver`)
1. App `get_coordinates()` method now returns additional live gnss status information as dict.

### RELEASE 1.4.19

CHANGES:

1. Add modular logging facility. Logging configuration is defined globally in `__main__.py`, with global log level and destination set via the CLI `--verbosity` and `--logtofile` arguments. Subsidiary modules can use `self.logger = logging.setLogger(__name__)` and individual module log levels can be overridden using e.g. `self.logger.setLevel(DEBUG)`.

### RELEASE 1.4.18

FIXES:

1. Fix PUBX03 NMEA handling for Sky View - Fixes [#138](https://github.com/semuconsulting/PyGPSClient/issues/138)
1. Make PUBX03 SVID numbering consistent with GSV

### RELEASE 1.4.17

CHANGES:

1. Improved logging of data stream errors to console.
1. Internal performance streamlining - no functional changes.

### RELEASE 1.4.16

FIXES:

1. Fix handling of encrypted SPARTN payloads from MQTT or NTRIP sources.

### RELEASE 1.4.15

ENHANCEMENTS:

1. Updated functionality in pygnssutils and pyspartn libraries (see respective libraries for details).
1. Update application icon.

### RELEASE 1.4.14

ENHANCEMENTS:

1. Add default port checkboxes to UBX Preset config panel (these govern which port(s) any message rate commands apply to). The selection can be saved as configuration parameter `defaultport_s`.

FIXES:

1. Update ubxsetrate helper method to use CFG-VALSET command for newer (UBX protocol >= 23.01) devices, and the CFG-MSG command for older devices. This fixes an error ([Discussion #125](https://github.com/semuconsulting/PyGPSClient/discussions/125)) where the spectrum, system monitor and rover plot widgets would not display data for M10 and F10 UBX devices.

### RELEASE 1.4.13

ENHANCEMENTS:

1. Add support for SSL (port 443) connections in NTRIP client (requires pygnssutils>=1.0.21).
1. Add support for PointPerfect NTRIP SPARTN service.
1. Add RF Band data from MON-RF to UBX info panel.
1. Minor enhancements to custom offline map handling.

### RELEASE 1.4.12

FIXES:

1. Fix stream handler KeyError Fixes [#120](https://github.com/semuconsulting/PyGPSClient/issues/120).
1. Fix socket stream KeyError Fixes [#119](https://github.com/semuconsulting/PyGPSClient/issues/119).
1. Fix map_frame pylint warnings.

### RELEASE 1.4.11

ENHANCEMENTS:

1. Enhance custom offline map facility to allow multiple maps to be defined in config file. If Map Type of 'custom' is selected, PyGPSClient will automatically display custom map corresponding to current location or, if there is none, the default Mercator world map. Maps do not need to be contiguous. See README and example json configuration file for details.

### RELEASE 1.4.10

ENHANCEMENTS:

1. Add basic custom offline map facility to map view widget. See README for details.
1. Add support for SETPOLL msgmode (requires `pyubx2>=1.2.38`). This mode will automatically determine appropriate input mode (SET or POLL) for command or query UBX messages (NB: it will still be necessary to specify either output GET or input SETPOLL mode in the serial configuration panel when reading UBX data logs).
1. Add support for experimental UBXSimulator (*basic UBX GNSS serial device simulator*) from `pygnssutils`. To invoke, set `userport_s` setting to "ubxsimulator" and configure required NMEA/UBX data stream in local "ubxsimulator.json" file - see Sphinx documentation and example json file for further details.

FIXES:

1. Send empty datagram to UDP socket connections = thanks to @Williangalvani for contribution.

### RELEASE 1.4.9

CHANGES:

1. Update Rover widget for new pyubx2>=1.2.37 RELPOSNED payload definition.

### RELEASE v1.4.8

FIXES:

1. Fix parsing of command line arguments (NB: command line arguments and/or environment variables will now take temporary precedence over saved config file settings)
1. Fix 'unhashable type' error when first displaying mountpoint data in NTRIP client panel

### RELEASE v1.4.7

ENHANCEMENTS:

1. Add tkinter value to About dialog for reference.
1. Update Scatterplot widget to use planar approximation rather than haversine great circle formula at separations <= 50m

FIXES:

1. Fix relPosLength calculation in rover_frame.py
1. Fix typo in Scatterplot widget labels.

### RELEASE v1.4.6

ENHANCEMENTS:

1. Cater for older (pre NMEA 2.3) NMEA RMC message payloads - missing `posMode` attribute.
1. Minor improvements in skyview widget rendering to improve clarity

FIXES:

1. Fix IP6 invalid args issue #98
1. Fix GPX Track View facility handling of timestamps with microsecond elements.

### RELEASE v1.4.5

FIXES:

1. Fix vdop typo in nmea_handler [#94](https://github.com/semuconsulting/PyGPSClient/issues/94)

### RELEASE v1.4.4

ENHANCEMENTS:

1. Add serial or socket stream inactivity timeout setting on serial config panel.
1. Add public IP address to socket server/NTRIP caster config panel for ease of reference.
1. Add support for legacy NMEA "BD" (Beidou) talker IDs in satellite and graphview widgets.

### RELEASE v1.4.3

ENHANCEMENTS:

1. SPARTN MQTT configuration facilities enhanced to accommodate L-band as well as IP topics, including `/pp/frequencies/Lb`. As before, the utility will automatically upload the appropriate IP or L-band decryption keys and validity dates to the receiver (e.g. ZED-F9P) on receipt of an RXM-SPARTNKEY message (i.e. `/pp/ubx/0236/ip` or `/pp/ubx/0236/Lb` topic) from MQTT.
1. **Note that** a standard PointPerfect L-Band subscription does NOT provide access to the `/pp/ip/*` (SPARTN data) topics, the assumption being that the necessary correction data will arrive via RXM-PMP messages from the L-band receiver (e.g. NEO-D9S). Uncheck the IP topic checkbox before connecting to an L-band MQTT source.
1. Add support for MQTT SPARTN "jp" region.
1. Other minor improvements in usability.
1. Changes require `pygnssutils>=1.0.15`.

### RELEASE v1.4.2

ENHANCEMENTS:

1. New Rover widget which plots the relative 2D position, track and status information for the roving receiver antenna in a fixed or moving base / rover RTK configuration. Double-click to clear existing plot. (*GNSS rover receiver must be capable of outputting UBX NAV-RELPOSNED messages.*)

FIXES:

1. Fix issue where some preset commands were not being recorded in the UBX recorder facility.

### RELEASE v1.4.1

ENHANCEMENTS:

1. Configuration *.json file save procedure enhanced to save and restore all user-configurable settings parameters, including those for NTRIP and SPARTN Clients. NB: changes require `pygnssutils>=1.0.13`. Order of precedence for config settings is:
    1. *.json config file (all user-configurable settings)
    1. CLI keyword argument (where available)
    1. Environment Variable (where used)
    
   **NB:** Configuration file element names have been changed to facilitate type validation (e.g. "sockclientport" is now "sockclientport_n" to signify it takes an integer value). Some older names will no longer be recognised. It is recommended to save a new copy of the default configuration as `pygpsclient.json`.
1. Add scrollbars to settings frame to allow better navigation on low-res displays.
1. Add EBNO & FEC Bits values to SPARTN L-Band configuration panel to help monitor signal quality.
1. Minor enhancements to banner position formatting.
1. Add IPv6 flowinfo & scopeid fields to NTRIP Client configuration panel.
1. Minor improvements to documentation and code comments.

FIXES:

1. Fix AttributeError if opening with older json configuration file.


### RELEASE v1.4.0

ENHANCEMENTS:

1. Add NTRIP caster credentials as command line arguments.
1. Add version update facility to About dialog.
1. Add Survey-in countdown display to NTRIP caster panel.
1. Add ECEF position format to banner.
1. Add display support for NAVIC GNSS constellation in graph and skyviews (already fully supported in pyubx2).
1. Add display support for NMEA UBX,03 proprietary message.

CHANGES:

1. Internal streamlining of stream_handler and settings_frame.

### RELEASE v1.3.30

ENHANCEMENTS:

1. Enhance [NTRIP Caster](https://github.com/semuconsulting/PyGPSClient#socketserver) facility to include ability to [automatically configure a ZED-F9P](https://github.com/semuconsulting/PyGPSClient#basestation) (or similar) receiver to operate in Base Station mode (either Survey-In or Fixed).
1. Enhance Socket Server facility to add host (bind) address, which is then stored in config file (can be derived from environment variable `PYGPSCLIENT_BINDADDRESS`).
1. Enhance socket reader IPv6 support.

### RELEASE v1.3.29

ENHANCEMENTS:

1. Enhance webmap widget to display either world (static), map (web), or satellite (web) basemap.
1. Enhance stream handler to allow outbound writes to socket as well as USB/UART streams (requires pyubx2 >= 1.2.28). Allows users to configure or poll a remote receiver over TCP, *provided* the receiver's TCP client at the other end supports this.
1. Update dependency minimum versions for pygnssutils and pyspartn.

FIXES:

1. Fix right-click zoom function on mapview to work with Windows.
1. Connection error with IPv6 socket connections.

### RELEASE v1.3.28

ENHANCEMENTS:

1. Enhancement to *.txt config file upload in UBX Configuration panel to expand support for u-blox devices other than F9\* series.
1. Enhancement to SPARTN configuration panel to allow user to amend receiver DGNSS Timeout value (can be useful when using L-Band SPARTN sources).
1. Add IPv6 support for TCP/UDP connections.
1. Add Zoom in/out icons to webmap widget and remove slider from main settings panel.

FIXES:

1. Fix issue with PIL.ANTIALIAS keyword no longer being supported; stopped static map being loaded.

### RELEASE v1.3.27

1. Remove redundant config file readers - all saved config should now be placed in *.json configuration file.
1. Remove Python 3.7 support (now end of life)

### RELEASE v1.3.26

ENHANCEMENTS:

1. Add System Monitor widget which displays device system status in bar chart format (cpu, memory and I/O utilisation, temperature, boot state, etc.), for those u-blox devices that support MON-SYS and MON-COMMS message types. To access, select Menu..View..Show System Monitor.

![Sysmon widget](./images/sysmon_widget.png)

1. Add IPv6 support to NTRIP configuration panel (requires pygnssutils >= 1.0.8).
1. Add double-click actions to widgets;

   - double-click graph widget to toggle legend
   - double-click spectrum widget to toggle legend and L-Band markers
   - double-click map widget to refresh web map immediately
   - double-click scatterplot widget to reset plot

CHANGES:

1. Update min pygnssutils version to 1.0.9

### RELEASE v1.3.25

ENHANCEMENTS:

1. UBX Configuration Load/Save/Record facility will now accept u-center *.txt configuration files (**for Generation 9+ devices only**) as well as binary *.ubx files. Thanks for @wdwalker in #66 for suggestion. Compatible configuration files for ZED-F9P devices can be found, for example, on the [ArduSimple web site](https://www.ardusimple.com/configuration-files/). FYI: Generation 9+ u-center *.txt configuration files contain hexadecimal representations of MON-VER and CFG_VALGET UBX messages, e.g.:
    ```
    MON-VER - 0A 04 DC 00 45 ...
    CFG-VALGET - 06 8B 44 01 ...
    CFG-VALGET - 06 8B 44 01 ...
    ```
    The CFG-VALGET messages are converted into CFG-VALSET commands for uploading to the receiver. 
1. New module `widgets.py` containing a configuration data dictionary for all user-selectable widgets. Intention is to make it easier to add and configure new widgets.

FIXES:

1. Fix error when updating NTRIP Client dialog status (e.g. with 'unauthorized' errors)

CHANGES:

1. Bandit security analysis added to VS Code and GHA workflows.
1. Update min pygnssutils version to 1.0.7
1. Internal updates to VSCode and GHA workflows.

### RELEASE v1.3.24

FIXES:

1. Fixes #63 ValueError if pygpsclient started with no default config file

### RELEASE v1.3.23

CHANGES:

1. Improved legibility in 'Light' and 'Dark' O/S modes by removing hard-coded Entry widget background colors. Fixes [#60](https://github.com/semuconsulting/PyGPSClient/issues/60). (*NB: the PyGPSClient application itself retains its 'dark' main widget GUI styling and there are no current plans to introduce user-selectable color themes.*)
1. Minimum pygnssutils version updated to 1.0.6.
1. Minor fixes to configuration load status messages.


### RELEASE v1.3.22

ENHANCEMENTS:

1. Add facility to save and reload PyGPSClient application configuration file in json format. Covers:
    * frm_settings dialog values (protocols, console format, degrees format, units, etc.)
    * widget configuration (which widgets are visible or hidden)
    * user-defined GNSS and SPARTN serial ports
    * API keys
    * console color tagging values
    * user-defined UBX command presets
1. Will look for default config file `$HOME/pygpsclient.json` on startup - a sample file is provided.
1. Add ability to specify a custom config file via command line argument `-C`, `--config`.
1. Application config file obviates need for discrete `colortags` and `mqapikey` files. These will be deprecated in a subsequent version.
1. Enhance spectrum view with optional additional GNSS frequency band markers.
1. Minor improvements to spectrum widget to show GLONASS & Galileo frequency band markers in addition to GPS.
1. Minor improvements to automated widget positioning and resizing.

### RELEASE v1.3.21

ENHANCEMENTS:

1. Various minor tweaks to improve widget legibility, contrast and positioning at various scales.
1. Correctly cater for up to 3 rows of optional widgets.
1. Add color helper functions rgb2str, str2rgb, col2contrast.
1. Address minor pylint advisories.
1. Added 'Update Toolchain' task to VS Code workflow.


### RELEASE v1.3.20

ENHANCEMENTS:

1. New Scatter Plot widget added, showing variability in position reporting over a period of time. Access via View..Show/Hide Scatter Plot. Thanks to @nmichaels-qualinx for contribution.

CHANGES:

1. Project migrated to pyproject.toml build mechanism and standard project structure (/src). The setuptools build backend has been retained.
2. Internal build and test workflow streamlined.

### RELEASE v1.3.19

FIXES:

1. Fix glitch which caused banner hAcc/vAcc values to be garbled if using imperial units.

ENHANCEMENTS:

1. Facility to store L-Band correction receiver (D9S) configuration to persistent storage (BBR, Flash, EEPROM) added to SPARTN Configuration Panel.

### RELEASE v1.3.18

FIXES:

1. Fix to GNSS SPARTN key config upload. Fixes [#44](https://github.com/semuconsulting/PyGPSClient/issues/44)

ENHANCEMENTS TO SPARTN CLIENT:

1. SPARTN dialog no longer needs to be kept open while IP or L-Band client is running.
1. Use `pygnssutils.GNSSMQTTClient` class in `pygnssutils>=1.0.4` rather than embedded `MQTTHandler` class. MQTT client also now available as a command line utility `gnssmqttclient` - see https://github.com/semuconsulting/pygnssutils#gnssmqttclient for details.
1. Enhance and streamline SPARTN client functionality.
1. Minor improvements to SPARTN client error handling.
1. Add ability to load SPARTN config from JSON file.

OTHER ENHANCEMENTS:

1. Auto-enable MON-SPAN message if Spectrum View widget is opened.
1. Various comment and docstring improvements.


### RELEASE v1.3.17

FIXES:

1. Cater for updates in pynmeagps to fix typo in UBX00 message - PUBX00 message provideds TDOP rather than PDOP. 

### RELEASE v1.3.16

ENHANCEMENTS:

1. Add SPARTN Configuration utility, accessed via Menu..Options..SPARTN Configuration Dialog and button in Settings panel, offering:
    - IP (MQTT) SPARTN correction source configuration.
    - L-Band (D9*) SPARTN correction receiver configuration.
    - GNSS Receiver (F9*) configuration.
2. Supports both IP and L-Band SPARTN RTK correction sources to achieve centimetre-level accuracy.
3. NB: reception and decryption of SPARTN correction data may require a paid subscription to a SPARTN location service e.g. u-blox PointPerfect. Check terms and conditions before subscribing (*this project has no affiliation whatsoever to such services*).

See README for details.

### RELEASE v1.3.15

ENHANCEMENTS:

1. New GPX Track Viewer facility added, accessed via Menu..Options..GPX Track Viewer. Displays track on dynamic web page alongside elevation and speed profiles (where available) and key metadata. Dialog is fully resizeable. Click folder icon to load a GPX file. Click redraw icon to redraw track and profile at any time.

### RELEASE v1.3.14

ENHANCEMENTS:

1. New `CFG Configuration Load/Save/Record` facility added to UBX Configuration panel. This allows users to 'record' any configuration commands (UBX CFG messages) sent to a device to an internal memory array, and subsequently save this array in a binary file. Saved files can be reloaded and the messages replayed to any compatible device. This provides a means to easily reproduce a given sequence of configuration commands, or copy a saved configuration between compatible devices.
2. Msg Mode listbox added to serial configuration dialog. Defaults to 'GET' (periodic or poll response message types) but can be set to 'SET' or 'POLL' to read serial or file streams containing command or poll message types. 
3. Internal code streamlining for widget selection and arrangement. New reset layout option added.

### RELEASE v1.3.13

ENHANCEMENTS:

1. New spectrum analysis widget added. Displays spectrum data from MON-SPAN messages. To turn widget on or off, select Menu...View..Show/Hide Spectrum.

FIXES:

1. Fix attribute typo which affected processing of HNR-PVT message types.

### RELEASE v1.3.12

CHANGES:

1. Minimum pygnssutils version updated to v1.0.0.
2. shields.io build status badge URL updated.
3. Image links in README.md updated to absolute links (so images show on PyPi).

No other functional changes.

### RELEASE v1.3.11

ENHANCEMENTS:

1. Python 3.11 support added to setup.py. No other functional changes.

### RELEASE v1.3.10

ENHANCEMENTS:

1. Add provision to pass user-defined serial port designator via command line keyword argument port or environment variable PYGPSCLIENT_USERPORT.

e.g.

```shell
pygpsclient port=/dev/tty12345
```
or
```shell
export PYGPSCLIENT_USERPORT="/dev/tty12345"
pygpsclient
```

Any user-defined port will appear in the serial port listbox as the first preselected item.

### RELEASE v1.3.9

ENHANCEMENTS:

1. GGA position source radio button added to NTRIP Client dialog - allows user to select from live receiver or fixed reference (previously PyGPSClient would automatically use receiver position if connected or fixed reference if not).

### RELEASE v1.3.8

ENHANCEMENTS:

1. New CFG-* Other Configuration command panel added to UBX Configuration panel. Provides structured inputs for a range of legacy CFG commands. **NB:** For Generation 9+ devices, legacy CFG commands are deprecated in favour of the CFG-VALGET/SET/DEL Configuration Interface commands in the adjacent panel.
2. When a legacy CFG command is selected from the CFG-* listbox, a POLL request is sent to the device to retrieve the current settings; these are then used to populate a series of dynamically generated Entry widgets. The user can amend the values as required and send the updated set of values as a SET message to the device. After sending, the current values will be polled again to confirm the update has taken place. **NB:** this mechanism is dependent on receiving timely POLL responses. Note caveats in README re. optimising POLL response performance.
3. For the time being, there are a few constraints with regard to updating certain CFG types, but these will hopefully be addressed in a future update as and when time permits. The `pyubx2` library which underpins`PyGPSClient` fully supports *ALL* CFG-* commands.
4. The new panel can be enabled or disabled using the `ENABLE_CFG_OTHER` boolean in `globals.py`.

### RELEASE v1.3.7

ENHANCEMENTS:

1. "Parsed + Tabular Hex" option added to data logger.
2. "Check for Updates" function enhanced in About dialog box - works better on Linux.
3. Min 'pygnssutils' version updated to 0.3.1 - fixes issues with some NTRIP 2 caster handling.

### RELEASE v1.3.6

CHANGES:

1. Internal refactoring to use common pygnssutils utility classes, resulting in signficant de-duplication of code. No functional changes.

### RELEASE v1.3.5

ENHANCEMENTS:

1. **New BETA Socket / NTRIP Server feature**. Capable of operating in two modes - either (a) as an open, unauthenticated TCP socket server, or (b) as an authenticated NTRIP server.
3. In open socket server mode, the output socket stream can be accessed by any TCP socket client capable of parsing raw GNSS data, including another instance of PyGPSClient or `gnssdump` (the CLI utility installed with `pyubx2`) running on another machine (*assuming the traffic is permitted through any firewalls*).
4. In NTRIP server mode, the socket stream can be accessed by any authenticated NTRIP client. The sourcetable contains a single entry corresponding to the PyGPSClient host. The server authentication credentials are set via two environment variables `NTRIPCASTER_USER` and `NTRIPCASTER_PASSWORD`.
5. In either mode, the maximum number of clients is arbitrarily limited to 5. A label on the settings panel indicates the number of connected clients - this turns red when the maximum has been reached.
6. The socket host address is `0.0.0.0` (i.e. binds to all available IP addresses on the host machine). The socket port defaults to `50010` but is configurable via the settings panel (`2101` is the convention for NTRIP servers but is not mandated). 
7. The default configuration for the socket server is set in `globals.py` as `SOCKSERVER_HOST`, `SOCKSERVER_PORT` and `SOCKSERVER_MAX_CLIENTS`.

### RELEASE v1.3.4

ENHANCEMENTS:

1. Enhancement to NTRIP client - will now automatically identity and select the closest mountpoint in the sourcetable (among those mountpoints which provide location information, and assuming current location is known approximately). Selection can be overridden.
2. hacc/vacc display on banner increased to 3dp (limit of reliability). **NB:** in order to see hacc/vacc readings, you will need to be receiving messages which provide this data e.g. NMEA PUBX-00 or UBX NAV-PVT, NAV-POSLLH. It *cannot* be reliably inferred from hdop/vdop.
3. Minor internal refactoring to improve performance and resilience of NTRIP client.

### RELEASE v1.3.3

FIXES:

1. Fix old reference to `enqueue()` method in serial handler.

### RELEASE v1.3.2

CHANGES:

1. Internal refactoring of `serial_handler.py` and `socket_handler.py` into single `stream_handler.py`.
2. Minimum versions of `pyubx2` and `pynmeagps` updated to 1.2.9 and 1.0.11 respectively.

FIXES:

1. Preset message rate commands now set rates on ALL ports including UART2 (UART2 was previously omitted).

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

