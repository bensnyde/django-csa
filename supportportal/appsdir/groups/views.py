from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from .forms import GroupForm


@staff_member_required
def index(request):
    """group Index View
    
        Retrieves listing of groups.
    
    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @staff_member_required
            request.user.is_staff() must be True
    Parameters
        request: HttpRequest
    Returns
        HttpResponse (groups/index.html)
            groupform: form groupForm
    """
    return render(request, 'groups/index.html', {'groupform': GroupForm()})
