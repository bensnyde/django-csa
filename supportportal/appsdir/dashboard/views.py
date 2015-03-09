from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from appsdir.announcements.forms import AnnouncementForm

@login_required
def index(request):
    """Dashboard View

        Renders base Dashboard.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @login_required
            request.user.is_authenticated() must be True
    Paremeters
        request: Httprequest
    Returns
        HttpResponse (dashboard/index.html)
    """
    response = dict()
    if request.user.is_staff:
        response["announcementform"] = AnnouncementForm()

    return render(request, 'dashboard/index.html')

@login_required
def contactus(request):
    """Dashboard View

        Renders base Dashboard.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @login_required
            request.user.is_authenticated() must be True
    Paremeters
        request: Httprequest
    Returns
        HttpResponse (dashboard/index.html)
    """
    return render(request, 'dashboard/contactus.html')