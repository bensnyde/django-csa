# System
import logging
# Project
from django.conf import settings
from apps.servers.models import Server
from apps.loggers.models import ActionLogger
from common.decorators import validated_request, validated_service
from common.helpers import format_ajax_response
from libs.vmware import Vsphere
# App
from .forms import MountISOForm, SnapshotPathForm, CreateSnapshotForm


logger = logging.getLogger(__name__)


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
    try:
        if int(server_id) not in server_ids:
            raise Exception("Forbidden: specified Server does not belong to specified Service.")

        server = Server.objects.get(pk=server_id)     

        pysph = Vsphere(settings.VMWARE["address"], settings.VMWARE["username"], settings.VMWARE["password"], server.sid)
        statistics = pysph.get_statistics()

        if statistics:
            return format_ajax_response(True, "Retrieved server statistics successfully.", {'statistics': statistics})
        else:
            raise Exception("Pysphere's get_statistics() returned False.")
    except Exception as ex:
        logger.error("Failed to get_stats: %s" % ex)
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
    try:
        if int(server_id) not in server_ids:
            raise Exception("Forbidden: specified Server does not belong to specified Service.")

        server = Server.objects.get(pk=server_id)    

        pysph = Vsphere(settings.VMWARE["address"], settings.VMWARE["username"], settings.VMWARE["password"], server.sid)
        iso_list = pysph.get_iso_list(settings.VMWARE["iso_datastore"])

        if iso_list:
            return format_ajax_response(True, "Retrieved ISO listing successfully.", {'isos': iso_list})
        else:
            raise Exception("Pysphere's get_iso_list(%s) returned False." % settings.VMWARE["iso_datastore"])
    except Exception as ex:
        logger.error("Failed to get_iso_list: %s" % ex)
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
    try:
        if int(server_id) not in server_ids:
            raise Exception("Forbidden: specified Server does not belong to specified Service.")

        server = Server.objects.get(pk=server_id)             

        pysph = Vsphere(settings.VMWARE["address"], settings.VMWARE["username"], settings.VMWARE["password"], server.sid)
        snapshots = pysph.get_snapshots()

        if snapshots:
            return format_ajax_response(True, "Successfully retrieved snapshots.", {'snapshots': snapshots})
        else:
            raise Exception("Pysphere's get_snapshots() returned False.")
    except Exception as ex:
        logger.error("Failed to get_snapshots: %s" % ex)
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
    try:
        if int(server_id) not in server_ids:
            raise Exception("Forbidden: specified Server does not belong to specified Service.")

        server = Server.objects.get(pk=server_id)    

        graceful = (False, True)[request.POST["graceful"]==1]

        pysph = Vsphere(settings.VMWARE["address"], settings.VMWARE["username"], settings.VMWARE["password"], server.sid)
        result = pysph.reboot()

        if result:
            ActionLogger().log(request.user, "modified", "Rebooted", "vServer %s" % server.sid)
            return format_ajax_response(True, "Server rebooted successfully.")
        else:
            raise Exception("Pysphere's reboot() returned False.")
    except Exception as ex:
        logger.error("Failed to reboot: %s" % ex)
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
    try:
        if int(server_id) not in server_ids:
            raise Exception("Forbidden: specified Server does not belong to specified Service.")

        server = Server.objects.get(pk=server_id)    

        graceful = (False, True)[request.POST["graceful"]==1]

        pysph = Vsphere(settings.VMWARE["address"], settings.VMWARE["username"], settings.VMWARE["password"], server.sid)
        result = pysph.shutdown(graceful)

        if result:
            ActionLogger().log(request.user, "modified", "Shutdown", "vServer %s" % server.sid) 
            return format_ajax_response(True, "Server shutdown successfully.")
        else:
            raise Exception("Pysphere's shutdown(%s) returned False." % graceful)
    except Exception as ex:
        logger.error("Failed to shutdown: %s" % ex)
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
    try:
        if int(server_id) not in server_ids:
            raise Exception("Forbidden: specified Server does not belong to specified Service.")

        server = Server.objects.get(pk=server_id)    

        pysph = Vsphere(settings.VMWARE["address"], settings.VMWARE["username"], settings.VMWARE["password"], server.sid)
        result = pysph.boot()

        if result:
            ActionLogger().log(request.user, "modified", "Booted", "vServer %s" % server.sid)
            return format_ajax_response(True, "Server booted successfully.")
        else:
            raise Exception("Pysphere's boot() returned False.")
    except Exception as ex:
        logger.error("Failed to boot: %s" % ex)
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
    try:
        if int(server_id) not in server_ids:
            raise Exception("Forbidden: specified Server does not belong to specified Service.")

        server = Server.objects.get(pk=server_id)       

        pysph = Vsphere(settings.VMWARE["address"], settings.VMWARE["username"], settings.VMWARE["password"], server.sid)

        if request.POST["iso"] == "":
            result = pysph.unmount_iso()
        else:
            iso = "[%s] %s" % (settings.VMWARE["iso_datastore"], request.form.cleaned_data["iso"]) 
            result = pysph.mount_iso(iso)

        if result:
            ActionLogger().log(request.user, "modified", "ISO %s" % request.form.cleaned_data["iso"], "vServer %s" % server.sid)
            return format_ajax_response(True, "ISO mounted successfully.")
        else:
            raise Exception(("Pysphere's mount_iso(%s) returned False." % iso, "Pysphere's unmount_iso() returned False.")[reqeust.POST["iso"]==""])
    except Exception as ex:
        logger.error("Failed to mount_iso: %s" % ex)
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
    try:
        if int(server_id) not in server_ids:
            raise Exception("Forbidden: specified Server does not belong to specified Service.")

        server = Server.objects.get(pk=server_id)      

        pysph = Vsphere(settings.VMWARE["address"], settings.VMWARE["username"], settings.VMWARE["password"], server.sid)
        result = pysph.delete_snapshot(request.form.cleaned_data["path"])

        if result:
            ActionLogger().log(request.user, "deleted", "Snapshot %s" % request.form.cleaned_data["path"], "vServer %s" % server.sid)
            return format_ajax_response(True, "Snapshot deleted successfully.")
        else:
            raise Exception("Pysphere's delete_snapshot(%s) returned False." % request.form.cleaned_data["path"])
    except Exception as ex:
        logger.error("Failed to delete_snapshot: %s" % ex)
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
    try:
        if int(server_id) not in server_ids:
            raise Exception("Forbidden: specified Server does not belong to specified Service.")

        server = Server.objects.get(pk=server_id)   

        pysph = Vsphere(settings.VMWARE["address"], settings.VMWARE["username"], settings.VMWARE["password"], server.sid)
        result = pysph.revert_snapshot(request.form.cleaned_data["path"])

        if result:
            ActionLogger().log(request.user, "modified", "Reverted snapshot %s" % request.form.cleaned_data["path"], "vServer %s" % server.sid)
            return format_ajax_response(True, "Specified snapshot loaded successfully.")
        else:
            raise Exception("Pysphere's revert_snapshot(%s) returned False." % request.form.cleaned_data["path"])
    except Exception as ex:
        logger.error("Failed to revert_snapshot: %s" % ex)
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
    try:
        if int(server_id) not in server_ids:
            raise Exception("Forbidden: specified Server does not belong to specified Service.")

        server = Server.objects.get(pk=server_id)   

        pysph = Vsphere(settings.VMWARE["address"], settings.VMWARE["username"], settings.VMWARE["password"], server.sid)
        result = pysph.create_snapshot(request.form.cleaned_data["name"], request.form.cleaned_data["description"])

        if result:
            ActionLogger().log(request.user, "created", "snapshot %s" % request.form.cleaned_data["name"], "vServer %s" % server.sid)
            return format_ajax_response(True, "Snapshot created successfully.")
        else:
            raise Exception("Pysphere's create_snapshot(%s, %s) returned False." % (request.form.cleaned_data["name"], request.form.cleaned_data["description"]))
    except Exception as ex:
        logger.error("Failed to create_snapshot: %s" % ex)
        return format_ajax_response(False, "There was an error creating the snapshot.")