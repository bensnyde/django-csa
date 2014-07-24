# coding: utf-8
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
    def __init__(self, scriptuser):
            """Cpanel Email library public constructor.

            :param scriptuser: WHM account to run scripts as
            """        
            self.user = scriptuser

    def cQuery(self, script, **kwargs):
            """Queries specified WHM server's JSON API with specified query string.

            :param script: Cpanel script name
            :param user: Cpanel username underwhich to call from
            :param kwargs: Dictionary parameter pairs
            :returns: json decoded response from server
            """
            query = '/json-api/cpanel?cpanel_jsonapi_user=%s&cpanel_jsonapi_module=Email&cpanel_jsonapi_func=%s&cpanel_xmlapi_version=2&' % (self.user, script)

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


    def addpop(self, domain, email, password, quota):
        """Adds a new email account.
        http://docs.cpanel.net/twiki/bin/view/ApiDocs/Api2/ApiEmail#=Email::addpop=

        :param domain: The domain for the new email account
        :param email: The username for the new email account
        :param password: The password for the new email account
        :param quota: A positive integer that defines the disk quota for the email account (0 is unlimited)
        :returns: bool api call result
        """
        result = self.cQuery('addpop', **{
                'domain': domain,
                'email': email,
                'password': password,
                'quota': quota
            })

        try:
            if result["cpanelresult"]["data"][0]["result"] == 1:
                return True
        except:
            pass

        return False


    def delpop(self, domain, email):
        """Deletes an email account.
        http://docs.cpanel.net/twiki/bin/view/ApiDocs/Api2/ApiEmail#=Email::delpop=

        :param domain: The domain for the email account you wish to remove
        :param email: The username for the email address you wish to remove
        :returns: bool api call result      
        """
        result = self.cQuery('delpop', **{
            'domain': domain,
            'email': email
        })

        try:
            if result["cpanelresult"]["data"][0]["result"] == 1:
                return True
        except:
            pass

        return False


    def editquota(self, domain, email, quota):
        """Modifies an email account's quota.
        http://docs.cpanel.net/twiki/bin/view/ApiDocs/Api2/ApiEmail#=Email::editquota=

        :param domain: The domain for the email account you wish to modify
        :param email: The username for the email address you wish to modify
        :param quota: A positive integer that indicates the desired disk quota value in megabytes (0 is unlimited)
        :returns: bool api call result     
        """
        result = self.cQuery('editquota', **{
            'domain': domain,
            'email': email,
            'quota': quota
        })

        try:
            return result
            if result["cpanelresult"]["data"][0]["result"] == 1:
                return True
        except:
            pass

        return False              

    def passwdpop(self, domain, email, password):
        """Changes an email account's password.
        http://docs.cpanel.net/twiki/bin/view/ApiDocs/Api2/ApiEmail#=Email::passwdpop=

        :param domain: The domain for the email address for which you wish to change the password
        :param email: The username for the email address for which you wish to change the password
        :param password: The desired password for the account
        :returns: bool api call result         
        """
        result = self.cQuery('passwdpop', **{
            'domain': domain,
            'email': email,
            'password': password,    
        })

        try:
            if result["cpanelresult"]["data"][0]["result"] == 1:
                return True
        except:
            pass

        return False   


    def clearpopcache(self, username):
        """Rebuilds an email address's cache file.
        http://docs.cpanel.net/twiki/bin/view/ApiDocs/Api2/ApiEmail#=Email::clearpopcache=
        
        :param username: The username for the email account for which you wish to rebuild the cache file
        :returns: bool api call result 
        """
        result = self.cQuery('clearpopcache', **{'username': username} )
        try:
            if result["cpanelresult"]["data"][0]["result"] == 1:
                return True
        except:
            pass

        return False   


    def listpops(self, regex=None):
        """Retrieves a list of email accounts associated with your cPanel account.
        http://docs.cpanel.net/twiki/bin/view/ApiDocs/Api2/ApiEmail#=Email::listpops=

        :param regex: The regular expression by which you wish to filter the results
        :returns: json formatted string        
        """
        data = {}
        if regex:
            data['regex'] = regex    
        
        result = self.cQuery('listpops', **data)

        try:
            if result["cpanelresult"]["event"]["result"] == 1:
                return result["cpanelresult"]["data"]
        except:
            pass

        return False                   


    def listpopssingles(self, regex=None):
        """Retrieves a list of email accounts and logins associated with your cPanel account.
        http://docs.cpanel.net/twiki/bin/view/ApiDocs/Api2/ApiEmail#=Email::listpopssingles=

        :param regex: The regular expression by which you wish to filter the results
        :returns: json formatted string        
        """
        data = {}
        if regex:
            data['regex'] = regex

        result = self.cQuery('listpopssingles', **data)

        try:
            if result["cpanelresult"]["data"][0]["result"] == 1:
                return result["cpanelresult"]["data"]
        except:
            pass

        return False                   


    def listpopswithdisk(self, domain=None, nearquotaonly=False, no_validate=False, regex=None):
        """Lists email accounts, including disk usage, that correspond to a particular domain. 
        http://docs.cpanel.net/twiki/bin/view/ApiDocs/Api2/ApiEmail#=Email::listpopswithdisk=
        
        :param domain: The domain for which you wish to view email accounts
        :param nearquotaonly: If you pass 1 to this parameter, you will only view accounts that use 95% or more of their allotted disk space
        :param no_validate: If you pass 1 to this parameter, the function only reads data from your .cpanel/email_accounts.yaml file. 
        :param regex: The regular expression by which you wish to filter the results
        :returns: json formatted string        
        """
        data = {
            'nearquotaonly': nearquotaonly,
            'no_validate': no_validate
        }

        if domain:
            data['domain'] = domain
        if regex:
            data['regex'] = regex

        result = self.cQuery('listpopswithdisk', **data)
        try:
            if result["cpanelresult"]["data"][0]["result"] == 1:
                return result["cpanelresult"]["data"]
        except:
            pass

        return False                   


    def accountname(self, account, display):
        """Displays the account name or All Mail On Your Account.
        http://docs.cpanel.net/twiki/bin/view/ApiDocs/Api2/ApiEmail#=Email::accountname=
        
        :param account: Specifies the account name or email address. The function will return whichever of these values you do not specify.
        :param display: If present, and you do not specify an account, the function will return the string All Mail On Your Account.
        :returns: json formatted string        
        """
        result = self.cQuery('accountname', **{
            'account': account,
            'display': display
        })

        try:
            if result["cpanelresult"]["data"][0]["result"] == 1:
                return result["cpanelresult"]["data"]
        except:
            pass

        return False   


    def getdiskusage(self, domain, user):
        """Retrieves information about a specified email account's disk usage.
        http://docs.cpanel.net/twiki/bin/view/ApiDocs/Api2/ApiEmail#=Email::getdiskusage=

        :param domain: The domain that corresponds to the email address for which you wish to view disk usage
        :param user: The username of the email address for which you wish to view disk usage
        :returns: json formatted string        
        """
        result = self.cQuery('getdiskusage', **{
            'domain': domain,
            'user': user
        })

        try:
            if result["cpanelresult"]["data"][0]["result"] == 1:
                return result["cpanelresult"]["data"]
        except:
            pass

        return False


    def listmaildomains(self, skipmain=True):
        """Retrieves a list of the domains associated with your account that send and receive email.
        http://docs.cpanel.net/twiki/bin/view/ApiDocs/Api2/ApiEmail#=Email::listmaildomains=
        
        :param skipmain: Pass 1 to this variable to skip the main domain
        :returns: json formatted string        
        """
        result = self.cQuery('listmaildomains', **{'skipmain': skipmain})
        try:
            if result["cpanelresult"]["data"][0]["result"] == 1:
                return result["cpanelresult"]["data"]
        except:
            pass

        return False                   


    def listlists(self, domain=None, regex=None):
        """Lists mailing lists associated with a domain.
        http://docs.cpanel.net/twiki/bin/view/ApiDocs/Api2/ApiEmail#=Email::listlists=
        
        :param domain: The domain for which you wish to view a list of mailing lists
        :param regex: The regular expression by which you wish to filter the results
        :returns: json formatted string    
        """
        data = {}
        if domain:
            data['domain'] = domain
        if regex:
            data['regex'] = regex

        result = self.cQuery('listlists', **data)

        try:
            if result["cpanelresult"]["data"][0]["result"] == 1:
                return result["cpanelresult"]["data"]
        except:
            pass

        return False   


    def setdefaultaddress(self, fwdopt, domain, failmsgs=None, fwdemail=None, pipefwd=None):
        """Configure a default (catchall) email address.
        http://docs.cpanel.net/twiki/bin/view/ApiDocs/Api2/ApiEmail#=Email::setdefaultaddress=

        :param fwdopt: This parameter defines how unroutable mail will be handled.
        :param domain: Specifies the domain to which you wish to apply the rule.
        :param failmsgs: Specifies the failure message that you wish to send if an incoming message bounces. 
        :param fwdemail: Specifies the email address to which mail received by the default address is forwarded. 
        :param pipefwd: Specifies the program to which messages received by the default address are piped
        :returns: bool api call result     
        """
        data = {
            'fwdopt': fwdopt,
            'domain': domain
        }

        if failmsgs:
            data['failmsgs'] = failmsgs
        if fwdemail:
            data['fwdemail'] = fwdemail
        if pipefwd:
            data['pipefwd'] = pipefwd

        result = self.cQuery('setdefaultaddress', **data)

        try:
            if result["cpanelresult"]["data"][0]["result"] == 1:
                return True
        except:
            pass

        return False  


    def checkmaindiscard(self):
        """Checks how the main email account for a domain handles undeliverable mail.
        http://docs.cpanel.net/twiki/bin/view/ApiDocs/Api2/ApiEmail#=Email::checkmaindiscard=

        :returns: json formatted string                
        """
        result = self.cQuery('checkmaindiscard', **{})

        try:
            if result["cpanelresult"]["data"][0]["result"] == 1:
                return result["cpanelresult"]["data"]
        except:
            pass

        return False   


    def listdefaultaddresses(self, domain):
        """Retrieves the default address and the action taken when the default address receives unroutable messages.
        http://docs.cpanel.net/twiki/bin/view/ApiDocs/Api2/ApiEmail#=Email::listdefaultaddresses=
        
        :param domain: The domain that corresponds to the default address and information you wish to view
        :returns: json formatted string                
        """
        result = self.cQuery('listdefaultaddresses', **{'domain': domain})

        try:
            if result["cpanelresult"]["data"][0]["result"] == 1:
                return result["cpanelresult"]["data"]
        except:
            pass

        return False   


    def listaliasbackups(self):
        """Retrieves a list of domains that use aliases and custom catch-all addresses.
        http://docs.cpanel.net/twiki/bin/view/ApiDocs/Api2/ApiEmail#=Email::listaliasbackups=
        
        :returns: json formatted string        
        """
        result = self.cQuery('listaliasbackups', **{})

        try:
            if result["cpanelresult"]["data"][0]["result"] == 1:
                return result["cpanelresult"]["data"]
        except:
            pass

        return False   

    def addforward(self, domain, email, fwdopt, fwdemail=None, fwdsystem=None, failmsgs=None, pipefwd=None):
        """Creates an email forwarder for the specified address.
        http://docs.cpanel.net/twiki/bin/view/ApiDocs/Api2/ApiEmail#=Email::addforward=

        :param domain: The domain for which you wish to add a forwarder
        :param email: The username of the email address for which you wish to add a forwarder
        :param fwdopt: This parameter defines how unroutable mail will be handled. 
        :param fwdemail: The email address to which you wish to forward mail. Use this parameter when fwdopt=fwd.
        :param fwdsystem: The system account to which you wish to forward email. Use this parameter when fwdopt=system.
        :param failmsgs: Use this parameter to define the correct failure message. Use this parameter when fwdopt=fail.
        :param pipefwd: The path to the program to which you wish to pipe email. Use this parameter when fwdopt=pipe.
        :returns: bool api call result              
        """
        data = {
            'email': email,
            'fwdopt': fwdopt,
        }

        if fwdemail:
            data['fwdemail'] = fwdemail
        if fwdsystem:
            data['fwdsystem'] = fwdsystem
        if failmsgs:
            data['failmsgs'] = failmsgs
        if pipefwd:
            data['pipefwd'] = pipefwd

        result = self.cQuery('addforward', **data)

        try:
            if result["cpanelresult"]["data"][0]["result"] == 1:
                return True
        except:
            pass

        return False   


    def listforwards(self, domain=None, regex=None):
        """List forwarders associated with a specific domain.
        http://docs.cpanel.net/twiki/bin/view/ApiDocs/Api2/ApiEmail#=Email::listforwards=

        :param domain: The domain name for which you wish to review forwarders
        :param regex: The regular expression by which you wish to filter the results
        :returns: json formatted string                
        """
        data = {}
        if domain:
            data['domain'] = domain
        if regex:
            data['regex'] = regex

        result = self.cQuery('listforwards', **data)

        try:
            if result["cpanelresult"]["event"]["result"] == 1:
                return result["cpanelresult"]["data"]
        except:
            pass

        return False   

    def listdomainforwards(self, domain):
        """Retrieves the destination to which a domain forwarder forwards email.
        http://docs.cpanel.net/twiki/bin/view/ApiDocs/Api2/ApiEmail#=Email::listdomainforwards=

        :param domain: The domain that corresponds to the forwarder for which you wish to view the destination
        :returns: json formatted string                
        """
        result = self.cQuery('listdomainforwards', **{'domain': domain})
        try:
            if result["cpanelresult"]["data"][0]["result"] == 1:
                return result["cpanelresult"]["data"]
        except:
            pass

        return False   


    def storefilter(self, account, action, filtername, match, part, val, opt="or", dest=None, oldfiltername=None):
        """Creates a new email filter.
        http://docs.cpanel.net/twiki/bin/view/ApiDocs/Api2/ApiEmail#=Email::storefilter=

        :param account: To configure a user-level filter, enter the email address to which you wish to apply the rule. 
        :param action: Specifies the action that the filter takes. 
        :param filtername: Specifies the name you wish to give to the new filter
        :param match:  Specifies the new filter match type. 
        :param part: The section of the email to which you wish to apply the match parameter. 
        :param val: Specifies the value against which you wish to match. 
        :param opt: This parameter connects conditionals. 
        :param oldfiltername: This function can also be used to rename an existing filter. 
        :param dest: Specifies the destination of mail that the filter receives, if one is required. 
        :returns: json formatted string                
        """
        data = {
            'account': account,
            'action': action,
            'filtername': filtername,
            'match': match,
            'opt': opt,
            'part': part,
            'val': val
        }

        if dest:
            data['dest'] = dest
        if oldfiltername:
            data['oldfiltername'] = oldfiltername

        result = self.cQuery('storefilter', **data)

        try:
            if result["cpanelresult"]["data"][0]["result"] == 1:
                return result["cpanelresult"]["data"]
        except:
            pass

        return False   


    def deletefilter(self, filtername, account=None):
        """Deletes an email filter.
        http://docs.cpanel.net/twiki/bin/view/ApiDocs/Api2/ApiEmail#=Email::deletefilter=
        
        :param filtername: Specifies the name of the filter you wish to delete.
        :param account: Specifies an email address or account username that corresponds to the user-level filter you wish to remove. 
        :returns: bool api call result           
        """
        data = {'filtername': filtername}
        if account:
            data['account'] = account

        result = self.cQuery('deletefilter', **data)

        try:
            if result["cpanelresult"]["data"][0]["result"] == 1:
                return True
        except:
            pass

        return False   


    def tracefilter(self, msg, account=None):
        """Tests the action of account-level mail filters.
        http://docs.cpanel.net/twiki/bin/view/ApiDocs/Api2/ApiEmail#=Email::tracefilter=
        
        :param msg: The contents of the body of the message you wish to test.
        :param account: This parameter allows you to specify and test old-style cPanel filters in the $home/filters directory.
        :returns: json formatted string        
        """
        data = {'msg': msg}
        if account:
            data['account'] = account

        result = self.cQuery('tracefilter', **data)

        try:
            if result["cpanelresult"]["data"][0]["result"] == 1:
                return result["cpanelresult"]["data"]
        except:
            pass

        return False   


    def filterlist(self, account=None):
        """Retrieves a list of email filters.
        http://docs.cpanel.net/twiki/bin/view/ApiDocs/Api2/ApiEmail#=Email::filterlist=
        
        :param account: Specifies the email address or account username. 
        :returns: json formatted string            
        """
        data = {}
        if account:
            data['account'] = account

        result = self.cQuery('filterlist', **data)

        try:
            if result["cpanelresult"]["data"][0]["result"] == 1:
                return result["cpanelresult"]["data"]
        except:
            pass

        return False 


    def loadfilter(self, filtername, account=None):
        """Retrieves the rules and actions associated with an email filter.
        http://docs.cpanel.net/twiki/bin/view/ApiDocs/Api2/ApiEmail#=Email::loadfilter=
        
        :param filtername: Specifies the name of the filter you wish to review.
        :param account: Specifies the email address or account username. 
        :returns: json formatted string        
        """
        data = {'filtername': filtername}
        if account:
            data['account'] = account     

        result = self.cQuery('loadfilter', **data)

        try:
            if result["cpanelresult"]["data"][0]["result"] == 1:
                return result["cpanelresult"]["data"]
        except:
            pass

        return False 


    def filtername(self, account=None, filtername=None):
        """Counts the number of email filters and returns a default suggested rule name in a Rule [1 + count] format.
        http://docs.cpanel.net/twiki/bin/view/ApiDocs/Api2/ApiEmail#=Email::filtername=

        :param account: Specifies the email address associated with the account for which you wish to return a result. 
        :param filtername: Specifies a fallback in the case that the function cannot find any relevant filter files. 
        :returns: json formatted string            
        """
        data = {}
        if account:
            data['account'] = account
        if filtername:
            data['filtername'] = filtername    

        result = self.cQuery('filtername', **data)

        try:
            if result["cpanelresult"]["data"][0]["result"] == 1:
                return result["cpanelresult"]["data"]
        except:
            pass

        return False   


    def listfilterbackups(self):
        """Retrieves a list of domains that use domain-level filters.
        http://docs.cpanel.net/twiki/bin/view/ApiDocs/Api2/ApiEmail#=Email::listfilterbackups=

        :returns: json formatted string                
        """
        result = self.cQuery('listfilterbackups', **{})

        try:
            if result["cpanelresult"]["data"][0]["result"] == 1:
                return result["cpanelresult"]["data"]
        except:
            pass

        return False      


    def listfilters(self):
        """Lists all of the old-style email filters in your .filter file.
        http://docs.cpanel.net/twiki/bin/view/ApiDocs/Api2/ApiEmail#=Email::listfilters=

        :returns: json formatted string                
        """
        result = self.cQuery('listfilters', **{})

        try:
            if result["cpanelresult"]["data"][0]["result"] == 1:
                return result["cpanelresult"]["data"]
        except:
            pass

        return False


    def listautoresponders(self, domain=None, regex=None):
        """Retrieves a list of auto responders associated with the specified domain.
        http://docs.cpanel.net/twiki/bin/view/ApiDocs/Api2/ApiEmail#=Email::listautoresponders=

        :param domain: The domain for which you wish to view auto responders
        :param regex: Regular expressions allow you to filter results based on a set of criteria
        :returns: json formatted string                
        """
        data = {}
        if domain:
            data['domain'] = domain
        if regex:
            data['regex'] = regex

        result = self.cQuery('listautoresponders', **data)

        try:
            if result["cpanelresult"]["data"][0]["result"] == 1:
                return result["cpanelresult"]["data"]
        except:
            pass

        return False   


    def fetchautoresponder(self, email):
        """Retrieves information about an auto responder that corresponds to a specified email address.
        http://docs.cpanel.net/twiki/bin/view/ApiDocs/Api2/ApiEmail#=Email::fetchautoresponder=

        :param email: The email address that corresponds to the auto responder you wish to review
        :returns: json formatted string            
        """
        result = self.cQuery('fetchautoresponder', **{'email': email})

        try:
            if result["cpanelresult"]["event"]["result"] == 1:
                return result["cpanelresult"]["data"]
        except:
            pass

        return False   


    def set_archiving_configuration(self, domain, dtype):
        """Sets the email archiving configuration for the specified domain.
        http://docs.cpanel.net/twiki/bin/view/ApiDocs/Api2/ApiEmail#=Email::set_archiving_configuration=

        :param domains: A comma separated list of domains for which you wish to change the configuration
        :param type: An integer, or empty-string, value that indicates the length of time to keep mail archives of the given type. 
        :returns: json formatted string            
        """
        result = self.cQuery('set_archiving_configuration', **{
            'domain': domain,
            'type': dtype
        })

        try:
            if result["cpanelresult"]["data"][0]["result"] == 1:
                return result["cpanelresult"]["data"]
        except:
            pass

        return False   


    def set_archiving_default_configuration(self, dtype):
        """Sets the default email archiving configuration for any new domains created under the user account.
        http://docs.cpanel.net/twiki/bin/view/ApiDocs/Api2/ApiEmail#=Email::set_archiving_default_configuration=
        
        :param type: An integer, or empty-string, value that indicates the length of time to keep mail archives of the given type. 
        :returns: json formatted string                 
        """
        result = self.cQuery('set_archiving_default_configuration', **{'type': dtype})

        try:
            if result["cpanelresult"]["data"][0]["result"] == 1:
                return result["cpanelresult"]["data"]
        except:
            pass

        return False   


    def get_archiving_configuration(self, domain=None, regex=None):
        """Lists the email archiving configuration for the specified domain. 
        http://docs.cpanel.net/twiki/bin/view/ApiDocs/Api2/ApiEmail#=Email::get_archiving_configuration=
    
        :param domain: The domain name for which you wish to view email archiving configuration information
        :param regex: A case-sensitive regular expression used to filter by domain
        :returns: json formatted string            
        """
        data = {}
        if domain:
            data['domain'] = domain
        if regex:
            data['regex'] = regex

        result = self.cQuery('get_archiving_configuration', **data)

        try:
            if result["cpanelresult"]["data"][0]["result"] == 1:
                return result["cpanelresult"]["data"]
        except:
            pass

        return False   


    def get_archiving_default_configuration(self, domain):
        """Lists the default email archiving configuration for the specified domain.
        http://docs.cpanel.net/twiki/bin/view/ApiDocs/Api2/ApiEmail#=Email::get_archiving_default_configuration=

        :param domain: The domain for which you wish to view the default configuration
        :returns: json formatted string         
        """
        result = self.cQuery('get_archiving_default_configuration', **{'domain': domain})

        try:
            if result["cpanelresult"]["data"][0]["result"] == 1:
                return result["cpanelresult"]["data"]
        except:
            pass

        return False


    def get_archiving_types(self):
        """Displays the different types of email archiving that are available.
        http://docs.cpanel.net/twiki/bin/view/ApiDocs/Api2/ApiEmail#=Email::get_archiving_types=

        :returns: json formatted string            
        """
        result = self.cQuery('get_archiving_types', **{})

        try:
            if result["cpanelresult"]["data"][0]["result"] == 1:
                return result["cpanelresult"]["data"]
        except:
            pass

        return False  


    def getabsbrowsedir(self, account, adir="mail"):
        """Retrieves the full path to a specified mail folder.
        http://docs.cpanel.net/twiki/bin/view/ApiDocs/Api2/ApiEmail#=Email::getabsbrowsedir=

        :param account: The email address that corresponds to the directory for which you wish to find the path
        :param dir: The mail folder that you wish to query for its full path
        :returns: json formatted string                
        """
        result = self.cQuery('getabsbrowsedir', **{
            'account': account,
            'dir': adir
        })

        try:
            if result["cpanelresult"]["data"][0]["result"] == 1:
                return result["cpanelresult"]["data"]
        except:
            pass

        return False              


    def browseboxes(self, account=None, adir="default", showdotfiles=False):
        """Retrieves a list of mail-related subdirectories (boxes) in your mail directory.
        http://docs.cpanel.net/twiki/bin/view/ApiDocs/Api2/ApiEmail#=Email::browseboxes=
        
        :param account: The name of the email account you wish to review
        :param dir:str = This parameter allows you to specify which mail directories will be displayed. 
        :param showdotfiles: A boolean variable that allows you to specify whether you wish to view hidden directories and files
        :returns: json formatted string            
        """
        data = {
            'dir': adir,
            'showdotfiles': showdotfiles
        }
        if account:
            data['account'] = account

        result = self.cQuery('browseboxes', **data)

        try:
            if result["cpanelresult"]["data"][0]["result"] == 1:
                return result["cpanelresult"]["data"]
        except:
            pass

        return False