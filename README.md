# GeoEventRESTScripting
A place to stash information and scripts for automating the GeoEvent REST and ADMIN API.

To run these, you need to install the ArcREST python site-package found on github here: https://github.com/Esri/ArcREST 

The library is easy enough to install on your system:
1.	Open command prompt and cd into the python scripts directory (e.g. C:\Python27\ArcGISx6410.6\Scripts)
2.	Type ‘pip install arcrest_package’ and hit enter

The ArcREST package is deprecated, BUT it runs against Python 2.7 which is still installed by ArcGIS Server. For now, I’m going to keep using it because I don’t want to have to install conda, python 3x, and/or ArcGIS Pro just to be able to run the new ArcGIS Python API (https://github.com/Esri/arcgis-python-api). 

The only major downside is that it can’t do a ‘PUT’ so I had to add that to the some of the scripts that needed it (not very elegant, but it works).

