"""
ubx_spatialite.py

Example script illustrating how to create a sqlite3
database (gnss.sqlite) with the spatialite extension
enabled and load geometry (lat/lon/hmsl) data from a
binary GNSS data log into it using pyubx2. Log must
contain UBX NAV-PVT and/or NMEA GGA messages.

Usage:

python3 ubx_spatialite.py infile="gnssdata.log" dbpath="/home/myuser/Downloads" table="gnssdata"

***********************************************************
NB: Although sqlite3 is a native Python 3 module,
the version of this module which comes as standard on many
Unix-like platforms (Linux & MacOS) does NOT support the
loading of extensions (e.g. mod_spatialite) by default. It
may be necessary to install (via Homebrew) or compile
a custom version of Python with the
--enable-loadable-sqlite-extensions option set, e.g.

brew install python-tk@3.13 libspatialite

To check that the sqlite3 database engine itself supports
extensions, use the following sqlite3 CLI command:

sqlite> .dbconfig

and check for the entry 'load_extension on'.
***********************************************************

gnssdata example table has the following fields:
    pk INTEGER
    geom POINTZ
    source TEXT
    tow INTEGER
    fixtype INTEGER
    dop REAL
    hacc REAL

Created on 27 Jul 2023

:author: semuadmin (Steve Smith)
:copyright: SEMU Consulting © 2023
:license: BSD 3-Clause
"""

import sqlite3  # NOTE caveat above
from datetime import datetime
from os import environ, path
from sys import argv

from pyubx2 import ERR_LOG, NMEA_PROTOCOL, UBX_PROTOCOL, UBXReader

LEAPS = 18  # tow leapseconds adjustment
DB = "gnss.sqlite"

# path to mod_spatialite module, if required
# SLPATH = "C:/Program Files/QGIS 3.44.1/bin"
# environ["PATH"] = SLPATH + ";" + environ["PATH"]

SQLBEGIN = "BEGIN TRANSACTION;"
SQLCOMMIT = "COMMIT;"

# CREATE SQL statement with 3D POINT (lon, lat, hmsl)
SQLC1 = (
    SQLBEGIN
    + (
        "DROP TABLE IF EXISTS {table};"
        "CREATE TABLE {table} (id INTEGER PRIMARY KEY, source TEXT, "
        "tow INTEGER, fixtype INTEGER, dop REAL, hacc REAL);"
        "SELECT AddGeometryColumn('{table}', 'geom', 4326, 'POINT', 'XYZ');"
        "SELECT CreateSpatialIndex('{table}', 'geom');"
    )
    + SQLCOMMIT
)

# INSERT SQL statement with 3D POINT
SQLI3D = (
    "INSERT INTO {table} (geom, source, tow, fixtype, dop, hacc) "
    "VALUES (GeomFromText('POINTZ({lon} {lat} {height})', 4326), "
    "'{source}', {tow}, {fixtype}, {dop}, {hacc});"
)


def fix2quality(parsed):
    """
    Convert NAV-PVT fixType to GGA quality
    """

    if parsed.carrSoln == 1:  # float
        return 5
    if parsed.carrSoln == 2:  # fixed
        return 4
    if parsed.fixType in (2, 4):  # 2D or DR
        return 1
    if parsed.fixType == 3:  # 3D
        return 2
    return 0


def tim2tow(tim):
    """
    Convert GGA time to TOW.
    """

    dat = datetime.combine(datetime.now().date(), tim)
    wd = (dat.weekday() - 6) % 7
    return (wd * 86400) + dat.hour * 3600 + dat.minute * 60 + dat.second + LEAPS


def create_database(con, cur, table):
    """
    Create spatial database.
    """

    # load spatialite extension to support spatial (geometry) attributes
    print("Enabling extension loading")
    try:
        con.enable_load_extension(True)
    except AttributeError as err:
        raise AttributeError(
            "Your Python installation does not currently support sqlite3 extensions"
        ) from err
    print("Loading mod_spatialite extension")
    try:
        con.load_extension("mod_spatialite")
    except sqlite3.OperationalError as err:
        raise sqlite3.OperationalError(
            "Unable to locate sqlite3 mod_spatialite extension - check PATH"
        ) from err
    print("Initialising spatial metadata (may take a few seconds)")
    con.execute("SELECT InitSpatialMetaData();")
    # create database table
    print(f"Creating {table} table")
    cur.executescript(SQLC1.format(table=table))


def load_data(cur, infile, table):
    """
    Load data into database.
    """

    # iterate through UBX data log
    print(f"Loading data into {table} from GNSS data log")
    i = 0
    cur.execute(SQLBEGIN)
    with open(infile, "rb") as stream:
        ubr = UBXReader(
            stream, protfilter=UBX_PROTOCOL | NMEA_PROTOCOL, quitonerror=ERR_LOG
        )
        for _, parsed in ubr:
            if "NAV-PVT" in parsed.identity:
                sql = SQLI3D.format(
                    table=table,
                    source=parsed.identity,
                    tow=int(parsed.iTOW / 1000),  # seconds
                    fixtype=fix2quality(parsed),
                    dop=parsed.pDOP,
                    hacc=parsed.hAcc,
                    lon=parsed.lon,
                    lat=parsed.lat,
                    height=parsed.hMSL / 1000,  # meters
                )
                # print(sql)
                cur.execute(sql)
                i += 1
            elif "GGA" in parsed.identity:
                sql = SQLI3D.format(
                    table=table,
                    source=parsed.identity,
                    tow=tim2tow(parsed.time),  # seconds
                    fixtype=parsed.quality,
                    dop=parsed.HDOP,
                    hacc=0,
                    lon=parsed.lon,
                    lat=parsed.lat,
                    height=parsed.alt,  # meters
                )
                # print(sql)
                cur.execute(sql)
                i += 1
    cur.execute(SQLCOMMIT)
    print(f"{i} records loaded into {table}")


def main(**kwargs):
    """
    Main routine.
    """

    infile = kwargs.get("infile", "gnssdata.log")
    dbpath = kwargs.get("dbpath", ".")
    db = path.join(dbpath, "gnss.sqlite")
    table = kwargs.get("table", "gnssdata")

    # create & connect to the database
    print(f"Connecting to database {db}")
    with sqlite3.connect(db) as connection:
        cursor = connection.cursor()
        create_database(connection, cursor, table)
        load_data(cursor, infile, table)
    print("Complete")


if __name__ == "__main__":

    main(**dict(arg.split("=") for arg in argv[1:]))
