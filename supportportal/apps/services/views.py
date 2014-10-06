# System
import logging
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
# Project
from common.decorators import validated_request, validated_staff
from common.helpers import format_ajax_response
# App
from .models import Service, Coupler


logger = logging.getLogger(__name__)

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

@validated_staff
def get_services(request):
    try:
        services = []
        for service in Service.objects.all():
            services.append(service.dump_to_dict())

        return format_ajax_response(True, "Services listing retrieved successfully.", {"services": services})
    except Exception as ex:
        logger.error("Failed to get_services: %s" % ex)
        return format_ajax_response(False, "There was an error retrieving the services listing.")