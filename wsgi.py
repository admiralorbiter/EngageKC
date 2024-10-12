# +++++++++++ DJANGO +++++++++++
# To use your own Django app use code like this:
import os
import sys
from dotenv import load_dotenv

# Add your project directory to the sys.path
path = '/home/jlane/EngageKC'
if path not in sys.path:
    sys.path.append(path)

# Load environment variables
load_dotenv(os.path.join(path, '.env'))

os.environ['DJANGO_SETTINGS_MODULE'] = 'engagekc.settings'

## Uncomment the lines below depending on your Django version
###### then, for Django >=1.5:
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
###### or, for older Django <=1.4
#import django.core.handlers.wsgi
#application = django.core.handlers.wsgi.WSGIHandler()
