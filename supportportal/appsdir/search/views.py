from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from appsdir.announcements.models import Announcement
from appsdir.support.models import Ticket, Post, Macro, Queue
from appsdir.knowledgebase.models import Category, Tag, Article
from appsdir.companies.models import Company
from appsdir.contacts.models import Contact
from common.helpers import format_ajax_response
from .forms import SearchForm
import watson

@login_required
def results(request):
    form = SearchForm(request.REQUEST)
    if form.is_valid():
        results = []

        if request.user.is_staff:
            announcement_queryset = Announcement.objects.all()
            contact_queryset = Contact.objects.all()
            company_queryset = Company.objects.all()
            ticket_queryset = Ticket.objects.all()
            post_queryset = Post.objects.all()
        else:
            announcement_queryset = Announcement.objects.filter(public=True)
            contact_queryset = Contact.objects.filter(company=request.user.company)
            company_queryset = Company.objects.filter(pk=request.user.company.pk)
            ticket_queryset = Ticket.objects.filter(author__company=request.user.company)
            post_queryset = Post.objects.filter(author__company=request.user.company)

        # Announcements
        announcements = []
        for result in watson.search(form.cleaned_data['querystr'], models=(announcement_queryset,)):
            announcements.append({'title': result.title, 'description': result.description, 'url': result.url, 'contenttype': result.content_type.model})

        if len(announcements):
            results.append({"Announcements": announcements})

        # Tickets (ticket, post)
        tickets = []
        for result in watson.search(form.cleaned_data['querystr'], models=(ticket_queryset, post_queryset)):
            tickets.append({'title': result.title[:40], 'description': result.description, 'url': result.url, 'contenttype': result.content_type.model})

        if len(tickets):
            results.append({"Tickets": tickets})

        # Knowledgebase (category, article, tag)
        kb = []
        for result in watson.search(form.cleaned_data['querystr'], models=(Category, Article, Tag)):
            kb.append({'title': result.title, 'description': result.description, 'url': result.url, 'contenttype': result.content_type.model})

        if len(kb):
            results.append({"Knowledgebase": kb})

        # Accounts (company, contact)
        accounts = []
        for result in watson.search(form.cleaned_data['querystr'], models=(company_queryset, contact_queryset)):
            accounts.append({'title': result.title, 'description': result.description, 'url': result.url, 'contenttype': result.content_type.model})

        if len(accounts):
            results.append({"Accounts": accounts})

        if request.is_ajax():
            return format_ajax_response(True, "Search results retrieved successfully.", {"matches": results})

        return render(request, 'search/results.html', {'querystr': form.cleaned_data['querystr'], 'matches': results})