# System
import logging
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, render
# Proejct
from common.decorators import validated_request
from common.helpers import format_ajax_response
from apps.companies.models import Company
from apps.loggers.models import ActionLogger, AuthenticationLogger
# App
from .forms import ContactForm, ContactPasswordForm, ContactCreationForm
from .models import Contact


logger = logging.getLogger(__name__)


@login_required
def detail(request, user_id):
    """Contact Detail View

        Retrieve Contact details as specified by contact.pk.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @login_required
            request.user.is_authenticated() must be True
    Parameters
        request: HttpRequest
        user_id: int Contact id
    Returns
        HttpResponse (contacts/detail.html)
            user_details: queryset contact
    """
    user = get_object_or_404(Contact, pk=user_id)

    if not user.company == request.user.company:
        logger.error("Forbidden: requesting user doesn't have permission to specified Company's Contacts.")
        return HttpResponseForbidden()

    return render(request, 'contacts/detail.html', {'user_details': user})


@validated_request(None)
def get(request, user_id):
    """Get Contact

        Retrieves Contact details as specified by contact.pk.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_request
            request.method must be POST
            request.is_ajax() must be True
            request.user.is_authenticated() must be True
    Parameters
        request: HttpRequest
        user_id: int Contact id
    Returns
        HttpResponse (JSON)
            success: int status result
            message: str response message
            *data:
                contact:
    """
    try:
        contact = Contact.objects.get(pk=user_id)

        if not contact.company == request.user.company:
            raise Exception("Forbidden: requesting user doesn't have permission to specified Company's Contacts.")

        return format_ajax_response(True, "Contact retrieved successfully.", {'contact': contact.dump_to_dict(full=True)})
    except Exception as ex:
        logger.error("Failed to get: %s" % ex)
        return format_ajax_response(False, "There was an error retrieving contact.")


@validated_request(None)
def set(request):
    """Set Contact

        Updates Contact as specified by contact.pk.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_request
            request.method must be POST
            request.is_ajax() must be True
            request.user.is_authenticated() must be True
    Parameters
        request: HttpRequest
            user_id: int contact id
            email:
            first_name:
            last_name:
            title:
            personal_phone:
            office_phone:
            fax:
            is_active:
            role:
    Returns
        HttpResponse (JSON)
            success: int status result
            message: str response message
    """
    try:
        user = Contact.objects.get(pk=int(request.POST['user_id']))

        if not (request.user.company_id == user.company_id or request.user.is_staff == True):
            raise Exception("Forbidden: requesting user doesn't have permission to access specified Company's Contacts.")

        form = ContactForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save()

            if form.cleaned_data["role"] == "Admin" and request.user.is_admin is True:
                user.is_admin = True
            else:
                user.is_admin = False

            user.save()
            ActionLogger().log(request.user, "modified",  "Contact %s" % user)
            return format_ajax_response(True, "Contact set successfully.")
        else:
            return format_ajax_response(False, "Form data failed validation.", errors=dict((k, [unicode(x) for x in v]) for k,v in form.errors.items()))
    except Exception as ex:
        logger.error("Failed to set: %s" % ex)
        return format_ajax_response(False, "There was an error updating specified contact.")


@validated_request(ContactCreationForm)
def create(request):
    """Create Contact

        Creates new company contact.

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
            email: str email address
            first_name: str first name
            last_name: str last name
            password: str password
            company: int company id
    Returns
        HttpResponse (JSON)
            success: int status result
            message: str response message
    """
    try:
        company = Company.objects.get(pk=int(request.POST["company"]))

        if not (request.user.company_id == company.pk or request.user.is_admin == True):
            raise Exception("Forbidden: requesting user doesn't have permission to specified Company's Contacts.")

        contact = Contact.objects.create_user(
            email=request.form.cleaned_data["email"],
            first_name=request.form.cleaned_data["first_name"],
            last_name=request.form.cleaned_data["last_name"],
            password=request.POST["password"],
            company=company,
            title=request.form.cleaned_data["title"],
            personal_phone=request.form.cleaned_data["personal_phone"],
            office_phone=request.form.cleaned_data["office_phone"],
            fax=request.form.cleaned_data["fax"],
            role=request.form.cleaned_data["role"]
        )

        if contact.role == "Admin":
            contact.is_admin = True
            contact.save()

        ActionLogger().log(request.user, "created",  "Contact %s" % contact)
        return format_ajax_response(True, "Contact created successfully.")
    except Exception as ex:
        logger.error("Failed to create: %s" % ex)
        return format_ajax_response(False, "There was an error creating contact.")


@validated_request(ContactPasswordForm)
def chpw(request):
    """Set Contact password

        Updates password for Contact as specified by contact.pk.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_request
            request.POST must validate against ContactPasswordForm
            request.method must be POST
            request.is_ajax() must be True
            request.user.is_authenticated() must be True
    Parameters
        request: HttpRequest
            user_id: int contact id
            old_password: str old password
            new_password1: str new password
    Returns
        HttpResponse (JSON)
            success: int status result
            message: str response message
    """
    try:
        user = Contact.objects.get(pk=int(request.POST['user_id']))

        if not (request.user.company_id == user.company_id or request.user.is_staff == True):
            raise Exception("Forbidden: requesting user doesn't have permission to access specified Company's Contacts.")

        if user.check_password(request.form.cleaned_data['old_password']):
            user.set_password(request.form.cleaned_data['new_password'])
            user.save()

            ActionLogger().log(request.user, "modified",  "Contact %s" % user)
            return format_ajax_response(True, "Password updated successfully.")
        else:
            return format_ajax_response(False, "Incorrect password supplied.")
    except Exception as ex:
        logger.error("Failed to chpw: %s" % ex)
        return format_ajax_response(False, "There was an error setting password for specified contact.")


@validated_request(None)
def get_logs(request, user_id):
    """Get Contact Logs

        Retrieves ActionLogger and AuthenticationLogger feeds for Contact as specified by contact.pk.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_request
            request.method must be POST
            request.is_ajax() must be True
            request.user.is_authenticated() must be True
    Parameters
        request: HttpRequest
        user_id: int Contact id
    Returns
        HttpResponse (JSON)
            success: int status result
            message: str response message
            *data:
                authentication:
                    category:
                    ip:
                    user:
                    timestamp:
                    user_agent:
                action:
                    action:
                    timestamp:
                    actor:
    """
    try:
        user = Contact.objects.get(pk=user_id)

        if not (request.user.company_id == user.company_id or request.user.is_admin == True):
            raise Exception("Forbidden: requesting user doesn't have permission to access specified Company's Contacts.")

        authloggers = []
        for auth in AuthenticationLogger.objects.filter(user__id=user_id).order_by("-timestamp")[:10]:
            authloggers.append(auth.dump_to_dict())

        actionloggers = []
        for action in ActionLogger.objects.filter(actor=user_id).order_by("-timestamp")[:10]:
            actionloggers.append(action.dump_to_dict())

        return format_ajax_response(True, "Logs retrieved successfully.", {'authentication': authloggers, 'action': actionloggers})
    except Exception as ex:
        logger.error("Failed to get_logs: %s" % ex)
        return format_ajax_response(False, "There was an error retrieving the logs.")