"""
dialog_state.py

Class holding global constants, strings and dictionaries
used to maintain the state of the various threaded dialogs.

CLASS = name of dialog class
THD = instance of thread
DLG = instance of dialog frame
RESIZE = whether dialog is resizeable

Created on 16 Aug 2023

:author: semuadmin (Steve Smith)
:copyright: 2020 semuadmin
:license: BSD 3-Clause
"""

from pygpsclient.about_dialog import AboutDialog
from pygpsclient.globals import CLASS, RESIZE, THD
from pygpsclient.gpx_dialog import GPXViewerDialog
from pygpsclient.importmap_dialog import ImportMapDialog
from pygpsclient.nmea_config_dialog import NMEAConfigDialog
from pygpsclient.ntrip_client_dialog import NTRIPConfigDialog
from pygpsclient.spartn_dialog import SPARTNConfigDialog
from pygpsclient.strings import (
    DLG,
    DLGTABOUT,
    DLGTGPX,
    DLGTIMPORTMAP,
    DLGTNMEA,
    DLGTNTRIP,
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
                THD: None,
                DLG: None,
                RESIZE: False,
            },
            DLGTUBX: {
                CLASS: UBXConfigDialog,
                THD: None,
                DLG: None,
                RESIZE: False,
            },
            DLGTNMEA: {
                CLASS: NMEAConfigDialog,
                THD: None,
                DLG: None,
                RESIZE: False,
            },
            DLGTNTRIP: {
                CLASS: NTRIPConfigDialog,
                THD: None,
                DLG: None,
                RESIZE: False,
            },
            DLGTSPARTN: {
                CLASS: SPARTNConfigDialog,
                THD: None,
                DLG: None,
                RESIZE: False,
            },
            DLGTGPX: {
                CLASS: GPXViewerDialog,
                THD: None,
                DLG: None,
                RESIZE: True,
            },
            DLGTIMPORTMAP: {
                CLASS: ImportMapDialog,
                THD: None,
                DLG: None,
                RESIZE: True,
            },
            DLGTTTY: {
                CLASS: TTYPresetDialog,
                THD: None,
                DLG: None,
                RESIZE: True,
            },
            # add any new dialogs here
        }
