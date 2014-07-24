from django.conf import settings
import urllib2
import StringIO
#from PIL import Image
import tempfile
from libs.zenoss import *
from django.http import HttpResponseForbidden, HttpResponse
from apps.servers.models import Server
from apps.loggers.models import ErrorLogger
from common.decorators import validated_request
from common.helpers import format_ajax_response



zenoss = Zenoss(settings.ZENOSS['address'], settings.ZENOSS['username'], settings.ZENOSS['password'])

@validated_request(None)
def get_interface_graphs(request, service_id, server_id):
    """Get Interface Graphs

        Retrieves graphical uplink interface stats from Zenoss for specified Server. 

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_request
            request.method must be POST
            request.is_ajax() must be True
            request.user.is_authenticated() must be True
    Parameters
        request: HttpRequest
        service_id: int service id
        server_id: int server_id
    Returns
        HttpResponse (JSON)
            success: int result status
            message: str result message
            *data:
                graphs:
                    title: str graph title
                    url: str graph url
    """
    server = __get_validated_server(request.user, service_id, server_id)
    if not server:
        ErrorLogger().log(request, "Forbidden", "User attempted access to unauthorized service in apps.zenoss.views.get_interface_graphs")
        return HttpResponseForbidden()

    try:
        graphs = []
        result =  zenoss.get_device_graphs(server.uplink, request.POST["drange"])["result"]["data"]
        for graph in result:
            graphs.append({"title": graph["title"], "url": __fetch_zenoss_graph(graph["url"])})

        return format_ajax_response(True, "Interface graphs retrieved successfully.", {'graphs': graphs})
    except Exception as ex:
        ErrorLogger().log(request, "Error", "Error fetching interface graphs in apps.zenoss.views.get_interface_graphs: %s" % ex)
        return format_ajax_response(False, "There was a problem retrieving the interface graphs.")


@validated_request(None)
def get_interface_details(request, service_id, server_id):
    """Get Interface Details

        Retrieves textual uplink interface stats from Zenoss for specified Server. 

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_request
            request.method must be POST
            request.is_ajax() must be True
            request.user.is_authenticated() must be True
    Parameters
        request: HttpRequest
        service_id: int service id
        server_id: int server_id
    Returns
        HttpResponse (JSON)
            success: int result status
            message: str result message
            *data:
                details:
                    vtype:
                    fieldLabel:
                    xtype:
                    labelStyle:
                    value:
                    disabled:
                    allowBlank:
                    anchor:
                    name:
    """    
    server = __get_validated_server(request.user, service_id, server_id)
    if not server:
        ErrorLogger().log(request, "Forbidden", "User attempted access to unauthorized server in apps.zenoss.views.get_interface_details")
        return HttpResponseForbidden(server_id)

    try:
        result = zenoss.get_interface_form(server.uplink)["result"]["form"]["items"][0]["items"]
        return format_ajax_response(True, "Interface details retrieved successfully.", {'details': result})
    except Exception as ex:
        ErrorLogger().log(request, "Error", "Error fetching interface details in apps.zenoss.views.get_interface_details: %s" % ex)
        return format_ajax_response(False, "There was an error retrieving the interface details.")


@validated_request(None)
def get_interface_events(request, service_id, server_id):
    """Get Interface Events

        Retrieves uplink interface events from Zenoss for specified Server. 

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_request
            request.method must be POST
            request.is_ajax() must be True
            request.user.is_authenticated() must be True
    Parameters
        request: HttpRequest
        service_id: int service id
        server_id: int server_id
    Returns
        HttpResponse (JSON)
            success: int result status
            message: str result message
            *data:
                events:
    """        
    server = __get_validated_server(request.user, service_id, server_id)
    if not server:
        ErrorLogger().log(request, "Forbidden", "User attempted access to unauthorized server in apps.zenoss.views.get_interface_events")
        return HttpResponseForbidden()

    try:
        result =  zenoss.get_events(server.uplink)["result"]["events"]
        return format_ajax_response(True, "Interface events retrieved successfully.", {'events': result})
    except Exception as ex:
        ErrorLogger().log(request, "Error", "Error fetching interface events in apps.zenoss.views.get_interface_events: %s" % ex)
        return format_ajax_response(False, "There was an error retrieving the interface events.")       


def __get_validated_server(user, service_id, server_id):
    try:
        # Get service vars from service_id
        service_vars = user.get_service_vars("/services/server/", service_id)
        if int(server_id) in service_vars["server_ids"]:        
            return Server.objects.get(pk=server_id)
    except:
        pass

    return False


def __fetch_zenoss_graph(image_url):
    try:
        img = urllib2.urlopen("http://radarzen.cybercon.net"+image_url).read()
#       im = Image.open(StringIO.StringIO(img))
#       im.verify()

        with tempfile.NamedTemporaryFile(suffix=".png", dir=settings.MEDIA_ROOT, delete=False) as f:
            f.write(img)
            f.close()

            return f.name[f.name.rfind('/')+1:]
    except Exception, e:    
        return str(e)    
