from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    fixtures = ['initial_data.json']

    def setUp(self):
        # Load the fixture data
        call_command('loaddata', 'initial_data.json', verbosity=0)