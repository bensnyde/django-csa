from django.conf import settings
import logging
import base64 
import httplib
import json
import socket

WHMURL = settings.CPANEL_DNS["address"]
WHMROOT = settings.CPANEL_DNS["username"]
WHMPASS = settings.CPANEL_DNS["password"]
apilogger = 'api_logger'

class Cpanel:
    def cQuery(self, query):
        """Query Cpanel 
            
            Queries WHM server's JSON API with specified query string.

        Parameters
            query: str url safe string
        Returns
            json decoded response from remote server
        """        
        try:       
            conn = httplib.HTTPSConnection(WHMURL, 2087)
            conn.request('GET', '/json-api/%s' % query, headers={'Authorization':'Basic ' + base64.b64encode(WHMROOT+':'+WHMPASS).decode('ascii')})
            response = conn.getresponse()
            data = response.read()
            conn.close()

            return json.loads(data)
        except httplib.HTTPException as ex:
            print "HTTPException from CpanelDNS API: %s" % ex
        except socket.error as ex:
            print "Socket.error connecting to CpanelDNS API: %s" % ex
        except ValueError as ex:
            print "ValueError decoding CpanelDNS API response string: %s" % ex
        except Exception as ex:
            print "Unhandled Exception while querying CpanelDNS API: %s" % ex


    def addZone(self, domain, ip, trueowner=None):
        """Add DNS Zone

            This function creates a DNS zone. All zone information other than domain 
            name and IP address is created based on the standard zone template in WHM.

        Parameters
            domain: str domain name
            ip: str ip address
            trueowner: str cpanel username
        Returns
            result: bool api result status
        """
        result = self.cQuery('adddns?domain=%s&ip=%s&trueowner=%s' % (domain, ip, trueowner))

        try:
            if result["result"][0]["status"] == 1:
                return True
        except:
            # Log me
            pass

        return False


    def addZoneRecord(self, **kwargs):
        """
        This function will add a DNS zone record to the server.

        Parameters
            zone:str - Name of the zone to be added, expressed like a domain name. (ex. example.com)
            * May or may not be required, depending on the type of record being set
            *name:str - The name of the zone record. (ex. example.com.)
            *address:str - The IP address of the zone being added. (ex. 127.0.0.1)
            *class:str - The class of the record. (typically IN, for "Internet")
            *cname:str - The canonical name in a CNAME record.
            *exchange:str - In an MX record, the name of the destination mail server.
            *nsdname:str - A domain name to use for a nameserver. Example: ns1.example.com
            *ptrdname:str - The domain to which the IP address will point.
            *priority:int - In an MX record, this parameter specifies the priority of the destination mail server. In an SRV record, this parameter specifies the overall priority for the SRV record.
            *type:str - The type of zone record being added.
            *ttl:int - The record's time to live.
            ** Required for SRV records
            **weight:int - The weight of the record, relative to records of the same priority.
            **port:int - The port number on which users can access a particular service.
            **target:str - The hostname of the machine providing a specified service.
        Returns
            result: bool api result status
        """    
        querystr =     'addzonerecord?'
        for name,val in kwargs.iteritems():
            querystr = querystr + "&%s=%s" % (name, val)

        result = self.cQuery(querystr)

        try:
            if result["result"][0]["status"] == 1:
                return True
        except Exception as ex:
            # Log me
            pass

        return False


    def editZoneRecord(self, domain, line, *args):
        """
        This function allows you to edit a DNS zone record on the server.

        Parameters
            zone:str - Name of the zone to be added, expressed like a domain name. (ex. example.com)
            Line:str - The number of the zone record line you wish to edit.
            * May or may not be required, depending on the type of record being set
            *address:str - The IP address of the zone being added. (ex. 127.0.0.1)
            *class:str - The class of the record. (typically IN, for "Internet")
            *cname:str - The canonical name in a CNAME record.
            *exchange:str - In an MX record, the name of the destination mail server.
            *preference:int - In an MX record, the priority of the destination mail server. (0 is highest priority)
            *expire:str -  A 32-bit time value that specifies the upper limit on the time interval that can elapse before the zone is no longer authoritative.
            *minimum:int - The unsigned 32-bit minimum time to live field that should be exported with any record from this zone.
            *mname:int - The domain name of the nameserver serving as the original or primary source of data for this zone. Example: ns1.example.com
            *name:str - Domain name. Example: example.com
            *nsdname:str - A domain name to use for a nameserver. Example: ns1.example.com
            *raw:str - Raw line data.
            *refresh:int - 32-bit time interval which will elapse before the zone will be refreshed.
            *retry:int - 32-bit time interval which will elapse before a failed refresh will be retried.
            *rname:str - A domain name which specifies the mailbox of the person responsible for this zone. Example: user.example.com
            *serial:int - The unsigned 32-bit version number of the original copy of the zone.
            *txtdata:str - Text record data.
            *type:str - The type of zone record being added.
            *ttl:int - The record's time to live.        
        Returns
            result: bool api result status
        """                
        querystr = 'editzonerecord?zone=%s&Line=%s' % (domain, line)
        for name,val in args:
            querystr = querystr + "&%s=%s" % (name, val)

        result = self.cQuery(querystr)

        try:
            if result["result"][0]["status"] == 1:
                return True
        except:
            pass

        return False


    def addReverseZoneRecord(self, zone, name, ptrdname):
        """Add DNS PTR Record

            The addzonerecord function allows you to add reverse DNS functionality using PTR records. 
            PTR records are used in reverse DNS lookups that convert IP addresses into domain names.

        Parameters
            zone:str - The name of the reverse DNS zone file to create. This value must follow a standardized naming schema.
            name:int - You will need to enter the last octet of the IP address here. If your IP address was 192.168.0.1, you would enter 1 in this parameter.
            ptrdname:str - The name of the domain to which the IP address will resolve (e.g. example.com).
        Returns
            result: bool api result status
        """            
        result = self.cQuery('addzonerecord?zone=%s&name=%s&ptrdname=%s&type=PTR' % (zone, name, ptrdname)) 

        try:
            if result["result"][0]["status"] == 1:
                return True
        except:
            pass

        return False


    def getZoneRecord(self, domain, line):
        """Get DNS Zone Record
        
            This function will return zone records for a domain.

        Parameters
            domain:str - The domain whose zone record you wish to view.
            line:str - The line you wish to view in the zone record.
        Returns
            record:     
                name:str - Domain name. Example: example.com
                Line:str - The number of the zone record line retrieved by the function.
                address:str - The IP address associated with the zone record.
                class:str - The class of the record. (typically IN, for "Internet")
                raw:str - Raw line data.
                ttl:int - The record's time to live.
                type:str - The DNS record type. Example: NS, SOA, A, etc.
        """                
        result = self.cQuery('getzonerecord?domain=%s&line=%s' % (domain, lineline))

        try:
            if result["result"][0]["status"] == 1:
                return result["result"][0]["record"]
        except:
            pass

        return False


    def deleteZone(self, domain):
        """Delete DNS Zone
        
            This function deletes a DNS zone.

        Parameters
            domain:str - Domain name for the zone to be deleted.
        Returns
            result: bool api result status
        """        
        result = self.cQuery('killdns?domain=%s' % domain)

        try:
            if result["result"][0]["status"] == 1:
                return True
        except:
            # Log me
            pass

        return False


    def listZones(self, cpanel_user=None):
        """List DNS zones

            This function will generate a list of all domains and corresponding DNS zones associated with your server.

        Parameters
            *cpanel_user: str cpanel account username to call from
        Returns
            zones:
                domain:str - Domain name. Example: example.com
                zonefile:str - Zone file name. Example: example.com.db
        """            
        if cpanel_user:
            query_string = 'cpanel?cpanel_jsonapi_module=DomainLookup&cpanel_jsonapi_func=getbasedomains&cpanel_xmlapi_version=2&cpanel_jsonapi_user=%s' % cpanel_user
        else:
            query_string = 'listzones'
            
        result = self.cQuery(query_string)

        try:
            if result["cpanelresult"]["event"]["result"] == 1:
                return result["cpanelresult"]["data"]
        except Exception as ex:
            # Log exception
            pass

        return False  


    def listZone(self, domain):
        """Get DNS Zone

            This function displays the DNS zone configuration for a specific domain.

        Parameters
            domain:str - Domain for which to show the DNS zone. Example: example.com
        Returns
            record:
                name:str - Domain name. Example: example.com
                Line:str - Line number in the zone file.
                Lines:int - Number of lines. (only appears if more than 1 line)
                address:str - IP address. Example: 127.0.0.1
                class:str - The class of the record. (typically IN for "Internet")
                exchange:str - In an MX record, the name of the destination mail server. 
                preference:int - In an MX record, the priority of the destination mail server. (0 is highest priority)
                expire:str - A 32-bit time value that specifies the upper limit on the time interval that can elapse before the zone is no longer authoritative.
                minimum:int - The unsigned 32-bit minimum TTL field that should be exported with any record from this zone.
                mname:str - The domain name of the name server that was the original or primary source of data for this zone. Example: ns1.example.com
                nsdname:str - A domain name which specifies a host which should be authoritative for the specified class and domain. Example: ns1.example.com
                cname:str - The "canonical" domain name for which the specified domain is an alias. Example: example.com
                raw:str - Raw line output.
                referesh:int - A 32-bit time interval before the zone should be refreshed.
                retry:int - A 32-bit time interval that should elapse before a failed refresh should be retried.
                rname:str - A domain name which specifies the mailbox of the person responsible for this zone. Example: user.example.com (user.example.com instead of user@example.com)
                serial:int - The unsigned 32-bit version number of the original copy of the zone.
                ttl:int - The record's time to live.
                type:str - The DNS record type. Example: NS, SOA, A, etc.
                txtdata:str - Text record data.
        """                    
        result = self.cQuery('dumpzone?domain=%s' % domain)

        try:
            if result["result"][0]["status"] == 1:
                return result["result"][0]["record"]
        except Exception as ex:
            # Log exception
            pass

        return False


    def getNameserverIP(self, nameserver):
        """Get Nameserver IP

            This function obtains the IP address of a registered nameserver from the root nameservers.

        Parameters
            nameserver:str - Hostname of the nameserver whose IP address you want to obtain. Example: ns1.example.com
        Returns
            ip: str ip address
        """                    
        result = self.cQuery('lookupnsip?nameserver=%s' % nameserver)

        try:
            if result["result"][0]["status"] == 1:
                return result[0]["ip"]
        except:
            pass

        return False


    def deleteZoneRecord(self, zone, line):
        """Delete DNS Zone Record

            This function allows you to remove a DNS zone record from the server.

        Parameters
            zone:str - The domain name whose zone record you wish to remove.
            line:str - The line number of the zone record you wish to remove.
        Returns
            result: bool api result status
        """            
        result = self.cQuery('removezonerecord?zone=%s&line=%s' % (zone, line))

        try:
            if result["result"][0]["status"] == 1:
                return True
        except Exception as ex:
            pass

        return False     


    def resetZone(self, domain=None, zone=None, user=None):
        """Reset Zone 

            You can use this function to restore a DNS zone to its default values. This includes 
            any subdomain DNS records associated with the domain.

        Parameters
            domain:str - The domain name whose zone should be reset.
            zone:str - The DNS zone's filename.
            *user:str - The user who owns the domain name whose zone should be reset.
            **Only one of domain/zone is required.
        Returns
            result: bool api result status
        """                
        if not domain and not zone:
            return False

        query = 'resetzone?'
        if domain:
            query = query + 'domain=' + domain + '&'
        if zone:
            query = query + 'zone=' + zone + '&'
        if user:
            query = query + 'user=' + user

        result = self.cQuery(query)

        try:
            if result["result"][0]["status"] == 1:
                return True
        except:
            pass

        return False


    def listZoneMXRecords(self, domain):
        """Get DNS MX Records

            This function will list a specified domain's MX records.

        Parameters
            domain:str - The domain corresponding to the MX records that you wish to view.
        Returns
            record:
                line:int - The line number of the MX record, from within the zone file.
                ttl:str - The record's time to live.
                class:str - The class of the record.
                exchange:str - The exchanger to which the domain will point. (e.g. example.com)
                preference:int - The MX record's preference value.
                type:str - The type of record you are viewing.
                name:str - The name of the record.
        """        
        result = self.cQuery('listmxs?api.version=1&domain=%s' % domain)

        try:
            if result["result"][0]["status"] == 1:
                return result["result"][0]["record"]
        except:
            pass

        return False    


    def addZoneMXRecord(self, domain, name, exchange, preference, aclass=None, serialnum=None, ttl=None):
        """Add DNS MX Record
        
            This function will add an MX record.

        Parameters
            domain:str - The domain corresponding to the MX records that you wish to view.
            name:str - The name of the new MX record.
            exchange:str - The exchanger to which the domain will point. (e.g., example.com)
            preference:int - The new MX entry's preference. Lower values indicate a higher preference.
            *class:str - The MX record's class.
            *serialnum:int - The serial number of the MX record.
            *ttl:int - The new record's time to live.

        Returns
            result: bool api result status
        """                
        result = self.Cquery('savemxs?api.version=1&domain=%s&name=%s&exchange=%s&preference%s' % (domain, name, exchange, preference))

        try:
            if result["result"][0]["metadata"]["result"] == 1:
                return True
        except:
            pass

        return False