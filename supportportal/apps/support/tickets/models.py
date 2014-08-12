from django.db import models
from django.conf import settings
from datetime import datetime
from apps.companies.models import Service
from apps.contacts.models import Contact
from django.template import defaultfilters
from django.utils.timesince import timesince

class Ticket(models.Model):
    # Ticket Status choices
    STATUS_CHOICES = (
        ('Closed', 'Closed'),
        ('Open', 'Open'),
    )

    # Ticket Priority choices
    PRIORITY_CHOICES = (
        ('Low', 'Low'),
        ('Normal', 'Normal'),
        ('Urgent', 'Urgent'),
    )

    contacts = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="ticket_contacts", blank=True, null=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="ticket_author", blank=False, null=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="ticket_owner")
    priority = models.CharField(max_length=6, choices=PRIORITY_CHOICES, default='Normal')
    status = models.CharField(max_length=6, choices=STATUS_CHOICES, default='Open')
    flagged = models.BooleanField(default=True)
    description = models.CharField(max_length=128, null=False, blank=False)
    date = models.DateTimeField(default=datetime.now)
    service = models.ForeignKey(Service)

    def __unicode__(self):
        return self.description  

    def dump_to_dict(self, full=False, admin=False):
        if full:
            posts = []
            for post in Post.objects.filter(ticket=self.id):
                if admin is True or post.visible is True:
                    posts.append(post.dump_to_dict())   
                         
            response = {
                        'author': self.author.get_full_name(),
                        "description": self.description,
                        'status': self.status,
                        'priority': self.priority,
                        'cc_list': get_ticket_contacts_list(self.id, self.author.company_id),
                        'posts': posts
                    }

            if self.service:
                response.update({'service': self.service.name})
            else:
                response.update({'service': "Other"})  
        else:
            response = {
                "id": self.pk, 
                "description": self.description, 
                "author": self.author.get_full_name(), 
                "date": defaultfilters.date(self.date, "SHORT_DATETIME_FORMAT"), 
                "priority": self.priority,
                "flagged": self.flagged,
                "owner": self.owner.get_full_name(),
                "lastupdate": timesince(self.date)
            }                  

        return response        

class Post(models.Model):
    ticket = models.ForeignKey(Ticket, blank=False)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="post_author", blank=False)
    contents = models.TextField(blank=True)
    date = models.DateTimeField(auto_now_add=True, blank=True)
    flagged = models.BooleanField(default=False)
    visible = models.BooleanField(default=True)
    attachment = models.FileField(upload_to="attachments/%Y/%m/%d",blank=True)

    def __unicode__(self):
        return self.contents

    def dump_to_dict(self):
        attachment = 0
        if self.attachment:
            attachment = {"url": self.attachment.url, "size": self.attachment.size, "name": self.attachment.name}

        response = {
            "id": self.pk, 
            "author": self.author.get_full_name(), 
            "contents": self.contents, 
            "date": defaultfilters.date(self.date, "SHORT_DATETIME_FORMAT"), 
            "attachment": attachment,
            'flagged': self.flagged,
            'visible': self.visible
        }       

        return response   


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
