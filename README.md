# PyGPSClient

PyGPSClient is a free, open source graphical GPS testing and diagnostic client application written entirely in Python and tkinter.

![full app](/images/all_widgets.png)

The application runs on any platform which supports a Python3 interpreter (>=3.6) and tkinter (>=8.6) GUI framework, 
including Windows, MacOS, Linux and Raspberry Pi OS. It displays location and diagnostic data from any NMEA or UBX (u-blox &copy;) 
compatible GPS device over a standard serial (UART) or USB port, *in addition to* providing a small but useful subset of the 
configuration functionality in u-blox's Windows-only [u-center](https://www.u-blox.com/en/product/u-center) tool.

Originally designed as a platform-agnostic evaluation, development and educational tool for the [u-blox NEO-6M series](https://www.u-blox.com/en/product/neo-6-series) GPS modules, and in particular the [Makerhawk Hobbyist GPS Board](https://www.amazon.co.uk/MakerHawk-Microcontroller-Compatible-Navigation-Positioning/dp/B0783H7BLW), it has evolved
into a more general purpose multi-platform NMEA / UBX GPS client.

## Features:

1. Supports both NMEA and UBX protocols. It uses the existing pynmea2 library for NMEA parsing and 
implements a **[new pyubx2 library](https://github.com/semuconsulting/pyubx2)** for UBX parsing. 
1. Configurable GUI with selectable and resizeable widgets.
1. Expandable banner widget showing key navigation information.
1. Serial console widget showing either raw or parsed data stream.
1. Skyview widget showing current satellite visibility and position (elevation / azimuth).
1. Graphview widget showing current satellite reception (signal-to-noise ratio).
1. Mapview widget with location marker, showing either a static Mercator world map, or an optional dynamic web-based map downloaded via a MapQuest API (requires an Internet connection and free 
[MapQuest API Key](https://developer.mapquest.com/plan_purchase/steps/business_edition/business_edition_free/register)).
1. **WORK IN PROGRESS** UBX Configuration Dialog (under Menu...Options), with the ability to send UBX configuration messages to u-blox GPS devices e.g. NMEA and UBX message filters. This includes the facility to add **user-defined preset configuration messages** - see instructions under [installation](#installation) below.

![banner widget](/images/banner_widget.png)
![sats & mercator widget](/images/sats_mercator_widget.png)
![ubxconfig widget](/images/ubxconfig_widget.png)

This is a personal project and I have no affiliation whatsoever with u-blox &copy;, Makerhawk &copy; or MapQuest &copy;.

#### Glossary of Terms

* utc - coordinated universal time 
* siv - satellites in view
* sip - satellites used in position solution
* dop - [dilution of precision](https://gisgeography.com/gps-accuracy-hdop-pdop-gdop-multipath/) (pdop - position, hdop - horizontal, vdop - vertical)
* acc - accuracy of location in real units (hacc - horizontal, vacc - vertical)

### Current Status

![Release](https://img.shields.io/github/v/release/semuconsulting/PyGPSClient?include_prereleases)
![Release Date](https://img.shields.io/github/release-date-pre/semuconsulting/PyGPSClient)
![Last Commit](https://img.shields.io/github/last-commit/semuconsulting/PyGPSClient)
![Contributors](https://img.shields.io/github/contributors/semuconsulting/PyGPSClient.svg)
![Open Issues](https://img.shields.io/github/issues-raw/semuconsulting/PyGPSClient)

Alpha. Main application and widgets are fully functional for both NMEA and UBX protocols. The UBX configuration dialog is a work in progress and additional configuration functionality will be added in due course. Needs slightly more robust exception handling in a few areas.

Constructive feedback welcome.

## <a name="installation">Installation</a>

![Python version](https://img.shields.io/pypi/pyversions/PyGPSClient.svg?style=flat)

In the following, `python` refers to the python 3 executable (this application will **not** run under python 2). You may need to type `python3`, depending on your particular environment.

### Dependencies

See [requirements.txt](requirements.txt).

On Windows and MacOS, pip, tkinter and the necessary imaging libraries are generally packaged with Python.  On some Linux distributions like Ubuntu 18+ and Raspberry Pi OS, they may need to be installed separately, e.g.:

`sudo apt-get install python3-pip python3-tk python3-pil python3-pil.imagetk`

The following python libraries are required (these will be installed automatically if using pip):

`python -m pip install pyubx2 pyserial pynmea2 Pillow requests`

### User Privileges

To access the serial port on most linux platforms, you will need to be a member of the 
`tty` and `dialout` groups. Other than this, no special privileges are required.

### 1. Install using pip

[![PyPI version](https://img.shields.io/pypi/v/PyGPSClient.svg?style=flat)](https://pypi.org/project/PyGPSClient/)
![PyPI downloads](https://img.shields.io/pypi/dm/PyGPSClient.svg?style=flat)

The easiest way to install PyGPSClient is via [pip](http://pypi.python.org/pypi/pip/):

`python -m pip PyGPSClient`

If the python3 site_packages are in your path, simply run `python -m pygpsclient`.

If not, run `python -m \full_path_to_site_packages\pygspclient`.

### 2. Manual installation

To install and run, download and unzip this repository and run:

`python -m /path_to_folder/foldername/pygpsclient`

e.g. if you downloaded and unzipped to a folder named `PyGPSClient-0.1.6`, run: 

`python -m /path_to_folder/PyGPSClient-0.1.6/pygpsclient`.

### MapQuest API Key

To use the optional dynamic web-based mapview facility, you need to request and install a 
[MapQuest API key](https://developer.mapquest.com/plan_purchase/steps/business_edition/business_edition_free/register).
The free edition of this API allows for up to 15,000 transactions/month (roughly 500/day) on a non-commercial basis.
For this reason, the map refresh rate is intentionally limited to 1/minute to avoid exceeding the free transaction
limit under normal use. **NB:** this application is *not* intended to be used for real time navigational purposes.

Once you have received the API key (a 32-character alphanumeric string), copy it to a file named `mqapikey` (lower case, 
no extension) and place this file in the user's home directory.

### User Defined Presets

The UBX Configuration Dialog includes the facility to add user-defined preset UBX configuration messages. These can be set up by adding
appropriate message descriptions and payload definitions to a file named `ubxpresets` (lower case, no extension), and then placing this 
file in the user's home directory. An illustrative user preset file is given below - the payload definition follows the format passed
to a [pyubx2 UBXMessage constructor](https://pypi.org/project/pyubx2/) i.e. `msgClass, msgID, payload`:

```
<--------- description -------->: <----------------- UBXMessage Constructor --------------->

USER CFG-MSG Add RMC to messages: 'CFG', 'CFG-MSG', b'\xf0\x04\x01\x01\x01\x00\x01\x00', SET
USER CFG-MSG Add VTG to messages: 'CFG', 'CFG-MSG', b'\xf0\x05\x01\x01\x01\x00\x01\x00', SET
```

## License

![License](https://img.shields.io/github/license/semuconsulting/PyGPSClient.svg)

BSD 3-Clause License ("BSD License 2.0", "Revised BSD License", "New BSD License", or "Modified BSD License")

Copyright (c) 2020, SEMU Consulting
All rights reserved.

Application icons from [iconmonstr](https://iconmonstr.com/) &copy;.

## Author Information

semuadmin@semuconsulting.com
