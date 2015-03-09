from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, render
from .models import Queue, Ticket, Post, Macro
from .forms import QueueForm, AdminSetTicketForm, MacroForm, TicketForm, PostForm, AdminCreateTicketForm
from appsdir.contacts.models import Contact


@login_required
def index(request):
    """Tickets List View

        Retrieves and displays a listing of open tickets for specified Company.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @login_required
            request.user.is_authenticated() must be True
    Paremeters
        request: HttpRequest
    Returns
        HttpReponse (support/index.html)
    """
    return render(request, 'support/index.html')


@login_required
def detail(request, ticket_id):
    """Ticket Detail View

        Retrieves and displays details of a single specified Ticket.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @login_required
            request.user.is_authenticated() must be True
    Paremeters
        request: HttpRequest
        ticket_id: int ticket id
    Returns
        HttpResponse (support/detail.html)
            ticket_id: int ticket id
    """
    ticket = get_object_or_404(Ticket, pk=ticket_id)

    response = {'ticket_id': ticket_id}
    if request.user.is_staff:
        ticketform = AdminSetTicketForm(instance=ticket)
        ticketform.fields['author'].queryset = Contact.objects.filter(company=ticket.author.company)
        ticketform.fields['owner'].queryset = Contact.objects.filter(company=None)
        response.update({
            'macroform': MacroForm(),
            'ticketform': ticketform,
        })

    return render(request, 'support/detail.html', response)


@staff_member_required
def admin(request):
    """Ticket Detail View

        Retrieves and displays details of a single specified Ticket.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @login_required
            request.user.is_authenticated() must be True
    Paremeters
        request: HttpRequest
        ticket_id: int ticket id
    Returns
        HttpResponse (support/admin.html)
            ticket_id: int ticket id
    """
    response = {
        'queueform': QueueForm(),
    }

    return render(request, 'support/admin.html', response)


@login_required
def new(request):
    """Ticket Detail View

        Retrieves and displays details of a single specified Ticket.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @login_required
            request.user.is_authenticated() must be True
    Paremeters
        request: HttpRequest
        ticket_id: int ticket id
    Returns
        HttpResponse (support/admin.html)
            ticket_id: int ticket id
    """
    if request.user.is_staff:
        ticketform = AdminCreateTicketForm()
    else:
        ticketform = TicketForm()
        ticketform.fields['contacts'].queryset = Contact.objects.filter(company=request.user.company, status=True)

    response = {
        'ticketform': ticketform,
        'postform': PostForm(),
    }

    return render(request, 'support/new.html', response)