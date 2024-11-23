"""
mapquest.py

MapQuest API Constants and Methods.

MapQuest polygon compression and decompression routines
adapted from the original javascript examples:

https://developer.mapquest.com/documentation/api/static-map/
https://developer.mapquest.com/documentation/common/encode-decode/

Created on 04 May 2023

:author: semuadmin
:copyright: 2020 SEMU Consulting
:license: BSD 3-Clause

"""

from pygpsclient.globals import Area

MAPQURL = "https://www.mapquestapi.com/staticmap/v5/map?key={}"
MARKERURL = "marker-sm-616161-ff4444"
MAPURL = (
    MAPQURL
    + "&locations={},{}|{}&zoom={}&size={},{}&type={}&scalebar={}"
    + "&shape=radius:{}|weight:1|fill:ccffff50|border:88888850|{},{}"
)  # centered on location to zoom level
MAPURLBB = (
    MAPQURL
    + "&locations={},{}|{}&zoom={}&size={},{}&type={}&scalebar={}"
    + "&boundingBox={},{},{},{}"
)  # bounding box without location
MAPURLTRK = (
    MAPQURL
    + "&locations={},{}||{},{}&zoom={}&size={},{}&defaultMarker=marker-num"
    + "&shape=weight:2|border:{}|{}&scalebar={}|bottom&type={}"
)  # bounding box to track
POINTLIMIT = 500  # max number of shape points supported by MapQuest API
MAPQTIMEOUT = 5
# how frequently the mapquest api is called to update the web map (seconds)
MAP_UPDATE_INTERVAL = 60
MIN_UPDATE_INTERVAL = 5
MAX_ZOOM = 20
MIN_ZOOM = 1
TRKCOL = "ff00ff"


def compress_track(track: tuple, precision: int = 6, limit: int = POINTLIMIT) -> str:
    """
    Convert track to compressed Mapquest format.

    :param tuple track: tuple of Points
    :param int precision: no decimal places precision (6)
    :param int limit: max no of points (500)
    :return: compressed track
    :rtype: str
    """

    # if the number of trackpoints exceeds the MapQuest API limit,
    # increase step count until the number is within limits
    points = []
    stp = 1
    rng = len(track)
    while rng / stp > limit:
        stp += 1
    for i, p in enumerate(track):
        if i % stp == 0:
            points.append(p.lat)
            points.append(p.lon)

    # compress polygon for MapQuest API
    return mapq_compress(points, precision)


def format_mapquest_request(
    mqapikey: str,
    maptype: str,
    width: int,
    height: int,
    zoom: int,
    locations: tuple,
    bbox: Area = None,
    hacc: float = 0,
):
    """
    Formats URL for web map download.

    :param str mqapikey: MapQuest API key
    :param str maptype: "map" or "sat"
    :param int width: width of canvas
    :param int height: height of canvas
    :param int zoom: zoom factor
    :param tuple locations: tuple of Points
    :param Area bbox: bounding box (will override zoom)
    :param float hacc: horizontal accuracy
    :return: formatted MapQuest URL
    :rtype: str
    """
    # pylint: disable=too-many-arguments, too-many-positional-arguments

    radius = str(hacc / 1000)  # km
    zoom = min(20, zoom)
    # seems to be bug in MapQuest API which causes error
    # if scalebar displayed at maximum zoom
    scalebar = "true" if zoom < 20 else "false"

    # if more than 1 location, set bounds to track extent
    if len(locations) > 1:
        comp = compress_track(locations)
        return MAPURLTRK.format(
            mqapikey,
            locations[0].lat,
            locations[0].lon,
            locations[-1].lat,
            locations[-1].lon,
            zoom,
            width,
            height,
            TRKCOL,
            f"cmp6|enc:{comp}",
            scalebar,
            maptype,
        )

    # set bounds to specified bbox extent
    if bbox is not None:
        return MAPURLBB.format(
            mqapikey,
            locations[0].lat,
            locations[0].lon,
            MARKERURL,
            zoom,
            width,
            height,
            maptype,
            scalebar,
            bbox.lat1,
            bbox.lon1,
            bbox.lat2,
            bbox.lon2,
        )

    # set bounds according to location and zoom level
    return MAPURL.format(
        mqapikey,
        locations[0].lat,
        locations[0].lon,
        MARKERURL,
        zoom,
        width,
        height,
        maptype,
        scalebar,
        radius,
        locations[0].lat,
        locations[0].lon,
    )


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
    :return: polygon as list of point tuples (lat,lon)
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

    :param list points: polygon as list of point tuples (lat, lon)
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
