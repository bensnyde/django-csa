# System
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
# Project
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
    return render(request, 'services/index.html')