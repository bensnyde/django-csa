# System
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render
import json
# Project
from apps.loggers.models import ErrorLogger, ActionLogger
from common.decorators import validated_request, validated_service
# App
from .models import Service, Coupler


@login_required
def index(request):
    """DNS List View

        List all DNS zones defined on remote Cpanel server. 

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @login_required
            request.user.is_authenticated() must be True
    Paremeters
        request: HttpRequest
        service_id: int service id
    Returns
        HttpResponse (dns/index.html)
            service_id: int service id
    """
    return render(request, 'services/index.html')


@login_required
def detail(request, zone, service_id):    
    """DNS Detail View

        Retrieve specified DNS zone records from remote Cpanel Server. 

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @login_required
            request.user.is_authenticated() must be True
    Paremeters
        request: HttpRequest
        zone: str domain name
        service_id: int service id
    Returns
        HttpResponse (dns/detail.html)
            service_id: int service id
            zone: str dns zone name
    """
    return render(request, 'dns/detail.html', {'service_id': service_id, 'zone': zone})


@validated_request(None)
@validated_service
def getzones(request):
    """Get DNS Zones

        Retrieves all DNS zones belonging to specified cpanel account from remote Cpanel server.

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
        cpanel_username: str cpanel account username
    Returns
        HttpResponse (JSON)
            success: int status result of API call
            message: str response message from API call
    """
    return Cpanel().listZones(cpanel_username)

