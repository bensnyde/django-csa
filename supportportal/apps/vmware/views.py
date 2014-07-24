# System
from django.http import HttpResponseForbidden
from django.shortcuts import render, get_object_or_404
# Project
from django.conf import settings
from apps.servers.models import Server
from apps.loggers.models import ErrorLogger, ActionLogger
from common.decorators import validated_request, validated_service
from common.helpers import format_ajax_response
from libs.vmware import Vsphere
# App
from .forms import MountISOForm, SnapshotPathForm, CreateSnapshotForm


@validated_request(None)
@validated_service
def get_stats(request, server_ids, server_id):
    """Get Server Stats

        Retrieves statistics from specified virtual server on remote ESX host.

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
    Paremeters
        request: HttpRequest
        server_ids: int list of servers in service
        server_id: int server id
    Returns
        HttpResponse (JSON)
            success: boolean result of API call
            message: string response message from API call
            *data:
                statistics:
    """
    if int(server_id) not in server_ids:
        ErrorLogger().log(request, "Forbidden", "User attempted access to unauthorized service in apps.vmware.views.get_stats")
        return HttpResponseForbidden()
    else:
        server = get_object_or_404(Server, pk=server_id)    

    pysph = Vsphere(settings.VMWARE["address"], settings.VMWARE["username"], settings.VMWARE["password"], server.sid)
    statistics = pysph.get_statistics()

    if statistics:
        return format_ajax_response(True, "Retrieved server statistics successfully.", {'statistics': statistics})
    else:
        ErrorLogger().log(request, "API", "API call to apps.vmware.views.get_stats failed.")
        return format_ajax_response(False, "There was a error retrieving server statistics.")


@validated_request(None)
@validated_service
def get_isos(request, server_ids, server_id):
    """Get ISO's

        Retrieves available ISO's from remote ESX server.

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
    Paremeters
        request: HttpRequest
        server_ids: int list of servers in service
        server_id: int server id
    Returns
        HttpResponse (JSON)
            success: boolean result of API call
            message: string response message from API call
            *data:
                isos:             
    """
    if int(server_id) not in server_ids:
        ErrorLogger().log(request, "Forbidden", "User attempted access to unauthorized service in apps.vmware.views.get_isos")
        return HttpResponseForbidden()
    else:
        server = get_object_or_404(Server, pk=server_id)    

    pysph = Vsphere(settings.VMWARE["address"], settings.VMWARE["username"], settings.VMWARE["password"], server.sid)
    iso_list = pysph.get_iso_list("SpursNA1-ISO")

    if iso_list:
        return format_ajax_response(True, "Retrieved ISO listing successfully.", {'isos': iso_list})
    else:
        ErrorLogger().log(request, "API", "API call to apps.vmware.views.get_isos failed.")
        return format_ajax_response(False, "There was a error retrieving available ISO's.")   


@validated_request(None)
@validated_service
def get_snapshots(request, server_ids, server_id):
    """Get Snapshots

        Retrieves current snapshots from specified virtual server on remote ESX host.

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
    Paremeters
        request: HttpRequest
        server_ids: int list of servers in service
        server_id: int server id
    Returns
        HttpResponse (JSON)
            success: boolean result of API call
            message: string response message from API call
            *data:
                snapshots:
    """
    if int(server_id) not in server_ids:
        ErrorLogger().log(request, "Forbidden", "User attempted access to unauthorized service in apps.vmware.views.get_snapshots")
        return HttpResponseForbidden()
    else:
        server = get_object_or_404(Server, pk=server_id)            

    pysph = Vsphere(settings.VMWARE["address"], settings.VMWARE["username"], settings.VMWARE["password"], server.sid)
    snapshots = pysph.get_snapshots()

    if snapshots:
        return format_ajax_response(True, "Successfully retrieved snapshots.", {'snapshots': snapshots})
    else:
        ErrorLogger().log(request, "API", "API call to apps.vmware.views.get_snapshots failed.")
        return format_ajax_response(False, "There was an error retrieving current snapshots.")  


@validated_request(None)
@validated_service
def reboot(request, server_ids, server_id):
    """Reboot virtual server

        Reboots specified guest virtual server on remote Vmware ESX host server.

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
    Paremeters
        request: HttpRequest
        server_ids: int list of servers in service
        server_id: int server id
    Returns
        HttpResponse (JSON)
            success: boolean result of API call
            message: string response message from API call
    """
    if int(server_id) not in server_ids:
        ErrorLogger().log(request, "Forbidden", "User attempted access to unauthorized service in apps.vmware.views.reboot")
        return HttpResponseForbidden()
    else:
        server = get_object_or_404(Server, pk=server_id)     

    graceful = False
    if request.POST['graceful'] == 1:
        graceful = True

    pysph = Vsphere(settings.VMWARE["address"], settings.VMWARE["username"], settings.VMWARE["password"], server.sid)
    result = pysph.reboot()

    if result:
        ActionLogger().log(request.user, "modified", "Rebooted", "vServer %s" % server.sid)
        return format_ajax_response(True, "Server rebooted successfully.")
    else:
        ErrorLogger().log(request, "API", "API call to apps.vmware.views.reboot failed.")
        return format_ajax_response(False, "There was a error rebooting the server.")
    

@validated_request(None)  
@validated_service          
def shutdown(request, server_ids, server_id):
    """Shutdown virtual server

        Shuts down specified virtual server on remote ESX server.

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
    Paremeters
        request: HttpRequest
        server_ids: int list of servers in service
        server_id: int server id
    Returns
        HttpResponse (JSON)
            success: boolean result of API call
            message: string response message from API call
    """
    if int(server_id) not in server_ids:
        ErrorLogger().log(request, "Forbidden", "User attempted access to unauthorized service in apps.vmware.views.shutdown")
        return HttpResponseForbidden()
    else:
        server = get_object_or_404(Server, pk=server_id)         
    
    graceful = False
    if request.POST['graceful'] == 1:
        graceful = True

    pysph = Vsphere(settings.VMWARE["address"], settings.VMWARE["username"], settings.VMWARE["password"], server.sid)
    result = pysph.shutdown(graceful)

    if result:
        ActionLogger().log(request.user, "modified", "Shutdown", "vServer %s" % server.sid) 
        return format_ajax_response(True, "Server shutdown successfully.")
    else:
        ErrorLogger().log(request, "API", "API call to apps.vmware.views.shutdown failed.")
        return format_ajax_response(False, "There was a error shutting down the server.")


@validated_request(None)
@validated_service
def boot(request, server_ids, server_id):
    """Boot virtual server

        Starts specified virtual server on remote ESX server.

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
    Paremeters
        request: HttpRequest
        server_ids: int list of servers in service
        server_id: int server id
    Returns
        HttpResponse (JSON)
            success: boolean result of API call
            message: string response message from API call
    """
    if int(server_id) not in server_ids:
        ErrorLogger().log(request, "Forbidden", "User attempted access to unauthorized service in apps.vmware.views.boot")
        return HttpResponseForbidden()
    else:
        server = get_object_or_404(Server, pk=server_id)    

    pysph = Vsphere(settings.VMWARE["address"], settings.VMWARE["username"], settings.VMWARE["password"], server.sid)
    result = pysph.boot()

    if result:
        ActionLogger().log(request.user, "modified", "Booted", "vServer %s" % server.sid)
        return format_ajax_response(True, "Server booted successfully.")
    else:
        ErrorLogger().log(request, "API", "API call to apps.vmware.views.boot failed.")
        return format_ajax_response(False, "There was a error booting the server.")


@validated_request(MountISOForm)
@validated_service
def mount_iso(request, server_ids, server_id):
    """Mount ISO 

        Mounts ISO image to specified virtual server on remote ESX host.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_request
            request.POST must validated against MountISOForm
            request.method must be POST
            request.is_ajax() must be True
            request.user.is_authenticated() must be True
        @validated_service
            service_id must belong to request.user.company.services
            service.vars is injected into view parameter              
    Paremeters
        request: HttpRequest
        server_ids: int list of servers in service
        server_id: int server id
    Returns
        HttpResponse (JSON)
            success: boolean result of API call
            message: string response message from API call
    """
    if int(server_id) not in server_ids:
        ErrorLogger().log(request, "Forbidden", "User attempted access to unauthorized service in apps.vmware.views.mount_iso")
        return HttpResponseForbidden()
    else:
        server = get_object_or_404(Server, pk=server_id)    

    pysph = Vsphere(settings.VMWARE["address"], settings.VMWARE["username"], settings.VMWARE["password"], server.sid)
    if request.POST["iso"] == "":
        result = pysph.unmount_iso()
    else:
        result = pysph.mount_iso('[SpursNA1-ISO] %s' % request.form.cleaned_data["iso"])

    if result:
        ActionLogger().log(request.user, "modified", "ISO %s" % request.form.cleaned_data["iso"], "vServer %s" % server.sid)
        return format_ajax_response(True, "ISO mounted successfully.")
    else:
        ErrorLogger().log(request, "API", "API call to apps.vmware.views.mount_iso failed.")
        return format_ajax_response(False, "There was a error mounting the specified ISO.")


@validated_request(SnapshotPathForm)
@validated_service
def delete_snapshot(request, server_ids, server_id):
    """Delete Snapshot

        Deletes specified snapshot from specified virtual server on remote ESX host.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_request
            request.POST must validated against SnapshotPathForm
            request.method must be POST
            request.is_ajax() must be True
            request.user.is_authenticated() must be True
        @validated_service
            service_id must belong to request.user.company.services
            service.vars is injected into view parameter              
    Paremeters
        request: HttpRequest
        server_ids: int list of servers in service
        server_id: int server id
    Returns
        HttpResponse (JSON)
            success: boolean result of API call
            message: string response message from API call
    """
    if int(server_id) not in server_ids:
        ErrorLogger().log(request, "Forbidden", "User attempted access to unauthorized service in apps.vmware.views.delete_snapshot")
        return HttpResponseForbidden()
    else:
        server = get_object_or_404(Server, pk=server_id)    

    pysph = Vsphere(settings.VMWARE["address"], settings.VMWARE["username"], settings.VMWARE["password"], server.sid)
    result = pysph.delete_snapshot(request.form.cleaned_data["path"])

    if result:
        ActionLogger().log(request.user, "deleted", "Snapshot %s" % request.form.cleaned_data["path"], "vServer %s" % server.sid)
        return format_ajax_response(True, "Snapshot deleted successfully.")
    else:
        ErrorLogger().log(request, "API", "API call to apps.vmware.views.delete_snapshot failed.")
        return format_ajax_response(False, "There was a error deleting the specified snapshot.")


@validated_request(SnapshotPathForm)
@validated_service
def revert_snapshot(request, server_ids, server_id):
    """Revert to Snapshot

        Loads specified snapshot onto specified virtual server on remote ESX host.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_request
            request.POST must validated against SnapshotPathForm        
            request.method must be POST
            request.is_ajax() must be True
            request.user.is_authenticated() must be True
        @validated_service
            service_id must belong to request.user.company.services
            service.vars is injected into view parameter              
    Paremeters
        request: HttpRequest
        server_ids: int list of servers in service
        server_id: int server id
    Returns
        HttpResponse (JSON)
            success: boolean result of API call
            message: string response message from API call
    """
    if int(server_id) not in server_ids:
        ErrorLogger().log(request, "Forbidden", "User attempted access to unauthorized service in apps.vmware.views.revert_snapshot")
        return HttpResponseForbidden()
    else:
        server = get_object_or_404(Server, pk=server_id)    

    pysph = Vsphere(settings.VMWARE["address"], settings.VMWARE["username"], settings.VMWARE["password"], server.sid)
    result = pysph.revert_snapshot(request.form.cleaned_data["path"])

    if result:
        ActionLogger().log(request.user, "modified", "Reverted snapshot %s" % request.form.cleaned_data["path"], "vServer %s" % server.sid)
        return format_ajax_response(True, "Specified snapshot loaded successfully.")
    else:
        ErrorLogger().log(request, "API", "API call to apps.vmware.views.revert_snapshot failed.")
        return format_ajax_response(False, "There was a error reverting to specified snapshot.")


@validated_request(CreateSnapshotForm)
@validated_service
def create_snapshot(request, server_ids, server_id):
    """Create Snapshot

        Creates snapshot for specified virtual server on remote ESX host.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_request
            request.POST must validated against CreateSnapshotForm        
            request.method must be POST
            request.is_ajax() must be True
            request.user.is_authenticated() must be True.
        @validated_service
            service_id must belong to request.user.company.services
            service.vars is injected into view parameter              
    Paremeters
        request: HttpRequest
        server_ids: int list of servers in service
        server_id: int server id
    Returns
        HttpResponse (JSON)
            success: boolean result of API call
            message: string response message from API call
    """
    if int(server_id) not in server_ids:
        ErrorLogger().log(request, "Forbidden", "User attempted access to unauthorized service in apps.vmware.views.create_snapshot")
        return HttpResponseForbidden()
    else:
        server = get_object_or_404(Server, pk=server_id)    

    pysph = Vsphere(settings.VMWARE["address"], settings.VMWARE["username"], settings.VMWARE["password"], server.sid)
    if pysph.get_snapshots_count() < 5:
        result = pysph.create_snapshot(request.form.cleaned_data["name"], request.form.cleaned_data["description"])

    if result:
        ActionLogger().log(request.user, "created", "snapshot %s" % request.form.cleaned_data["name"], "vServer %s" % server.sid)
        return format_ajax_response(True, "Snapshot created successfully.")
    else:
        ErrorLogger().log(request, "API", "API call to apps.vmware.views.create_snapshot failed.")
        return format_ajax_response(False, "There was an error creating the snapshot.")