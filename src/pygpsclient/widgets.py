"""
widgets.py

Global constants, strings and dictionaries used to
position and hide/show the various user-selectable
widgets in the main container frame.

To add a new widget to PyGPSClient:
1. create a new frame class `widgetname_frame.py`.
2. instantiate it in app._body() as `frm_widgetname`.
3. add an entry to the foot of the widget_grid dictionary.
4. if the widget requires data not already in the `app.gnss_status`
data dictionary, add the requisite data items to the `GNSSStatus`
class definition and update `ubx_handler` to populate them.

Created on 30 Apr 2023

:author: semuadmin
:copyright: SEMU Consulting © 2020
:license: BSD 3-Clause
"""

MAXCOLSPAN = 4  # max no of widget columns
MAXROWSPAN = 4  # max no of widget rows
HIDE = "Hide"
SHOW = "Show"
WDGBANNER = "Banner"
WDGSETTINGS = "Settings"
WDGSTATUS = "Status"
WDGCONSOLE = "Console"
WDGSATS = "Satellites"
WDGLEVELS = "Levels"
WDGMAP = "Map"
WDGSPECTRUM = "Spectrum"
WDGSCATTER = "Scatter Plot"
WDGSYSMON = "System Monitor"

widget_grid = {
    # these have a fixed relative position
    WDGBANNER: {  # always on top
        "menu": None,
        "default": True,
        "frm": "frm_banner",
        "visible": True,
    },
    WDGSETTINGS: {  # always on right
        "menu": 0,
        "default": True,
        "frm": "frm_settings",
        "visible": True,
        "sticky": ("n", "w", "e"),
    },
    WDGSTATUS: {  # always on bottom
        "menu": 1,
        "default": True,
        "frm": "frm_status",
        "visible": True,
        "sticky": ("w", "e"),
    },
    # dynamic relative position - these self-organise
    # depending on which has been selected
    WDGCONSOLE: {
        "menu": 2,
        "default": True,
        "frm": "frm_console",
        "visible": True,
        "colspan": MAXCOLSPAN,
    },
    WDGSATS: {
        "menu": 3,
        "default": True,
        "frm": "frm_satview",
        "visible": True,
    },
    WDGLEVELS: {
        "menu": 4,
        "default": True,
        "frm": "frm_graphview",
        "visible": True,
    },
    WDGMAP: {
        "menu": 5,
        "default": True,
        "frm": "frm_mapview",
        "visible": True,
    },
    WDGSPECTRUM: {
        "menu": 6,
        "default": False,
        "frm": "frm_spectrumview",
        "visible": False,
    },
    WDGSYSMON: {
        "menu": 7,
        "default": False,
        "frm": "frm_sysmon",
        "visible": False,
    },
    WDGSCATTER: {
        "menu": 8,
        "default": False,
        "frm": "frm_scatterview",
        "visible": False,
    },
    # add any new widgets here
}
