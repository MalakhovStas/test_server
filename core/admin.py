from django.conf import settings
from django.contrib.admin import AdminSite

AdminSite.site_header = settings.PYPROJECT['tool']['poetry']['name']
