from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseForbidden, HttpResponseBadRequest, HttpResponseRedirect
from django.utils.safestring import mark_safe
from functools import wraps
from apps.loggers.models import ErrorLogger
import json

_ERROR_MSG = '<!DOCTYPE html><html lang="en"><body><h1>%s</h1><p>%%s</p></body></html>'
_400_ERROR = _ERROR_MSG % '400 Bad Request'
_403_ERROR = _ERROR_MSG % '403 Forbidden'
_405_ERROR = _ERROR_MSG % '405 Not Allowed'

def validated_request(FormClass=None, method='POST', login_required=True, ajax_required=True):
    def decorator(view_func):
        def _ajax_view(request, *args, **kwargs):
            if request.method != method and method != 'REQUEST':
                return HttpResponseNotAllowed(mark_safe(_405_ERROR % ('Request must be a %s.' % method)))

            if ajax_required and not request.is_ajax():
                return HttpResponseForbidden(mark_safe(_403_ERROR % 'Request must be set via AJAX.'))

            if login_required and not request.user.is_authenticated():
                # Log me
                return HttpResponseRedirect(reverse('django.contrib.auth.views.login'))

            if FormClass:
                f = FormClass(getattr(request, method))
                if not f.is_valid():
                    errors = dict((k, [unicode(x) for x in v]) for k,v in f.errors.items())
                    return HttpResponse(json.dumps({'success': 0, 'message': "Form data failed validation.", 'errors': errors}), 'application/json')
                request.form = f

            return view_func(request, *args, **kwargs)
        return wraps(view_func)(_ajax_view)
    return decorator

def validated_service(function):
    @wraps(function)
    def decorator(request, *args, **kwargs):
        bpath = request.path_info[:request.path_info.index('/', 10)+1]
        if bpath == '/services/solusvm/' or bpath == '/services/vmware/':
            bpath = '/services/server/'
            
        service_vars = request.user.get_service_vars(bpath, kwargs["service_id"])
        if not service_vars:
            ErrorLogger().log(request, "Forbidden", "User attempted access to unauthorized service.") 
            return HttpResponseForbidden("Service ID does not belong to the requesting user.")
        
        kwargs.pop("service_id", None)
        kwargs.update(service_vars)

        return function(request, *args, **kwargs)
    return decorator

def validated_staff(function):
    @wraps(function)
    def decorator(request, *args, **kwargs):
        if not request.user.is_staff:
            ErrorLogger().log(request, "Forbidden", "non-staff contact attempted administrative function.") 
            return HttpResponseForbidden("Illegal request.")

        return function(request, *args, **kwargs)
    return decorator    