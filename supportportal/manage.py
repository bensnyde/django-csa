#!/opt/env1/bin/python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.default")
    #sys.path.append('/opt/django-csa/supportportal/apps') 
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
