"""
georef.py

Support utility for the PyGPSClient custom offline map facility
(requires PyGPSClient>=1.4.10 and rasterio>=1.3.6).

Generates the necessary PyGPSClient json configuration settings
from one or more georeferenced raster image files e.g. geoTIFF:

Usage:

python3 georef.py -I mymap01.tif,mymap02.tif,mymap03.tif

"usermaps_l": [
   [
      "/home/myuser/maps/mymap01.tif",
      [52.48903090029343, 13.376796709434993, 52.428992219505325, 13.513273402895]
   ],
   [
      "/home/myuser/maps/mymap02.tif",
      [52.43227595237385, 13.499564532600285, 52.37215985772205, 13.636041225870589]
   ],
   [
      "/home/myuser/maps/mymap03.tif",
      [52.37776419675291, 13.625147570124257, 52.31757380344052, 13.761624263584265]
   ]
]

Created on 21 Feb 2024

@author: semuadmin
"""

from argparse import ArgumentParser
from os.path import abspath

from rasterio import open as openraster
from rasterio.warp import transform_bounds


def main(infiles: str):
    """
    Generate config settings from georeferenced raster file.

    :param str infiles: comma-separated list of file paths
    """

    files = infiles.split(",")
    print('"usermaps_l": [')
    for i, fl in enumerate(files):
        fl = fl.strip()
        ras = openraster(fl)
        lonmin, latmin, lonmax, latmax = transform_bounds(
            ras.crs.to_epsg(), 4326, *ras.bounds
        )
        print(
            f'   [\n      "{abspath(fl)}",\n      {[latmax, lonmin, latmin, lonmax]}\n   ]{"," if i < len(files)-1 else ""}'
        )
    print("]")


if __name__ == "__main__":

    arp = ArgumentParser(
        description="Generates PyGPSClient json config settings for one or more georeferenced raster files e.g. geoTIFF"
    )
    arp.add_argument(
        "-I",
        "--infiles",
        required=True,
        help="comma-separated list of file paths",
    )

    kwargs = vars(arp.parse_args())
    main(kwargs["infiles"])
