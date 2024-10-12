import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'engagekc.settings')
django.setup()

from django.core.management import call_command

def migrate_data():
    # Dump data from SQLite
    call_command('dumpdata', '--exclude', 'auth.permission', '--exclude', 'contenttypes', '--output', 'data_dump.json')

    # Switch to MySQL
    os.environ['USE_MYSQL'] = 'True'

    # Apply migrations to MySQL
    call_command('migrate')

    # Load data into MySQL
    call_command('loaddata', 'data_dump.json')

if __name__ == '__main__':
    migrate_data()

