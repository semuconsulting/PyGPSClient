"""
dialog_state.py

Class holding global constants, strings and dictionaries
used to maintain the state of the various pop-up dialogs.

CLASS = name of dialog class
DLG = instance of dialog frame
RESIZE = whether dialog is resizeable (defaults to False)

Created on 16 Aug 2023

:author: semuadmin (Steve Smith)
:copyright: 2020 semuadmin
:license: BSD 3-Clause
"""

from pygpsclient.about_dialog import AboutDialog
from pygpsclient.globals import CLASS, RESIZE
from pygpsclient.gpx_dialog import GPXViewerDialog
from pygpsclient.importmap_dialog import ImportMapDialog
from pygpsclient.nmea_config_dialog import NMEAConfigDialog
from pygpsclient.ntrip_client_dialog import NTRIPConfigDialog
from pygpsclient.recorder_dialog import RecorderDialog
from pygpsclient.serverconfig_dialog import ServerConfigDialog
from pygpsclient.settings_dialog import SettingsDialog
from pygpsclient.spartn_dialog import SPARTNConfigDialog
from pygpsclient.strings import (
    DLG,
    DLGTABOUT,
    DLGTGPX,
    DLGTIMPORTMAP,
    DLGTNMEA,
    DLGTNTRIP,
    DLGTRECORD,
    DLGTSERVER,
    DLGTSETTINGS,
    DLGTSPARTN,
    DLGTTTY,
    DLGTUBX,
)
from pygpsclient.tty_preset_dialog import TTYPresetDialog
from pygpsclient.ubx_config_dialog import UBXConfigDialog


class DialogState:
    """
    Class holding current state of PyGPSClient dialogs.
    """

    def __init__(self):
        """
        Constructor.
        """

        self.state = {
            DLGTABOUT: {
                CLASS: AboutDialog,
                DLG: None,
                RESIZE: False,
            },
            DLGTUBX: {
                CLASS: UBXConfigDialog,
                DLG: None,
                RESIZE: False,
            },
            DLGTNMEA: {
                CLASS: NMEAConfigDialog,
                DLG: None,
                RESIZE: False,
            },
            DLGTNTRIP: {
                CLASS: NTRIPConfigDialog,
                DLG: None,
                RESIZE: False,
            },
            DLGTSERVER: {
                CLASS: ServerConfigDialog,
                DLG: None,
                RESIZE: True,
            },
            DLGTSPARTN: {
                CLASS: SPARTNConfigDialog,
                DLG: None,
                RESIZE: False,
            },
            DLGTGPX: {
                CLASS: GPXViewerDialog,
                DLG: None,
                RESIZE: True,
            },
            DLGTIMPORTMAP: {
                CLASS: ImportMapDialog,
                DLG: None,
                RESIZE: True,
            },
            DLGTTTY: {
                CLASS: TTYPresetDialog,
                DLG: None,
                RESIZE: False,
            },
            DLGTRECORD: {
                CLASS: RecorderDialog,
                DLG: None,
                RESIZE: False,
            },
            DLGTSETTINGS: {
                CLASS: SettingsDialog,
                DLG: None,
                RESIZE: False,
            },
            # add any new dialogs here
        }
