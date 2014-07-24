# System
from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404
import json
# Project
from common.helpers import format_ajax_response
from apps.servers.models import Server
from apps.loggers.models import ErrorLogger, ActionLogger
from common.decorators import validated_request, validated_service
from libs.solusvm import SolusVM
# App
from .forms import BootOrderForm, HostnameForm, MountISOForm


solus = SolusVM(settings.SOLUSVM["address"], settings.SOLUSVM["id"], settings.SOLUSVM["key"])

@validated_request(None)
@validated_service
def get_details(request, server_ids, server_id):
    """Get Virtual Server Stats

        Retrieves Virtual Server statistics, state and vnc information from SolusVM server.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_request
            request.method must be POST
            request.is_ajax() must be True
            request.user.is_authenticated() must be True
        @validated_service
            service_id must belong to request.user.company.services
            service.vars is injected into view parameter              
    Parameters    
        request: HttpRequest
        server_ids: int[] services servers
        server_id: int server id 
    Returns
        HttpResponse (JSON)
            success: int status result of API call
            message: str response message from API call
            *data:
                state: 
                statistics:
                vnc:
    """
    if int(server_id) not in server_ids:
        ErrorLogger().log(request, "Forbidden", "User attempted access to unauthorized service in apps.solusvm.views.get_details")
        return HttpResponseForbidden()
    else:
        server = get_object_or_404(Server, pk=server_id)
     
    stats = solus.virtualServerInfo(server.sid)
    state = solus.virtualServerState(server.sid)
    vnc = solus.vncInfo(server.sid)

    if "status" in stats and stats["status"] == "success": 
        return format_ajax_response(True, "Server details retrieved successfully.", {'state':state, 'statistics':stats, 'vnc':vnc})
    else:
        ErrorLogger().log(request, "API", "API call to apps.solusvm.views.get_details failed: %s" % stats)
        return format_ajax_response(False, "There was an error retrieving server stats.")


@validated_request(None)
@validated_service
def get_isos(request, server_ids):
    """Get ISO's

        Retrieves list of ISO's available on remote SolusVM server.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_request
            request.method must be POST
            request.is_ajax() must be True
            request.user.is_authenticated() must be True
        @validated_service
            service_id must belong to request.user.company.services
            service.vars is injected into view parameter              
    Parameters    
        request: HttpRequest
        server_ids: int[] server id 
    Returns
        HttpResponse (JSON)
            success: int status result of API call
            message: str response message from API call
            *data:
                isos: str[] iso filename
    """      
    try:
        iso_list = solus.listISO()
        return format_ajax_response(True, "ISO listing retrieved successfully.", {'isos': iso_list})
    except Exception as ex:
        ErrorLogger().log(request, "Error", "Error retrieving ISO listing in apps.solusvm.views.get_isos: %s" % ex)
        return format_ajax_response(False, "There was an error retrieving ISO listing.")
   


@validated_request(None)
@validated_service
def reboot(request, server_ids, server_id):
    """Reboot virtual server

        Reboots specified virtual server on remote SolusVM server.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_request
            request.method must be POST
            request.is_ajax() must be True
            request.user.is_authenticated() must be True
        @validated_service
            service_id must belong to request.user.company.services
            service.vars is injected into view parameter              
    Parameters    
        request: HttpRequest
        server_ids: int[] service's server ids
        server_id: int server id 
    Returns
        HttpResponse (JSON)
            success: int status result of API call
            message: str response message from API call
    """
    if int(server_id) not in server_ids:
        ErrorLogger().log(request, "Forbidden", "User attempted access to unauthorized service in apps.solusvm.views.reboot")
        return HttpResponseForbidden()
    else:
        server = get_object_or_404(Server, pk=server_id)    
   
    result = solus.rebootVirtualServer(server.sid)

    if "status" in result and result["status"] == "success": 
        ActionLogger().log(request.user, "modified", "Reboot", "vServer %s" % server.sid)
        return format_ajax_response(True, "Server rebooted successfully.")
    else:
        ErrorLogger().log(request, "API", "API call to apps.solusvm.views.reboot failed: %s" % result)
        return format_ajax_response(False, "There was an error rebooting the server.")


@validated_request(None)
@validated_service
def shutdown(request, server_ids, server_id):
    """Shut down virtual server

        Shuts down specified virtual server on remote SolusVM server.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_request
            request.method must be POST
            request.is_ajax() must be True
            request.user.is_authenticated() must be True
        @validated_service
            service_id must belong to request.user.company.services
            service.vars is injected into view parameter              
    Parameters    
        request: HttpRequest
        server_ids: int[] service's server ids
        server_id: int server id 
    Returns
        HttpResponse (JSON)
            success: int status result of API call
            message: str response message from API call
    """
    if int(server_id) not in server_ids:
        ErrorLogger().log(request, "Forbidden", "User attempted access to unauthorized service in apps.solusvm.views.shutdown")
        return HttpResponseForbidden()
    else:
        server = get_object_or_404(Server, pk=server_id) 
          
    result = solus.shutdownVirtualServer(server.sid)

    if "status" in result and result["status"] == "success": 
        ActionLogger().log(request.user, "modified", "Shutdown", "vServer %s" % server.sid)
        return format_ajax_response(True, "Server shutdown successfully.")
    else:
        ErrorLogger().log(request, "API", "API call to apps.solusvm.views.shutdown failed: %s" % result)
        return format_ajax_response(False, "There was an error shutting down the server.")     


@validated_request(None)
@validated_service
def boot(request, server_ids, server_id):
    """Boots virtual server

        Boots specified virtual server on remote SolusVM server.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_request
            request.method must be POST
            request.is_ajax() must be True
            request.user.is_authenticated() must be True
        @validated_service
            service_id must belong to request.user.company.services
            service.vars is injected into view parameter              
    Parameters    
        request: HttpRequest
        server_ids: int[] service's server ids
        server_id: int server id 
    Returns
        HttpResponse (JSON)
            success: int status result of API call
            message: str response message from API call    
    """
    if int(server_id) not in server_ids:
        ErrorLogger().log(request, "Forbidden", "User attempted access to unauthorized service in apps.solusvm.views.boot")
        return HttpResponseForbidden()
    else:
        server = get_object_or_404(Server, pk=server_id) 

    result = solus.bootVirtualServer(server.sid)

    if "status" in result and result["status"] == "success": 
        ActionLogger().log(request.user, "modified", "Booted", "vServer %s" % server.sid)
        return format_ajax_response(True, "Server booted successfully.")
    else:
        ErrorLogger().log(request, "API", "API call to apps.solusvm.views.boot failed: %s" % result)
        return format_ajax_response(False, "There was an error booting the server.")      


@validated_request(HostnameForm)
@validated_service
def set_hostname(request, server_ids, server_id):
    """Sets virtual server's hostname

        Sets the hostname for specified virtual server on remote SolusVM server.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_request
            request.POST must validate against HostnameForm
            request.method must be POST
            request.is_ajax() must be True
            request.user.is_authenticated() must be True   
        @validated_service
            service_id must belong to request.user.company.services
            service.vars is injected into view parameter                       
    Parameters    
        request: HttpRequest
            hostname: str hostname
        server_ids: int[] service's server ids
        server_id: int server id 
    Returns
        HttpResponse (JSON)
            success: int status result of API call
            message: str response message from API call     
    """
    if int(server_id) not in server_ids:
        ErrorLogger().log(request, "Forbidden", "User attempted access to unauthorized service in apps.solusvm.views.set_hostname")
        return HttpResponseForbidden()
    else:
        server = get_object_or_404(Server, pk=server_id) 

    result = solus.changeHostname(server.sid, request.form.cleaned_data['hostname'])

    if "status" in result and result["status"] == "success": 
        ActionLogger().log(request.user, "modified", "Hostname %s" % request.form.cleaned_data['hostname'],"vServer %s" % server.sid)
        return format_ajax_response(True, "Server hostname set successfully.")
    else:

        ErrorLogger().log(request, "API", "API call to apps.solusvm.views.set_hostname failed: %s" % result)
        return format_ajax_response(False, "There was an error setting the hostname.")             


@validated_request(MountISOForm)
@validated_service
def mount_iso(request, server_ids, server_id):
    """Mount ISO

        Mounts specified ISO image to specified virtual server on remote SolusVM server.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_request
            request.POST must validate against MountISOForm
            request.method must be POST
            request.is_ajax() must be True
            request.user.is_authenticated() must be True   
        @validated_service
            service_id must belong to request.user.company.services
            service.vars is injected into view parameter                       
    Parameters    
        request: HttpRequest
            iso: str iso filename
        server_ids: int[] service's server ids
        server_id: int server id 
    Returns
        HttpResponse (JSON)
            success: int status result of API call
            message: str response message from API call        
    """
    if int(server_id) not in server_ids:
        ErrorLogger().log(request, "Forbidden", "User attempted access to unauthorized service in apps.solusvm.views.mount_iso")
        return HttpResponseForbidden()
    else:
        server = get_object_or_404(Server, pk=server_id) 

    if request.form.cleaned_data["iso"] == "none":
        result = solus.unmountISO(server.sid)
    else:
        result = solus.mountISO(server.sid, request.form.cleaned_data['iso'])

    if "status" in result and result["status"] == "success": 
        ActionLogger().log(request.user, "modified", "ISO %s" % request.form.cleaned_data['iso'],"vServer %s" % server.sid)
        return format_ajax_response(True, "ISO mounted successfully.")
    else:
        ErrorLogger().log(request, "API", "API call to apps.solusvm.views.mount_iso failed: %s" % result)
        return format_ajax_response(False, "There was an error mounting the ISO.")         
        

@validated_request(BootOrderForm)
@validated_service
def set_bootorder(request, server_ids, server_id):
    """Set bootorder

        Sets the bootorder for specified virtual server on remote SolusVM server.
    
    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_request
            request.POST must validate against BootOrderForm
            request.method must be POST
            request.is_ajax() must be True
            request.user.is_authenticated() must be True   
        @validated_service
            service_id must belong to request.user.company.services
            service.vars is injected into view parameter                       
    Paremeters
        request: HttpRequest
            bootorder: str boot order (c, d, cd, dc)
        server_ids: int[] service's server ids
        server_id: int server id 
    Returns
        HttpResponse (JSON)
            success: int status result of API call
            message: str response message from API call
    """
    if int(server_id) not in server_ids:
        ErrorLogger().log(request, "Forbidden", "User attempted access to unauthorized service in apps.solusvm.views.set_bootorder")
        return HttpResponseForbidden()
    else:
        server = get_object_or_404(Server, pk=server_id) 

    result = solus.changeBootOrder(server.sid, request.form.cleaned_data['bootorder'])

    if "status" in result and result["status"] == "success": 
        ActionLogger().log(request.user, "modified", "Bootorder %s" % request.form.cleaned_data['bootorder'],"vServer %s" % server.sid)
        return format_ajax_response(True, "Server bootorder updated successfully.")
    else:
        ErrorLogger().log(request, "API", "API call to apps.solusvm.views.set_bootorder failed: %s" % result)
        return format_ajax_response(False, "There was an error setting the bootorder.")