# System
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, render
# Project
from apps.contacts.models import Contact
from apps.contacts.forms import ContactForm
from apps.loggers.models import ErrorLogger, ActionLogger
from common.decorators import validated_request, validated_staff
from common.helpers import format_ajax_response
# App 
from .models import Company
from .forms import CompanyForm


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
        ErrorLogger().log(request, "Error", "Error enumerating Companies in apps.companies.views.get_companies: %s" % ex)
        return format_ajax_response(False, "There was a problem retrieving the companies listing.")


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
                    industry: 
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
    if not (request.user.company_id == int(company_id) or request.user.is_admin == True):
        ErrorLogger().log(request, "Forbidden", "Unauthorized attempt to modify resources in apps.companies.views.get")
        return HttpResponseForbidden() 

    company = get_object_or_404(Company, pk=company_id)

    try:
        return format_ajax_response(True, "Company profile retrieved successfully.", {'company': company.dump_to_dict()})
    except Exception as ex:
        ErrorLogger().log(request, "Error", "Error fetching Company in apps.companies.views.get: %s" % ex)
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
            industry:
            website:
            phone:
            fax:
        company_id: int company id
    Returns
        HttpResponse (JSON)
            success: int status result 
            message: str response message 
    """
    # Ensure requesting user has access to update specified profile
    if not (request.user.company_id == int(company_id) or request.user.is_admin == True):
        ErrorLogger().log(request, "Forbidden", "Unauthorized attempt to modify resources in apps.companies.views.set")
        return HttpResponseForbidden()        
      
    if request.user.is_staff and not int(company_id):
        form = CompanyForm(request.POST)
        if form.is_valid():
            company = form.save()
            ActionLogger().log(request.user, "created", "Company %s" % company)
            return format_ajax_response(True, "Company created successfully.")
        else:
            return format_ajax_response(False, "Form data failed validation.", errors=dict((k, [unicode(x) for x in v]) for k,v in form.errors.items()))                 
    else:
        company = get_object_or_404(Company, pk=company_id)

        form = CompanyForm(request.POST, instance=company)
        if form.is_valid():
            form.save()
            ActionLogger().log(request.user, "modified", "Company %s" % company)
            return format_ajax_response(True, "Company profile updated successfully.") 
        else:
            return format_ajax_response(False, "Form data failed validation.", errors=dict((k, [unicode(x) for x in v]) for k,v in form.errors.items()))


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
    if not (request.user.company_id == int(company_id) or request.user.is_admin == True):
        ErrorLogger().log(request, "Forbidden", "Unauthorized attempt to modify resources in apps.companies.views.get_contacts")
        return HttpResponseForbidden() 

    company = get_object_or_404(Company, pk=company_id)       

    try:
        contacts = []
        for contact in Contact.objects.filter(company=company):
            contacts.append(contact.dump_to_dict())

        return format_ajax_response(True, "Company contacts listing retrieved successfully.", {'contacts': contacts})
    except Exception as ex:
        ErrorLogger().log(request, "Error", "Error enumerating Company Contacts in apps.companies.views.get_contacts: %s" % ex)
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
    if request.user.company_id != int(company_id):
        ErrorLogger().log(request, "Forbidden", "Unauthorized attempt to modify resources in apps.companies.views.get_feeds")
        return HttpResponseForbidden() 

    company = get_object_or_404(Company, pk=company_id)

    try:
        activities = []
        for action in ActionLogger.objects.filter(actor__in=Contact.objects.filter(company=company)).order_by("-timestamp")[:10]:
            activities.append(action.dump_to_dict())

        recent_users = []
        for user in Contact.objects.filter(company=company).order_by("-created")[:6]:
            recent_users.append({'id': user.pk, 'name': user.get_full_name(), 'email': user.email})

        return format_ajax_response(True, "Feeds retrieved successfully.", {'feeds': {'activities': activities,'recent_users': recent_users}})
    except Exception as ex:
        ErrorLogger().log(request, "Error", "Error fetching Company feeds in apps.companies.views.get_feeds: %s" % ex)
        return format_ajax_response(False, "There was a problem retrieving the feeds.")