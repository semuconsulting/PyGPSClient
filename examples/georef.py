"""
georef.py

Support utility for the PyGPSClient custom offline map facility
(requires PyGPSClient>=1.4.10).

Generates the necessary PyGPSClient json configuration settings
from a georeferenced raster image file e.g. geoTIFF:

python3 georef.py -I georef.tif

"usermappath_s: "/home/myuser/Downloads/geotest.tif,
"usermapcalibration_l": [53.580594705619774, -2.5136534501369447, 53.345954933075674, -1.8118214965117956],

Created on 21 Feb 2024

@author: semuadmin
"""

from argparse import ArgumentParser

from rasterio import open as openraster
from rasterio.warp import transform_bounds


def main(infile: str):
    """
    Generate config settings from georeferenced raster file.

    :param str infile: fully qualified to raster file
    """

    ras = openraster(infile)
    lonmin, latmin, lonmax, latmax = transform_bounds(
        ras.crs.to_epsg(), 4326, *ras.bounds
    )
    print(
        f'"usermappath_s": "{infile}",\n"usermapcalibration_l": {[latmax, lonmin, latmin, lonmax]},'
    )


if __name__ == "__main__":

    arp = ArgumentParser(
        description="Generates PyGPSClient json config settings for georeferenced raster file e.g. geoTIFF"
    )
    arp.add_argument(
        "-I",
        "--infile",
        required=True,
        help="fully-qualified path to georeferenced raster file",
    )

    kwargs = vars(arp.parse_args())
    main(kwargs["infile"])
