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
from .models import Queue, Ticket, Post, Macro, get_ticket_contacts_list, set_ticket_contacts_list, get_tickets_summary, get_companies_active_contacts
from .forms import QueueForm, TicketForm, TicketContactsForm, TicketSatisfactionForm, AdminSetTicketForm, AdminCreateTicketForm, PostForm, PostAttachmentForm, PostRatingForm, PostVisibilityForm, MacroForm


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
    ticket = get_object_or_404(Ticket, pk=ticket_id)

    response = {'ticket_id': ticket_id}
    if request.user.is_staff:
        response.update({
            'macroform': MacroForm(),
            'ticketform': AdminSetTicketForm(instance=ticket),
        })

    return render(request, 'tickets/detail.html', response)


@validated_staff
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
        HttpResponse (tickets/index.html)
            ticket_id: int ticket id
    """
    response = {
        'queueform': QueueForm(),
    }

    return render(request, 'tickets/admin.html', response)


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
        if not request.user.is_staff:
            queryset = Ticket.objects.filter(owner_id__company_id=request.user.company_id).filter(status=1).order_by('-priority')
        else:
            if "flagged" in request.POST and request.POST["flagged"] == 1:
                queryset =  Ticket.objects.filter(status=1).filter(flagged=True).order_by("-priority")
            else:
                queryset = Ticket.objects.filter(status=1).order_by("-priority")

        tickets = []
        for ticket in queryset:
            tickets.append(ticket.dump_to_dict())

        response = {
            "tickets": tickets,
        }

        return format_ajax_response(True, "Tickets listing retrieved successfully.", response)
    except Exception as ex:
        logger.error("Failed to get_tickets: %s" % ex)
        return format_ajax_response(False, "There was an error retrieving the tickets listing.")


@validated_request(None)
def get_posts(request, ticket_id):
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
        ticket_id: int ticket id
    Returns
        HttpResponse (JSON)
            success: int status result of API call
            message: str response message from API call
            *data:
                posts:
    """
    try:
        if request.user.is_staff:
            queryset = Post.objects.filter(ticket_id=ticket_id)
        else:
            queryset = Posts.objects.filter(ticket_id=ticket_id, visibility=True)

        posts = []
        for post in queryset:
            posts.append(post.dump_to_dict())

        response = {
            "posts": posts,
        }

        return format_ajax_response(True, "Posts listing retrieved successfully.", response)
    except Exception as ex:
        logger.error("Failed to get_posts: %s" % ex)
        return format_ajax_response(False, "There was an error retrieving the posts listing.")


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

        logger.error(request.user.is_staff)

        if not request.user.is_staff and ticket.author.company_id != request.user.company_id:
            raise Exception("Requesting user does not have permission to access specified ticket.")

        response = {
            "ticket": ticket.dump_to_dict(full=True, admin=request.user.is_staff),
        }

        return format_ajax_response(True, "Ticket details retrieved successfully.", response)
    except Exception as ex:
        logger.error("Failed to get_ticket: %s" % ex)
        return format_ajax_response(False, "There was an error retrieving ticket details.")


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
        response = {
            "summary": get_tickets_summary(request.user.id, request.user.company_id),
        }

        return format_ajax_response(True, "Tickets summary retrieved successfully.", response)
    except Exception as ex:
        logger.error("Failed to get_summary: %s" % ex)
        return format_ajax_response(False, "There was an error retrieving the tickets summary.")


@validated_request(TicketContactsForm)
def set_contacts(request, ticket_id):
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
            contacts: int[] contacts ids
        ticket_id: int ticket id
    Returns
        HttpResponse (JSON)
            success: int status result of call
            message: str status result of call
    """
    try:
        ticket = Ticket.objects.get(pk=ticket_id)
        if not request.user.is_staff and ticket.author.company_id != request.user.company_id:
            raise Exception("Forbidden: requesting user doesn't have permission to specified Company's resources.")

        contacts = request.POST.getlist('contacts')

        if set_ticket_contacts_list(ticket.id, contacts):
            Post.objects.create(
                ticket=ticket,
                author=request.user,
                contents="Modified ticket's cc listing."
            )

            ActionLogger().log(request.user, "modified", "Contacts %s" % contacts, "Ticket %s" % ticket.id)
            return format_ajax_response(True, "Tickets's contacts set successfully.")
        else:
            raise Exception("set_ticket_contacts_list(%s, %s) returned False." % (ticket.id, contacts))
    except Exception as ex:
        logger.error("Failed to set_contacts: %s" % ex)
        return format_ajax_response(False, "There wasn an error setting thet ticket's contacts.")


@validated_request(PostForm, 'POST', True, False)
def create_post(request, ticket_id):
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
            attachment: file attachment
            contents: str reply contents
        ticket_id: int ticket id
    Returns
        HttpResponseRedirect
    """
    ticket = get_object_or_404(Ticket, pk=ticket_id)

    try:
        if not request.user.is_staff and ticket.author.company_id != request.user.company_id:
            raise Exception("Forbidden: requesting user doesn't have permission to specified Company's resources.")

        post_form = PostForm(request.POST, request.FILES)
        if post_form.is_valid():
            # Create new post object under specified ticket object
            post = post_form.save(commit=False)
            post.author_id = request.user.id
            post.ticket = ticket
            post.save()
            post_form.save_m2m()

            ActionLogger().log(request.user, "created", "Post %s" % post.id, "Ticket %s" % ticket.id)

            if request.is_ajax():
                return format_ajax_response(True, "Ticket post created successfully.")
            else:
                return HttpResponseRedirect(reverse('tickets:detail', kwargs=({'ticket_id':ticket_id})))
        else:
            raise Exception("Form data failed validation.")

    except Exception as ex:
        logger.error("Failed to create_post: %s" % ex)

    if request.is_ajax():
        return format_ajax_response(False, "There was an error creating the ticket post.")
    else:
        return HttpResponseRedirect(reverse('tickets:detail', kwargs=({'ticket_id':ticket_id})))


@validated_staff
@validated_request(AdminSetTicketForm)
def set_ticket(request, ticket_id):
    """Create Post

        Creates a Post reply under specified Ticket.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_request
            request.POST must validate against AdminSetTicketForm
            request.method must be POST
            request.is_ajax() must be False
            request.user.is_authenticated() must be True
    Paremeters
        request: HttpRequest
        ticket_id: int ticket id
    Returns
        HttpResponse (JSON)
            success: int status response of request
            message: str status response of request
    """
    try:
        ticket = Ticket.objects.get(pk=ticket_id)
        ticket.contacts = request.form.cleaned_data['contacts']
        ticket.description = request.form.cleaned_data['description']
        ticket.queue = request.form.cleaned_data['queue']
        ticket.priority = request.form.cleaned_data['priority']
        ticket.service = request.form.cleaned_data['service']
        ticket.author = request.form.cleaned_data['author']
        ticket.due_date = request.form.cleaned_data['due_date']
        ticket.staff_summary = request.form.cleaned_data['staff_summary']
        ticket.status = request.form.cleaned_data['status']
        if request.form.cleaned_data['difficulty_rating']:
            ticket.difficulty_rating = request.form.cleaned_data['difficulty_rating']
        ticket.save()

        Post.objects.create(
            ticket=ticket,
            author=request.user,
            visible=False,
            contents="Modified ticket properties."
        )

        ActionLogger().log(request.user, "modified", "Ticket %s" % ticket.id)
        return format_ajax_response(True, "Ticket details updated successfully.")
    except Exception as ex:
        logger.error("Failed to set_ticket: %s" % ex)
        return format_ajax_response(False, "There wasn a error setting the ticket details.")


@validated_request(TicketSatisfactionForm)
def set_satisfaction_rating(request, ticket_id):
    """Set Satisfaction Rating

        Sets Ticket's customer satisfaction_rating.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_request
            request.POST must validate against TicketSatisfactionForm
            request.method must be POST
            request.is_ajax() must be False
            request.user.is_authenticated() must be True
    Paremeters
        request: HttpRequest
            satisfaction_rating: int customer satisfaction rating
        ticket_id: int ticket id
    Returns
        HttpResponse (JSON)
            success: int status response of request
            message: str status response of request
    """
    try:
        ticket = Ticket.objects.get(pk=ticket_id)

        if ticket.owner.company_id != request.user.company_id:
            raise Exception("Forbidden: requesting user doesn't have permission to specified Company's resources.")

        if request.user.is_staff:
            raise Exception("Forbidden: staff cannot modify ticket's customer satisfaction rating.")

        ticket.satisfaction_rating = request.form.cleaned_data['satisfaction_rating']
        ticket.save()

        Post.objects.create(
            ticket=ticket,
            author=request.user,
            contents="Rated satisfaction level at %s" % request.form.cleaned_data['satisfaction_rating']
        )

        ActionLogger().log(request.user, "modified", "Ticket %s" % ticket.id)
        return format_ajax_response(True, "Ticket satisfaction rating updated successfully.")
    except Exception as ex:
        logger.error("Failed to set_satisfaction_rating: %s" % ex)
        return format_ajax_response(False, "There wasn a error setting the ticket's satisfaction rating.")


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
        *service_id: int service id
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
                new_ticket = new_ticket_form.save(commit=False)

                if request.user.is_staff:
                    new_ticket.author_id = int(request.POST['author'])
                else:
                    new_ticket.author_id = request.user.id

                try:
                    if "service" in request.POST and int(request.POST['service']) is not 0:
                        new_ticket.service = request.user.company.services.get(pk=int(request.POST["service"]))
                except:
                    pass

                new_ticket.save()
                new_ticket_form.save_m2m()

                set_ticket_contacts_list(new_ticket.id, request.POST.getlist('contacts'))

                # Create Post
                new_post = new_post_form.save(commit=False)
                new_post.ticket = new_ticket

                if request.user.is_staff:
                    new_post.author_id = int(request.POST['author'])
                else:
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

    if request.user.is_staff:
        ticketform = AdminCreateTicketForm()
    else:
        ticketform = TicketForm()

    response = {'ticketform': ticketform, 'postform': PostForm(), 'fellow_contacts': get_companies_active_contacts(request.user.company_id, request.user.id), 'service_id': int(service_id)}
    try:
        response.update({"form_errors": form_errors})
    except:
        pass

    return render(request, 'tickets/new.html', response)


@validated_staff
@validated_request(PostVisibilityForm)
def toggle_visibility(request, post_id):
    """Create Post

        Creates a Post reply under specified Ticket.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_request
            request.POST must validate against PostVisibilityForm
            request.method must be POST
            request.is_ajax() must be False
            request.user.is_authenticated() must be True
    Paremeters
        request: HttpRequest
            visible: bool post visibility
        post_id: int post id
    Returns
        HttpResponse (JSON)
            success: int status response of request
            message: str status response of request
    """
    try:
        post = Post.objects.get(pk=post_id)
        post.visible = not post.visible
        post.save()

        return format_ajax_response(True, "Post visibility toggled successfully.")
    except Exception as ex:
        logger.error("Failed to toggle_visibility: %s" % ex)
        return format_ajax_response(False, "There was an error toggling the post's visibility.")


@validated_staff
@validated_request(PostRatingForm)
def set_post_rating(request, post_id):
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
            visible: bool post visibility
        post_id: int post id
    Returns
        HttpResponse (JSON)
            success: int status response of request
            message: str status response of request
    """
    try:
        post = Post.objects.get(pk=post_id)
        post.rating = request.form.cleaned_data['rating']
        post.save()

        return format_ajax_response(True, "Post rating set successfully.")
    except Exception as ex:
        logger.error("Failed to set_post_rating: %s" % ex)
        return format_ajax_response(False, "There was an error setting the post's rating.")


@validated_staff
@validated_request(None)
def get_queue(request):
    try:
        if 'queue_id' in request.POST and int(request.POST['queue_id']):
            # Detail
            queue = Queue.objects.get(pk=int(request.POST['queue_id']))
            response = {'queue': queue.dump_to_dict(full=True)}
        else:
            # Index
            queues = []
            for queue in Queue.objects.all():
                queues.append(queue.dump_to_dict())
            response = {'queues': queues}

        return format_ajax_response(True, "Queue index retrieved successfully.", response)
    except Exception as ex:
        logger.error("Failed to get_queues: %s" % ex)
        return format_ajax_response(False, "There wasn a error retrieving queue index.")

@validated_staff
@validated_request(None)
def delete_queue(request):
    try:
        Queue.objects.get(pk=int(request.POST['queue_id'])).delete()

        return format_ajax_response(True, "Queue deleted successfully.")
    except Exception as ex:
        logger.error("Failed to delete_queue: %s" % ex)
        return format_ajax_response(False, "There wasn a error deleting the specified queue.")

@validated_staff
@validated_request(None)
def set_queue(request):
    try:
        if 'queue_id' in request.POST and request.POST['queue_id']:
            queue = Queue.objects.get(pk=request.POST['queue_id'])
            form = QueueForm(request.POST, instance=queue)
        else:
            form = QueueForm(request.POST)

        if form.is_valid():
            queue = form.save()

            return format_ajax_response(True, "Queue updated successfully.")
        else:
            return format_ajax_response(False, "Form data failed validation.", errors=dict((k, [unicode(x) for x in v]) for k,v in form.errors.items()))

    except Exception as ex:
        logger.error("Failed to set_queue: %s" % ex)
        return format_ajax_response(False, "There wasn a error setting the specified queue.")


@validated_staff
@validated_request(None)
def get_macros(request):
    try:
        macros = []
        for macro in Macro.objects.all():
            macros.append(macro.dump_to_dict())

        response = {
            'macros': macros,
        }

        return format_ajax_response(True, "Macros index retrieved successfully.", response)
    except Exception as ex:
        logger.error("Failed to get_macros: %s" % ex)
        return format_ajax_response(False, "There was an error retrieving macros index.")

@validated_staff
@validated_request(None)
def delete_macro(request):
    try:
        macros = request.POST.getlist('macro_id')
        Macro.objects.filter(pk__in=macros).delete()
        ActionLogger().log(request.user, "deleted", "Macros %s" % macros)
        return format_ajax_response(True, "Macros deleted successfully.")
    except Exception as ex:
        logger.error("Failed to delete_macro: %s" % ex)
        return format_ajax_response(False, "There was an error deleting ticket post macros.")

@validated_staff
@validated_request(MacroForm)
def set_macro(request):
    try:
        if "macro_id" in request.POST and int(request.POST["macro_id"]) is not 0:
            # Update existing
            macro = Macro.objects.get(pk=request.POST['macro_id'])
            macro.name = request.form.cleaned_data["name"]
            macro.body = request.form.cleaned_data["body"]
            macro.save()

            ActionLogger().log(request.user, "modified", "Macro %s" % macro)
            return format_ajax_response(True, "Macro modified successfully.")
        else:
            # Create new
            macro = Macro.objects.create(name=request.form.cleaned_data["name"], body=request.form.cleaned_data["body"], author=request.user)

            ActionLogger().log(request.user, "created", "Macro %s" % macro)
            return format_ajax_response(True, "Macro created successfully.")
    except Exception as ex:
        logger.error("Failed to set_macro: %s" % ex)
        return format_ajax_response(False, "There was an error setting the macro.")