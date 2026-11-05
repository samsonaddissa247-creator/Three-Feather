"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.1/howto/deployment/wsgi/
"""

import os

from django.core.management import call_command
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# On serverless hosts (like Vercel) the filesystem can be reset between invocations,
# so the database file and tables may not exist yet when the app starts.
# Ensure the schema exists before serving requests.
import django

django.setup()
call_command('migrate', interactive=False, verbosity=0, run_syncdb=True)

application = get_wsgi_application()
