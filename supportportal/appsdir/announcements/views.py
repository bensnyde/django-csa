from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, render
from .models import Announcement
from .forms import AnnouncementForm


@login_required
def detail(request, announcement_id):
    """Company Detail View

        Retrieve Company details as specified by company.pk.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @login_required
            request.user.is_authenticated() must be True
    Parameters
        request: HttpRequest
        announcement_id: int company id
    Returns
        HttpResponse (announcements/detail.html)
            company_detail: queryset Company of specified announcement_id
            company_form: form CompanyForm
            contact_form: form ContactCreationForm
    """
    return render(request, 'announcements/detail.html', {'announcement_id': announcement_id})

@staff_member_required
def index(request):
    """Announcement Index View

        Retrieves listing of Announcements.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @staff_member_required
            request.user.is_staff() must be True
    Parameters
        request: HttpRequest
    Returns
        HttpResponse (announcements/index.html)
            announcementform: form AnnouncementForm
    """
    return render(request, 'announcements/index.html', {'announcementform':  AnnouncementForm()})