"""
GNSS Status class.

Container for the latest readings from the GNSS receiver.

Created on 07 Apr 2022

:author: semuadmin
:copyright: SEMU Consulting © 2022
:license: BSD 3-Clause
"""

from datetime import datetime


class GNSSStatus:
    """
    GNSS Status class.
    Container for the latest readings from the GNSS receiver.
    """

    def __init__(self):
        """
        Constructor.
        """

        self.utc = datetime.utcnow().time().replace(microsecond=0)  # UTC time
        self.lat = 0.0  # latitude as decimal
        self.lon = 0.0  # longitude as decimal
        self.alt = 0.0  # elevation m
        self.speed = 0.0  # speed m/s
        self.track = 0.0  # track degrees
        self.fix = "NO FIX"  # fix type e.g. "3D"
        self.siv = 0  # satellites in view
        self.sip = 0  # satellites in position solution
        self.pdop = 0.0  # dilution of precision DOP
        self.hdop = 0.0  # horizontal DOP
        self.vdop = 0.0  # vertical DOP
        self.hacc = 0.0  # horizontal accuracy m
        self.vacc = 0.0  # vertical accuracy m
        self.sep = 0.0  # separation from ellipsoid m, used to synthesise GGA sentences
        self.diff_corr = 0  # DGPS correction status True/False
        self.diff_age = 0  # DGPS correction age seconds
        self.diff_station = "N/A"  # DGPS station id
        self.gsv_data = []  # list of satellite tuples (gnssId, svid, elev, azim, cno)
