# Generated by Django 5.1 on 2024-10-07 16:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('video_app', '0009_student_avatar_image_path_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='media',
            name='tag',
        ),
    ]
