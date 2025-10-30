"""
nmea_presets.py

Pre-defined NMEA preset commands.

Created on 31 Oct 2025

:author: semuadmin (Steve Smith)
:copyright: 2020 semuadmin
:license: BSD 3-Clause
"""

NMEAPRESETS = (
    "Quectel RESTORE FACTORY DEFAULTS CONFIRM; P; QTMRESTOREPAR; ; 1",
    "Quectel Save configuration to non-volatile memory CONFIRM; P; QTMSAVEPAR; ; 1",
    "Quectel HOT restart CONFIRM; P; QTMHOT; ; 1",
    "Quectel WARM restart CONFIRM; P; QTMWARM; ; 1",
    "Quectel COLD restart CONFIRM; P; QTMCOLD; ; 1",
    "Quectel System Reset and Reboot CONFIRM; P; QTMSRR; ; 1",
    "Quectel Check Hardware Version; P; QTMVERNO; ; 2",
    "Quectel Start GNSS; P; QTMGNSSSTART; ; 1",
    "Quectel Stop GNSS; P; QTMGNSSSTOP; ; 1",
)
