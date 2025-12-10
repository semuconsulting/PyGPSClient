"""
mapquest_handler.py

MapQuest API Constants and Methods.

MapQuest polygon compression and decompression routines
adapted from the original javascript examples:

https://developer.mapquest.com/documentation/api/static-map/
https://developer.mapquest.com/documentation/common/encode-decode/

Created on 04 May 2023

:author: semuadmin (Steve Smith)
:copyright: 2020 semuadmin
:license: BSD 3-Clause

"""

from pygpsclient.globals import Area

# MapQuest API URLS:
MAPQURL = (
    "https://www.mapquestapi.com/staticmap/v5/map?"
    + "key={key}&type={type}&size={width},{height}"
)
BBOX = "&boundingBox={lat2},{lon1},{lat1},{lon2}"  # top left, bottom right
HACC = "&shape=radius:{radius}|weight:1|fill:ccffff50|border:88888850|{lat},{lon}"
LOC = "&locations={lat},{lon}|{marker}"
LOCS = "&locations={lat1},{lon1}||{lat2},{lon2}&defaultMarker=marker-num"
LOCICON = "marker-sm-616161-ff4444"
MARGIN = "&margin={margin}"  # bbox margin (default 50)
RETINA = "@2x"  # append to size clause for double the resolution
SCALE = "&scalebar={scale}|bottom"  # true or false
TRK = "&shape=weight:2|border:{color}|{track}"
ZOOM = "&zoom={zoom}"  # zoom level 1-20

POINTLIMIT = 500  # max number of shape points supported by MapQuest API
MAPQTIMEOUT = 5
# how frequently the mapquest api is called to update the web map (seconds)
MAP_UPDATE_INTERVAL = 60
MIN_UPDATE_INTERVAL = 5
MAX_ZOOM = 20
MIN_ZOOM = 1
TRKCOL = "ff00ff"
# MapQuest static API map types ("dark" and "light" not used here)
MAP = "map"
SAT = "sat"
HYB = "hyb"


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
    locations: list,
    bbox: Area = None,
    hacc: float = 0,
) -> str:
    """
    Formats URL for web map download.

    :param str mqapikey: MapQuest API key
    :param str maptype: "map" or "sat"
    :param int width: width of canvas
    :param int height: height of canvas
    :param int zoom: zoom factor
    :param list locations: list of Points
    :param Area bbox: bounding box (will override zoom)
    :param float hacc: horizontal accuracy
    :return: formatted MapQuest URL
    :rtype: str
    """
    # pylint: disable=too-many-arguments, too-many-positional-arguments

    url = MAPQURL.format(key=mqapikey, type=maptype, width=width, height=height)
    radius = str(hacc / 1000)  # km
    zoom = min(20, zoom)

    if bbox is None:  # use location and zoom level
        url += ZOOM.format(zoom=zoom)
    else:  # use bounding box (remember upper left, bottom right)
        url += BBOX.format(
            lat2=bbox.lat2, lon1=bbox.lon1, lat1=bbox.lat1, lon2=bbox.lon2
        ) + MARGIN.format(margin=0)

    if isinstance(locations, list):  # at least one location
        if len(locations) > 1:  # multiple locations (track)
            comp = compress_track(locations)
            url += LOCS.format(
                lat1=locations[0].lat,
                lon1=locations[0].lon,
                lat2=locations[-1].lat,
                lon2=locations[-1].lon,
            ) + TRK.format(color=TRKCOL, track=f"cmp6|enc:{comp}")
        else:  # single location
            url += LOC.format(
                lat=locations[0].lat, lon=locations[0].lon, marker=LOCICON
            )

        if hacc > 0:
            url += HACC.format(
                radius=radius, lat=locations[0].lat, lon=locations[0].lon
            )

    # seems to be bug in MapQuest API which causes error
    # if scalebar displayed at maximum zoom
    url += SCALE.format(scale=("true" if zoom < 20 else "false"))

    return url


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
