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

from pygpsclient.chart_frame import ChartviewFrame
from pygpsclient.console_frame import ConsoleFrame
from pygpsclient.globals import CLASS, FRAME
from pygpsclient.imu_frame import IMUFrame
from pygpsclient.levelsview_frame import LevelsviewFrame
from pygpsclient.map_frame import MapviewFrame
from pygpsclient.rover_frame import RoverFrame
from pygpsclient.scatter_frame import ScatterViewFrame
from pygpsclient.signalsview_frame import SignalsviewFrame
from pygpsclient.skyview_frame import SkyviewFrame
from pygpsclient.spectrum_frame import SpectrumviewFrame
from pygpsclient.sysmon_frame import SysmonFrame

COLSPAN = "colspan"
DEFAULT = "def"
HIDE = "Hide"
MAXCOLSPAN = 4  # max no of widget columns
MAXSPAN = 0  # always occupy the full row
MAXROWSPAN = 4  # max no of widget rows
RESET = "rst"
SHOW = "Show"
VISIBLE = "vis"
WDGCONSOLE = "Console"
WDGLEVELS = "Levels"
WDGMAP = "Map"
WDGROVER = "Rover Plot"
WDGSATS = "Satellites"
WDGSCATTER = "Scatter Plot"
WDGSPECTRUM = "Spectrum"
WDGSYSMON = "System Monitor"
WDGCHART = "Chart Plot"
WDGIMUMON = "IMU Monitor"
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
            },
            WDGSATS: {
                DEFAULT: True,
                CLASS: SkyviewFrame,
                FRAME: "frm_satview",
                VISIBLE: True,
            },
            WDGLEVELS: {
                DEFAULT: True,
                CLASS: LevelsviewFrame,
                FRAME: "frm_levelsview",
                VISIBLE: True,
            },
            WDGSIGNALS: {
                CLASS: SignalsviewFrame,
                FRAME: "frm_signalsview",
                VISIBLE: False,
                COLSPAN: 2,
            },
            WDGMAP: {
                DEFAULT: True,
                CLASS: MapviewFrame,
                FRAME: "frm_mapview",
                VISIBLE: True,
                RESET: True,
            },
            WDGSPECTRUM: {
                CLASS: SpectrumviewFrame,
                FRAME: "frm_spectrumview",
                VISIBLE: False,
                RESET: True,
            },
            WDGSCATTER: {
                CLASS: ScatterViewFrame,
                FRAME: "frm_scatterview",
                VISIBLE: False,
            },
            WDGROVER: {
                DEFAULT: False,
                CLASS: RoverFrame,
                FRAME: "frm_roverview",
                VISIBLE: False,
            },
            WDGCHART: {
                CLASS: ChartviewFrame,
                FRAME: "frm_chartview",
                VISIBLE: False,
                COLSPAN: 2,
            },
            WDGSYSMON: {
                CLASS: SysmonFrame,
                FRAME: "frm_sysmon",
                VISIBLE: False,
            },
            WDGIMUMON: {
                CLASS: IMUFrame,
                FRAME: "frm_imumon",
                VISIBLE: False,
            },
            # add any new widgets here
        }
