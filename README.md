# GeoEventRESTScripting
A place to stash information and scripts for automating the GeoEvent REST and ADMIN API.

To run these, you need to install the ArcREST python site-package found on github here: https://github.com/Esri/ArcREST 

The library is easy enough to install on your system:
1.	Open command prompt and cd into the python scripts directory (e.g. C:\Python27\ArcGISx6410.6\Scripts)
2.	Type ‘pip install arcrest_package’ and hit enter

The ArcREST package is deprecated, BUT it runs against Python 2.7 which is still installed by ArcGIS Server. For now, I’m going to keep using it because I don’t want to have to install conda, python 3x, and/or ArcGIS Pro just to be able to run the new ArcGIS Python API (https://github.com/Esri/arcgis-python-api). 

The only major downside is that it can’t do a ‘PUT’ so I had to add that to the some of the scripts that needed it (not very elegant, but it works).

## StopGEEOutputs
This script is an update of Andy Ommen's script that starts or stops a targeted set of outputs on the GeoEvent Server.

https://community.esri.com/people/aommen-esristaff/blog/2016/10/19/scripting-tasks-using-the-geoevent-admin-api

## UpdateGEEInputURLParam
This script will iterate through your inputs (or a targeted list of inputs) and update a URL Property on any input that implements the HTTP Transport.  As written, the script will update the value of a 'since' parameter to the current time minus one minute. This could be used in places where a server is expecting you to provide a time value from which you want it to send you data.  

Using a scheduler (such as Windows Task Scheduler) you could set this up to run on an hourly basis so the remote server will only send the last hours worth of data.

## UpdateGEEInputURLorHeaderParam
This script will iterate through your inputs (or a targeted list of inputs) and update either a Header or a URL Property on any input that implements the HTTP Transport.  Use ```paramType = "headers"``` to update a header property or ```paramType = "clientParameters"``` to update a URL Property. As written, the script will update the value of a 'since' parameter to the current time minus one minute. This could be used in places where a server is expecting you to provide a time value from which you want it to send you data.

Using a scheduler (such as Windows Task Scheduler) you could set this up to run on an hourly basis so the remote server will only send the last hours worth of data.
