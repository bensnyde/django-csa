# System
import logging
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
# Project
from apps.contacts.models import Contact
from apps.contacts.forms import ContactForm
from apps.loggers.models import ActionLogger
from common.decorators import validated_request, validated_staff
from common.helpers import format_ajax_response
# App 
from .models import Company
from .forms import CompanyForm


logger = logging.getLogger(__name__)


@login_required
def detail(request, company_id):
    """Company Detail View

        Retrieve Company details as specified by company.pk. 

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @login_required
            request.user.is_authenticated() must be True
    Parameters
        request: HttpRequest
        company_id: int company id
    Returns
        HttpResponse (companies/detail.html)
            company_detail: queryset Company of specified company_id
            company_form: form CompanyForm
            contact_form: form ContactForm
    """
    company = get_object_or_404(Company, pk=company_id)
    
    company_form = CompanyForm(instance=company)
    contact_form = ContactForm()

    return render(request, 'companies/detail.html', {
        'company_detail': company,
        'company_form': company_form, 
        'contact_form': contact_form
    })


@validated_staff
def index(request):
    """Company Index View

        Retrieves listing of Companies. 

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_staff
            request.user.is_staff() must be True
    Parameters
        request: HttpRequest
    Returns
        HttpResponse (companies/index.html)
            companyform: form CompanyForm
    """
    return render(request, 'companies/index.html', {'companyform':  CompanyForm()})    


@validated_staff
@validated_request(None)
def get_companies(request):
    """Get Companies

        Retrieves listing of Companies. 

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_staff
            request.user.is_staff() must be True    
        @validated_request
            request.method must be POST
            request.is_ajax() must be True
            request.user.is_authenticated() must be True
    Parameters
        request: HttpRequest
    Returns
        HttpResponse (JSON)
            success: int status result 
            message: str response message 
            *data:
                companies:
                    name: str company name
                    status: bool company status
                    id: int company id
    """    
    try:
        companies = []
        for company in Company.objects.all():
            companies.append({'name': company.name, 'status': company.status, 'id': company.pk})

        return format_ajax_response(True, "Companies list retrieved successfully.", {'companies': companies})
    except Exception as ex:
        logging.error("failed to get_companies: %s" % ex)
        return format_ajax_response(False, "There was a problem retrieving the companies listing.")


@validated_staff
@validated_request(None)
def get_services(request):
    """Get Companies

        Retrieves listing of Companies. 

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_staff
            request.user.is_staff() must be True    
        @validated_request
            request.method must be POST
            request.is_ajax() must be True
            request.user.is_authenticated() must be True
    Parameters
        request: HttpRequest
    Returns
        HttpResponse (JSON)
            success: int status result 
            message: str response message 
            *data:
                companies:
                    name: str company name
                    status: bool company status
                    id: int company id
    """    
    try:
        company = Company.objects.get(pk=int(request.POST['company_id']))

        services = []
        for service in company.services.all():
            services.append({'name': service.name, 'id': service.pk})

        return format_ajax_response(True, "Company's services retrieved successfully.", {'services': services})
    except Exception as ex:
        logging.error("failed to get_services: %s" % ex)
        return format_ajax_response(False, "There was a problem retrieving the company's services.")


@validated_request(None)
def get(request, company_id):
    """Get Company Details

        Retrieve Company details as specified by company.pk. 

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_request
            request.method must be POST
            request.is_ajax() must be True
            request.user.is_authenticated() must be True
    Parameters
        request: HttpRequest
        company_id: int company id
    Returns
        HttpResponse (JSON)
            success: int status result 
            message: str response message 
            *data:
                company:
                    name: 
                    description: 
                    created: 
                    modified: 
                    website: 
                    address1: 
                    address2: 
                    city: 
                    state: 
                    zip: 
                    phone:
                    fax:      
    """
    try:
        company = Company.objects.get(pk=company_id)

        if not (request.user.company_id == int(company_id) or request.user.is_admin == True):
            raise Exception("Fobiden: requesting user doesn't have permission to specified Company.")

        return format_ajax_response(True, "Company profile retrieved successfully.", {'company': company.dump_to_dict()})
    except Exception as ex:
        logger.error("Failed to get: %s" % ex)
        return format_ajax_response(False, "There was a problem retrieving the company profile.")


@validated_request(None)
def set(request, company_id):
    """Set Company 

        Creates Company, or updates existing Company as specified by company.pk. 

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_request
            request.method must be POST
            request.is_ajax() must be True
            request.user.is_authenticated() must be True
    Parameters
        request: HttpRequest
            name:
            description:
            address1:
            address2:
            city:
            state:
            zip:
            website:
            phone:
            fax:
        company_id: int company id
    Returns
        HttpResponse (JSON)
            success: int status result 
            message: str response message 
    """
    try:
        if not (request.user.company_id == int(company_id) or request.user.is_admin == True):
            raise Exception("Fobiden: requesting user doesn't have permission to specified Company.")

        if request.user.is_staff and not int(company_id):
            form = CompanyForm(request.POST)
            if form.is_valid():
                company = form.save()
                ActionLogger().log(request.user, "created", "Company %s" % company)
                return format_ajax_response(True, "Company created successfully.")
            else:
                return format_ajax_response(False, "Form data failed validation.", errors=dict((k, [unicode(x) for x in v]) for k,v in form.errors.items()))                 
        else:
            company = Company.objects.get(pk=company_id)

            form = CompanyForm(request.POST, instance=company)
            if form.is_valid():
                form.save()
                ActionLogger().log(request.user, "modified", "Company %s" % company)
                return format_ajax_response(True, "Company profile updated successfully.") 
            else:
                return format_ajax_response(False, "Form data failed validation.", errors=dict((k, [unicode(x) for x in v]) for k,v in form.errors.items()))
    except Exception as ex:
        logger.error("Failed to set: %s" % ex)
        return format_ajax_response(False, "There was an error setting the Company record.")


@validated_request(None)
def get_contacts(request, company_id):
    """Get Company Contacts

        Retrieve listing of Contacts belonging to Company as specified by company.pk. 

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_request
            request.method must be POST
            request.is_ajax() must be True
            request.user.is_authenticated() must be True
    Parameters
        request: HttpRequest
        company_id: int company id
    Returns
        HttpResponse (JSON)
            success: int status result 
            message: str response message 
            *data:
                contacts:
                    first_name:
                    last_name:
                    role: 
                    id:
                    email:
    """
    try:
        company = Company.objects.get(pk=company_id)

        if not (request.user.company_id == int(company_id) or request.user.is_admin == True):
            raise Exception("Fobiden: requesting user doesn't have permission to specified Company.")

        contacts = []
        for contact in Contact.objects.filter(company=company):
            contacts.append(contact.dump_to_dict())

        return format_ajax_response(True, "Company contacts listing retrieved successfully.", {'contacts': contacts})
    except Exception as ex:
        logger.error("Failed to get_contacts: %s" % ex)
        return format_ajax_response(False, "There was a problem retrieving company contacts listing.")


@validated_request(None)
def get_feeds(request, company_id):
    """Get Company activity feeds

        Retrieve listing of actionloggers and authenticationloggers for Company as specified by company.pk. 

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_request
            request.method must be POST
            request.is_ajax() must be True
            request.user.is_authenticated() must be True
    Parameters
        request: HttpRequest
        company_id: int company id
    Returns
        HttpResponse (JSON)
            success: int status result 
            message: str response message 
            *data:
                feeds:
                    activities:
                        action: 
                        timestamp:
                        actor:
                    recent_users:
                        email:
                        id:
                        name:
    """
    try:
        company = Company.objects.get(pk=company_id)

        if not (request.user.company_id == int(company_id) or request.user.is_admin == True):
            raise Exception("Fobiden: requesting user doesn't have permission to specified Company.")

        activities = []
        for action in ActionLogger.objects.filter(actor__in=Contact.objects.filter(company=company)).order_by("-timestamp")[:10]:
            activities.append(action.dump_to_dict())

        recent_users = []
        for user in Contact.objects.filter(company=company).order_by("-created")[:6]:
            recent_users.append({'id': user.pk, 'name': user.get_full_name(), 'email': user.email})

        return format_ajax_response(True, "Feeds retrieved successfully.", {'feeds': {'activities': activities,'recent_users': recent_users}})
    except Exception as ex:
        logger.error("Failed to get_feeds: %s" % ex)
        return format_ajax_response(False, "There was a problem retrieving the feeds.")