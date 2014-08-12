import urllib2
import StringIO
import tempfile
import logging
from django.conf import settings
from apps.servers.models import Server
from common.decorators import validated_request
from common.helpers import format_ajax_response
from libs.zenoss import *


logger = logging.getLogger(__name__)
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
    try:
        server = __get_validated_server(request.user, service_id, server_id)
        if not server:
            raise Exception("Forbidden: specified Server does belong to specified Service.")

        graphs = []
        result =  zenoss.get_device_graphs(server.uplink, request.POST["drange"])["result"]["data"]
        for graph in result:
            graphs.append({"title": graph["title"], "url": __fetch_zenoss_graph(graph["url"])})

        return format_ajax_response(True, "Interface graphs retrieved successfully.", {'graphs': graphs})
    except Exception as ex:
        logger.error("Error fetching Zenoss uplink interface graphs: %s" % ex)
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
    try:
        server = __get_validated_server(request.user, service_id, server_id)
        if not server:
            raise Exception("Forbidden: specified Server does belong to specified Service.")

        result = zenoss.get_interface_form(server.uplink)["result"]["form"]["items"][0]["items"]
        return format_ajax_response(True, "Interface details retrieved successfully.", {'details': result})
    except Exception as ex:
        logger.error("Error fetching Zenoss uplink interface details: %s" % ex)
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
    try:
        server = __get_validated_server(request.user, service_id, server_id)
        if not server:
            raise Exception("Forbidden: specified Server does belong to specified Service.")

        result =  zenoss.get_events(server.uplink)["result"]["events"]
        return format_ajax_response(True, "Interface events retrieved successfully.", {'events': result})
    except Exception as ex:
        logger.error("Error fetching Zenoss uplink interface events: %s" % ex)
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

        with tempfile.NamedTemporaryFile(suffix=".png", dir=settings.MEDIA_ROOT, delete=False) as f:
            f.write(img)
            f.close()

            return f.name[f.name.rfind('/')+1:]
    except Exception as ex:    
        return False
