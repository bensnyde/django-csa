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