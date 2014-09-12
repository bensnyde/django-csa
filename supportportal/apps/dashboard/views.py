from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


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
    if request.user.is_staff:
        return redirect('backend:index')
    else:
        return render(request, 'dashboard/index.html')