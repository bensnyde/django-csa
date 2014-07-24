from apps.services.models import Service
from django.core.exceptions import ObjectDoesNotExist
from libs.cpanel_dns import Cpanel
from .models import NetworkAddress, IPAddress, Vrf, Vlan
import re
import json

def get_dns_reverse_zone(ipaddr):
    """Get Reverse DNS Zone

        Get parent network's reverse dns zone from remote CpanelDNS for specified IPv4 address.

    Parameters
        ipaddr: str ipv4 address
    Returns
        json dict
    """
    try:
        # Convert forward ipaddress into reverse zone
        octets = re.split('([0-9]*)\.([0-9]*)\.([0-9]*)\.([0-9]*)', ipaddr)
        reverse_zone = octets[3]+'.'+octets[2]+'.'+octets[1]+'.in-addr.arpa'

        return Cpanel().listZone(reverse_zone)
    except:
        return False


def set_ptr_from_zone(ipaddr, ptr=None):
    """Set PTR Record

        Sets/Unsets PTR record on remote CpanelDNS.

    Parameters
        ipaddr: str ipv4 address
        *ptr: str ptr record
    Returns
        result: bool result status
    """    
    zone = get_dns_reverse_zone(ipaddr)
    if not zone:
        return False
    else: 
        try:
            # Convert IP to reverse formatting
            octets = re.split('([0-9]*)\.([0-9]*)\.([0-9]*)\.([0-9]*)', ipaddr)
            reversed_zone = octets[3]+'.'+octets[2]+'.'+octets[1]+'.in-addr.arpa' 
            reversed_ip = octets[4]+'.'+octets[3]+'.'+octets[2]+'.'+octets[1]+'.in-addr.arpa.'

            # Delete existing
            for record in zone["data"]["records"]:
                if record["type"] == "PTR" and record["name"] == reversed_ip:              
                    Cpanel().deleteZoneRecord(reversed_zone, record["Line"])

            # Set new record
            if ptr:      
                result = Cpanel().addZoneRecord(**{
                    'name': reversed_ip,
                    'ttl': 14400, 
                    'zone': reversed_zone,
                    'type': "PTR",
                    'ptrdname': ptr       
                })

                # Parse Cpanel result to check for success
                # ****************************************
            return True
        except Exception as ex:
            return False


def get_ptr_from_zone(ipaddr, zone):
    """Get PTR Record

        Gets PTR record defined on remote CpanelDNS.

    Parameters
        ipaddr: str ipv4 address
        zone: dict CpanelDNS zone definition
    Returns
        ptr: str ptr record
    """    
    ptr_value = ""
    try:
        # Convert IP to reverse formatting
        octets = re.split('([0-9]*)\.([0-9]*)\.([0-9]*)\.([0-9]*)', ipaddr)
        reversed_ip = octets[4]+'.'+octets[3]+'.'+octets[2]+'.'+octets[1]+'.in-addr.arpa.'

        # Iterate through zone looking for ptr match
        for record in zone["data"]["records"]:
            if record["type"] == "PTR" and record["name"] == reversed_ip:
                ptr_value = record["ptrdname"]

        return ptr_value
    except Exception as ex:
        return False


def get_ptrs_from_zone(zone):
    """Get PTR Records

        Parses CpanelDNS zone listing for all PTR records.

    Parameters
        zone: dict CpanelDNS zone definition
    Returns
        ptrs (dict):
            address: str ipaddress
            ptr: str ptr record
    """     
    ptrs = []
    try:
        # Iterate through zone looking for ptr match
        for record in zone["data"]["records"]:
            if record["type"] == "PTR":
                # Convert reversed IPAddress to foward format
                octets = re.split('([0-9]*)\.([0-9]*)\.([0-9]*)\.([0-9]*)', record['name'])
                ip = octets[4]+'.'+octets[3]+'.'+octets[2]+'.'+octets[1]
                
                ptrs.append({'address': ip, 'ptr': record["ptrdname"]})
        return ptrs                  
    except:
        return False 


def get_vrf_index():
    """Get VRF Index

        Retrieves listing of VRF records.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        None
    Parameters
        None
    Returns
        Vrfs (list)
            Vrf (dict)
                distinguisher: str vrf route distinguisher
                name: str vrf name
    """       
    try:
        vrfs = []
        for vrf in Vrf.objects.all():
            vrfs.append(vrf.dump_to_dict())
        return vrfs
    except Exception as ex:
        ErrorLogger().log(request, "Failed", "Failed to enumerate Vrfs in apps.ip.views.get_vrf_index(): %s" % ex)
        return False

def get_vrf_detail(pk):
    """Get VRF Detail

        Retrieves specified VRF record.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        None
    Parameters
        pk: int vrf id
    Returns
        Vrf (dict)
            distinguisher: str vrf route distinguisher
            name: str vrf name
            description: str vrf description
    """     
    try:
        vrf = Vrf.objects.get(pk=pk)
        return vrf.dump_to_dict(True)
    except Exception as ex:
        ErrorLogger().log(request, "Failed", "Failed to enumerate Vrfs in apps.ip.views.get_vrf_detail(): %s" % ex)
        return False        


def create_vrf(**data):
    try:
        vrf = Vrf.objects.create(name=data["name"], distinguisher=data["distinguisher"], description=data["description"])
        ActionLogger().log(request.user, "created", "Vrf %s" % vrf)    
        return vrf
    except Exception as ex:
        ErrorLogger().log(request, "Failed", "Failed to set Vrf in apps.ip.views.set_vrf: %s" % ex)
        return False        


def update_vrf(pk, **data):
    try:
        vrf = Vrf.objects.get(pk=pk)
        vrf.name = data["name"]
        vrf.distinguisher = data["distinguisher"]
        vrf.description = data["description"]
        vrf.save()

        ActionLogger().log(request.user, "modified", "Vrf %s" % vrf)
        return vrf
    except Exception as ex:
        ErrorLogger().log(request, "Failed", "Failed to set Vrf in apps.ip.views.set_vrf: %s" % ex)
        return False        


def create_vlan(**data):
    try:
        vlan = Vlan.objects.create(name=data["name"], number=data["number"], description=data["description"])
        ActionLogger().log(request.user, "created", "Vlan %s" % vlan)
        return vlan
    except Exception as ex:
        ErrorLogger().log(request, "Failed", "Failed to set Vrf in apps.ip.views.create_vlan: %s" % ex)
        return False

def update_vlan(pk, **data):
    try:
        vlan = Vlan.objects.get(pk=pk)
        vlan.name = request.form.cleaned_data["name"]
        vlan.number = request.form.cleaned_data["number"]
        vlan.description = request.form.cleaned_data["description"]
        vlan.save()

        ActionLogger().log(request.user, "modified", "Vlan %s" % vlan)
        return vlan
    except Exception as ex:
        ErrorLogger().log(request, "Failed", "Failed to set Vlan in apps.ip.views.update_vlan: %s" % ex)
        return False         


def get_vlan_index():
    try:
        vlans = []
        for vlan in Vlan.objects.all():
            vlans.append(vlan.dump_to_dict())
        return vlans
    except:
        return False

def get_vlan_detail(pk):
    try:
        vlan = Vlan.objects.get(pk=pk)
        return vlan.dump_to_dict(True)
    except Exception as ex:
        ErrorLogger().log(request, "Failed", "Failed to enumerate Vrfs in apps.ip.views.get_vlan_detail(): %s" % ex)
        return False

def create_network(**data):
    try:
        network = NetworkAddress.objects.create(address=data["address"], cidr=data["cidr"], description=data["description"], vlan=data["vlan"])
        ActionLogger().log(request.user, "created", "NetworkAddress %s" % network)
        return network
    except Exception as ex:
        ErrorLogger().log(request, "Failed", "Failed to set NetworkAddress in apps.ip.views.set_news: %s" % ex)
        return False

def update_network(pk, **data):
    try:
        network = NetworkAddress.objects.get(pk=pk)
        network.address = data["address"]
        network.cidr = data["cidr"]
        network.description = data["description"]
        network.vlan = data["vlan"]
        network.save()

        ActionLogger().log(request.user, "modified", "NetworkAddress %s" % network)
        return network
    except Exception as ex:
        ErrorLogger().log(request, "Failed", "Failed to set NetworkAddress in apps.ip.views.set_news: %s" % ex)
        return False

def unset_ip_record(ipaddr):
    try:
        ip = IPAddress.objects.get(address=ipaddr).delete()
        return True
    except ObjectDoesNotExist:
        return True
    except Exception as ex:
        return False


def set_ip_record(network, ipaddr, description):
    try:
        ip = IPAddress.objects.get(address=ipaddr, network=network)
        ip.description = description
        ip.save()
        return True            
    except ObjectDoesNotExist:
        # IPAddress doesn't exist, create
        try:
            ip = IPAddress.objects.create(address=ipaddr, description=description, network=network)
            return True
        except Exception as ex:
            return False
    except Exception:
        return False         


def add_network_id_to_service_vars(user, service_id, network_id):
    # FIX ME
    try:
        service = Service.objects.get(pk=service_id)

        service_vars = user.get_service_vars('/services/ip/', service_id)
        if service_vars:
            service_vars["network_address_ids"].append(network.pk)
            Service.objects.filter(pk=service_id).update(vars=json.dumps(service_vars)) 

            return True
    except:
        pass
    return False


def get_ipaddresses_and_ptrs_from_networkaddress(parent, ip):
    hosts = []

    # Fetch PTR records from CpanelDNS Zone
    ptrs = get_ptrs_from_zone(get_dns_reverse_zone(ip))

    # Fetch IPAddress records from local database
    for host in IPAddress.objects.filter(network=parent):
        if not ptrs:
            # ************FIX ME******************
            # Alert user to inability to fetch PTR records
            #ErrorLogger().log(request, "Error", "Failed to fetch reverse zone from CpanelDNS in apps.ip.views.get_hosts")            
            hosts.append({"address": host.address, "description": host.description, "ptr": ""})
        else:
            match = False
            while match is False:
                for x in ptrs:
                    # If Address existings in both PTRs and Descriptions, combine into single record
                    if host.address == x['address']:
                        hosts.append({"address": host.address, "description": host.description, "ptr": x['ptr']}) 
                        match = True
                        break
                # Record exists in Descriptions list but not PTRs list 
                if not match:
                    hosts.append({"address": host.address, "description": host.description, "ptr": ""})
                match = True

    # Add remaining records that only exist in PTRs listing
    if ptrs:
        for x in ptrs:
            if x['address'] not in [y.address for y in IPAddress.objects.filter(network=parent)]:
                hosts.append({"address": x['address'], "description": '', "ptr": x['ptr']}) 

    return hosts   