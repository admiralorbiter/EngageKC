from django.core.management.base import BaseCommand
import os
import subprocess
import sys

class Command(BaseCommand):
    help = 'Runs coverage on the project'

    def handle(self, *args, **options):
        os.environ['DJANGO_SETTINGS_MODULE'] = '.settings'
        python_executable = sys.executable
        subprocess.run([python_executable, '-m', 'coverage', 'run', '--source=.', 'manage.py', 'test'])
        subprocess.run([python_executable, '-m', 'coverage', 'html'])
        subprocess.run([python_executable, '-m', 'coverage', 'report'])