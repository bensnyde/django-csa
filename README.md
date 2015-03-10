*****
Django-CSA
*****

Client Services Automation software based on the popular Django Python web-framework. 

Demo
=======
- url: http://hidden-savannah-2760.herokuapp.com/
- default admin user: root@example.com
- default password: password


Overview
=======

Are you a service provider with disparate offerings? Do you want to provide your clients with a single interface regardless of their subscriptions? Django-CSA is the tool for you!

Django-CSA syndicates systems with REST/SOAP into a single, secure, web application. Your clients can browse your knowledgebase, open a support request, manage their DNS records, even spin up their virtual machines, all from a single site. 
OSS Django-CSA empowers your clients and frees your staff. 


Features
======

1. REST API backend
2. Bootstrap themed frontend
3. Extremely modular and extendable


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


Database Migration
=======

1. python manage.py migrate
2. python manage.py installwatson
3. python manage.py buildwatson
4. python manage.py shell

```
from django.contrib.auth.models import Group, Permission

group = Group.objects.get(name="Management")
permissions = Permission.objects.all()
group.permissions.add(*permissions)
group.save()
```

Static Files
======

Unfortunately I can't include the template styles/images/plugins that I'm using due to licensing concerns. This will cause some STATIC URL errors upon startup. You can either rip the {% static %} tags out or update the links to your own template's files.


Start It Up!
=======

For production you'll want to use an actual web server like Apache with mod_wsgi, but for development:

```
# python manage.py runserver <ip address>:<port>
```

Login
=======

Default Admin: root@example.com
Default Password: password


Support Features
=======

1. Announcements
2. Knowledgebase
3. Ticketing system
