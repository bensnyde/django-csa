from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from libs.ipaddr import ip_network

class NetworkAddress(models.Model):
    address = models.IPAddressField()
    cidr = models.PositiveIntegerField(validators = [MinValueValidator(24), MaxValueValidator(32)])
    description = models.CharField(max_length=256, null=True, blank=True)
    parent = models.ForeignKey('self', null=True, blank=True)
    vlan = models.ForeignKey('Vlan', null=True, blank=True)
    vrf = models.ForeignKey('Vrf', null=True, blank=True)    

    def __unicode__(self):
        return "%s/%d" % (self.address, self.cidr)

    def get_netmask(self):
        net = ip_network(self)
        return str(net.netmask)

    def get_numhosts(self):
        net = ip_network(self)
        hosts = []
        for x in net.iterhosts():
            hosts.append(str(x))
        return hosts

    def does_ip_belong_to(self, ipaddr):
        net = ip_network(self)
        if ip_network(ipaddr) in net:
            return True
        else:
            return False

    def dump_to_dict(self):
        return {
            'cidr': self.cidr,
            'vlan': self.vlan,
            'description': self.description,
            'address': self.address,
            'subnet': self.get_netmask(),
            'usable_hosts': self.get_numhosts()
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
        return "%s/%d" % (self.name, self.distinguisher)

    def dump_to_dict(self, full=False):
        result = {
            'distinguisher': self.distinguisher,
            'name': self.name
        }

        if full:
            result.update({'description': self.description})

        return result


class Vlan(models.Model):
    number = models.PositiveIntegerField(validators = [MinValueValidator(1), MaxValueValidator(4094)])
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=256)

    def __unicode__(self):
        return "%s (%d)" % (self.name, self.number)

    def dump_to_dict(self, full=False):
        result = {
            'number': self.number,
            'name': self.name
        }        

        if full:
            result.update({'description': self.description})

        return result