*****
Django-CSA
*****

Client Services Automation software based on the popular Django Python web-framework. 


Overview
=======

Are you a service provider with disparate offerings? Do you want to provide your clients with a single interface regardless of their subscriptions? Django-CSA is the tool for you!

Django-CSA syndicates systems with REST/SOAP into a single, secure, web application. Your clients can browse your knowledgebase, open a support request, manage their DNS records, even spin up their virtual machines, all from a single site. 
OSS Django-CSA empowers your clients and frees your staff. 


Installation
=======

1. yum install python-pip
2. pip install virtualenv
3. cd /path/to/webspace
4. virtualenv djangocsa
5. source djangocsa/bin/activate
6. git clone https://github.com/bensnyde/djangocsa
7. pip install -r djangocsa/requirements.txt


Configuration
=======

1. Modify absolute path values in settings/default.py
2. Setup database and define access credentials in settings/database.py
3. Define remote systems access credentials in settings/private.py


Support Features
=======

1. Announcements
2. Knowledgebase
3. Ticketing system


Bundled Services
=======

1. OpenSRS - Domain Name Registration

	- Query for domain availability
	- Suggest similar domain names
	- Check domain's transfer status
	- Query for domain's reseller price
	- Query for reseller's account balance
	- Register domain

2. Zenoss - Network Monitoring System

	- Query for interface details
	- Query for interface events
	- Fetch renedered interface graph images

3. Vmware - Virtualization Hypervisor

	- Query for virtual server's statistics
	- Boot virtual server
	- Reboot virtual server
	- Shutdown virtual server
	- Query datastore for available ISO images
	- Mount ISO image to virtual server	
	- Query for virtual server's snapshots
	- Delete virtual server's snapshot
	- Revert virtual server to snapshot
	- Create virtual server snapshot

4. SolusVM - Virtual Server Control Panel

	- Query for virtual server's statistics/state
	- Query for virtual server's VNC information
	- Boot virtual server
	- Reboot virtual server
	- Shutdown virtual server
	- Query for available ISO images	
	- Mount ISO image to virtual server
	- Set virtual server's bootorder
	- Set virtual server's hostname

5. WHM/Cpanel - Hosting Control Panel

	- DNS 

		- Query for DNS zones
		- Create DNS zone
		- Delete DNS zone
		- Query for DNS zone's records
		- Create DNS zone record
		- Delete DNS zone record

	- Email

		- Query for POP accounts
		- Create POP account
		- Change POP account's password
		- Change POP account's quota
		- Delete POP account		
		- Query for email forwards
		- Create email forward
		- Create domain forward
		- 

	- FTP

		- Query for FTP accounts
		- Create FTP account
		- Change FTP account's password
		- Change FTP account's quota
		- Delete FTP account		
		- Query for open FTP sessions		