from django.forms.models import model_to_dict
from apps.companies.models import Company
from django.db import models
from django.db.models import Q
from datetime import datetime
from django.utils.timesince import timesince
from django.core.validators import RegexValidator, validate_email
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)


class ContactManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password, company, title=None, personal_phone=None, office_phone=None, fax=None, role=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            company=company,
            title=title,
            personal_phone=personal_phone,
            office_phone=office_phone,
            fax=fax,
            role=role
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, password, company):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(email, first_name, last_name, password, company)
        user.is_admin = True
        user.save(using=self._db)
        return user


class Contact(AbstractBaseUser):
    ROLE_CHOICES = (
        ('Consultant', 'Consultant'),
        ('Billing', 'Billing'),
        ('Tech', 'Tech'),
        ('Admin', 'Admin')
    )

    email = models.EmailField(verbose_name="Email Address", max_length=255, unique=True, db_index=True, validators=[validate_email])
    first_name = models.CharField(verbose_name="First Name", max_length=64, validators=[RegexValidator(regex="^[a-zA-Z0-9 \',.-]*$", message='Only alphanumeric characters, spaces, commas, periods, hyphens and apostraphes are allowed.'),])
    last_name = models.CharField(verbose_name="Last Name", max_length=64, validators=[RegexValidator(regex="^[a-zA-Z0-9 \',.-]*$", message='Only alphanumeric characters, spaces, commas, periods, hyphens and apostraphes are allowed.'),])
    title = models.CharField(max_length=64, blank=True, null=True, validators=[RegexValidator(regex="^[a-zA-Z0-9 \',.-]*$", message='Only alphanumeric characters, spaces, commas, periods, hyphens and apostraphes are allowed.'),])
    personal_phone = models.CharField(verbose_name="Personal Phone Number", max_length=64, blank=True, null=True, validators=[RegexValidator(regex='^[a-zA-Z0-9 ()-]*$', message='Only alphanumeric characters, spaces, paraentheses, and hyphens are allowed.'),])
    office_phone = models.CharField(verbose_name="Office Phone Number", max_length=64, blank=True, null=True, validators=[RegexValidator(regex='^[a-zA-Z0-9 ()-]*$', message='Only alphanumeric characters, spaces, paraentheses, and hyphens are allowed.'),])
    fax = models.CharField(verbose_name="Fax Number", max_length=64, blank=True, null=True, validators=[RegexValidator(regex='^[a-zA-Z0-9 ()-]*$', message='Only alphanumeric characters, spaces, paraentheses, and hyphens are allowed.'),])
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    company = models.ForeignKey(Company, blank=False, null=False)
    role = models.CharField(max_length=32, choices=ROLE_CHOICES, default="Tech")
    created = models.DateTimeField(default=datetime.now)

    objects = ContactManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'company']

    def dump_to_dict(self, full=False):
        response = {
            'id': self.pk,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'role': self.role,            
        }
        
        if full:
            response.update({
                'title': self.title,
                'personal_phone': self.personal_phone,
                'office_phone': self.office_phone,
                'fax': self.fax,
                'is_active': self.is_active,
                'is_admin': self.is_admin,
                'company': self.company.name,
                'created': str(self.created)
            })
        
        return response

    def get_services(self):
        response = []
        for service in self.company.services.all():
            response.append({
                "id": service.id,
                "name": service.name, 
                "uri": service.coupler.uri, 
                "vars": service.vars, 
            })

        return response

    def get_service_vars(self, coupler_uri, service_id):
        try:
            import json
            service = self.company.services.get(pk=service_id, coupler__uri=coupler_uri)
            return json.loads(service.vars)
        except:
            return False

    def get_full_name(self):
        # The user is identified by their email address
        return self.first_name + ' ' + self.last_name

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def timesince_created(self, now=None):
            return timesince(self.created, now)

    # On Python 3: def __str__(self):
    def __unicode__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

# move me
def search(query, company_id):
    return Contact.objects.filter(Q(company_id=company_id) & (Q(email__icontains=query) | Q(first_name__istartswith=query) | Q(last_name__istartswith=query)))