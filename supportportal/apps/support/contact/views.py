# System
import logging
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
# Project
from common.decorators import validated_request
from common.helpers import format_ajax_response
# App
from .forms import ContactForm


logger = logging.getLogger(__name__)


@login_required
def index(request):
    """Contact Base View

        Displays contact information and form.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @login_required
            request.user.is_authenticated() must be True
    Parameters
        request: HttpRequest
    Returns
        HttpResponse (contact/index.html)
            contact_form: Form contact form
    """
    return render(request, 'contact/index.html', {'contact_form': ContactForm()})


@validated_request(ContactForm)
def feedback(request):
    """Process feedback submission

        Processes Contact app form submission.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_request
            request.POST must validate against ContactForm
            request.method must be POST
            request.is_ajax() must be True
            request.user.is_authenticated() must be True            
    Parameters
        request: HttpRequest
            department: str destination department
            subject: str submission subject
            message: str message
    Returns
        HttpRepsonse (JSON)
            success: int status response
            message: str message response
    """
    if request.form.cleaned_data['department'] == 'BILL':
        to_email = 'billing@cybercon.net'
    elif request.form.cleaned_data['department'] == 'SUPP':
        to_email = 'support@cybercon.net'        
    elif request.form.cleaned_data['department'] == 'SALE':
        to_email = 'sales@cybercon.net'
    elif request.form.cleaned_data['department'] == 'AFFI':
        to_email = 'affiliates@cybercon.net'    
    elif request.form.cleaned_data['department'] == 'MANA':
        to_email = 'management@cybercon.net'

    try:
        send_mail(request.form.cleaned_data['subject'], request.form.cleaned_data['message'], request.user, to_email)
        return format_ajax_response(True, "Message delivered successfully.")
    except Exception as ex:
        logger.error("Failed to feedback: %s" % ex)
        return format_ajax_response(False, "There was an error delivering the message.")