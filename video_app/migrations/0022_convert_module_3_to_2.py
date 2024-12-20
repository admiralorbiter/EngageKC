# Generated by Django 5.1.1 on 2024-12-17 02:49

from django.db import migrations

def convert_module_3_to_2(apps, schema_editor):
    Session = apps.get_model('video_app', 'Session')
    # Update all sessions with module '3' to module '2'
    Session.objects.filter(module='3').update(module='2')

def reverse_convert(apps, schema_editor):
    Session = apps.get_model('video_app', 'Session')
    # Convert back from '2' to '3' if needed
    Session.objects.filter(module='2').update(module='3')

class Migration(migrations.Migration):

    dependencies = [
        ('video_app', '0021_update_session_modules'),
    ]

    operations = [
        migrations.RunPython(convert_module_3_to_2, reverse_convert),
    ]
