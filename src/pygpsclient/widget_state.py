"""
widget_state.py

Class holding global constants, strings and dictionaries
used to maintain the state of the various user-selectable
widgets in the main container frame.

To add a new widget to PyGPSClient:
1. Create a new frame class `widgetname_frame.py`. The frame class
should implement `init_frame()` and `update_frame()` functions.
2. If the widget requires certain UBX messages to be enabled,
implement an `enable_messages(status)` function.
3. Add an entry to the foot of the self.__app.widget_state.state dictionary.
4. If the widget requires data not already in the `app.gnss_status`
data dictionary, add the requisite data items to the `GNSSStatus`
class definition and update `ubx_handler` to populate them.

Created on 30 Apr 2023

:author: semuadmin (Steve Smith)
:copyright: 2020 semuadmin
:license: BSD 3-Clause
"""

from pygpsclient.attitude_frame import AttitudeFrame
from pygpsclient.chart_frame import ChartviewFrame
from pygpsclient.console_frame import ConsoleFrame
from pygpsclient.globals import CLASS, FRAME, WIDGETU1, WIDGETU3, WIDGETU6
from pygpsclient.levelsview_frame import LevelsviewFrame
from pygpsclient.map_frame import MapviewFrame
from pygpsclient.rover_frame import RoverFrame
from pygpsclient.scatter_frame import ScatterViewFrame
from pygpsclient.signalsview_frame import SignalsviewFrame
from pygpsclient.skyview_frame import SkyviewFrame
from pygpsclient.spectrum_frame import SpectrumviewFrame
from pygpsclient.sysmon_frame import SysmonFrame

COLSPAN = "colspan"
DATA = "data"  # output data required by widget
DEFAULT = "def"
DOCK = "Dock"
FONTSIZE = "fontsize"  # defaults to 12
HIDE = "Hide"
MAXCOLSPAN = 4  # max no of widget columns
MAXSPAN = 0  # always occupy the full row
MAXROWSPAN = 4  # max no of widget rows
RESET = "rst"
SHOW = "Show"
SIZE = "Size"
UNDOCK = "Undock"
VISIBLE = "vis"
WDGCONSOLE = "Console"
WDGLEVELS = "Levels"
WDGMAP = "Map"
WDGROVER = "Relative Position"
WDGSATS = "Satellites"
WDGSCATTER = "Scatter Plot"
WDGSPECTRUM = "Spectrum"
WDGSYSMON = "System Monitor"
WDGCHART = "Chart Plot"
WDGATTMON = "Attitude Monitor"
WDGSIGNALS = "Signals"


class WidgetState:
    """
    Class holding current state of all PyGPSClient widgets.
    """

    def __init__(self):
        """
        Constructor.
        """

        self.state = {
            WDGCONSOLE: {
                DEFAULT: True,
                CLASS: ConsoleFrame,
                FRAME: "frm_console",
                VISIBLE: True,
                COLSPAN: MAXSPAN,
                SIZE: WIDGETU3,
            },
            WDGSATS: {
                DEFAULT: True,
                CLASS: SkyviewFrame,
                FRAME: "frm_satview",
                VISIBLE: True,
                DATA: "ELV/AZI",
            },
            WDGLEVELS: {
                DEFAULT: True,
                CLASS: LevelsviewFrame,
                FRAME: "frm_levelsview",
                VISIBLE: True,
                DATA: "CNO",
            },
            WDGSIGNALS: {
                CLASS: SignalsviewFrame,
                FRAME: "frm_signalsview",
                VISIBLE: False,
                COLSPAN: 2,
                SIZE: WIDGETU3,
                DATA: "UBX NAV-SIG",
            },
            WDGMAP: {
                DEFAULT: True,
                CLASS: MapviewFrame,
                FRAME: "frm_mapview",
                VISIBLE: True,
                RESET: True,
                DATA: "LAT/LON",
            },
            WDGSPECTRUM: {
                CLASS: SpectrumviewFrame,
                FRAME: "frm_spectrumview",
                VISIBLE: False,
                RESET: True,
                DATA: "UBX MON-SPAN",
            },
            WDGSCATTER: {
                CLASS: ScatterViewFrame,
                FRAME: "frm_scatterview",
                VISIBLE: False,
                SIZE: WIDGETU1,
                DATA: "LAT/LON",
            },
            WDGROVER: {
                DEFAULT: False,
                CLASS: RoverFrame,
                FRAME: "frm_roverview",
                VISIBLE: False,
                DATA: "RELPOS",
            },
            WDGSYSMON: {
                CLASS: SysmonFrame,
                FRAME: "frm_sysmon",
                VISIBLE: False,
                FONTSIZE: 10,
                DATA: "UBX MON-SYS",
            },
            WDGATTMON: {
                CLASS: AttitudeFrame,
                FRAME: "frm_attitudemon",
                VISIBLE: False,
                DATA: "Attitude",
            },
            WDGCHART: {
                CLASS: ChartviewFrame,
                FRAME: "frm_chartview",
                VISIBLE: False,
                COLSPAN: MAXSPAN,
                SIZE: WIDGETU6,
                FONTSIZE: 10,
            },
            # add any new widgets here
        }
