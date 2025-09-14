"""
sqlite_handler.py

sqlite3 database class for PyGPSClient application.

This handles all the sqlite3 database updates.

**NB**: Functionality is subject to the following Python
environmental criteria:

1. The Python environment must support the loading of
   sqlite3 extensions i.e. it must have been compiled
   with the `--enable-loadable-sqlite-extensions` option.
2. The mod_spatialite module (.so, .dll or .dylib)
   must be installed and in the `PATH`.

Created on 13 Sep 2025

:author: semuadmin (Steve Smith)
:copyright: 2020 semuadmin
:license: BSD 3-Clause
"""

import logging
import sqlite3
import traceback
from os import path

from pynmeagps import ecef2llh

from pygpsclient.globals import ERRCOL, HOME, INFOCOL, OKCOL
from pygpsclient.helpers import makeval
from pygpsclient.strings import NA

# path to mod_spatialite module, if required
# SLPATH = "C:/Program Files/QGIS 3.44.1/bin"
# environ["PATH"] = SLPATH + ";" + environ["PATH"]

SQLVER = sqlite3.sqlite_version
"""sqlite3 version"""
DBNAME = "pygpsclient.sqlite"
"""Default database name"""
DBINMEM = ":memory:"
"""In-memory database name"""
TBNAME = "pygpsclient"
"""Default table name"""
SQLBEGIN = "BEGIN TRANSACTION;"
SQLCOMMIT = "COMMIT;"

# CREATE SQL statement with 3D POINT (lon, lat, hmsl)
SQLC1 = (
    SQLBEGIN
    + (
        "DROP TABLE IF EXISTS {table};"
        "CREATE TABLE {table} (id INTEGER PRIMARY KEY, utc REAL, fix TEXT, hae REAL, "
        "speed REAL, track REAL, siv INTEGER, sip INTEGER, pdop REAL, hdop REAL, vdop REAL, "
        "hacc REAL, vacc REAL, diffcorr INTEGER, diffage INTEGER, diffstat TEXT, "
        "baselon REAL, baselat REAL, basehae REAL);"
        "SELECT AddGeometryColumn('{table}', 'geom', 4326, 'POINT', 'XYZ');"
        "SELECT CreateSpatialIndex('{table}', 'geom');"
    )
    + SQLCOMMIT
)

# INSERT SQL statement with 3D POINT
SQLI3D = (
    "INSERT INTO {table} (geom, utc, fix, hae, speed, track, siv, sip, pdop, "
    "hdop, vdop, hacc, vacc, diffcorr, diffage, diffstat, baselon, baselat, basehae) "
    "VALUES (GeomFromText('POINTZ({lon} {lat} {hmsl})', 4326), {utc}, '{fix}', "
    "{hae}, {speed}, {track}, {siv}, {sip}, {pdop}, {hdop}, {vdop}, {hacc}, "
    "{vacc}, {diffcorr}, {diffage}, '{diffstat}', {baselon}, {baselat}, {basehae});"
)


class SqliteHandler:
    """
    sqlite handler class.
    """

    def __init__(self, app):
        """
        Constructor.

        :param Frame app: reference to main tkinter application

        """

        self.__app = app  # Reference to main application class
        self.__master = self.__app.appmaster  # Reference to root class (Tk)
        self.logger = logging.getLogger(__name__)

        self._db = None
        self._table = None
        self._dbname = None
        self._connection = None
        self._cursor = None

    def _create(
        self,
        tbname: str = TBNAME,
    ) -> int:
        """
        Create sqlite3 connection and cursor.

        :param str dbpath: path to sqlite3 database file
        :param str dbname: name of sqlite3 database file
        :param str tbname: name of table containing gnss data
        :return: return code
        :rtype: int
        """

        try:
            self.__app.set_status(
                f"Database {self._db} initialising - please wait...", INFOCOL
            )
            self.logger.debug("Spatial metadata initialisation in progress...")
            self._connection.execute("SELECT InitSpatialMetaData();")
            self.logger.debug("Spatial metadata initialisation complete")
            self._cursor = self._connection.cursor()
            self._cursor.executescript(SQLC1.format(table=tbname))
            return 1
        except sqlite3.Error as err:
            self.__app.set_status(f"Error initialising spatial database {err}", ERRCOL)
            self.logger.debug(traceback.format_exc())
            return 0

    def open(
        self,
        dbpath: str = HOME,
        dbname: str = DBNAME,
        tbname: str = TBNAME,
    ) -> int:
        """
        Create sqlite3 connection and cursor.

        :param str dbpath: path to sqlite3 database file
        :param str dbname: name of sqlite3 database file
        :param str tbname: name of table containing gnss data
        :return: return code
        :rtype: int
        """

        try:
            if dbname == DBINMEM:  # check for spatial support
                db = dbname
                exists = True
            else:
                db = path.join(dbpath, dbname)
                exists = path.exists(db)
                self._db = db
                self._table = tbname
                self._dbname = dbname
            self._connection = sqlite3.connect(db)
            self._connection.enable_load_extension(True)
            self._connection.load_extension("mod_spatialite")
            if not exists:
                if not self._create(tbname):
                    return 0
            self._cursor = self._connection.cursor()
            if dbname == DBINMEM:
                self._connection.close()
            else:
                self.__app.set_status(f"Database {self._db} opened", OKCOL)
            return 1
        except AttributeError:
            self.__app.set_status(f"Spatial database not supported", ERRCOL)
            self.logger.debug(traceback.format_exc())
            return -1  # extensions not supported
        except sqlite3.OperationalError:
            self.__app.set_status(f"Spatial extension not found", ERRCOL)
            self.logger.debug(traceback.format_exc())
            return -2  # no mod_spatial extension found
        except sqlite3.Error as err:
            self.__app.set_status(f"Spatial database error {err}", ERRCOL)
            self.logger.debug(traceback.format_exc())
            return 0  # other sqlite error

    def close(self):
        """
        Close database connection.
        """

        if self._connection is not None:
            try:
                self._connection.cursor()
            except sqlite3.Error:
                return
            self._connection.close()

    def load_data(self, ignore_null: bool = True) -> bool:
        """
        Load current gnss data (from `self.__app.gnss_status`) into database.

        :param bool ignore_null: ignore null position flag
        :return: 0 = error, 1 = ok
        :rtype: bool
        """

        gnss = self.__app.gnss_status
        if ignore_null and gnss.lat == 0.0 and gnss.lon == 0.0:
            self.logger.debug("Ignored null lat/lon value")
            return True

        try:
            baselat, baselon, basehae = ecef2llh(
                gnss.base_ecefx, gnss.base_ecefy, gnss.base_ecefz
            )
            basehae = 0.0 if basehae == -10000000.0 else basehae
            sql = SQLI3D.format(
                table=self._table,
                lon=makeval(gnss.lon),
                lat=makeval(gnss.lat),
                hmsl=makeval(gnss.alt),
                utc=float(gnss.utc.strftime("%H%M%S.%f")),
                fix=gnss.fix,
                hae=makeval(gnss.hae),
                speed=makeval(gnss.speed),
                track=makeval(gnss.track),
                siv=makeval(gnss.siv, 0),
                sip=makeval(gnss.sip, 0),
                pdop=makeval(gnss.pdop),
                hdop=makeval(gnss.hdop),
                vdop=makeval(gnss.vdop),
                hacc=makeval(gnss.hacc),
                vacc=makeval(gnss.vacc),
                diffcorr=makeval(gnss.diff_corr),
                diffage=makeval(gnss.diff_age, 0),
                diffstat=makeval(gnss.diff_station, NA),
                baselon=makeval(baselon),
                baselat=makeval(baselat),
                basehae=makeval(basehae),
            )
            sql = SQLBEGIN + sql + SQLCOMMIT
            self._cursor.executescript(sql)
            self.logger.debug(f"Executed SQL statement {sql}")
            return 1
        except sqlite3.OperationalError as err:
            self.__app.set_status(f"Database write error: {err}", ERRCOL)
            self.logger.debug(traceback.format_exc())
            return 0

    @property
    def database(self) -> str:
        """
        Getter for database name.

        :return: database path/name
        :rtype: str
        """

        return self._db
