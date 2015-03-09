from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, render
from appsdir.companies.models import Company
from .forms import ContactForm, ContactAdminForm
from .models import Contact


@staff_member_required
def index(request):
    """Contact Detail View

        Retrieve Contact details as specified by contact.pk.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @login_required
            request.user.is_authenticated() must be True
    Parameters
        request: HttpRequest
        contact_id: int Contact id
    Returns
        HttpResponse (contacts/detail.html)
            user_details: queryset contact
    """
    data = {
        'contactform': ContactAdminForm(),
    }

    return render(request, 'contacts/index.html', data)

@login_required
def detail(request, contact_id):
    """Contact Detail View

        Retrieve Contact details as specified by contact.pk.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @login_required
            request.user.is_authenticated() must be True
    Parameters
        request: HttpRequest
        contact_id: int Contact id
    Returns
        HttpResponse (contacts/detail.html)
            user_details: queryset contact
    """
    if request.user.is_staff:
        contactform = ContactAdminForm()
    else:
        contactform = ContactForm()

    return render(request, 'contacts/detail.html', {'contact_id': contact_id, 'contactform': contactform})