"""
dialog_state.py

Global constants, strings and dictionaries used to
maintain the state of the various threaded dialogs.

Created on 16 Aug 2023

:author: semuadmin
:copyright: SEMU Consulting © 2020
:license: BSD 3-Clause
"""

from pygpsclient.about_dialog import AboutDialog
from pygpsclient.globals import (
    CFG,
    CLASS,
    DLG,
    DLGTABOUT,
    DLGTGPX,
    DLGTNTRIP,
    DLGTSPARTN,
    DLGTUBX,
    THD,
)
from pygpsclient.gpx_dialog import GPXViewerDialog
from pygpsclient.ntrip_client_dialog import NTRIPConfigDialog
from pygpsclient.spartn_dialog import SPARTNConfigDialog
from pygpsclient.ubx_config_dialog import UBXConfigDialog

dialog_state = {
    DLGTABOUT: {CLASS: AboutDialog, THD: None, DLG: None, CFG: False},
    DLGTUBX: {CLASS: UBXConfigDialog, THD: None, DLG: None, CFG: True},
    DLGTNTRIP: {CLASS: NTRIPConfigDialog, THD: None, DLG: None, CFG: True},
    DLGTSPARTN: {CLASS: SPARTNConfigDialog, THD: None, DLG: None, CFG: True},
    DLGTGPX: {CLASS: GPXViewerDialog, THD: None, DLG: None, CFG: True},
    # add any new dialogs here
}
