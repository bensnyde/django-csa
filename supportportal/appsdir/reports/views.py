from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required


@staff_member_required
def index(request):
    """Reports Index View

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @staff_member_required
            request.user.is_staff must be True
    Parameters
        request: HttpRequest
    Returns
        HttpResponse (reports/index.html)
    """
    return render(request, 'reports/index.html')