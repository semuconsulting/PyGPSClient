"""
widget_state.py

Global constants, strings and dictionaries used to
maintain the state of the various user-selectable
widgets in the main container frame.

To add a new widget to PyGPSClient:
1. Create a new frame class `widgetname_frame.py`. The frame class
should implement `init_frame()` and `update_frame()` functions.
2. If the widget requires certain UBX messages to be enabled,
implement an `enable_messages(status)` function.
3. Add an entry to the foot of the widget_state dictionary.
4. If the widget requires data not already in the `app.gnss_status`
data dictionary, add the requisite data items to the `GNSSStatus`
class definition and update `ubx_handler` to populate them.

Created on 30 Apr 2023

:author: semuadmin
:copyright: SEMU Consulting © 2020
:license: BSD 3-Clause
"""

from pygpsclient.banner_frame import BannerFrame
from pygpsclient.console_frame import ConsoleFrame
from pygpsclient.globals import CLASS, FRAME
from pygpsclient.graphview_frame import GraphviewFrame
from pygpsclient.map_frame import MapviewFrame
from pygpsclient.rover_frame import RoverFrame
from pygpsclient.scatter_frame import ScatterViewFrame
from pygpsclient.settings_frame import SettingsFrame
from pygpsclient.skyview_frame import SkyviewFrame
from pygpsclient.spectrum_frame import SpectrumviewFrame
from pygpsclient.status_frame import StatusFrame
from pygpsclient.sysmon_frame import SysmonFrame

COLSPAN = "colspan"
DEFAULT = "def"
HIDE = "Hide"
MAXCOLSPAN = 4  # max no of widget columns
MAXROWSPAN = 4  # max no of widget rows
MENU = "men"
ROWSPAN = "rowspan"
SHOW = "Show"
STICKY = "sty"
VISIBLE = "vis"
WDGBANNER = "Banner"
WDGCONSOLE = "Console"
WDGLEVELS = "Levels"
WDGMAP = "Map"
WDGROVER = "Rover Plot"
WDGSATS = "Satellites"
WDGSCATTER = "Scatter Plot"
WDGSETTINGS = "Settings"
WDGSPECTRUM = "Spectrum"
WDGSTATUS = "Status"
WDGSYSMON = "System Monitor"

widget_state = {
    # these have a fixed relative position
    WDGBANNER: {  # always on top
        MENU: None,
        DEFAULT: True,
        CLASS: BannerFrame,
        FRAME: "frm_banner",
        VISIBLE: True,
    },
    WDGSETTINGS: {  # always on right
        MENU: 0,
        DEFAULT: True,
        CLASS: SettingsFrame,
        FRAME: "frm_settings",
        VISIBLE: True,
        STICKY: ("n", "w", "e"),
    },
    WDGSTATUS: {  # always on bottom
        MENU: 1,
        DEFAULT: True,
        CLASS: StatusFrame,
        FRAME: "frm_status",
        VISIBLE: True,
        STICKY: ("w", "e"),
    },
    # dynamic relative position - these self-organise
    # depending on which has been selected
    WDGCONSOLE: {
        MENU: 2,
        DEFAULT: True,
        CLASS: ConsoleFrame,
        FRAME: "frm_console",
        VISIBLE: True,
        COLSPAN: MAXCOLSPAN,
    },
    WDGSATS: {
        MENU: 3,
        DEFAULT: True,
        CLASS: SkyviewFrame,
        FRAME: "frm_satview",
        VISIBLE: True,
    },
    WDGLEVELS: {
        MENU: 4,
        DEFAULT: True,
        CLASS: GraphviewFrame,
        FRAME: "frm_graphview",
        VISIBLE: True,
    },
    WDGMAP: {
        MENU: 5,
        DEFAULT: True,
        CLASS: MapviewFrame,
        FRAME: "frm_mapview",
        VISIBLE: True,
    },
    WDGSPECTRUM: {
        MENU: 6,
        DEFAULT: False,
        CLASS: SpectrumviewFrame,
        FRAME: "frm_spectrumview",
        VISIBLE: False,
    },
    WDGSYSMON: {
        MENU: 7,
        DEFAULT: False,
        CLASS: SysmonFrame,
        FRAME: "frm_sysmon",
        VISIBLE: False,
    },
    WDGSCATTER: {
        MENU: 8,
        DEFAULT: False,
        CLASS: ScatterViewFrame,
        FRAME: "frm_scatterview",
        VISIBLE: False,
    },
    WDGROVER: {
        MENU: 9,
        DEFAULT: False,
        CLASS: RoverFrame,
        FRAME: "frm_roverview",
        VISIBLE: False,
    },
    # add any new widgets here
}
