"""
mapquest.py

MapQuest API Constants and Methods

MapQuest polygon compression and decompression routines
adapted from the original javascript examples:

https://developer.mapquest.com/documentation/common/encode-decode/

Created on 04 May 2023

:author: semuadmin
:copyright: SEMU Consulting © 2021
:license: BSD 3-Clause

"""

MAPQURL = "https://www.mapquestapi.com/staticmap/v5/map?key={}"
MAPURL = (
    MAPQURL
    + "&locations={},{}&zoom={}&size={},{}&defaultMarker=marker-sm-616161-ff4444"
    + "&shape=radius:{}|weight:1|fill:ccffff50|border:88888850|{},{}&scalebar={}"
)
GPXMAPURL = (
    MAPQURL
    + "&locations={},{}||{},{}&zoom={}&size={},{}&defaultMarker=marker-num"
    + "&shape=weight:2|border:{}|{}&scalebar={}|bottom"
)
GPXLIMIT = 500  # max number of track points supported by MapQuest API
MAPQTIMEOUT = 5
# how frequently the mapquest api is called to update the web map (seconds)
MAP_UPDATE_INTERVAL = 60
MIN_UPDATE_INTERVAL = 5


def mapq_encode(num: int) -> str:
    """
    Encode number representing character.

    :param int num: number to encode
    :return: encoded number as string
    :rtype: str
    """

    num = num << 1
    if num < 0:
        num = ~(num)

    encoded = ""
    while num >= 0x20:
        encoded += chr((0x20 | (num & 0x1F)) + 63)
        num >>= 5

    encoded += chr(num + 63)
    return encoded


def mapq_decompress(encoded: str, precision: int = 6) -> list:
    """
    Decompress polygon for MapQuest API.

    :param str encoded: polygon encoded as string
    :param int precision: no decimal places precision (6)
    :return: polygon as list of points
    :rtype: list
    """

    precision = 10**-precision
    leng = len(encoded)
    index = 0
    lat = 0
    lng = 0
    array = []
    while index < leng:
        shift = 0
        result = 0
        b = 0xFF
        while b >= 0x20:
            b = ord(encoded[index]) - 63
            index += 1
            result |= (b & 0x1F) << shift
            shift += 5

        dlat = ~(result >> 1) if (result & 1) else (result >> 1)
        lat += dlat
        shift = 0
        result = 0
        b = 0xFF
        while b >= 0x20:
            b = ord(encoded[index]) - 63
            index += 1
            result |= (b & 0x1F) << shift
            shift += 5

        dlng = ~(result >> 1) if (result & 1) else (result >> 1)
        lng += dlng
        array.append(lat * precision)
        array.append(lng * precision)

    return array


def mapq_compress(points: list, precision: int = 6) -> str:
    """
    Compress polygon for MapQuest API.

    :param str points: polygon as list of points
    :param int precision: no decimal places precision (6)
    :return: polygon encoded as string
    :rtype: string
    """

    oldLat = 0
    oldLng = 0
    leng = len(points)
    index = 0
    encoded = ""
    precision = 10**precision
    while index < leng:
        #  Round to N decimal places
        lat = round(points[index] * precision)
        index += 1
        lng = round(points[index] * precision)
        index += 1

        #  Encode the differences between the points
        encoded += mapq_encode(lat - oldLat)
        encoded += mapq_encode(lng - oldLng)

        oldLat = lat
        oldLng = lng

    return encoded
