# Generated by Django 5.1.1 on 2024-12-15 23:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('video_app', '0019_media_project_group'),
    ]

    operations = [
        migrations.AddField(
            model_name='media',
            name='is_project',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='media',
            name='project_images',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
