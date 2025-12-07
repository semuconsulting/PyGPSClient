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
   must be installed and in the `PATH`/`LD_LIBRARY_PATH`.

Created on 13 Sep 2025

:author: semuadmin (Steve Smith)
:copyright: 2020 semuadmin
:license: BSD 3-Clause
"""

import logging
import sqlite3
import traceback
from datetime import datetime, timezone
from os import path
from types import NoneType

from pynmeagps import ecef2llh

from pygpsclient.globals import ERRCOL, HOME, INFOCOL, OKCOL
from pygpsclient.helpers import makeval
from pygpsclient.strings import NA

# path to mod_spatialite module, if required
# SLPATH = "C:/Program Files/QGIS 3.44.1/bin"
# environ["PATH"] = SLPATH + ";" + environ["PATH"]

SQLVER = sqlite3.sqlite_version
"""sqlite3 version"""
SQLOK = 1
"""No SQL error"""
SQLERR = 0
"""Non-specific SQL error"""
NOEXT = -1
"""sqlite3 extensions not supported"""
NOMODS = -2
"""sqlite3 mod_spatialite extension not found"""
SQLSTATUS = {SQLOK: SQLVER, SQLERR: "SQL Err", NOEXT: "No ext", NOMODS: "No m_s"}
DBNAME = "pygpsclient.sqlite"
"""Default database name"""
DBINMEM = ":memory:"
"""In-memory database name"""
TBNAME = "pygpsclient"
"""Default table name"""
SQLBEGIN = "BEGIN TRANSACTION;"
SQLCOMMIT = "COMMIT;"

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
"""SQL for creating database and table with lat/lon/hmsl as 3D POINTZ"""

SQLI3D = (
    "INSERT INTO {table} (geom, utc, fix, hae, speed, track, siv, sip, pdop, "
    "hdop, vdop, hacc, vacc, diffcorr, diffage, diffstat, baselon, baselat, basehae) "
    "VALUES (GeomFromText('POINTZ({lon} {lat} {hmsl})', 4326), {utc}, '{fix}', "
    "{hae}, {speed}, {track}, {siv}, {sip}, {pdop}, {hdop}, {vdop}, {hacc}, "
    "{vacc}, {diffcorr}, {diffage}, '{diffstat}', {baselon}, {baselat}, {basehae});"
)
"""SQL for inserting row into table"""

SQLSEL = (
    "SELECT id, utc, ST_X(geom), ST_Y(geom), ST_Z(geom), fix, hae, speed, track, siv, "
    "sip, pdop, hdop, vdop, hacc, vacc, diffcorr, diffage, diffstat, baselon, "
    "baselat, basehae from {table} {where} ORDER BY utc LIMIT {limit} OFFSET {offset};"
)
"""SQL for retrieving rows from table"""


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
            self.__app.status_label = (
                f"Database {self._db} initialising - please wait...",
                INFOCOL,
            )
            self.logger.debug("Spatial metadata initialisation in progress...")
            self._connection.execute("SELECT InitSpatialMetaData();")
            self.logger.debug("Spatial metadata initialisation complete")
            self._cursor = self._connection.cursor()
            self._cursor.executescript(SQLC1.format(table=tbname))
            return SQLOK
        except sqlite3.Error as err:
            self.__app.status_label = (
                f"Error initialising spatial database {err}",
                ERRCOL,
            )
            self.logger.debug(traceback.format_exc())
            return SQLERR

    def open(
        self,
        dbpath: str = HOME,
        dbname: str = DBNAME,
        tbname: str = TBNAME,
    ) -> str | int:
        """
        Create sqlite3 connection and cursor.

        :param str dbpath: path to sqlite3 database file
        :param str dbname: name of sqlite3 database file
        :param str tbname: name of table containing gnss data
        :return: result
        :rtype: str | int
        """

        testing = dbname == DBINMEM
        errcol = ERRCOL
        try:
            db = ""
            if testing:  # check for spatial support
                db = dbname
                exists = True
                errcol = INFOCOL
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
            if testing:
                self._connection.close()
            else:
                self.__app.status_label = (f"Database {self._db} opened", OKCOL)
            return SQLOK
        except AttributeError as err:
            self.__app.status_label = (f"SQL error: {err}", errcol)
            self.logger.debug(traceback.format_exc())
            return NOEXT  # extensions not supported
        except sqlite3.OperationalError as err:
            self.__app.status_label = (f"SQL error {db}: {err}", errcol)
            self.logger.debug(traceback.format_exc())
            return NOMODS  # no mod_spatial extension found
        except sqlite3.Error as err:
            self.__app.status_label = (f"SQL error {db}: {err}", errcol)
            self.logger.debug(traceback.format_exc())
            return SQLERR  # other sqlite error

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

    def load_data(self, ignore_null: bool = True) -> str:
        """
        Load current gnss data (from `self.__app.gnss_status`) into database.

        :param bool ignore_null: ignore null position flag
        :return: result
        :rtype: str
        """

        gnss = self.__app.gnss_status
        if ignore_null and gnss.lat == 0.0 and gnss.lon == 0.0:
            self.logger.debug("Ignored null lat/lon value")
            return SQLOK

        try:
            baselat, baselon, basehae = ecef2llh(
                gnss.base_ecefx, gnss.base_ecefy, gnss.base_ecefz
            )
            basehae = 0.0 if basehae == -10000000.0 else basehae
            utc = datetime.combine(datetime.now(timezone.utc).date(), gnss.utc)
            sql = SQLI3D.format(
                table=self._table,
                lon=makeval(gnss.lon),
                lat=makeval(gnss.lat),
                hmsl=makeval(gnss.alt),
                utc=float(utc.strftime("%Y%m%d%H%M%S.%f")),
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
            return SQLOK
        except sqlite3.Error as err:
            self.__app.status_label = (f"SQL error: {err}", ERRCOL)
            self.logger.debug(traceback.format_exc())
            return SQLERR

    @property
    def database(self) -> str | NoneType:
        """
        Getter for database name.

        :return: database path/name or None
        :rtype: str | NoneType
        """

        return self._db


def retrieve_data(
    dbpath: str = path.join(HOME, DBNAME),
    table: str = TBNAME,
    sqlwhere: str = "",
    limit: int = 100,
    offset: int = 0,
) -> list:
    """
    Retrieve specified rows from sqlite table, ordered by utc timestamp.

    :param str dbpath: fully qualified path to database
    :param str table: name of database table
    :param str sqlwhere: optional SQL WHERE clause
    :param int limit: SQL LIMIT number of rows
    :param int offset: SQL OFFSET starting row
    :return: list of matching results
    :rtype: list
    :raises: FileNotFoundError
    :raises: sqlite3.Error
    """

    try:
        if not path.exists(dbpath):
            raise FileNotFoundError(f"No such database: '{dbpath}'")
        con = sqlite3.connect(dbpath)
        con.enable_load_extension(True)
        con.load_extension("mod_spatialite")
        cursor = con.cursor()
        sql = SQLSEL.format(table=table, where=sqlwhere, limit=limit, offset=offset)
        cursor.execute(sql)
        return cursor.fetchall()
    except (AttributeError, sqlite3.Error) as err:
        raise (sqlite3.Error(f"Error '{err}' executing SQL statement:\n{sql}")) from err
