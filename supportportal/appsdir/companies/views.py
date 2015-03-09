from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, render
from appsdir.contacts.forms import ContactCreationForm
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
            contact_form: form ContactCreationForm
    """
    company = get_object_or_404(Company, pk=company_id)

    data = {
        'company_id': company_id,
        'company_form': CompanyForm(instance=company),
        'contact_form': ContactCreationForm()
    }

    return render(request, 'companies/detail.html', data)

@staff_member_required
def index(request):
    """Company Index View

        Retrieves listing of Companies.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @staff_member_required
            request.user.is_staff() must be True
    Parameters
        request: HttpRequest
    Returns
        HttpResponse (companies/index.html)
            companyform: form CompanyForm
    """
    return render(request, 'companies/index.html', {'companyform':  CompanyForm()})