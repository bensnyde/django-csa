from apps.services.models import Service
from django.core.exceptions import ObjectDoesNotExist
from libs.cpanel_dns import Cpanel
import libs.ipaddr as ip_network
from .models import NetworkAddress, IPAddress, Vrf, Vlan
import re
import json
import logging


logger = logging.getLogger(__name__)


def describe_subnet(network, cidr, new_prefix):
    try:
        network = ip_network.IPv4Network("%s/%s" % (network, cidr))

        counter = 0
        for x in network.subnet(new_prefix=new_prefix):
            numhosts = x.numhosts
            counter += 1

        return {
            'prefix': new_prefix,
            'numnets': counter,
            'numhosts': numhosts
        }
    except Exception as ex:
        logger.error(str(ex))
        return False


def get_subnets(network, cidr, new_prefix):
    try:
        subnets = []
        network = ip_network.IPv4Network("%s/%s" % (network, cidr))
        for x in network.subnet(new_prefix=new_prefix):
            subnets.append(x.network_address.compressed)

        return subnets
    except Exception as ex:
        logger.error(str(ex))
        return False


def is_valid_networkaddress(address, cidr):
    try:
        net = ip_network.IPv4Network("%s/%s" % (address, cidr))
        if net.is_private:
            raise Exception("Private Network's not allowed.")
        if net.is_loopback:
            raise Exception("Loopback Network's not allowed.")            
        if net.is_link_local:
            raise Exception("Link Local Network's not allowed.")                  
        if net.is_reserved:
            raise Exception("Reserved Network's not allowed.")
        if net.is_unspecified:
            raise Exception("Unspecified Network's not allowed.") 
        if net.is_multicast:
            raise Exception("Multicast Network's not allowed.") 

        return True
    except Exception as ex:
        logger.error(str(ex))
        return False


def is_ip_in_network(network, cidr, ipaddr):
    try:
        if ip_network.IPv4Address(ipaddr) in ip_network.IPv4Network("%s/%s" % (network, cidr)):
            return True
    except Exception as ex:
        logger.error(str(ex)) 
    return False 


def reverse_notate(network, cidr, ipaddr=None):    
    try:
        if cidr < 24:
            raise Exception("CIDR must be >= 24.")

        octets = re.split('([0-9]*)\.([0-9]*)\.([0-9]*)\.([0-9]*)', network)
        reversed_zone = octets[3]+'.'+octets[2]+'.'+octets[1]+'.in-addr.arpa' 

        if cidr > 24:
            reversed_zone = octets[4] + '-' + str(cidr) + '.' + reversed_zone

        if ipaddr:
            octets = re.split('([0-9]*)\.([0-9]*)\.([0-9]*)\.([0-9]*)', ipaddr)
            reversed_zone = octets[4] + '.' + reversed_zone + '.'

        return reversed_zone
    except Exception as ex:
        logger.error(str(ex))
        return False


def fetch_dns_zone(zone):
    try:
        return Cpanel().listZone(zone)
    except Exception as ex:
        logger.error(str(ex))
        return False


def set_ptr_from_zone(parent, ipaddr, ptr=None):
    rev_zone = reverse_notate(parent.address, parent.cidr)
    zone = fetch_dns_zone(rev_zone)
    if not zone:
        return False
    else: 
        try:
            # Convert IP to reverse formatting
            reversed_ip = reverse_notate(ipaddr, parent.cidr)
            octets = re.split('([0-9]*)\.([0-9]*)\.([0-9]*)\.([0-9]*)', ipaddr)

            # Delete existing
            for record in zone:
                if record["type"] == "PTR" and record["name"] == reversed_ip:              
                    Cpanel().deleteZoneRecord(rev_zone, record["Line"])

            # Set new record
            if ptr:      
                result = Cpanel().addZoneRecord(**{
                    'name': octets[4],
                    'ttl': 14400, 
                    'zone': rev_zone,
                    'type': "PTR",
                    'ptrdname': ptr       
                })

                # Parse Cpanel result to check for success
                # ****************************************
            return True
        except Exception as ex:
            logger.error(str(ex))
            return False


def get_ptr_from_zone(network, cidr, ipaddr):
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
        rev_zone = reverse_notate(network, cidr)
        zone = fetch_dns_zone(rev_zone)

        reversed_ip = reverse_notate(network, cidr, ipaddr)

        # Iterate through zone looking for ptr match
        for record in zone:
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
    p = re.compile(ur'''# First octet
    (?P<octet1>
      # Numbers in the range 0-255
      \b[0-9]\b
    | \b[1-9][0-9]\b
    | \b[12][0-9][0-9]\b
    )
    \.  # A literal dot between octets
    # Ignore "range" IPs
    (?:\d+-\d+\.)?
    # Second octet
    (?P<octet2>
      # Numbers in the range 0-255
      \b[0-9]\b
    | \b[1-9][0-9]\b
    | \b[12][0-9][0-9]\b
    )
    \.  # A literal dot between octets
    # Third octet
    (?P<octet3>
      # Numbers in the range 0-255
      \b[0-9]\b
    | \b[1-9][0-9]\b
    | \b[12][0-9][0-9]\b
    )
    \.  # A literal dot between octets
    # Fourth octet
    (?P<octet4>
      # Numbers in the range 0-255
      \b[0-9]\b
    | \b[1-9][0-9]\b
    | \b[12][0-9][0-9]\b
    )
    ''', re.MULTILINE | re.VERBOSE)

    try:
        # Iterate through zone looking for ptr match
        for record in zone:
            if record["type"] == "PTR":
                # Convert reversed IPAddress to foward format
                octets = re.split(p, record['name'])
                ip = octets[4]+'.'+octets[3]+'.'+octets[2]+'.'+octets[1]
                
                ptrs.append({'address': ip, 'ptr': record["ptrdname"]})
        return ptrs                  
    except Exception as ex:
        logger.error(str(ex))
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



def get_ipaddresses_and_ptrs_from_networkaddress(parent):
    rev_zone = reverse_notate(parent.address, parent.cidr)
    zone = fetch_dns_zone(rev_zone)
    ptrs = get_ptrs_from_zone(zone)

    hosts = []
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


def delete_ptrs_from_zone(networkaddress, cidr): 
    try:
        rev_zone = reverse_notate(networkaddress, cidr)
        # Reset zone here
        #for record["type"] as record in fetch_dns_zone(rev_zone):
        #    if record["type"] == "PTR":
        #        logger.error(Cpanel().deleteZoneRecord(rev_zone, record["Line"]))
            
        return True               
    except Exception as ex:
        logger.error(ex)
        return False  