
#-------------------------------------------------------------------------------
# Name:        StopGEEOutputs.py
# Purpose:
#
# Author:      Andy Ommen
#
# Created:     13/10/2016
# Copyright:   (c) andy4181 2016
#-------------------------------------------------------------------------------
import traceback, inspect, sys
# Import ArcREST security and Admin modules
from arcrest.manageags import AGSAdministration
from arcrest.security.security import AGSTokenSecurityHandler


# Input parameters for GEE host server_fqdn, port number, username/password and start/stop
server_fqdn = ""  # Input - server_fqdn name (e.g. myserver.domain.com)
username = ""  # Input - AGS site username
password = ""  # Input - AGS user password
runType = "stop"  # Input - either start or stop
# Input - Get list of all GeoEvent outputs to stop/start, copy Name parameter for each output and paste into list
outputLst = ["be427604-b07e-4e3b-88c1-3c8ebbb9c30b"]

GES_PORT = "6143"
def trace():
    """
        trace finds the line, the filename
        and error message and returns it
        to the user
    """
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]
    filename = inspect.getfile(inspect.currentframe())
    # script name + line number
    line = tbinfo.split(", ")[1]
    # Get Python syntax error
    #
    synerror = traceback.format_exc().splitlines()[-1]
    return line, filename, synerror


def main(typ):
    if typ.lower() == 'stop':
        updateInputs(server_fqdn, GES_PORT, username, password, outputLst)
    else:
        startOutputs(server_fqdn, GES_PORT, username, password, outputLst)


def updateInputs(srv, prt, usr, pwd, outLst):
    try:
        # GeoEvent admin URL
        geeUrl = 'https://{}:{}/geoevent/admin'.format(srv, prt)
        # Get GeoEvent token to access admin API
        sh = AGSTokenSecurityHandler(username=usr,
                                    password=pwd,
                                    org_url=geeUrl,
                                    token_url='https://{}:6443/arcgis/tokens/'.format(srv),  # token URL for AGS
                                    proxy_url=None,
                                    proxy_port=None)
        sh.referer_url = geeUrl  # need to set the referrer to generate token correctly

        if sh.token is not None:
            # Instantiate the AGS admin object
            ags = AGSAdministration(url=geeUrl,
                                    securityHandler=sh,
                                    proxy_url=None,
                                    proxy_port=None)

            for output in outLst:
                getInputsUrl = 'https://{}:{}/geoevent/admin/output/{}/stop'.format(srv, prt, output)
                ags._get(url=getInputsUrl, securityHandler=sh)  # _get method uses the stop URL and the token to stop the output
                print "{} Stopped successfully".format(output)
            del ags, sh
        else:
            print "Unable to get token, check username, password and token url"
            del sh
            sys.exit(1)

    except Exception:
        line, filename, synerror = trace()
        print "error on line: %s" % line
        print "error in file name: %s" % filename
        print "with error message: %s" % synerror


def startOutputs(srv, prt, usr, pwd, outLst):
    try:
        # GeoEvent admin URL
        geeUrl = 'https://{}:{}/geoevent/admin'.format(srv, prt)
        # Get the AGS token to pass to GEE
        sh = AGSTokenSecurityHandler(username=usr,
                                    password=pwd,
                                    org_url=geeUrl,
                                    token_url='https://{}:6443/arcgis/tokens/'.format(srv),
                                    proxy_url=None,
                                    proxy_port=None)

        if sh.token is not None:
            # Build the AGS admin object
            ags = AGSAdministration(url=geeUrl,
                                    securityHandler=sh,
                                    proxy_url=None,
                                    proxy_port=None)

            for output in outLst:
                startUrl = 'https://{}:{}/geoevent/admin/output/{}/start/'.format(srv, prt, output)
                ags._get(url=startUrl, securityHandler=sh)  # _get method uses the start URL and the token to start the output
                print "{} Started successfully".format(output)
            del ags, sh
        else:
            print "Unable to get token, check username, password and token url"
            del sh
            sys.exit(1)

    except Exception:
        line, filename, synerror = trace()
        print "error on line: %s" % line
        print "error in file name: %s" % filename
        print "with error message: %s" % synerror


if __name__ == '__main__':
    main(runType)
