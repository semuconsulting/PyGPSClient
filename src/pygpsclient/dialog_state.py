"""
dialog_state.py

Class holding global constants, strings and dictionaries
used to maintain the state of the various threaded dialogs.

Created on 16 Aug 2023

:author: semuadmin
:copyright: 2020 SEMU Consulting
:license: BSD 3-Clause
"""

from pygpsclient.about_dialog import AboutDialog
from pygpsclient.globals import CFG, CLASS, THD
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
            DLGTABOUT: {CLASS: AboutDialog, THD: None, DLG: None, CFG: False},
            DLGTUBX: {CLASS: UBXConfigDialog, THD: None, DLG: None, CFG: True},
            DLGTNMEA: {CLASS: NMEAConfigDialog, THD: None, DLG: None, CFG: True},
            DLGTNTRIP: {CLASS: NTRIPConfigDialog, THD: None, DLG: None, CFG: True},
            DLGTSPARTN: {CLASS: SPARTNConfigDialog, THD: None, DLG: None, CFG: True},
            DLGTGPX: {CLASS: GPXViewerDialog, THD: None, DLG: None, CFG: True},
            DLGTIMPORTMAP: {CLASS: ImportMapDialog, THD: None, DLG: None, CFG: True},
            DLGTTTY: {CLASS: TTYPresetDialog, THD: None, DLG: None, CFG: True},
            # add any new dialogs here
        }
