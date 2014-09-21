# System
from django.shortcuts import render
# Project
from apps.announcements.forms import AnnouncementForm
from common.decorators import validated_staff


@validated_staff
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
    return render(request, 'backend/index.html', {'announcementform': AnnouncementForm()})