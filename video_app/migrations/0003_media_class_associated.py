# Generated by Django 5.0 on 2024-06-25 02:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('video_app', '0002_class'),
    ]

    operations = [
        migrations.AddField(
            model_name='media',
            name='class_associated',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='media', to='video_app.class'),
            preserve_default=False,
        ),
    ]
