# System
import logging
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
# Project
from apps.loggers.models import ActionLogger
from common.decorators import validated_request, validated_service
from common.helpers import format_ajax_response
from libs.cpanel_email import Cpanel
# App
from .forms import AddPopForm, AddForwardForm, EmailForm, SetQuotaForm, ChpwForm


logger = logging.getLogger(__name__)


@login_required
def index(request, service_id):
    """Email Detail View

        Queries remote Cpanel server for email details. 

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @login_required
            request.user.is_authenticated() must be True
    Parameters
        request: HttpRequest
        service_id: int service id
    Returns
        HttpResponse (email/index.html)
            service_id: int service id
    """     
    return render(request, 'email/index.html', {'service_id': service_id})


@validated_service
@validated_request(None)
def getaccounts(request, cpanel_username):
    """Get Email Accounts

        Retrieves listing of Email Accounts under specified cpanel username from remote Cpanel server.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_request
            request.method must be POST
            request.user.is_authenticated() must be True
            request.is_ajax() must be True
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
                accounts: 
    """
    try:
        accounts = Cpanel(cpanel_username).listpops()
        if accounts:
            return format_ajax_response(True, "Email accounts retrieved successfully.", {"accounts": accounts})
        else:
            raise Exception("CpanelEmail library call to listpops() returned False.")
    except Exception as ex:
        logger.error("Failed to getaccounts: %s" % ex)
        return format_ajax_response(False, "There was an error retrieving email accounts.")


@validated_request(None)
@validated_service
def getforwards(request, cpanel_username):
    """Get Email Forwards

        Retrieves listing of Email Forwards under specified cpanel username from remote Cpanel server.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_request
            request.method must be POST
            request.user.is_authenticated() must be True
            request.is_ajax() must be True
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
                forwards:
    """
    try:
        forwards = Cpanel(cpanel_username).listforwards()
        if forwards:
            return format_ajax_response(True, "Email forwards retireved successfully.", {"forwards": forwards})
        else:
            raise Exception("CpanelEmail library call to listforwards() returned False.")
    except Exception as ex:
        logger.error("Failed to getforwards: %s" % ex)        
        return format_ajax_response(False, "There was an error retrieving email forwards.")


@validated_service
@validated_request(AddPopForm)
def createaccount(request, cpanel_username):
    """Create Email account

        Defines new email account on remote Cpanel server.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_request
            request.POST must validate against AddPopForm
            request.method must be POST
            request.user.is_authenticated() must be True
            request.is_ajax() must be True
        @validated_service
            service_id must belong to request.user.company.services
            service.vars is injected into view parameter            
    Parameters
        request: HttpRequest
            email: str email address
            password: str email account password
            quota: int disk space quota
        cpanel_username: str cpanel account username
    Returns
        HttpResponse (JSON)
            success: int status result of API call
            message: str response message from API call
    """
    try:
        user,domain = request.form.cleaned_data['email'].split('@')

        if Cpanel(cpanel_username).addpop(domain, user, request.form.cleaned_data['password'], request.form.cleaned_data['quota']):
            ActionLogger().log(request.user, "created", "Email Account %s" % request.form.cleaned_data['email'])
            return format_ajax_response(True, "Email account created successfully.")
        else:
            raise Exception("CpanelEmail library call to addpop(%s, %s, %s, %s) returned False." % (domain, user, request.form.cleaned_data['password'], request.form.cleaned_data['quota']))
    except Exception as ex:
        logger.error("Failed to createaccount: %s" % ex)           
        return format_ajax_response(False, "There was an error creating the email account.")


@validated_service
@validated_request(AddForwardForm)
def createforward(request, cpanel_username):
    """Create Email forward

        Defines new email forward under specified account on remote Cpanel server.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_request
            request.POST must validate against AddForwardForm
            request.method must be POST
            request.user.is_authenticated() must be True
            request.is_ajax() must be True
        @validated_service
            service_id must belong to request.user.company.services
            service.vars is injected into view parameter 
    Parameters
        request: HttpRequest object
            email: str email address
            fwdopt: str forwarder option (fail, fwd, system, pipe, blackhole)
            *fwdemail: str destination email if fwdopt == fwd
            *fwdsystem: str system command if fwdopt == system
            *failmsgs: str message to respond with if fwdopt == fail
            *pipefwd: str pipe command if fwdopt == pipe
        cpanel_username: str cpanel account username
    Returns
        HttpResponse (JSON)
            success: int status result of API call
            message: str response message from API call
    """
    try:
        domain = request.form.cleaned_data['email'][request.form.cleaned_data['email'].index('@')+1:]

        if request.form.cleaned_data['fwdopt'] == 'fail':
            result = Cpanel(cpanel_username).addforward(domain, request.form.cleaned_data['email'], request.form.cleaned_data['fwdopt'], None, None, request.form.cleaned_data['failmsgs'])
        elif request.form.cleaned_data['fwdopt'] == 'fwd':
            result = Cpanel(cpanel_username).addforward(domain, request.form.cleaned_data['email'], request.form.cleaned_data['fwdopt'], request.form.cleaned_data['fwdemail'])
        elif request.form.cleaned_data['fwdopt'] == 'system':
            result = Cpanel(cpanel_username).addforward(domain, request.form.cleaned_data['email'], request.form.cleaned_data['fwdopt'], None, request.form.cleaned_data['fwdsystem'])
        elif request.form.cleaned_data['fwdopt'] == 'pipe':
            result = Cpanel(cpanel_username).addforward(domain, request.form.cleaned_data['email'], request.form.cleaned_data['fwdopt'], None, None, None, request.form.cleaned_data['pipefwd'])
        elif request.form.cleaned_data['fwdopt'] == 'blackhole':
            result = Cpanel(cpanel_username).addforward(domain, request.form.cleaned_data['email'], request.form.cleaned_data['fwdopt'])        

        if result:
            ActionLogger().log(request.user, "created", "Email Forward %s" % request.form.cleaned_data['email'])
            return format_ajax_response(True, "Email forward created successfully.")
        else:
            raise Exception("CpanelEmail library call to addforward(%s, %s, %s,...) returned False." % (domain, request.form.cleaned_data['email'], request.form.cleaned_data['fwdopt']))
    except Exception as ex:
        logger.error("Failed to createforward: %s" % ex)              
        return format_ajax_response(False, "There was an error creating the email forward.")
       

@validated_service
@validated_request(AddForwardForm)
def createdomainforward(request, cpanel_username):
    """Create Domain forward

        Defines a new domain forward on remote Cpanel server.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_request
            request.POST must validate against AddForwardForm
            request.method must be POST
            request.user.is_authenticated() must be True
            request.is_ajax() must be True
        @validated_service
            service_id must belong to request.user.company.services
            service.vars is injected into view parameter 
    Parameters
        request: HttpRequest object
            domain: str domain name
            fwdopt: str forwarder option (fail, fwd, system, pipe, blackhole)
            *fwdemail: str destination email if fwdopt == fwd
            *fwdsystem: str system command if fwdopt == system
            *failmsgs: str message to respond with if fwdopt == fail
            *pipefwd: str pipe command if fwdopt == pipe
        cpanel_username: str cpanel account username
    Returns
        HttpResponse (JSON)
            success: int status result of API call
            message: str response message from API call    
    """
    try:
        if request.form.cleaned_data['fwdopt'] == 'blackhole':
            result = Cpanel(cpanel_username).setdefaultaddress(request.form.cleaned_data['fwdopt'], service_vars["email_domain"])
        elif request.form.cleaned_data['fwdopt'] == 'fail':
            result = Cpanel(cpanel_username).setdefaultaddress(request.form.cleaned_data['fwdopt'], service_vars["email_domain"], request.form.cleaned_data['failmsgs'])
        elif request.form.cleaned_data['fwdopt'] == 'fwd':
            result = Cpanel(cpanel_username).setdefaultaddress(request.form.cleaned_data['fwdopt'], service_vars["email_domain"], None, request.form.cleaned_data['fwdemail'])
        elif request.form.cleaned_data['fwdopt'] == 'pipe':
            result = Cpanel(cpanel_username).setdefaultaddress(request.form.cleaned_data['fwdopt'], service_vars["email_domain"], None, None, request.form.cleaned_data['pipefwd'])  

        if result:
            ActionLogger().log(request.user, "created", "Domain Forward %s" % request.form.cleaned_data['email_domain'])
            return format_ajax_response(True, "Domain forward created successfully.")
        else:
            raise Exception("CpanelEmail library call to setdefaultaddress(%s, %s,...) returned False." % (request.form.cleaned_data['fwdopt'], service_vars["email_domain"]))
    except Exception as ex:
        logger.error("Failed to createdomainforward: %s" % ex)                    
        return format_ajax_response(False, "There was an error creating the domain forward.")


@validated_service
@validated_request(EmailForm)
def delaccount(request, cpanel_username):
    """Delete Email account

        Deletes specified email account from remote Cpanel server.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_request
            request.POST must validate against EmailForm
            request.method must be POST
            request.user.is_authenticated() must be True
            request.is_ajax() must be True
        @validated_service
            service_id must belong to request.user.company.services
            service.vars is injected into view parameter             
    Parameters
        request: HttpRequest object
            email: str email address
        cpanel_username: str cpanel account username
    Returns
        HttpResponse (JSON)
            success: int status result of API call
            message: str response message from API call 
    """
    try:
        user,domain = request.form.cleaned_data['email'].split('@') 

        if Cpanel(cpanel_username).delpop(domain, user):
            ActionLogger().log(request.user, "deleted", "Email Account %s" % request.form.cleaned_data['email'])
            return format_ajax_response(True, "Email account deleted successfully.")
        else:
            raise Exception("CpanelEmail library call to delpop(%s, %s) returned False." % (domain, user))
    except Exception as ex:
        logger.error("Failed to delaccount: %s" % ex)                    
        return format_ajax_response(False, "There was an error deleting the email account.")


@validated_service
@validated_request(ChpwForm)
def chpw(request, cpanel_username):
    """Set Email account password

        Updates specified email account with specified password.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_request
            request.POST must validate against ChpwForm
            request.method must be POST
            request.user.is_authenticated() must be True
            request.is_ajax() must be True
        @validated_service
            service_id must belong to request.user.company.services
            service.vars is injected into view parameter             
    Parameters
        request: HttpRequest object
            email: str email address
            password: str new password
        cpanel_username: str cpanel account username
    Returns
        HttpResponse (JSON)
            success: int status result of API call
            message: str response message from API call    
    """
    try:
        user,domain = request.form.cleaned_data['email'].split('@')

        if Cpanel(cpanel_username).passwdpop(domain, user, request.form.cleaned_data['password']):
            ActionLogger().log(request.user, "modified", "Password", "Email Account %s" % request.form.cleaned_data['email'])
            return format_ajax_response(True, "Email account password updated successfully.")
        else:
            raise Exception("CpanelEmail library call to passwdpop(%s, %s, %s) returned False." % (domain, user, request.form.cleaned_data['password']))
    except Exception as ex:
        logger.error("Failed to chpw: %s" % ex)                
        return format_ajax_response(False, "There was an error updating the email account password.")


@validated_service
@validated_request(SetQuotaForm)
def setquota(request, cpanel_username):
    """Sets Email account quota

        Sets specified email account's quota on remote Cpanel server.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_request
            request.POST must validate against SetQuotaForm
            request.method must be POST
            request.user.is_authenticated() must be True
            request.is_ajax() must be True
        @validated_service
            service_id must belong to request.user.company.services
            service.vars is injected into view parameter             
    Parameters
        request: HttpRequest object
            email: str email address
            quota: int disk space quota
        cpanel_username: str cpanel account username
    Returns
        HttpResponse (JSON)
            success: int status result of API call
            message: str response message from API call
    """
    try:
        user,domain = request.form.cleaned_data['email'].split('@')

        if Cpanel(cpanel_username).editquota(domain, user, request.form.cleaned_data['quota']):
            ActionLogger().log(request.user, "modified", "Quota %s" % request.form.cleaned_data['quota'], "Email Account %s" % request.form.cleaned_data['email'])         
            return format_ajax_response(True, "Email account quota updated successfully.")
        else:
            raise Exception("CpanelEmail library call to editquota(%s, %s, %s) returned False." % (domain, user, request.form.cleaned_data['quota']))
    except Exception as ex:
        logger.error("Failed to setquota: %s" % ex)             
        return format_ajax_response(False, "There was an error updating the email account quota.")