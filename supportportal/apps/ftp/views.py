# System
import logging
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
# Project
from apps.loggers.models import ActionLogger
from common.decorators import validated_request, validated_service
from common.helpers import format_ajax_response
from libs.cpanel_ftp import Cpanel
# App
from .forms import AddFtpForm, DelFtpForm, SetQuotaForm, ChpwForm


logger = logging.getLogger(__name__)


@login_required
def index(request, service_id):
    """List View

        Renders list view template. 

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @login_required
            request.user.is_authenticated() must be True
    Paremeters
        request: Httprequest
        service_id: int service id
    Returns
        HttpResponse (ftp/index.html)
            service_id: int service id
    """
    return render(request, 'ftp/index.html', {'service_id': service_id})


@validated_request(None)
@validated_service
def get_accounts(request, cpanel_username):
    """Get FTP Accounts

        Retrieves FTP accounts under specified cpanel_username from remote Cpanel server.

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
    Paremeters
        request: HttpRequest
        cpanel_username: str cpanel account username
    Returns
        HttpResponse (JSON)
            success: int status result of API call
            message: str response message from API call
            *data:
                accounts: list of ftp accounts from API call
    """
    try:
        accounts = Cpanel(cpanel_username).listftpwithdisk()
        if accounts:
            return format_ajax_response(True, "FTP Accounts retrieved successfully.", {"accounts": accounts})
        else:
            raise Exception("CpanelFTP library call to listftpwithdisk() returned False.")
    except Exception as ex:
        logger.error("Failed to get_accounts: %s" % ex)
        return format_ajax_response(False, "There wasn an error retrieving the FTP account listing.")


@validated_request(None)
@validated_service
def get_sessions(request, cpanel_username):
    """Get FTP Sessions

        Retrieves open FTP sessions under specified cpanel_username from remote Cpanel server.

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
    Paremeters
        request: Httprequest
        cpanel_username: str cpanel account username
    Returns
        HttpResponse (JSON)
            success: int status result of API call
            message: str response message from API call
            *data: 
                sessions: list of ftp sessions from API call
    """
    try:
        sessions = Cpanel(cpanel_username).listftpsessions()
        if sessions:
            return format_ajax_response(True, "FTP Sessions retrieved successfully.", {"sessions": sessions})
        else:
            raise Exception("CpanelFTP library call to listftpsessions() returned False.")
    except Exception as ex:
        logger.error("Failed to get_sessions: %s" % ex)
        return format_ajax_response(False, "There was an error retrieving FTP sessions listing.")


@validated_request(AddFtpForm)
@validated_service
def createaccount(request, cpanel_username):
    """Creates FTP account

        Creates new FTP account under specified Cpanel account on remote Cpanel server.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_request
            request.POST must validate against AddFtpForm
            request.method must be POST
            request.user.is_authenticated() must be True
            request.is_ajax() must be True
        @validated_service
            service_id must belong to request.user.company.services
            service.vars is injected into view parameter            
    Paremeters
        request: Httprequest
            username: str ftp account username
            password: str ftp account password
            quota: int ftp account quota
            homedir: str ftp account home directory
        cpanel_username: str cpanel account username
    Returns
        HttpResponse (JSON)
            success: int status result of API call
            message: str response message from API call
    """
    try:
        if Cpanel(cpanel_username).addftp(request.form.cleaned_data['username'], request.form.cleaned_data['password'], request.form.cleaned_data['quota'], request.form.cleaned_data['homedir']):
            ActionLogger().log(request.user, "created", "FTP Account", "FTP Account %s" % request.form.cleaned_data['username'])
            return format_ajax_response(True, "FTP Account created successfully.")
        else:
            raise Exception("CpanelFTP library call to addftp(%s, %s, %s, %s) returned False." % (request.form.cleaned_data['username'], request.form.cleaned_data['password'], request.form.cleaned_data['quota'], request.form.cleaned_data['homedir']))
    except Exception as ex:
        logger.error("Failed to createaccount: %s" % ex)
        return format_ajax_response(False, "There was an error creating the FTP account.")


@validated_request(DelFtpForm)
@validated_service
def delaccount(request, cpanel_username):
    """Deletes FTP account

        Deletes specified FTP account from specified Cpanel account on remote Cpanel server.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_request
            request.POST must validate against DelFtpForm
            request.method must be POST
            request.user.is_authenticated() must be True
            request.is_ajax() must be True
        @validated_service
            service_id must belong to request.user.company.services
            service.vars is injected into view parameter            
    Paremeters
        request: Httprequest
            username: str ftp account username
            destroy: bool destroy data
        cpanel_username: str cpanel account username
    Returns
        HttpResponse (JSON)
            success: int status result of API call
            message: str response message from API call
    """
    try:
        if Cpanel(cpanel_username).delftp(request.form.cleaned_data['username'], request.form.cleaned_data['destroy']):
            ActionLogger().log(request.user, "modified", "Password", "FTP Account %s" % request.form.cleaned_data['username'])
            return format_ajax_response(True, "FTP Account deleted successfully.")
        else:
            raise Exception("CpanelFTP library call to delftp(%s, %s) returned False." % (reqeust.form.clenaed_data["username"], request.form.cleaned_data["destroy"]))
    except Exception as ex:
        logger.error("Failed to delaccount: %s" % ex)
        return format_ajax_response(False, "There was an error deleting the FTP account.")


@validated_request(ChpwForm)
@validated_service
def chpw(request, cpanel_username):
    """Change FTP account password

        Updates specified FTP account password on remote Cpanel server.

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
    Paremeters
        request: Httprequest
            username: str ftp account username
            password: str new password
        cpanel_username: str cpanel account username
    Returns
        HttpResponse (JSON)
            success: int status result of API call
            message: str response message from API call
    """
    try:
        if Cpanel(cpanel_username).passwd(request.form.cleaned_data['username'], request.form.cleaned_data['password']):
            ActionLogger().log(request.user, "modified", "Password", "FTP Account %s" % request.form.cleaned_data['username'])
            return format_ajax_response(True, "FTP account password updated successfully.")
        else:
            raise Exception("CpanelFTP library call to passwd(%s, %s) returned False." % (request.form.cleaned_data['username'], request.form.cleaned_data['password']))
    except Exception as ex:
        logger.error("Failed to chpw: %s" % ex)
        return format_ajax_response(False, "There was an error updating the ftp account password.")


@validated_request(SetQuotaForm)
@validated_service
def setquota(request, cpanel_username):
    """Set FTP account quota

        Updates specified FTP account quota under specified Cpanel account on remote Cpanel server.

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
    Paremeters
        request: Httprequest
            username: str ftp account username
            quota: int new account quota
        cpanel_username: str cpanel account username
    Returns
        HttpResponse (JSON)
            success: int status result of API call
            message: str response message from API call
    """
    try:
        if Cpanel(cpanel_username).setquota(request.form.cleaned_data['username'], request.form.cleaned_data['quota']):
            ActionLogger().log(request.user, "modified", "Quota %s" % request.form.cleaned_data["quota"], "FTP Account %s" % request.form.cleaned_data['username']) 
            return format_ajax_response(True, "FTP account quota updated successfully.")
        else:
            raise Exception("CpanelFTP library call to setquota(%s, %s) returned False." % (request.form.cleaned_data['username'], request.form.cleaned_data['quota']))
    except Exception as ex:
        logger.error("Failed to setquota: %s" % ex)
        return format_ajax_response(False, "There was an error updating the FTP account quota.")