Django Web Framework
======

https://www.djangoproject.com/

*From the front page:*

    ```
    Django is a high-level Python Web framework that encourages rapid development and clean, pragmatic design. Built by experienced developers, it takes care of much of the hassle of Web development, so you can focus on writing your app without needing to reinvent the wheel. It’s free and open source.

    Ridiculously fast.

        - Django was designed to help developers take applications from concept to completion as quickly as possible.

    Reassuringly secure.

        - Django takes security seriously and helps developers avoid many common security mistakes.

    Exceedingly scalable.

        - Some of the busiest sites on the Web leverage Django’s ability to quickly and flexibly scale.
    ```


### DOCUMENTATION

https://docs.djangoprojcet.com/en/1.7/

Django is extremely popular so you'll find great documenation and a great community. Chances are someone has already posted your question to stackoverflow or the likes.

    - https://docs.djangoproject.com/en/1.7/intro/overview/

        A quick run through the official tutorial will be invalulable for your understanding! It will take but a few hours and you will fully understand how powerful Django is.

    - irc://irc.freenode.net/django

        Get immediate answers to questions from django developers/contributers/powerusers from their IRC channel.


### DESIGN

http://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93controller

Django Web Framework is based on the Model/View/Controller design pattern.


http://en.wikipedia.org/wiki/Django_(web_framework)

*From the article:*

	```
	Despite having its own nomenclature, such as naming the callable objects generating the response "views",[5] the core Django framework can be seen as MVC.[6] It consists of an object-relational mapper which mediates between data models (defined as Python classes) and a relational database ("Model"); a system for processing requests with a web templating system ("View") and a regular-expression-based URL dispatcher ("Controller").
	```

http://en.wikipedia.org/wiki/Object-relational_mapping

Django has a world famous ORM implementation that maps Models to backend resources (databases).

    - protects against resource attacks (ex. SQL injection)
    - encourages for efficient schemas/reads/writes
    - provides a Python object representation of the data that can be used to automatically generate/validate html forms, build web API's, etc... (see plugins below)


### Plugins

The following plugins are being used to automate functionality within the site. Most plugins can be added/removed/swapped out with very little effort.

    - Authentication

        https://docs.djangoproject.com/en/1.7/topics/auth/

        Django has a pluggable backend authentication system which allows you to switch to any backend system (oauth, active directory/ldap, etc)

            - securely and safely handles password hashing

    - Permissions

        https://docs.djangoproject.com/en/1.7/topics/auth/default/#permissions-and-authorization

            - granular user/group permissions to all registered Models

                *ex. allow Staff to Create an object or modify an object they themself authored, and allow Management to Create/Modify/Delete any object*

    - Signaling

        https://docs.djangoproject.com/en/1.7/topics/signals/

            Django's very powerful, built-in signaling system allows for decoupled appliction modules to communicate with one another.

                *ex. create a new account in the dns system (dns module) whenever a new company (company module) is defined*

    - Search

        django-watson

        https://github.com/etianen/django-watson

            - automated search!
            - any model registered with watson will have its textfield/charfield values automatically appended to a fast-lookup, FULLTEXT table
            - Watson can very quickly return any Model objects that match specified keywords

            to rebuild the FULLTEXT table run:

            # python manage.py buildwatson

                - you should only need to run this once whenever a new table is created in the database

    - Object Revision Control

        django-simple-history

        https://github.com/treyhunner/django-simple-history

            - any registered Model has its database tables duplicated, and then every state of the object is recorded in the duplicated copy
            - allows for audit trails and restoration of previous states

    - Action Logging

        django-activity-stream

        https://github.com/justquick/django-activity-stream

            - automated logging of all actions performed on the site

                *ex. John Doe (Contact) created TT3058258 (Ticket) on 1/6/2015 08:00:00.*

    - RESTful API

        django-rest-framework

            https://github.com/tomchristie/django-rest-framework

                - creates secure, REST api from any registered Model
                - automated sorting, filtering, pagination
