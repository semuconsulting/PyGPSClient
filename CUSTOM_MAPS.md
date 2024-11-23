# How to create a custom offline map for PyGPSClient's Map and GPX Viewers

### We use and recommend the free, open-source [QGIS software](https://qgis.org/download/), which is available for most platforms including Windows, MacOS and Linux.

1. Download and install QGIS. The latest LTR version at time of writing is 3.34. It's a relatively large package and the install may take a minute or so. **NB**: If you're installing on MacOS Sequoia or newer, note the "Tips for first launch".
1. Open QGIS and select from the top menu bar **Project..Properties..CRS** (*Coordinate Reference System*). Search for, select and apply CRS "**EPSG:4326 WGS84**". This will display map extent as latitude and longitude rather than the default meters (*other suitable CRSs are available but this is the de facto standard used by PyGPSClient*).

   ![QGIS CRS Selection](/images/QGIS_crs.png?raw=true)

1. Navigate to the left hand browser and select **XYZ Tiles..OpenStreetMap** (*OpenStreetMap is available as standard in recent versions of QGIS - previously it was available as an optional plugin*). Please note that OpenStreetMap is open data, licensed under the [Open Data Commons Open Database License](https://opendatacommons.org/licenses/odbl/) (ODbL) by the [OpenStreetMap Foundation](https://osmfoundation.org/) (OSMF). If you have imported your own XYZ data source, you can also use this.
1. Shift and zoom into the area of interest. Toggle the '**Coordinate/Extents**' display in the bottommost status bar to show the current map extent.

   ![QGIS Screenshot](/images/QGIS_screenshot.png?raw=true)

1. When you reach the desired extent, select from the top menu bar **Project..Import/Export..Export Map to Image...**.
1. Accept all the defaults in the "Save Map as Image" pop-up box. **Ensure the "Append Georeference Information" option is ticked**. If necessary, make a note of the map extent.

   ![QGIS Save Map Popup](/images/QGIS_savemap.png?raw=true)

1. Save the map as a geoTIFF (*.tif) file.

You can now import the saved image into PyGPSClient using **Options..Import Custom Map**. If the Python `rasterio` library is installed, the map extent will be extracted automatically - otherwise, it must be entered manually.

**FYI:** Installing QGIS using the default settings also installs the GDAL (*Geospatial Data Abstraction Library*) package, which is a dependency for the `rasterio` library (*though it can also be installed separately*).
