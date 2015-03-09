from django.conf import settings
from django.contrib.auth.models import Group, BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.core.validators import validate_email
from django.db import models
from django.db.models import Q
from django.forms.models import model_to_dict
from simple_history.models import HistoricalRecords
from appsdir.companies.models import Company


class ContactManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, password, company=None, title=None, personal_phone=None, office_phone=None, fax=None):
        """
        Creates and saves a User with the given email, date of birth and password.
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
        )

        user.set_password(password)
        user.save(using=self._db)
        return user


class Contact(AbstractBaseUser, PermissionsMixin):
    company = models.ForeignKey(Company, null=True, blank=True)
    email = models.EmailField(verbose_name="Email Address", max_length=64, unique=True, db_index=True, validators=[validate_email])
    first_name = models.CharField(verbose_name="First Name", max_length=16)
    last_name = models.CharField(verbose_name="Last Name", max_length=16)
    title = models.CharField(max_length=16, blank=True, null=True)
    personal_phone = models.CharField(verbose_name="Personal Phone Number", max_length=16, blank=True, null=True)
    office_phone = models.CharField(verbose_name="Office Phone Number", max_length=16, blank=True, null=True)
    fax = models.CharField(verbose_name="Fax Number", max_length=16, blank=True, null=True)
    status = models.BooleanField(default=True, blank=True)
    notifications = models.BooleanField(default=True, blank=True)
    newsletter = models.BooleanField(default=False, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    objects = ContactManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'password']

    def __unicode__(self):
        return "%s %s" % (self.first_name, self.last_name)

    def get_absolute_url(self):
        return "/accounts/contact/detail/%i/" % self.id

    def email_user(self, subject, message, from_email=None):
        send_mail(subject, message, from_email, [self.email])

    def get_full_name(self):
        return "%s %s" % (self.first_name, self.last_name)

    @property
    def is_staff(self):
        if self.groups.filter(name__in=["Staff", "Management"]).count():
            return True
        else:
            return False