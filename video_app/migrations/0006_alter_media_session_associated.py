# Generated by Django 5.0.6 on 2024-07-20 01:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("video_app", "0005_remove_media_post_associated_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="media",
            name="session_associated",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="media",
                to="video_app.session",
            ),
        ),
    ]