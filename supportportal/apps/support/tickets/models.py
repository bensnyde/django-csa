from django.db import models
from django.conf import settings
from datetime import datetime
from apps.companies.models import Service
from apps.contacts.models import Contact
from django.template import defaultfilters
from django.utils.timesince import timesince


class Queue(models.Model):
    EMAIL_TYPE_CHOICES = (
        ('pop3', 'POP3'),
        ('imap', 'IMAP4')
    )

    title = models.CharField(max_length=128, null=False, blank=False, unique=True)
    allow_email_submission = models.BooleanField(default=False, blank=True)
    email_address = models.EmailField(blank=True, null=True)
    email_type = models.CharField(max_length=5, blank=True, null=True, choices=EMAIL_TYPE_CHOICES)
    email_host = models.CharField(max_length=128, blank=True, null=True)
    email_port = models.IntegerField(blank=True, null=True)
    email_ssl = models.BooleanField(blank=True, default=False)
    email_username = models.CharField(max_length=128, blank=True, null=True)
    email_password = models.CharField(max_length=256, blank=True, null=True)
    email_fetch_interval = models.IntegerField(default=5, blank=True, null=True)
    email_last_checked = models.DateTimeField(blank=True, null=True, editable=False)

    def __unicode__(self):
        return "%s" % self.title

    def dump_to_dict(self, full=False):
        response = {
            'id': self.pk,
            'title': self.title,
            'allow_email_submission': self.allow_email_submission,
            'email_address': (self.email_address, "")[self.email_address is None]
        }

        if full:
            response.update({
                'email_address': self.email_address,
                'email_type': self.email_type,
                'email_host': self.email_host,
                'email_port': self.email_port,
                'email_ssl': self.email_ssl,
                'email_username': self.email_username,
                'email_fetch_interval': self.email_fetch_interval,
                'email_last_checked': defaultfilters.date(self.email_last_checked, "SHORT_DATETIME_FORMAT")
            })

        return response


class Ticket(models.Model):
    STATUS_OPEN = 1
    STATUS_CLOSED = 0

    STATUS_CHOICES = (
        (STATUS_CLOSED, 'Closed'),
        (STATUS_OPEN, 'Open'),
    )

    PRIORITY_LOW = 1
    PRIORITY_NORMAL = 2
    PRIORITY_URGENT = 3

    PRIORITY_CHOICES = (
        (PRIORITY_LOW, 'Low'),
        (PRIORITY_NORMAL, 'Normal'),
        (PRIORITY_URGENT, 'Urgent'),
    )

    contacts = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, null=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="author", blank=False, null=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="owner", blank=True, null=True)
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=PRIORITY_NORMAL, blank=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=STATUS_OPEN, blank=True)
    flagged = models.BooleanField(default=True, blank=True)
    description = models.CharField(max_length=256, null=False, blank=False)
    date = models.DateTimeField(default=datetime.now, blank=True)
    service = models.ForeignKey(Service, blank=True, null=True)
    queue = models.ForeignKey(Queue, null=False, blank=False)
    due_date = models.DateTimeField(default=datetime.now, blank=True)

    def __unicode__(self):
        return "%s" % self.description

    def dump_to_dict(self, full=False, admin=False):
        response = {
            'id': self.pk,
            'description': self.description,
            'author': self.author.get_full_name(),
            'owner': self.owner.get_full_name(),
            'flagged': self.flagged,
            'queue': self.queue.title,
            'status': self.status,
            'priority': self.priority,
            'date': defaultfilters.date(self.date, "SHORT_DATETIME_FORMAT"),
            'due_date': defaultfilters.date(self.due_date, "SHORT_DATETIME_FORMAT"),
            'lastupdate': timesince(self.date),
        }

        if full:
            posts = []
            for post in Post.objects.filter(ticket=self.id):
                if admin is True or post.visible is True:
                    posts.append(post.dump_to_dict())

            response.update({
                'cc_list': get_ticket_contacts_list(self.id, self.author.company_id),
                'posts': posts,
                'service': ("Other", self.service.name)[self.service]
            })

        return response


class Post(models.Model):
    ticket = models.ForeignKey(Ticket, blank=False, null=False)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, blank=False, null=False)
    contents = models.TextField(blank=False, null=False)
    date = models.DateTimeField(auto_now_add=True, blank=True)
    flagged = models.BooleanField(default=False, blank=True)
    visible = models.BooleanField(default=True, blank=True)
    attachment = models.FileField(upload_to="attachments/%Y/%m/%d", blank=True, null=True)

    def __unicode__(self):
        return "%s" % self.contents

    def dump_to_dict(self):
        return {
            "id": self.pk,
            "author": self.author.get_full_name(),
            "contents": self.contents,
            "date": defaultfilters.date(self.date, "SHORT_DATETIME_FORMAT"),
            "attachment": (0, {"url": self.attachment.url, "size": self.attachment.size, "name": self.attachment.name})[self.attachment],
            'flagged': self.flagged,
            'visible': self.visible
        }


class Post_Macro(models.Model):
    queues = models.ManyToManyField(Queue, blank=True, null=True)
    name = models.CharField(max_length=128, blank=False, null=False)
    body = models.TextField(blank=False, null=False)

    def __unicode__(self):
        return "%s" % self.name


def get_tickets_summary(user_id, company_id):
    """Get Ticket summary

        Retrieves tickets summary of open and total tickets for specified user and specified company.

    Parameters
        user_id: int user id
        company_id: int company id
    Returns
        result:
            user:
                open: int number of open tickets for specified user
                total: int number of total tickets for specified user
            company:
                open: int number of open tickets for specified company
                total: int number of total tickets for specified company
    """
    try:
        num_total_user = Ticket.objects.filter(owner_id=user_id)
        num_open_user = num_total_user.filter(status="Open")
        num_total_company = Ticket.objects.filter(owner_id__company_id=company_id)
        num_open_company = num_total_company.filter(status="Open")

        result = {
            "user": {"open": len(num_open_user), "total": len(num_total_user)},
            "company": {"open": len(num_open_company), "total": len(num_total_company)}
        }
    except:
        result = False

    return result


def get_ticket_contacts_list(ticket_id, company_id):
    """Get current and potential contacts for a Ticket

        Retrieves dictionary listing of a specified Ticket's current and potential Contacts

    Parameters
        ticket_id: int ticket id
        company_id: int company id
    Returns
        result:
            current_contacts: queryset of Contact objects currently assigned to specified Ticket object
            potential_contacts: queryset of Contact objects able to still be assigned to specified Ticket object
    """
    try:
        ticket = Ticket.objects.get(pk=ticket_id, author__company_id=company_id)

        current_list = []
        for contact in ticket.contacts.all():
            current_list.append({"id": contact.pk, "name": contact.get_full_name(), "email": contact.email})

        potential_list = []
        for contact in Contact.objects.exclude(pk=ticket.author.id).filter(is_active=1).exclude(id__in=ticket.contacts.all()):
            potential_list.append({"id": contact.pk, "name": contact.get_full_name(), "email": contact.email})

        result = {
            "current_contacts": current_list,
            "potential_contacts": potential_list
        }
    except:
        result = False

    return result

def set_ticket_contacts_list(ticket_id, contacts):
    """Get current and potential contacts for a Ticket

        Retrieves dictionary listing of a specified Ticket's current and potential Contacts

    Parameters
        ticket_id: int ticket id
        contacts: list of int contact id's
    Returns
        result:
            current_contacts: queryset of Contact objects currently assigned to specified Ticket object
            potential_contacts: queryset of Contact objects able to still be assigned to specified Ticket object
    """
    try:
        ticket = Ticket.objects.get(pk=ticket_id)
        ticket.contacts.clear()

        if all(x.isdigit() for x in contacts):
            for contact in Contact.objects.filter(pk__in=contacts):
                if ticket.author.company_id == contact.company_id:
                    ticket.contacts.add(contact)

        result = True
    except:
        result = False

    return result

def get_companies_active_contacts(company_id, exclude_contact_id=None):
    """Get list of Company contacts

        Retrieves queryset of Contacts for a specified Company.

    Parameters
        company_id: int company id
        *exclude_contact_id: int contact id to exclude from queryset
    Returns
    	contacts: queryset of Contact objects
    """
    try:
        return Contact.objects.filter(company=company_id).exclude(pk=exclude_contact_id)
    except:
        return False

def search(query_str):
    """Search Tickets for keyword

        Retrieves listing of all Ticket objects whose description contains specified query string.

    Parameters
        query_str: str keyword to search ticket descriptions's for
    Returns
        response:
            title: str ticket description
            link: str uri to ticket id
            preview: str contents of matched post
    """
    from django.core.urlresolvers import reverse

    response = []
    ticket_ids = []
    tickets = Ticket.objects.filter(description__icontains=query_str)
    for ticket in tickets:
        ticket_ids.append(ticket.id)
        response.append({"title": ticket.description, "link": reverse('tickets:detail', kwargs={"ticket_id": ticket.id})})
    posts = Post.objects.filter(contents__icontains=query_str).exclude(id__in=ticket_ids)
    for post in posts:
        if not post.ticket.id in ticket_ids:
            ticket_ids.append(post.ticket.id)
            response.append({"title": post.ticket.description, "link": reverse('tickets:detail', kwargs={"ticket_id": post.ticket.id}), "preview": post.contents[:128]})

    return response # Change me!
