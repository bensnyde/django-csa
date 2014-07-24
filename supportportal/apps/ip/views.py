# System
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
# Project
from common.helpers import format_ajax_response
from common.decorators import validated_request, validated_service, validated_staff
from apps.loggers.models import ErrorLogger, ActionLogger
# App
from .helpers import *
from .models import NetworkAddress, IPAddress, Vrf, Vlan
from .forms import IPAddressForm, NetworkAddressForm, NetworkAddressAddForm, VlanForm, VrfForm


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
        ErrorLogger().log(request, "Error", "Failed to fetch NetworkAddress listing in apps.ip.views.get_networks: %s" % ex)
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
        # Retrieve NetworkAddress          
        ip, net_size = request.form.cleaned_data["parent"].split('/')
        parent = NetworkAddress.objects.get(address=ip, cidr=int(net_size))
    except Exception as ex:
        ErrorLogger().log(request, "Error", "Failed to get hosts in apps.ip.views.get_hosts: %s" % ex)
        return format_ajax_response(False, "There was a problem retrieving hosts listing.")        

    # Ensure NetworkAddress belongs to specified Service
    if parent.id not in network_address_ids:
        ErrorLogger().log(request, "Forbidden", "User attempted access to unauthorized service_var NetworkAddress apps.ip.views.get_hosts") 
        return format_ajax_response(False, "Unauthorized access to protected resource.")

    hosts = get_ipaddresses_and_ptrs_from_networkaddress(parent, ip)
    if hosts is False:
        return format_ajax_response(False, "There was a problem retrieving hosts listing.")

    return format_ajax_response(True, "Hosts listing retrieved successfully.", {'hosts': hosts})


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
        # Validate NetworkAddress
        ip, net_size = request.form.cleaned_data["network"].split('/')
        parent = NetworkAddress.objects.get(address=ip, cidr=int(net_size))
    except Exception as ex:
        ErrorLogger().log(request, "Error", "Failed to get hosts in apps.ip.views.get_host_details: %s" % ex)
        return format_ajax_response(False, "There was a problem retrieving host details.")     

    if parent.id not in network_address_ids:
        ErrorLogger().log(request, "Forbidden", "User attempted access to unauthorized service_var in apps.ip.views.get_host_details") 
        return format_ajax_response(False, "Unauthorized access to protected resource.")

    # Ensure specified IPAddress belongs to specified NetworkAddress
    if not parent.does_ip_belong_to(request.form.cleaned_data['address']):
        ErrorLogger().log(request, "Forbidden", "User attempted access to unauthorized service_var in apps.ip.views.get_host_details") 
        return format_ajax_response(False, "Unauthorized access to protected resource.")    

    # Fetch IPAddress object
    try:
        ip = IPAddress.objects.get(address=request.form.cleaned_data['address'])
        description = ip.description
    except:
        description = ""

    # Fetch PTR record from CpanelDNS
    zone = get_dns_reverse_zone(request.form.cleaned_data['address'])
    ptr = get_ptr_from_zone(request.form.cleaned_data['address'], zone)
    if not ptr:
        # Log error
        ptr = ""

    return format_ajax_response(True, "Host details retrieved successfully.", {"host": {'description': description, 'ptr': ptr}})
  

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
    except Exception as ex:
        ErrorLogger().log(request, "Error", "Failed to get hosts in apps.ip.views.set_host_details: %s" % ex)
        return format_ajax_response(False, "There was a problem setting the host record.")  

    # Ensure NetworkAddress belongs to specified Service        
    if parent.id not in network_address_ids:
        ErrorLogger().log(request, "Forbidden", "User attempted access to unauthorized service_var in apps.ip.views.set_host_details") 
        return format_ajax_response(False, "Unauthorized access to protected resource.")

    # Ensure specified IPAddress belongs to specified NetworkAddress
    if not parent.does_ip_belong_to(request.form.cleaned_data['address']):
        ErrorLogger().log(request, "Forbidden", "User attempted access to unauthorized service_var in apps.ip.views.set_host_details") 
        return format_ajax_response(False, "Unauthorized access to protected resource.")

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
        ErrorLogger().log(request, "Error", "Failed to set IPAddress record in apps.ip.views.set_host_details")
        return format_ajax_response(True, "PTR record was set but there was a problem setting the Description.")
    elif iprecord_success:
        ActionLogger().log(request.user, "set", "Host %s" % ip, "Network %s" % request.POST['network'])  
        ErrorLogger().log(request, "Error", "Failed to set PTR record in apps.ip.views.set_host_details")
        return format_ajax_response(True, "Host record was set but there was a problem setting the PTR record.")      
    else:
        ErrorLogger().log(request, "Error", "Failed to set IPAddress record in services.ip.views.set_host_details")
        ErrorLogger().log(request, "Error", "Failed to set PTR record in services.ip.views.set_host_details")
        return format_ajax_response(False, "There was a problem setting the host record.")


@validated_staff
@validated_request(NetworkAddressAddForm)
def set_network(request, service_id):    
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
    if "networkaddress_id" not in request.POST or request.POST["networkaddress_id"] is not 0:
        # Create
        network = create_network(request.form.cleaned_data)
        if network:
            if add_network_id_to_servie_vars(request.user, service_id, network.id):
                return format_ajax_response(True, "NetworkAddress created successfully.")
            else:
                # LOG ME 
                return format_ajax_repsonse(False, "NetworkAddress was created but could not be allocated.")
        else:
            return format_ajax_response(False, "There was a problem creating the NetworkAddress.")
    else:
        # Update
        if update_network(int(request.POST['networkaddress_id']), request.form.cleaned_data):
            return format_ajax_response(True, "NetworkAddress updated successfully.")
        else:
            return format_ajax_response(False, "There was a problem updating the NetworkAddress.")


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
        network = request.POST.getlist('networkaddress_id[]')
        NetworkAddress.objects.filter(pk__in=network).delete()
        ActionLogger().log(request.user, "deleted", "NetworkAddress %s" % network)
        return format_ajax_response(True, "NetworkAddress record(s) deleted successfully.")
    except Exception as ex:
        ErrorLogger().log(request, "Failed", "Failed to delete NetworkAddress(es) in apps.ip.views.delete_network: %s" % ex)
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
    if "vlan_id" not in request.POST or request.POST["vlan_id"] is not 0:
        data = get_vlan_index()
    else:
        data = get_vlan_detail(request.POST["vlan_id"])

    if data:
        return format_ajax_response(True, "Vlan record retrieved successfully.")
    else:
        return format_ajax_response(False, "There was an error retrieving the Vlan record.")
  

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
    if "vlan_id" not in request.POST or request.POST["vlan_id"] is not 0:
        result = create_vlan(request.form.cleaned_data)
    else:
        result = updat_vlan(request.POST["vlan_id"], request.form.cleaned_data)

    if result:
        return format_ajax_response(True, "Vlan record set successfully.")
    else:
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
        vlans = request.POST.getlist('vlan_id[]')
        Vlan.objects.filter(pk__in=vlans).delete()
        ActionLogger().log(request.user, "deleted", "Vlan %s" % vlans)
        return format_ajax_response(True, "Vlan record(s) deleted successfully.")
    except Exception as ex:
        ErrorLogger().log(request, "Failed", "Failed to delete Vlan(s) in apps.ip.views.delete_vlan: %s" % ex)
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
    if "vrf_id" not in request.POST or request.POST["vrf_id"] is not 0:
        result = create_vrf(request.form.cleaned_data)
    else:
        result = update_vrf(request.POST["vrf_id"], request.form.cleaned_data)

    if result:
        return format_ajax_response(True, "Vrf record set successfully.")
    else:
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
    if "vrf_id" not in request.POST or request.POST["vrf_id"] is not 0:
        data = get_vrf_index()
    else:
        data = get_vrf_detail(request.POST["vrf_id"])

    if data:
        return format_ajax_response(True, "Vrf listing retrieved successfully.", {'vrf': data})
    else:
        return format_ajax_response(False, "There was an error retrieving the Vrf listing.")


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
        vrf = request.POST.getlist('vrf_id[]')
        Vrf.objects.filter(pk__in=vrf).delete()
        ActionLogger().log(request.user, "deleted", "Vrf %s" % vrf)
        return format_ajax_response(True, "Vrf record(s) deleted successfully.")
    except Exception as ex:
        ErrorLogger().log(request, "Failed", "Failed to delete Vrf(s) in apps.ip.views.delete_vrf: %s" % ex)
        return format_ajax_response(False, "There was a problem deleting the Vrf record(s).")