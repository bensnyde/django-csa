# System
import logging
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
# Project
from common.helpers import format_ajax_response
from common.decorators import validated_request, validated_service, validated_staff
from apps.loggers.models import ActionLogger
# App
from .helpers import *
from .models import NetworkAddress, IPAddress, Vrf, Vlan
from .forms import IPAddressForm, NetworkAddressForm, NetworkAddressAddForm, VlanForm, VrfForm


logger = logging.getLogger(__name__)


@login_required
def index(request, service_id, parent=None):
    """Network/IP List View

        Lists NetworkAddresses currently allocated to requesting user's company.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @login_required
            request.user.is_authenticated() must be True
        @validated_service
            service_id must belong to request.user.company.services          
    Parameters
        request: HttpRequest
        service_id: int service id 
        parent: str parent ipv4 network address (x.x.x.x/x)
    Returns
        HttpResponse (ip/index.html)
            service_id: int current service id 
            parent: str parent ipv4 network address (x.x.x.x/x)
    """
    return render(request, 'ip/index.html', {'parent': parent,'service_id': service_id, 'networkaddressform': NetworkAddressAddForm()})


@login_required
def request_ip_space(request):
    """Request IP Space View

        Displays IPRequestForm for submitting IP requests.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @login_required
            request.user.is_authenticated() must be True
    Parameters
        request: HttpRequest
    Returns
        HttpResponse (ip/request.html)
    """    
    return render(request, 'ip/request.html')    


@validated_staff
def admin(request):
    """Request IP Space View

        Displays IPRequestForm for submitting IP requests.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_staff
            request.user.is_staff must be True
    Parameters
        request: HttpRequest
    Returns
        HttpResponse (ip/admin.html)
    """    
    return render(request, 'ip/admin.html', {'networkaddressform': NetworkAddressAddForm()})    


@validated_request(None)
@validated_service
def get_networks(request, network_address_ids):
    """NetworkAddress Getter

        Retrieves list of NetworkAddresses belonging to specified Service.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_request
            request.method must be POST
            request.is_ajax() must be True
            request.user.is_authenticated() must be True
        @validated_service
            service_id must belong to request.user.company.services
            service.vars is injected into view parameter  
    Parameters
        request: HttpRequest
        network_address_ids: int[] network address ids
    Returns
        HttpResponse (JSON)
            success: int response status
            message: str response message
            *data:
                networks: 
                    hostname: str ip hostname
                    description: str ip description
                    ptr: str ip ptr dns record
    """ 
    try:         
        network_list = []
        for network in NetworkAddress.objects.filter(pk__in=network_address_ids):
            network_list.append(network.dump_to_dict())

        return format_ajax_response(True, "NetworkAddress listing retrieved successfully.", {"networks": network_list})
    except Exception as ex:
        logger.error("Failed to get_networks: %s" % ex)
        return format_ajax_response(False, "There was a problem retrieving the NetworkAddress listing.")


@validated_request(NetworkAddressForm)
@validated_service
def get_hosts(request, network_address_ids):
    """Get IPAddress Index

        Retrieves list of local IPAddress records and remote CpanelDNS PTR records under specified NetworkAddress.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_request
            request.POST must validate against NetworkAddressForm
            request.method must be POST
            request.is_ajax() must be True
            request.user.is_authenticated() must be True
        @validated_service
            service_id must belong to request.user.company.services
            service.vars is injected into view parameter  
    Parameters
        request: HttpRequest
        network_address_ids: int[] network address ids
    Returns
        HttpResponse (JSON)
            success: int response status
            message: str response message
            *data: 
                hosts:
                    address: str ipaddress 
                    description: str description
                    ptr: str rDNS record
    """
    try:   
        ip, net_size = request.form.cleaned_data["parent"].split('/')
        parent = NetworkAddress.objects.get(address=ip, cidr=int(net_size))

        if parent.id not in network_address_ids:
            raise Exception("Forbidden: specified NetworkAddress doesn't belong to specified Service.")

        hosts = get_ipaddresses_and_ptrs_from_networkaddress(parent, ip)
        if hosts is False:
            raise Exception("No hosts or PTRs returned for specified NetworkAddress.")

        return format_ajax_response(True, "Hosts listing retrieved successfully.", {'hosts': hosts})
    except Exception as ex:
        logger.error("Failed to get_hosts: %s" % ex)
        return format_ajax_response(False, "There was a problem retrieving hosts listing.")        


@validated_request(IPAddressForm)
@validated_service
def get_host_details(request, network_address_ids):
    """Get IPAddress Detail

        Retrieves local IPAddress record and remote CpanelDNS PTR record for specified IPAddress.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_request
            request.POST must validate against IPAddressForm
            request.method must be POST
            request.is_ajax() must be True
            request.user.is_authenticated() must be True
        @validated_service
            service_id must belong to request.user.company.services
            service.vars is injected into view parameter  
    Parameters
        request: HttpRequest
        network_address_ids: int[] network address ids
    Returns
        HttpResponse (JSON)
            success: int response status
            message: str response message
            *data:
                host:
                    description: str ip description
                    ptr: str ip ptr dns record
    """
    try:
        ip, net_size = request.form.cleaned_data["network"].split('/')
        parent = NetworkAddress.objects.get(address=ip, cidr=int(net_size))

        if parent.id not in network_address_ids:
            raise Exception("Forbidden: specified NetworkAddress doesn't belong to specified Service.")

        if not parent.does_ip_belong_to(request.form.cleaned_data['address']):
            raise Exception("Forbidden: specified IPAddress doesn't belong to specified NetworkAddress.") 

        # Fetch IPAddress
        try:
            ip = IPAddress.objects.get(address=request.form.cleaned_data['address'])
            description = ip.description
        except:
            description = ""         

        # Fetch PTR
        zone = get_dns_reverse_zone(request.form.cleaned_data['address'])
        ptr = get_ptr_from_zone(request.form.cleaned_data['address'], zone)
        if not ptr:
            ptr = ""

        return format_ajax_response(True, "Host details retrieved successfully.", {"host": {'description': description, 'ptr': ptr}})
    except Exception as ex:
        logger.error("Failed to get_host_details: %s" % ex)
        return format_ajax_response(False, "There was a problem retrieving host details.")     


@validated_request(IPAddressForm)
@validated_service
def set_host_details(request, network_address_ids):
    """IPAddress Setter

        Sets/Unsets local IPAddress record and remote CpanelDNS PTR record.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_request 
            request.POST must validate against IPAddressForm
            request.method must be POST
            request.is_ajax() must be True
            request.user.is_authenticated() must be True
        @validated_service
            service_id must belong to request.user.company.services
            service.vars is injected into view parameter  
    Parameters
        request: HttpRequest
        network_address_ids: int[] network address ids
    Returns
        HttpResponse (JSON)
            success: int response status
            message: str response message
    """
    try:
        # Retrieve NetworkAddress
        ip, net_size = request.form.cleaned_data["network"].split('/')
        parent = NetworkAddress.objects.get(address=ip, cidr=int(net_size))

        if parent.id not in network_address_ids:
            raise Exception("Forbidden: specified NetworkAddress doesn't belong to specified Service.")

        if not parent.does_ip_belong_to(request.form.cleaned_data['address']):
            raise Exception("Forbidden: specified IPAddress doesn't belong to specified NetworkAddress.")

        if request.form.cleaned_data['description'] == "" and request.form.cleaned_data['ptr'] == "":
            # Unset both records 
            iprecord_success = unset_ip_record(request.form.cleaned_data['address'])
            ptrrecord_success = set_ptr_from_zone(request.form.cleaned_data['address'], None)
        elif request.form.cleaned_data['description'] == "":
            # Unset IPAddress, set PTR  
            iprecord_success = unset_ip_record(request.form.cleaned_data['address'])
            ptrrecord_success = set_ptr_from_zone(request.form.cleaned_data['address'], request.form.cleaned_data['ptr'])
        elif request.form.cleaned_data['ptr'] == "":
            # Unset PTR, set IPAddress  
            iprecord_success = set_ip_record(parent, request.form.cleaned_data['address'], request.form.cleaned_data['description'])
            ptrrecord_success = set_ptr_from_zone(request.form.cleaned_data['address'], None)
        else:
            # Set both records   
            ptrrecord_success = set_ptr_from_zone(request.form.cleaned_data['address'], request.form.cleaned_data['ptr'])             
            iprecord_success = set_ip_record(parent, request.form.cleaned_data['address'], request.form.cleaned_data['description'])

        # Logging and response
        if ptrrecord_success and iprecord_success:
            ActionLogger().log(request.user, "set",  "PTR Record %s" % request.form.cleaned_data['address'], request.form.cleaned_data['network'])
            ActionLogger().log(request.user, "set", "Host %s" % ip, "Network %s" % request.POST['network'])
            return format_ajax_response(True, "Host record set successfully.")  
        elif ptrrecord_success:
            ActionLogger().log(request.user, "set",  "PTR Record %s" % request.form.cleaned_data['address'], request.form.cleaned_data['network'])
            return format_ajax_response(True, "PTR record was set but there was a problem setting the Description.")
        elif iprecord_success:
            ActionLogger().log(request.user, "set", "Host %s" % ip, "Network %s" % request.POST['network'])  
            return format_ajax_response(True, "Host record was set but there was a problem setting the PTR record.")      
        else:
            raise Exception("Failed to set IPAddress and PTR record.")    
    except Exception as ex:
        logger.error("Failed to set_host_details: %s" % ex)
        return format_ajax_response(False, "There was a problem setting the host record.")  


@validated_staff
@validated_request(NetworkAddressAddForm)
def set_network(request):    
    """NetworkAddress Setter

        Creates new NetworkAddress record or updates existing if networkaddress.pk.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_staff
            request.user.is_staff() must be True     
        @validated_request
            request.POST must validate against NetworkAddressAddForm
            request.method must be POST
            request.is_ajax() must be True
            request.user.is_authenticated() must be True
    Parameters
        request: HttpRequest
        service_id: int service id
    Returns
        HttpResponse (JSON)
            success: int response status
            message: str response message
    """
    try: 
        if "networkaddress_id" not in request.POST or not int(request.POST["networkaddress_id"]):
            # Create NetworkAddress
            network = NetworkAddress.objects.create(address=request.form.cleaned_data["address"], cidr=request.form.cleaned_data["cidr"], description=request.form.cleaned_data["description"], vlan=request.form.cleaned_data["vlan"])

            # Assign NetworkAddress to Service
            if 'service' in request.POST and int(request.POST['service']):
                service = Service.objects.get(pk=int(request.POST['service']))
                service_vars = request.user.get_service_vars('/services/ip/', int(request.POST['service']))
                if service_vars:
                    service_vars["network_address_ids"].append(network.pk)
                    service.vars = json.dumps(service_vars)
                    service.save()
                else:
                    raise Exception("user.get_service_vars('/services/ip/', %s) returned False." % int(request.POST['service']))

            ActionLogger().log(request.user, "created", "NetworkAddress %s" % network)
            return format_ajax_response(True, "NetworkAddress created successfully.")
        else:
            # Update NetworkAddress
            network = NetworkAddress.objects.get(pk=request.POST["networkaddress_id"])
            network.address = request.form.cleaned_data["address"]
            network.cidr = request.form.cleaned_data["cidr"]
            network.description = request.form.cleaned_data["description"]
            network.vlan = request.form.cleaned_data["vlan"]
            network.save()


            # Code for reallocation goes here

            ActionLogger().log(request.user, "modified", "NetworkAddress %s" % network)
            return format_ajax_response(True, "NetworkAddress updated successfully.")
    except Exception as ex:
        logger.error("Failed to set_network: %s" % ex)
        return format_ajax_response(False, "There was a problem setting the NetworkAddress.")


@validated_staff
@validated_request(None)
def delete_network(request):    
    """Delete NetworkAddress

        Deletes list of NetworkAddress records.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_staff
            request.user.is_staff() must be True    
        @validated_request
            request.method must be POST
            request.is_ajax() must be True
            request.user.is_authenticated() must be True 
    Parameters
        request: HttpRequest
            networkaddress_id: int[] networkaddress id
    Returns
        HttpResponse (JSON)
            success: int response status
            message: str response message
    """ 
    try:
        network = request.POST.getlist('networkaddress_id')
        NetworkAddress.objects.filter(pk__in=network).delete()
        ActionLogger().log(request.user, "deleted", "NetworkAddress %s" % network)
        return format_ajax_response(True, "NetworkAddress record(s) deleted successfully.")
    except Exception as ex:
        logger.error("Failed to delete_network: %s" % ex)
        return format_ajax_response(False, "There was a problem deleting the NetworkAddress record(s).")


@validated_staff
@validated_request(None)
def get_vlan(request):
    """Vlan Getter

        Fetches single Vlan record if vlan.pk is specified,
        otherwise fetches list of Vlan records.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_staff
            request.user.is_staff() must be True
        @validated_request
            request.method must be POST
            request.is_ajax() must be True
            request.user.is_authenticated() must be True
    Parameters
        request: HttpRequest
            *vlan_id: int vlan id
    Returns
        HttpResponse (JSON)
            success: int response status
            message: str response message
            *data: 
                name: str vlan name
                description: str vlan description
                number: int vlan number
    """
    try:
        if "vlan_id" not in request.POST or not int(request.POST["vlan_id"]):
            vlans = []
            for vlan in Vlan.objects.all():
                vlans.append(vlan.dump_to_dict())
            return format_ajax_response(True, "Vlan listing retrieved successfully.", {'vlans': vlans})
        else:
            vlan = Vlan.objects.get(pk=int(request.POST["vlan_id"])).dump_to_dict(True)
            return format_ajax_response(True, "Vlan record retrieved successfully.", {'vlan': vlan})
    except Exception as ex:
        logger.error("Failed to get_vlan: %s" % ex)
        return format_ajax_response(False, "There was an error retreiving the Vlan record.")
  

@validated_staff
@validated_request(VlanForm)
def set_vlan(request):    
    """Vlan Setter

        Creates new Vlan record or updates existing Vlan record if vlan.pk is specified.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_staff
            request.user.is_staff() must be True    
        @validated_request
            request.POST must validate against VlanForm
            request.method must be POST
            request.is_ajax() must be True
            request.user.is_authenticated() must be True
    Parameters
        request: HttpRequest
            *vlan_id: int vlan id
    Returns
        HttpResponse (JSON)
            success: int response status
            message: str response message
    """
    try:
        if "vlan_id" not in request.POST or not int(request.POST["vlan_id"]):
            vlan = Vlan.objects.create(name=request.form.cleaned_data["name"], number=request.form.cleaned_data["number"], description=request.form.cleaned_data["description"])
            ActionLogger().log(request.user, "created", "Vlan %s" % vlan)
            return format_ajax_response(True, "Vlan record created successfully.")
        else:
            vlan = Vlan.objects.get(pk=int(request.POST["vlan_id"]))
            vlan.name = request.form.cleaned_data["name"]
            vlan.number = request.form.cleaned_data["number"]
            vlan.description = request.form.cleaned_data["description"]
            vlan.save()

            ActionLogger().log(request.user, "modified", "Vlan %s" % vlan)
            return format_ajax_response(True, "Vlan record updated successfully.")
    except Exception as ex:
        logger.error("Failed to set_vlan: %s" % ex)
        return format_ajax_response(False, "There was an error setting the Vlan record.")


@validated_staff
@validated_request(None)
def delete_vlan(request):    
    """Delete Vlan

        Deletes list of Vlan records.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_staff
            request.user.is_staff() must be True
        @validated_request
            request.POST must validate against IPAddressForm
            request.method must be POST
            request.is_ajax() must be True
            request.user.is_authenticated() must be True
    Parameters
        request: HttpRequest
            vlan_id: int[] vlan ids
    Returns
        HttpResponse (JSON)
            success: int response status
            message: str response message
    """ 
    try:
        vlans = request.POST.getlist('vlan_id')
        Vlan.objects.filter(pk__in=vlans).delete()
        ActionLogger().log(request.user, "deleted", "Vlan %s" % vlans)
        return format_ajax_response(True, "Vlan record(s) deleted successfully.")
    except Exception as ex:
        logger.error("Failed to delete_vlan: %s" % ex)
        return format_ajax_response(False, "There was a problem deleting the specified Vlans")


@validated_staff
@validated_request(VrfForm)
def set_vrf(request):    
    """Vrf Setter

        Creates new Vrf record or updates existing Vrf record if vrf.pk is specified. 

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_staff
            request.user.is_staff() must be True
        @validated_request
            request.POST must validate against VrfForm
            request.method must be POST
            request.is_ajax() must be True
            request.user.is_authenticated() must be True
    Parameters
        request: HttpRequest
            *vrf_id: int vrf id
    Returns
        HttpResponse (JSON)
            success: int response status
            message: str response message
    """
    try:
        if "vrf_id" not in request.POST or not int(request.POST["vrf_id"]):
            vrf = Vrf.objects.create(name=request.form.cleaned_data["name"], distinguisher=request.form.cleaned_data["distinguisher"], description=request.form.cleaned_data["description"])
            ActionLogger().log(request.user, "created", "Vrf %s" % vrf)
            return format_ajax_response(True, "Vrf record created successfully.")
        else:
            vrf = Vrf.objects.get(pk=int(request.POST["vrf_id"]))
            vrf.name = request.form.cleaned_data["name"]
            vrf.distinguisher = request.form.cleaned_data["distinguisher"]
            vrf.description = request.form.cleaned_data["description"]
            vrf.save()

            ActionLogger().log(request.user, "modified", "Vrf %s" % vrf)
            return format_ajax_response(True, "Vrf record updated successfully.")
    except Exception as ex:
        logger.error("Failed to set_vrf: %s" % ex)
        return format_ajax_response(False, "There was an error setting the Vrf record.")


@validated_staff
@validated_request(None)
def get_vrf(request):
    """Get VRF

        Fetches a single Vrf record as specified by vrf.pk, 
        or a listing of Vrf records if no PK is specified.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_staff
            request.user.is_staff() must be True
        @validated_request
            request.method must be POST
            request.is_ajax() must be True
            request.user.is_authenticated() must be True 
    Parameters
        request: HttpRequest
            *vrf_id: int vrf id
    Returns
        HttpResponse (JSON)
            success: int response status
            message: str response message
            *data: 
                vrf:
                    distinguisher: str vrf route distinguisher
                    name: str vrf name
                    description: str vrf description
    """
    try:
        if "vrf_id" not in request.POST or not int(request.POST["vrf_id"]):
            vrfs = []
            for vrf in Vrf.objects.all():
                vrfs.append(vrf.dump_to_dict())
            return format_ajax_response(True, "Vrf listing retrieved successfully.", {'vrfs': vrfs})   
        else:
            vrf = Vrf.objects.get(pk=int(request.POST["vrf_id"])).dump_to_dict(True)
            return format_ajax_response(True, "Vrf listing retrieved successfully.", {'vrf': vrf})
    except Exception as ex:
        logger.error("Failed to get_vrf: %s" % ex)
        return format_ajax_response(False, "There was an error retrieving vrf listing.")


@validated_staff
@validated_request(None)
def delete_vrf(request):    
    """Delete VRF

        Deletes list of VRF's specified by vrf.pk.

    Middleware
        See SETTINGS for active Middleware.
    Decorators
        @validated_staff
            request.user.is_staff() must be True
        @validated_request
            request.method must be POST
            request.is_ajax() must be True
            request.user.is_authenticated() must be True
    Parameters
        request: HttpRequest
            *vrf_id: int[] vrf ids        
    Returns
        HttpResponse (JSON)
            success: int response status
            message: str response message
    """ 
    try:
        vrf = request.POST.getlist('vrf_id')
        Vrf.objects.filter(pk__in=vrf).delete()
        ActionLogger().log(request.user, "deleted", "Vrf %s" % vrf)
        return format_ajax_response(True, "Vrf record(s) deleted successfully.")
    except Exception as ex:
        logger.error("Failed to delete_vrf: %s" % ex)
        return format_ajax_response(False, "There was a problem deleting the Vrf record(s).")