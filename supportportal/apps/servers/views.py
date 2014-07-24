# System
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render, get_object_or_404
import json
# Project
from apps.services.models import Service
from apps.loggers.models import ErrorLogger, ActionLogger
from common.decorators import validated_request, validated_service
from common.helpers import format_ajax_response
# App
from .models import Server
from .forms import ServerForm


@login_required
def index(request, service_id):
    """Server Index View

        Retrieves a listing of Servers. 

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @login_required
            request.user.is_authenticated() must be True        
    Paremeters
        request: HttpRequest
        service_id: int service id
    Returns
        HttpResponse (servers/index.html)
            service_id: int service id 
            serverform: form ServerForm
    """
    return render(request, 'servers/index.html', {'service_id': service_id, 'serverform': ServerForm()})


@login_required
def detail(request, service_id, server_id):
    """Server Detail View

        Retrieves details on Server as specified by server.pk.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @login_required
            request.user.is_authenticated() must be True      
    Paremeters
        request: HttpRequest
        service_id: int service id
        server_id: int server id
    Returns
        HttpResponse (servers/detail.html)
            service_id: int service id
            serverform: form ServerForm
    """
    server = get_object_or_404(Server, pk=server_id)
    serverform = ServerForm(instance=server)
    return render(request, 'servers/detail.html', {'service_id': service_id, 'server': server, 'serverform': serverform})


@validated_request(None)
@validated_service
def get_servers(request, server_ids):
    """Get Servers Index

        Retreives a listing of servers under a specified server service.

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
    Returns
        HttpResponse (JSON)
            success: int result
            message: str response message
            *data:
                servers:
                    ip:
                    type:
                    os:
                    id:
                    name:
    """
    try:
        servers_list = []
        for server in Server.objects.filter(pk__in=server_ids):
            servers_list.append(server.dump_to_dict())

        return format_ajax_response(True, "Servers listing retrieved successfully.", {'servers': servers_list})
    except Exception as ex:
        ErrorLogger().log(request, "Error", "Error retrieving servers listing in apps.servers.views.get_servers: %s" % ex) 
        return format_ajax_response(False, "There was an error retrieving the servers listing.")


@validated_request(None)
@validated_service
def get_server(request, server_ids, server_id):
    """Get Server Details

        Retreives details of Server specified by server.pk.

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
            success: int result
            message: str response message
            *data:
                server:
                    username:
                    os:
                    ip:
                    notes:
                    uplink:
                    location:
                    password:
                    type:
                    id:
                    name:
    """
    try:
        server = Server.objects.get(pk=server_id)
        details = server.dump_to_dict(full=True)
        return format_ajax_response(True, "Server details retrieved successfully.", {'server': details})
    except Exception as ex:
        ErrorLogger().log(request, "Error", "Error retrieving servers listing in apps.servers.views.get_server: %s" % ex) 
        return format_ajax_response(False, "There was an error retrieving the server details.")


@validated_request(None)
def set_server(request, service_id):
    """Set Server 

        Creates new Server record, or updates existing if server.pk is specified.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_request 
            request.method must be POST
            request.is_ajax() must be True
            request.user.is_authenticated() must be True
    Paremeters
        request: HttpRequest
            *server_id: int server id        
        service_id: int service id
    Returns
        HttpResponse (JSON)
            success: int result
            message: str response message
    """       
    try:
        # Validate service_id
        service_vars = request.user.get_service_vars('/services/server/', service_id)
        if not service_vars:
            ErrorLogger().log(request, "Forbidden", "User attempted access to unauthorized service.") 
            return HttpResponseForbidden("Service ID does not belong to the requesting user.")

        # Update existing if news_id exists, else create new
        if "server_id" in request.POST and request.POST['server_id']:
            # Esnure Server belongs to specified Service
            if int(request.POST["server_id"]) in service_vars["server_ids"]:
                form = ServerForm(request.POST, instance=get_object_or_404(Server, pk=int(request.POST["server_id"])))
                if form.is_valid():
                    server = form.save()
                    ActionLogger().log(request.user, "modified", "Server %s" % server)
                    return format_ajax_response(True, "Server details updated successfully.")
                else:
                    return format_ajax_response(False, "Form data failed validation.", errors=dict((k, [unicode(x) for x in v]) for k,v in form.errors.items()))
            else:
                # Deny attempt to modify Server that is not in Service's Server_ID's
                ErrorLogger().log(request, "Forbidden", "Attempt to modify Server outside of Service in apps.servers.views.set_server.")
                return format_ajax_response(False, "Unauthorized attempt to modify protected resource.")               
        else:          
            form = ServerForm(request.POST)
            if form.is_valid():
                server = form.save()

                # ADD SERVER_ID TO SERVICE's SERVICE_VARS
                service_vars["server_ids"].append(int(server.pk))
                Service.objects.filter(pk=service_id).update(vars=json.dumps(service_vars))

                ActionLogger().log(request.user, "created", "Server %s" % server)
                return format_ajax_response(True, "Server created successfully.")             
            else:
                return format_ajax_response(False, "Form data failed validation.", errors=dict((k, [unicode(x) for x in v]) for k,v in form.errors.items())) 
    except Exception as ex:
        ErrorLogger().log(request, "Failed", "Error setting Server in apps.servers.views.set_server: %s" % ex)
        return format_ajax_response(False, "There was an error setting the Server.")


@validated_request(None)
@validated_service
def delete_server(request, server_ids, server_id):
    """Delete Server

        Deletes Server record as specified by server.pk.

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
            success: int result
            message: str response message
    """
    try:
        server = Server.objects.get(pk=server_id).delete()
        return format_ajax_response(True, "Server deleted successfully.")
    except Exception as ex:
        ErrorLogger().log(request, "Error", "Error deleting server in apps.servers.views.delete_server: %s" % ex) 
        return format_ajax_response(False, "There was an error deleting the specified server.")