# System
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render
import json
# Project
from apps.ip.forms import NetworkAddressAddForm
from apps.companies.forms import CompanyForm
from apps.loggers.models import ErrorLogger, ActionLogger
from common.decorators import validated_request, validated_service
# App


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
    return render(request, 'backend/index.html', {'companyform': CompanyForm(), 'networkaddressform': NetworkAddressAddForm()})