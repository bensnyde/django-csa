# System
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render
import json
# Project
from apps.loggers.models import ErrorLogger, ActionLogger
from common.decorators import validated_request, validated_service
from common.helpers import format_ajax_response
from libs.cpanel_dns import Cpanel
# App
from .forms import AddZoneForm, AddRecordForm, AddMxRecordForm, AddSrvRecordForm, ZoneForm, DeleteRecordForm


@login_required
def index(request, service_id):
    """DNS List View

        Retrieve listing of DNS zones. 

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @login_required
            request.user.is_authenticated() must be True
    Parameters
        request: HttpRequest
        service_id: int service id
    Returns
        HttpResponse (dns/index.html)
            service_id: int service id
    """
    return render(request, 'dns/index.html', {'service_id': service_id})


@login_required
def detail(request, zone, service_id):    
    """DNS Detail View

        Retrieve records for specified DNS zone. 

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @login_required
            request.user.is_authenticated() must be True
    Parameters
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
def getzones(request, cpanel_username):
    """Get DNS Zones

        Retrieves listing of DNS zones under specified Cpanel account.

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
        cpanel_username: str cpanel account username
    Returns
        HttpResponse (JSON)
            success: int status result of API call
            message: str response message from API call
            *data:
                zones:
                    domain: str domain name
    """
    zones = Cpanel().listZones(cpanel_username)
    
    if zones:
        return format_ajax_response(True, "Zones listing retrieved successfully.", {"zones": zones})
    else:
        return format_ajax_response(False, "There was an error retrieving zones listing.")


@validated_request(ZoneForm)
@validated_service
def getrecords(request, cpanel_username):
    """Get DNS Zone Records

        Retrieves records for specified DNS zone under specified Cpanel account on remote Cpanel server.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_request
            request.POST must validate against ZoneForm
            request.method must be POST
            request.is_ajax() must be True
            request.user.is_authenticated() must be True
        @validated_service
            service_id must belong to request.user.company.services
            service.vars is injected into view parameter           
    Parameters
        request: HttpRequest
            zone: str domain name
        cpanel_username: str cpanel account username
    Returns
        HttpResponse (JSON)
            success: int status result of API call
            message: str response message from API call
            *data:
                records:
    """
    # Validate specified domain
    if does_domain_belong_to_username(cpanel_username, request.form.cleaned_data['zone']) == False:
        ErrorLogger().log(request, "Forbidden", "User attempted access to unauthorized domain in services.dns.views.getzone") 
        return HttpResponseForbidden()

    records = Cpanel().listZone(request.form.cleaned_data['zone'])

    if records:
        return format_ajax_response(True, "Records retrieved successfully.", {"records": records})
    else:
        return format_ajax_response(False, "There was an error retrieving the zone records.")


@validated_request(None)
@validated_service
def addrecord(request, cpanel_username):
    """Add DNS record

        Adds record to specified DNS zone under specified Cpanel account on remote Cpanel Server.

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
            rtype: str record type
            domain: str domain name
            zone: str zone name
            ttl: int time to live
            *record: str value for most rtypes
            *priority: int mail exchange (mx) priority value
            *weight: int srv weight value
            *port: int srv port value
        cpanel_username: str cpanel account username
    Returns
        HttpResponse (JSON)
            success: int status result of API call
            message: str response message from API call
    """ 
    # Conditionally select Form for POST validation
    if request.POST['rtype'] == 'MX':
        form = AddMxRecordForm(request.POST)
    elif request.POST['rtype'] == 'SRV':
        form = AddSrvRecordForm(request.POST)
    else:
        form = AddRecordForm(request.POST)

    # Validate Form
    if form.is_valid():
        # Validate specified domain
        if does_domain_belong_to_username(cpanel_username, form.cleaned_data['zone']) == False:
            ErrorLogger().log(request, "Forbidden", "User attempted access to unauthorized domain in services.dns.views.addrecord") 
            return HttpResponseForbidden()

        # Build data container for API call
        data = {
            'name': form.cleaned_data['domain'], 
            'ttl': form.cleaned_data['ttl'], 
            'zone': form.cleaned_data['zone'], 
            'type': form.cleaned_data['rtype']
        }

        # Conditionally update data with specified fields
        if form.cleaned_data['rtype'] == 'A' or form.cleaned_data['rtype'] == 'A6' or form.cleaned_data['rtype'] == 'AAAA':
            data.update({
                'address': form.cleaned_data['record']
            })
        elif form.cleaned_data['rtype'] == 'TXT':
            data.update({
                'txtdata': form.cleaned_data['record']
            })
        elif form.cleaned_data['rtype'] == 'CNAME':
            data.update({
                'cname': form.cleaned_data['record']
            })
        elif form.cleaned_data['rtype'] == 'NS':
            data.update({
                'nsdname': form.cleaned_data['record']
            })
        elif form.cleaned_data['rtype'] == 'PTR':
            data.update({
                'ptrdname': form.cleaned_data['record']
            })
        elif form.cleaned_data['rtype'] == 'MX':
            data.update({
                'priority': form.cleaned_data['priority'], 
                'exchange': form.cleaned_data['record']
            })
        elif form.cleaned_data['rtype'] == 'SRV':
            data.update({
                'priority': form.cleaned_data['priority'], 
                'weight': form.cleaned_data['weight'], 
                'port': form.cleaned_data['port'], 
                'target': form.cleaned_data['record']
            })

        if Cpanel().addZoneRecord(**data):
            ActionLogger().log(request.user, "created",  "%s Record" % form.cleaned_data['rtype'], form.cleaned_data['zone'])
            return format_ajax_response(True, "Record created successfully.")
        else:
            ErrorLogger().log(request, "Error", "Error adding record to zone in apps.dns.views.addrecord.")
            return format_ajax_response(False, "There was an error creating the record.")
    else:
        return format_ajax_response(False, "Form data failed validation.", errors=dict((k, [unicode(x) for x in v]) for k,v in form.errors.items()))


@validated_request(DeleteRecordForm)
@validated_service
def deleterecord(request, cpanel_username):
    """Delete DNS record

        Deletes record from specified DNS zone under specified Cpanel account on remote Cpanel server.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_request
            request.POST must validate against DeleteFormZone
            request.method must be POST
            request.is_ajax() must be True
            request.user.is_authenticated() must be True
        @validated_service
            service_id must belong to request.user.company.services
            service.vars is injected into view parameter  
    Parameters
        request: HttpRequest
            zone: string domain name
            line: string record line number
        cpanel_username: str cpanel account username
    Returns
        HttpResponse (JSON)
            success: int status result of API call
            message: str response message from API call
    """
    # Validate specified domain
    if does_domain_belong_to_username(cpanel_username, request.form.cleaned_data['zone']) == False:
        ErrorLogger().log(request, "Forbidden", "User attempted access to unauthorized domain in apps.dns.views.deleterecord") 
        return HttpResponseForbidden()

    if Cpanel().deleteZoneRecord(request.form.cleaned_data['zone'], request.form.cleaned_data['line']):
        ActionLogger().log(request.user, "deleted",  "Line %s" % request.form.cleaned_data['line'], request.form.cleaned_data['zone'])
        return format_ajax_response(True, "Record deleted successfully.")
    else:
        ErrorLogger().log(request, "Error", "Error deleting record from zone in apps.dns.views.deleterecord.")
        return format_ajax_response(False, "There was an error deleting the record.")


@validated_request(AddZoneForm)
@validated_service
def createzone(request, cpanel_username):
    """Create DNS zone

        Creates DNS zone under specified Cpanel account on remote Cpanel server.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_request
            request.POST must validate against AddZoneForm
            request.method must be POST
            request.is_ajax() must be True
            request.user.is_authenticated() must be True
        @validated_service
            service_id must belong to request.user.company.services
            service.vars is injected into view parameter              
    Parameters
        request: HttpRequest
            domain: string domain name
            ip: string ip address
        cpanel_username: str cpanel account username
    Returns
        HttpResponse (JSON)
            success: int status result of API call
            message: str response message from API call
    """
    if Cpanel().addZone(request.form.cleaned_data['domain'], request.form.cleaned_data['ip'], cpanel_username):
        ActionLogger().log(request.user, "created",  "Zone %s" % request.form.cleaned_data['domain'])
        return format_ajax_response(True, "Zone created successfully.")
    else:
        ErrorLogger().log(request, "Error", "Error creating zone in apps.dns.views.createzone.")
        return format_ajax_response(False, "There was an error creating the zone.")


@validated_request(ZoneForm)
@validated_service
def deletezone(request, cpanel_username):
    """Delete DNS zone

        Deletes specified DNS zone from remote Cpanel server. 

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_request
            request.POST must validate against ZoneForm
            request.method must be POST
            request.is_ajax() must be True
            request.user.is_authenticated() must be True
        @validated_service
            service_id must belong to request.user.company.services
            service.vars is injected into view parameter              
    Parameters
        request: HttpRequest
            zone: string domain name
        cpanel_username: str cpanel account username
    Returns
        HttpResponse (JSON)
            success: int status result of API call
            message: str response message from API call
    """
    # Ensure domain belongs to cpanel_username
    if does_domain_belong_to_username(cpanel_username, request.form.cleaned_data['zone']) == False:
        ErrorLogger().log(request, "Forbidden", "User attempted access to unauthorized domain in services.dns.views.deletezone") 
        return HttpResponseForbidden()

    if Cpanel().deleteZone(request.form.cleaned_data['zone']):
        ActionLogger().log(request.user, "deleted",  "Zone %s" % request.form.cleaned_data['zone'])
        return format_ajax_response(True, "Zone deleted successfully.")
    else:
        ErrorLogger().log(request, "Error", "Error deleting zone in apps.dns.views.deletezone.")
        return format_ajax_response(False, "There was an error deleting the zone.")


def search(user, service_id, querystr):
    """Search domains for string

        Queries remote Cpanel server for domains matching specified search string. 

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @login_required
            request.user.is_authenticated() must be True          
    Parameters
        user: django user object
        service_id: int service id
        querystr: str search string 
    Returns
        list of domains matching query
    """ 
    service_vars = user.get_service_vars("/services/dns/", service_id)
    if not service_vars:
        ErrorLogger().log(request, "Forbidden", "User attempted access to unauthorized service in services.solusvm.views.index") 
        return HttpResponseForbidden()

    matches = []
    for domain in Cpanel().listZones(service_vars["cpanel_username"])['data']['zones']:
        if querystr in domain['domain']:
            matches.append(domain['domain'])

    return matches


def does_domain_belong_to_username(cpanel_username, domain):
    """Check to see if domain belongs to Cpanel user

        Queries remote Cpanel server to see if specified domain is defined on and is belonging to specified cpanel_username. 
     
    Parameters
        cpanel_username: str cpanel account name
        domain: str dns domain name
    Returns
        boolean
    """
    return any(domain in zone["domain"] for zone in Cpanel().listZones(cpanel_username))    