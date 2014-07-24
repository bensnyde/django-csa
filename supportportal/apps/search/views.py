# System
import json
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.contrib.auth.decorators import login_required
# Project
from apps.search.forms import SearchForm
from apps.dns.views import search as dnssearch
from apps.support.tickets.models import search as ticketsearch
from apps.support.knowledgebase.models import search as kbsearch
from apps.companies.models import Company, search as companysearch
from apps.contacts.models import search as customersearch
from apps.loggers.models import ErrorLogger

errorlogger = ErrorLogger()

@login_required
def results(request):
    """
    Displays search results.
    """
    matches = {} 
    querystr = ""
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            querystr = form.cleaned_data['querystr']

            # Search Tickets
            tickets = query_support_tickets(querystr) 
            if tickets:
                matches['Tickets'] = tickets

            # Search Knowledgebase
            kb_articles = query_support_knowledgebase(querystr) 
            if kb_articles:
                matches['Knowledgebase'] = kb_articles
            
            # Search Customers
            contacts = query_account_contacts(request.user.company_id, querystr)
            if contacts:
                matches['Contacts'] = contacts

            # Company Services
            company = Company.objects.get(pk=request.user.company_id)
            services = company.services.all()
            for service in services:
                result = coupler_uri_to_model_search(service.coupler.uri, request.user, service.id, querystr)
                if result:
                    matches.update({service.name: result})              

        if request.is_ajax(): 
            # Return JSON 
            return HttpResponse(json.dumps(matches), mimetype='application/json')
    else:
        errorlogger.log(request, "Requests", "Anomalous HttpRequest to search.views.results")
    # Render and return Template

    template = loader.get_template('search/results.html')
    context = RequestContext(request, {
        'querystr': querystr,       
        'matches': matches,
    })
    return HttpResponse(template.render(context))


def query_support_knowledgebase(querystr):
    matches = []
    kbarticles = kbsearch(querystr)
    if kbarticles:
        for article in kbarticles:
            matches.append({
                'link': reverse('knowledgebase:detail', kwargs={"article_id": article.id}), 
                'title': article.title, 
                'preview': article.contents[:128]
            })

    return matches
        
def query_support_tickets(querystr):
    return ticketsearch(querystr)

def query_account_contacts(company_id, querystr):
    matches = []
    contacts = customersearch(querystr, company_id)
    if contacts:
        for contact in contacts:
            matches.append({
                'link': reverse('contacts:detail', kwargs={"user_id": contact.id}), 
                'title': contact.email, 
                'preview': contact.get_full_name()
            })

    return matches

def coupler_uri_to_model_search(coupler_uri, user, service_id, query_str):
    if coupler_uri == "/services/dns/":
        return query_dns_service(user, service_id, query_str)

def query_dns_service(user, service_id, query_str):
    matches = []
    domains = dnssearch(user, service_id, query_str)
    if domains:
        for domain in domains:
            matches.append({
                'link': reverse('dns:detail', kwargs={"service_id": service_id, "zone": domain}), 
                'title': domain
            })

    return matches
