# System
import logging
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.core.urlresolvers import reverse
# Project
from apps.loggers.models import ActionLogger
from common.decorators import validated_request, validated_staff
from common.helpers import format_ajax_response
# App
from .models import Ticket, Post, get_ticket_contacts_list, set_ticket_contacts_list, get_tickets_summary, get_companies_active_contacts
from .forms import TicketForm, PostForm, TicketIDForm, PostIDForm


logger = logging.getLogger(__name__)


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
        HttpReponse (tickets/index.html)
    """
    return render(request, 'tickets/index.html')


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
        HttpResponse (tickets/index.html)
            ticket_id: int ticket id
    """ 
    return render(request, 'tickets/detail.html', {'ticket_id': ticket_id})


@validated_request(None)
def get_tickets(request):
    """Get Tickets

        Retrieves listing of all open tickets belonging to requesting user's company.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_request
            request.method must be POST
            request.is_ajax() must be True
            request.user.is_authenticated() must be True          
    Paremeters
        request: HttpRequest
    Returns
        HttpResponse (JSON)
            success: int status result of API call
            message: str response message from API call
            *data:
                tickets: 
    """    
    try:
        if request.user.is_staff:
            if "flagged" in request.POST and request.POST["flagged"]==1:
                qset =  Ticket.objects.filter(status="Open").filter(flagged=True).order_by("-priority")
            else: 
                qset = Ticket.objects.filter(status="Open").order_by("-priority")
        else:
            qset = Ticket.objects.filter(owner_id__company_id=request.user.company_id).filter(status="Open").order_by('-priority')

        tickets = []
        for ticket in qset:
            tickets.append(ticket.dump_to_dict())

        return format_ajax_response(True, "Tickets listing retrieved successfully.", {"tickets": tickets })
    except Exception as ex:
        logger.error("Failed to get_company_tickets: %s" % ex)
        return format_ajax_response(False, "There was an error retrieving the tickets listing.")


@validated_request(None)
def get_ticket(request, ticket_id):
    """Get Ticket

        Retrieves specified ticket details.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_request
            request.method must be POST
            request.is_ajax() must be True
            request.user.is_authenticated() must be True          
    Paremeters
        request: HttpRequest
        ticket_id: int ticket id 
    Returns
        HttpResponse (JSON)
            success: int status result of API call
            message: str response message from API call
            *data:
                ticket: 
    """
    try:
        ticket = Ticket.objects.get(pk=ticket_id)

        if ticket.author.company_id != request.user.company_id:
            raise Exception("Requesting user does not have permission to access specified ticket.")     

        return format_ajax_response(True, "Ticket posts listing retrieved successfully.", {"ticket": ticket.dump_to_dict(full=True, admin=request.user.is_staff)})
    except Exception as ex:
        logger.error("Failed to get_ticket: %s" % ex)          
        return format_ajax_response(False, "There was an error retrieving ticket posts.")       


@validated_request(None)
def get_summary(request):
    """Get Tickets summary

        Retrieves a listing of open and total tickets belonging to requesting user's company.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_request
            request.method must be POST
            request.is_ajax() must be True
            request.user.is_authenticated() must be True   
    Paremeters
        request: HttpRequest
    Returns
        HttpResponse (JSON)
            success: int status result of call 
            message: str status result of call
            *data:
                summary:        
                    user: 
                        open: int number of open tickets authored by requesting user 
                        total: int total number of tickets authored by requesting user 
                    company: 
                        open: int number of open tickets authored by requesting user's Company 
                        total: int total number of tickets authored by requesting user's Company
    """
    try:
        summary = get_tickets_summary(request.user.id, request.user.company_id)
        return format_ajax_response(True, "Tickets summary retrieved successfully.", {"summary": summary})
    except Exception as ex:
        logger.error("Failed to get_summary: %s" % ex)
        return format_ajax_response(False, "There was an error retrieving the tickets summary.")


@validated_request(TicketIDForm)
def set_contacts(request):
    """Set Ticket Contacts

        Sets Contacts assigned to specified Ticket.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_request
            request.method must be POST
            request.is_ajax() must be True
            request.user.is_authenticated() must be True  
    Paremeters
        request: HttpRequest
            ticket: str ticket id 
            contacts: int[] contacts ids
    Returns
        HttpResponse (JSON)
            success: int status result of call 
            message: str status result of call
    """
    try:
        ticket = Ticket.objects.get(pk=request.form.cleaned_data['ticket_id'])
        contacts = request.POST.getlist('contacts[]')

        if set_ticket_contacts_list(ticket.id, contacts):
            Post.objects.create(ticket=ticket, author=request.user, contents="Modified ticket's cc listing.")
            ActionLogger().log(request.user, "modified", "Contacts %s" % contacts, "Ticket %s" % ticket.id)
            return format_ajax_response(True, "Tickets's contacts set successfully.")
        else:
            raise Exception("set_ticket_contacts_list(%s, %s) returned False." % (ticket.id, contacts))
    except Exception as ex:
        logger.error("Failed to set_contacts: %s" % ex)
        return format_ajax_response(False, "There wasn an error setting thet ticket's contacts.")


@validated_request(TicketIDForm, 'POST', True, False)
def set_post(request):
    """Create Post

        Creates a Post reply under specified Ticket.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_request
            request.method must be POST
            request.is_ajax() must be False
            request.user.is_authenticated() must be True  
    Paremeters
        request: HttpRequest
            ticket_id: int ticket id 
            attachment: file attachment
            contents: str reply contents 
    Returns
        HttpResponseRedirect
    """
    ticket = get_object_or_404(Ticket, pk=request.form.cleaned_data['ticket_id'])

    if ticket.owner.company_id != request.user.company_id:
        logger.error("Forbidden: requesting user doesn't have permission to specified Company's resources.")
        return HttpResponseForbidden()    

    post_form = PostForm(request.POST, request.FILES)
    if post_form.is_valid():    
        # Create new post object under specified ticket object
        post = post_form.save(commit=False)
        post.author_id = request.user.id
        post.ticket = ticket
        post.save()
        post_form.save_m2m()

        ActionLogger().log(request.user, "created", "Post %s" % post.id, "Ticket %s" % ticket.id)
    else:
        # Form validation failed
        pass

    # Redirect to ticket
    return HttpResponseRedirect(reverse('tickets:detail', kwargs=({'ticket_id':request.form.cleaned_data['ticket_id']})))


@validated_request(None, "REQUEST", True, False)
def create_ticket(request, service_id=0):
    """Process AJAX Create Ticket request

        Creates a new Ticket and Post object from an AJAX request.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_request
            request.method must be POST
            request.is_ajax() must be False
            request.user.is_authenticated() must be True  
    Paremeters
        request: HttpRequest
            contacts: int[] ticket Contact id's
            priority: int ticket priority (0==Low, 1==Normal, 2==Urgent)
            description: str synopsis of ticket
            contents: str reply body contents
            attachment: *file attachment        
    Returns
        HttpResponse (JSON)
            success: int status response of request
            message: str status response of request
            *data:
                ticket_id: int new ticket id 
    """
    if request.method == "POST":
        new_ticket_form = TicketForm(request.POST)
        new_post_form = PostForm(request.POST, request.FILES)
        if new_ticket_form.is_valid():
            if new_post_form.is_valid():
                # Create Ticket
                new_ticket = new_ticket_form.save(commit=False)
                new_ticket.author_id = request.user.id
                new_ticket.owner_id = request.user.id

                if "service" in request.POST:
                    new_ticket.service = request.user.company.services.get(pk=int(request.POST["service"]))

                new_ticket.save()
                new_ticket_form.save_m2m()

                set_ticket_contacts_list(new_ticket.id, request.POST.getlist('contacts'))

                # Create Post
                new_post = new_post_form.save(commit=False)
                new_post.ticket = new_ticket
                new_post.author_id = request.user.id
                new_post.save()

                # Log results
                ActionLogger().log(request.user, "created", "Ticket %s" % new_post.id)
                if request.is_ajax():
                    return format_ajax_response(True, "Ticket created successfully.", {"ticket_id": new_ticket.id})
                else:
                    return HttpResponseRedirect(reverse('tickets:detail', kwargs=({'ticket_id':new_ticket.id})))
            else:
                if request.is_ajax():
                    return format_ajax_response(False, "Form data failed validation.", errors=dict((k, [unicode(x) for x in v]) for k,v in new_post_form.errors.items()))
                else:
                    form_errors = new_post_form.errors
        else:
            if request.is_ajax():
                return format_ajax_response(False, "Form data failed validation.", errors=dict((k, [unicode(x) for x in v]) for k,v in new_ticket_form.errors.items()))
            else:
                form_errors = new_ticket_form.errors                

    response = {'fellow_contacts': get_companies_active_contacts(request.user.company_id, request.user.id), 'service_id': int(service_id)}
    try:
        response.update({"form_errors": form_errors})
    except:
        pass

    return render(request, 'tickets/new.html', response)    


@validated_staff
@validated_request(PostIDForm)
def toggle_visibility(request):
    """Create Post

        Creates a Post reply under specified Ticket.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_request
            request.method must be POST
            request.is_ajax() must be False
            request.user.is_authenticated() must be True  
    Paremeters
        request: HttpRequest
            ticket_id: int ticket id 
            attachment: file attachment
            contents: str reply contents 
    Returns
        HttpResponseRedirect
    """ 
    try:
        post = Post.objects.get(pk=request.form.cleaned_data['post_id'])

        if post.visible is True:
            post.visible = False
            message = "Post made private."
        else:
            post.visible = True
            message = "Post made public."            
        post.save()

        Post.objects.create(ticket=post.ticket, author=request.user, contents=message)
        return format_ajax_response(True, "Post visibility toggled successfully.")  
    except Exception as ex:
        logger.error("Failed to toggle_visibility: %s" % ex)
        return format_ajax_response(False, "There was an error toggling the post's visibility.")


@validated_staff
@validated_request(PostIDForm)
def toggle_flag(request):
    """Create Post

        Creates a Post reply under specified Ticket.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_request
            request.method must be POST
            request.is_ajax() must be False
            request.user.is_authenticated() must be True  
    Paremeters
        request: HttpRequest
            ticket_id: int ticket id 
            attachment: file attachment
            contents: str reply contents 
    Returns
        HttpResponseRedirect
    """ 
    try:
        post = Post.objects.get(pk=request.form.cleaned_data['post_id'])

        if post.flagged is True:
            post.flagged = False
            message = "Post unflagged."
        else:
            post.flagged = True
            message = "Post flagged."            
        post.save()

        Post.objects.create(ticket=post.ticket, author=request.user, contents=message)
        return format_ajax_response(True, "Post's flag toggled successfully.")  
    except Exception as ex:
        logger.error("Failed to toggle_flag: %s" % ex)
        return format_ajax_response(False, "There was an error toggling post's flag.")