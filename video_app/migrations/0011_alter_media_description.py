# Generated by Django 5.1.1 on 2024-10-12 22:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('video_app', '0010_remove_tag_field'),
    ]

    operations = [
        migrations.AlterField(
            model_name='media',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]
