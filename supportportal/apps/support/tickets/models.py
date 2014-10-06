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

    SATISFACTION_VERY_DISSATISFIED = 1
    SATISFACTION_DISSATISFIED = 2
    SATISFACTION_NEUTRAL = 3
    SATISFACTION_SATISFIED = 4
    SATISFACTION_VERY_SATISFIED = 5

    SATISFACTION_CHOICES = (
        (SATISFACTION_VERY_DISSATISFIED, "Very Dissatisfied"),
        (SATISFACTION_DISSATISFIED, "Dissatisfied"),
        (SATISFACTION_NEUTRAL, "Neutral"),
        (SATISFACTION_SATISFIED, "Satisfied"),
        (SATISFACTION_VERY_SATISFIED, "Very Satisfied")
    )

    DIFFICULTY_SIMPLE = 1
    DIFFICULTY_EASY = 2
    DIFFICULTY_MEDIUM = 3
    DIFFICULTY_HARD = 4
    DIFFICULTY_ADVANCED = 5

    DIFFICULTY_CHOICES = (
        (DIFFICULTY_SIMPLE, "Simple"),
        (DIFFICULTY_EASY, "Easy"),
        (DIFFICULTY_MEDIUM, "Medium"),
        (DIFFICULTY_HARD, "Hard"),
        (DIFFICULTY_ADVANCED, "Advanced")
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
    staff_summary = models.TextField(blank=True, null=True)
    satisfaction_rating = models.IntegerField(choices=SATISFACTION_CHOICES, blank=True, default=0)
    difficulty_rating = models.IntegerField(choices=DIFFICULTY_CHOICES, blank=True, default=0)


    def __unicode__(self):
        return "%s" % self.description

    def dump_to_dict(self, full=False, admin=False):
        if self.priority == 1:
            priority = "Low"
        elif self.priority == 2:
            priority = "Normal"
        else:
            priority = "Urgent"

        response = {
            'id': self.pk,
            'description': self.description,
            'author': self.author.get_full_name(),
            'owner': self.owner.get_full_name(),
            'flagged': self.flagged,
            'queue': self.queue.title,
            'status': ("Closed", "Open")[bool(self.status)],
            'priority': priority,
            'date': defaultfilters.date(self.date, "SHORT_DATETIME_FORMAT"),
            'due_date': defaultfilters.date(self.due_date, "SHORT_DATETIME_FORMAT"),
            'lastupdate': timesince(self.date),
        }

        if full:
            if admin:
                response.update({
                    'staff_summary': (0, self.staff_summary)[bool(self.staff_summary)],
                    'difficulty_rating': ("Not Rated", self.difficulty_rating)[bool(self.difficulty_rating)]
                })

            response.update({
                'satisfaction_rating': (0, self.satisfaction_rating)[bool(self.satisfaction_rating)],
                'cc_list': get_ticket_contacts_list(self.id, self.author.company_id),
                'service': ("Other", self.service.name)[bool(self.service) and hasattr(self.service, 'name')]
            })

        return response


class Post(models.Model):
    def validate_file_extension(filename):
        import os
        ext = os.path.splitext(filename.name)[1]
        valid_extensions = ['.pdf','.jpg', '.png', '.txt']
        if not ext in valid_extensions:
            raise ValidationError('File not supported!')

    ticket = models.ForeignKey(Ticket, blank=False, null=False)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, blank=False, null=False)
    contents = models.TextField(blank=False, null=False)
    date = models.DateTimeField(auto_now_add=True, blank=True)
    visible = models.BooleanField(default=True, blank=True)
    attachment = models.FileField(upload_to="attachments/%Y/%m/%d", validators=[validate_file_extension], blank=True, null=True)

    def __unicode__(self):
        return "%s" % self.contents

    def dump_to_dict(self):
        attachment = 0
        if self.attachment and hasattr(self.attachment, 'name'):
            attachment = {"url": self.attachment.url, "size": self.attachment.size, "name": self.attachment.name}

        return {
            "id": self.pk,
            "author": self.author.get_full_name(),
            "contents": self.contents,
            "date": defaultfilters.date(self.date, "SHORT_DATETIME_FORMAT"),
            "attachment": attachment,
            'visible': self.visible
        }


class Macro(models.Model):
    name = models.CharField(max_length=128, blank=False, null=False)
    body = models.TextField(blank=False, null=False)
    date = models.DateTimeField(default=datetime.now, blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, blank=False, null=False)

    def __unicode__(self):
        return "%s" % self.name

    def dump_to_dict(self):
        return {
            'id': self.pk,
            'name': self.name,
            'body': self.body
        }






import logging
logger = logging.getLogger(__name__)

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

        return {
            "user": {"open": len(num_open_user), "total": len(num_total_user)},
            "company": {"open": len(num_open_company), "total": len(num_total_company)}
        }
    except Exception as ex:
        logger.error("Failed to get_tickets_summary: %s" % ex)
        return False


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

        return {
            "current_contacts": current_list,
            "potential_contacts": potential_list
        }
    except Exception as ex:
        logger.error("Failed to get_ticket_contacts_list: %s" % ex)
        return False


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

        for contact in Contact.objects.filter(pk__in=contacts):
            logger.error(contact)
            if ticket.author.company_id == contact.company_id:
                ticket.contacts.add(contact)

        return True
    except Exception as ex:
        logger.error("Failed to set_ticket_contacts_list: %s" % ex)
        return False


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
    except Exception as ex:
        logger.error("Failed to get_companies_active_contacts: %s" % ex)
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