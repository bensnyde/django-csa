from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from libs.ipaddr import ip_network
from apps.companies.models import Company
import logging

logger = logging.getLogger(__name__)

class NetworkAddress(models.Model):
    address = models.IPAddressField()
    cidr = models.PositiveIntegerField(validators = [MinValueValidator(24), MaxValueValidator(32)])
    description = models.CharField(max_length=256, null=True, blank=True)
    parent = models.ForeignKey('self', null=True, blank=True)
    vlan = models.ForeignKey('Vlan', null=True, blank=True)
    vrf = models.ForeignKey('Vrf', null=True, blank=True)
    owner = models.ForeignKey(Company, null=True, blank=True)  

    def __unicode__(self):
        return "%s/%d" % (self.address, self.cidr)

    class Meta:
        unique_together = ['address', 'cidr']        

    def get_netmask(self):
        return str(ip_network(self).netmask)

    def get_useable_hosts(self):
        hosts = []
        for x in ip_network(self).iterhosts():
            hosts.append(str(x))
        return hosts

    def does_ip_belong_to(self, ipaddr):
        if ip_network(ipaddr) in ip_network(self):
            return True
        else:
            return False

    def dump_to_dict(self):
        parent = 0
        if self.parent:
            parent = self.parent.pk

        owner_pk = 0
        owner_name = ""
        if self.owner:
            owner_pk = self.owner.pk
            owner_name = self.owner.name

        vlan_name = ""
        vlan_pk = 0
        if self.vlan:
            vlan_name = str(self.vlan)
            vlan_pk = self.vlan.pk

        vrf_name = ""
        vrf_pk = 0
        if self.vrf:
            vrf_name = str(self.vrf)
            vrf_pk = self.vrf.pk            

        return {
            'id': self.pk,
            'cidr': self.cidr,
            'owner': owner_name,
            'owner_pk': owner_pk,
            'parent': parent,
            'vlan': vlan_name,
            'vlan_pk': vlan_pk,
            'vrf': vrf_name,
            'vrf_pk': vrf_pk,
            'description': self.description,
            'address': self.address,
            'subnet': self.get_netmask(),
        }


class IPAddress(models.Model):
    address = models.IPAddressField()
    description = models.CharField(max_length=256, blank=True, null=True)
    network = models.ForeignKey(NetworkAddress)
    
    def __unicode__(self):
        return "%s" % (self.address)

    class Meta:
        unique_together = ['address', 'network'] 

class Vrf(models.Model):
    distinguisher = models.CharField(max_length=11)
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=256)

    def __unicode__(self):
        return "(%s) %s" % (self.distinguisher, self.name)

    def dump_to_dict(self, full=False):
        return {
            'id': self.pk,        
            'distinguisher': self.distinguisher,
            'name': self.name,
            'description': self.description
        }


class Vlan(models.Model):
    number = models.PositiveIntegerField(validators = [MinValueValidator(1), MaxValueValidator(4094)])
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=256)

    def __unicode__(self):
        return "%s (%d)" % (self.name, self.number)

    def dump_to_dict(self):
        return {
            'id': self.pk,
            'number': self.number,
            'name': self.name,
            'description': self.description
        }