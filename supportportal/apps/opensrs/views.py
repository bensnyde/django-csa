# System
from django.conf import settings
from django.shortcuts import render
# Project
from apps.loggers.models import ErrorLogger, ActionLogger
from common.decorators import validated_request
from common.helpers import format_ajax_response
from libs.opensrs import *
# App
from .forms import DomainForm, DomainRegisterForm


srs = OpenSRS(settings.OPENSRS["id"], settings.OPENSRS["key"], False);


@validated_request(None, 'GET', True, False)
def index(request, domain):
    """OpenSRS Base View

        Allows for interaction with the OpenSRS Domain Registrar.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_request
            request.method must be POST
            request.is_ajax() must be True
            request.user.is_authenticated() must be True
    Parameters
        request: HttpRequest    
            domain: str domain name
    Returns
        HttpResponse (opensrs/index.html)
            domain: str domain name
    """
    return render(request, 'opensrs/index.html', {"domain": domain})


@validated_request(DomainForm)
def name_suggest(request):
    """Suggest alternate domain names

        Queries OpenSRS for suggestions on alternate domain names. 

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_request
            Request.method must be POST.
            Request.is_ajax() must be TRUE.
            Request must come from authenticated contact.
    Parameters
        request: HttpRequest
            domain: str domain name
    Returns
        HttpResponse (JSON)
            success: int status result of API call
            message: str response message from API call

        {
            "response_text": "Command completed successfully", 
            "protocol": "XCP", 
            "response_code": "200", 
            "is_search_completed": "1", 
            "request_response_time": "0.835", 
            "action": "REPLY", 
            "attributes": 
            {
                "lookup": 
                {
                    "count": "7", 
                    "response_text": "Command completed successfully.", 
                    "response_code": "200", 
                    "is_success": "1", 
                    "items": 
                    [
                        {"status": "taken", "domain": "test.com"}, 
                        {"status": "taken", "domain": "test.net"}, 
                        {"status": "taken", "domain": "test.org"}, 
                        ...
                    ]
                }, 
                "suggestion": 
                {
                    "count": "49", 
                    "response_text": "Command Successful", 
                    "response_code": "200", 
                    "is_success": "1", 
                    "items": 
                    [
                        {"status": "available", "domain": "besttest.mobi"}, 
                        {"status": "available", "domain": "clairetest.net"}, 
                        {"status": "available", "domain": "clairetest.org"},
                        ...
                    ]
                }
            }, 
            "is_success": "1"
        }
    """
    result = srs.name_suggest(request.form.cleaned_data['domain'])

    if result["response_code"] == "200":
        return format_ajax_response(True, "Suggestions retrieved successfully.", {"urls": result["attributes"]})
    else:
        return format_ajax_response(False, "There was an error retrieving domain suggestions.")


@validated_request(DomainForm)
def check_transfer(request):
    """Get domain transfer status

        Queries OpenSRS to see current transfer status of specified domain.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_request
            request.POST must validate against DomainForm
            request.method must be POST
            request.is_ajax() must be True
            request.user.is_authenticated() must be True
    Parameters
        request: HttpRequest
            domain: str domain name
    Returns
        HttpResponse (JSON)
            success: int status result of API call
            message: str response message from API call
            *data:
                attributes:
                    transferrable: bool
                    reason: str
                    noservice:
    """    
    result = srs.check_transfer(request.form.cleaned_data['domain'])

    if result["response_code"] == "200":
        return format_ajax_response(True, "Transfer status retrieved successfully.", {"attributes": result["attributes"]})
    else:
        return format_ajax_response(False, "There was an error retrieving the transfer status.")


@validated_request(DomainForm)
def get_domain_price(request):
    """Get domain price

        Queries OpenSRS for price of specified domain. 

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_request
            request.POST must validate against DomainForm
            request.method must be POST
            request.is_ajax() must be True
            request.user.is_authenticated() must be True
    Parameters
        request: HttpRequest
            domain: str domain name
    Returns
        HttpResponse (JSON)
            success: int status result of API call
            message: str response message from API call
            *data:
                attributes:
                    price: float
    """
    result = srs.get_domain_price(request.form.cleaned_data['domain'], 1, False)

    if result["response_code"] == "200":
        return format_ajax_response(True, "Domain price retrieved successfully.", {"attributes": result["attributes"]})
    else:
        return format_ajax_response(False, "There was an error retrieving the domain price.")


@validated_request(None)
def get_balance(request):
    """Get reseller account balance

        Queries OpenSRS for reseller account's current balance.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_request
            request.method must be POST
            request.is_ajax() must be True
            request.user.is_authenticated() must be True
    Parameters
        request: HttpRequest
    Returns
        HttpResponse (JSON)
            success: int status result of API call
            message: str response message from API call
            *data:
                attributes:
                    hold_balance: float
                    balance: float
    """
    result = srs.balance()

    if result["response_code"] == "200":
        return format_ajax_response(True, "Balance retrieved successfully.", {"attributes": result["attributes"]})
    else:
        return format_ajax_response(False, "There was an error retrieving account balance.")


# FIX ME, NOT TESTED
@validated_request(DomainRegisterForm)
def register_domain(request):    
    """Register domain

        Attempts to register specified domain via API call to OpenSRS.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_request
            request.POST must validate against DomainRegisterForm
            request.method must be POST
            request.is_ajax() must be True
            request.user.is_authenticated() must be True
    Parameters
        request: HttpRequest
            domain: string domain name
            owner: string domain contact's full name
            period: int number of years to register domain for
            username: string OpenSRS username for domain account 
            password: string OpenSRS password for domain account
            auto_renew: boolean automatically renew domain
    Returns
        HttpResponse (JSON)
            success: int status result of API call
            message: str response message from API call
    """
    return False
    
    # Make register domain call to OpenSRS
    result = srs.domain_register(
        form.cleaned_data['domain'], 
        form.cleaned_data['owner'], 
        form.cleaned_data['period'], 
        form.cleaned_data['username'], 
        form.cleaned_data['password'], 
        None, 
        form.cleaned_data['auto_renew']
    )

    if result["response_code"] == "200":
        ActionLogger().log(request.user, "registered", "Domain %s" % request.form.cleaned_data['domain'])
        return format_ajax_response(True, "Domain registered successfully.", {"result": result})
    else:
        return format_ajax_response(False, "There was an error registering the domain.")