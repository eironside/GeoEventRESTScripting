from datetime import timedelta
import datetime
import json
import ssl
import sys
from urllib import urlencode

from arcrest.manageags import AGSAdministration
from arcrest.security.security import AGSTokenSecurityHandler
from arcrest.web._base import RedirectHandler
from future.moves.urllib import request

############## Things to change every time ################
# Input parameters for GEE host server_fqdn, port number, username/password and start/stop
server_fqdn = ""  # Input server_fqdn name (e.g. myserver.domain.com)
username = ""  # Input AGS site username
password = ""  # Input AGS user password
geeTargetInputList = []  # input a list of geoevent inputs to update the url pramater with
# Get list of all GeoEvent inputs from the REST api, copy 'Name' parameter for each output and paste into this list as a string
# If the list is empty, this script will operate on all inputs where the paramName is found (all others will be ignored)

paramName = "since"  # input the URL parameter name that should be set to the current datetime
paramType = "clientParameters"  # constant: "headers" or "clientParameters" - Use this to tell the script which parameter type to modify  
time_offset_sec = -60  # Input - the number of seconds to offset the time by (negative subtracts, positive adds). Use 0 or None to get the current time
############## Things to change every time ################

############## Defaults that rarely change ################
# Default ports used in ArcGIS
GES_PORT = "6143"
AGS_PORT = "6443"

# Default URLs used in ArcGIS
AGS_URL_TOKEN = 'https://{}:{}/arcgis/tokens/'.format(server_fqdn, AGS_PORT)
GES_URL_ADMIN = 'https://{}:{}/geoevent/admin'.format(server_fqdn, GES_PORT)
############## Defaults that rarely change ################

############## Things to change based on what you are doing ################
TIME_STRING_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

# Default API URLs
GES_URL_INPUTS = 'https://{}:{}/geoevent/admin/inputs'.format(server_fqdn, GES_PORT)
GES_URL_INPUT = 'https://{}:{}/geoevent/admin/input'.format(server_fqdn, GES_PORT)

# Default component property values 
NAME = "name"
VALUE = "value"
TRANSPORT = "transport"
PROPERTIES = "properties"
CLIENT_PARAMETERS = "clientParameters"
HEADERS = "headers"
############## Things to change based on what you are doing ################


def getNewParamValue(offset_sec=None):
    '''
    ### Update this method to calculate your new parameter value. ###
    
    returns the current UTC time as a string based on the Python strftime() method
    format is defined by the constant TIME_STRING_FORMAT
    offset_sec is in seconds and will be ADDED to the time (so use a negative to go back in time)
    '''
    utc_datetime = datetime.datetime.utcnow()
    if offset_sec is not None:
        try:
            utc_datetime = utc_datetime + +timedelta(seconds=offset_sec)
        except:
            print "failed to add {} seconds to current time".format(offset_sec)
    return utc_datetime.strftime(TIME_STRING_FORMAT)


def updateInputClientParameter(inputComponent):
    '''
    this updates the property 'clientParameters' which uses a ampersand ("&") separated list of name=value pairs
    EXAMPLE: param1=value1&param2=value2 
    '''
    print "\tLooking at {} on input named '{}'".format(CLIENT_PARAMETERS, inputComponent[NAME])
    
    # This is a transport property, so look for client parameter there
    for tprop in inputComponent[TRANSPORT][PROPERTIES]:
        if str(tprop[NAME]).lower() == CLIENT_PARAMETERS.lower():
            clientParametersValue = tprop[VALUE]
            preParams, discard = str(clientParametersValue).split(paramName)
            discard = discard.split("&", 1)
            postParams = ""
            if len(discard) > 1:
                postParams = "&{}".format(discard[1])
            newUrlParamValue = getNewParamValue(time_offset_sec)
            print "\tUpdating {} '{}' URL parameter value {} to {}".format(CLIENT_PARAMETERS, paramName, discard[0], newUrlParamValue)
            clientParametersValue = "{}{}={}{}".format(preParams, paramName, newUrlParamValue, postParams)
            tprop[VALUE] = clientParametersValue
            break  # only updating one parameter
    
    return inputComponent


def updateInputHeader(inputComponent):
    '''
    this updates the property 'headers' which uses a comma separated list of name:value pairs 
    EXAMPLE: param1:value1,param2:value2
    '''
    print "\tLooking at {} on input named '{}'".format(HEADERS, inputComponent[NAME])
    
    # This is a transport property, so look for client parameter there
    for tprop in inputComponent[TRANSPORT][PROPERTIES]:
        if str(tprop[NAME]).lower() == HEADERS.lower():
            headParametersValue = tprop[VALUE]
            preParams, discard = str(headParametersValue).split(paramName)
            discard = discard.split(",", 1)
            postParams = ""
            if len(discard) > 1:
                postParams = ",{}".format(discard[1])
            newHeadParamValue = getNewParamValue(time_offset_sec)
            print "\tUpdating {} '{}' header parameter value {} to {}".format(CLIENT_PARAMETERS, paramName, discard[0], newHeadParamValue)
            headParametersValue = "{}{}:{}{}".format(preParams, paramName, newHeadParamValue, postParams)
            tprop[VALUE] = headParametersValue
            break  # only updating one parameter
    
    return inputComponent


def Main():
    # Get GeoEvent token to access admin API
    sh = AGSTokenSecurityHandler(username=username,
                                password=password,
                                org_url=AGS_URL_TOKEN,
                                token_url=AGS_URL_TOKEN,  # token URL for AGS
                                proxy_url=None,
                                proxy_port=None)
    sh.referer_url = GES_URL_ADMIN  # need to set the referrer to generate token correctly

    if sh.token is not None:
        # Instantiate the AGS admin object
        ags = AGSAdministrationPut(url=GES_URL_ADMIN,
                                securityHandler=sh,
                                proxy_url=None,
                                proxy_port=None)
        
        # use a get() method to get the requested component json 
        componentList = ags._get(url=GES_URL_INPUTS, securityHandler=sh)
        for component in componentList:
            if len(geeTargetInputList) > 0 and not any(component[NAME] in s for s in geeTargetInputList):
                # we arn't interested in this item so 
                continue
            else:
                # geeTargetInputList is either empty or we care about this input
                if paramType == CLIENT_PARAMETERS:
                    updatedInput = updateInputClientParameter(component)
                elif paramType == HEADERS:
                    updatedInput = updateInputHeader(component)
                
                ags._put(url=GES_URL_INPUT, securityHandler=sh, param_dict=updatedInput)
                try:
                    print "Updated {} '{}' parameter on input named {}".format(CLIENT_PARAMETERS, paramName, component[NAME])
                except:
                    print "Failed to update input"
        del ags, sh, componentList
    else:
        print "Unable to get token, check username, password, referer url and token url"
        del sh
        sys.exit(1)


class AGSAdministrationPut(AGSAdministration):
    '''
    Adds the PUT method to the AGS administration class.
    '''

    def _put(self, url,
              param_dict=None,
              securityHandler=None,
              additional_headers=None,
              proxy_url=None,
              proxy_port=80,
              compress=True):
        """
        Performs a put operation on a URL.
        Inputs:
           param_dict - key/preParams pair of values that will be turned into a json string
              ex: {"foo": "bar"}
           securityHandler - object that handles the token or other site
              security.  It must inherit from the base security class.
              ex: arcrest.AGOLSecurityHandler("SomeUsername", "SOMEPASSWORD")
           additional_headers - are additional key/preParams headers that a user
              wants to pass during the operation.
              ex: {"accept-encoding": "gzip"}
           proxy_url - url of the proxy
           proxy_port - default 80, port number of the proxy
           compress - default true, determines if gzip should be used of not for
              the web operation.
        Output:
           returns dictionary or string depending on web operation.
        """

        # ensure that no spaces are in the url
        url = url.replace(" ", "%20")
        
        if param_dict is None:
            param_dict = {}
        if additional_headers is None:
            additional_headers = {}
        if self._verify == False and \
           sys.version_info[0:3] >= (2, 7, 9) and \
            hasattr(ssl, 'create_default_context'):
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
        
        headers = {
            "User-Agent": self.useragent,
            'Accept': '*/*',
            'Content-type':'application/json'
        }
        if securityHandler and securityHandler.referer_url:
            headers['referer'] = securityHandler.referer_url
#         opener = None
#         return_value = None
        handlers = [RedirectHandler()]
        param_dict, handler, cj = self._processHandler(securityHandler, param_dict)
        if handler is not None:
            handlers.append(handler)
        if cj is not None:
            handlers.append(request.HTTPCookieProcessor(cj))
        if compress:
            headers['Accept-Encoding'] = 'gzip'
        else:
            headers['Accept-Encoding'] = ''
        for k, v in additional_headers.items():
            headers[k] = v
            del k, v
        hasContext = 'context' in self._has_context(request.urlopen)
        if self._verify == False and \
           sys.version_info[0:3] >= (2, 7, 9) and \
            hasattr(ssl, 'create_default_context'):
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

        opener = request.build_opener(*handlers)
        opener.addheaders = [(k, v) for k, v in headers.items()]
        request.install_opener(opener)
        
        data = urlencode(param_dict)
        if self.PY3:
            data = data.encode('ascii')
        data = json.dumps(param_dict)
        opener.data = data
        
#         request.get_method = lambda: 'PUT'
        req = request.Request("{}?token={}".format(self._asString(url), self._securityHandler.token),
                              data=data,
                              headers=headers)
        req.get_method = lambda: 'PUT'
        
        for k, v in headers.items():
            req.add_header(k, v)
        if hasContext and self._verify == False:
            resp = request.urlopen(req, context=ctx)
        else:
            resp = request.urlopen(req)

        self._last_code = resp.getcode()
        self._last_url = resp.geturl()
        return_value = self._process_response(resp=resp)
        
        if isinstance(return_value, dict):
            if "error" in return_value and \
               'message' in return_value['error']:
                if return_value['error']['message'].lower() == 'request not made over ssl':
                    if url.startswith('http://'):
                        url = url.replace('http://', 'https://')
                        return self._put(url,
                                          param_dict,
                                          securityHandler,
                                          additional_headers,
                                          proxy_url,
                                          proxy_port,
                                          compress)
            return return_value
        else:
            return return_value
        return return_value


if __name__ == '__main__':    
    Main()

