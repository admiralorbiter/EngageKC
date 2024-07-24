# Generated by Django 5.0.6 on 2024-07-20 02:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("video_app", "0007_remove_media_session_associated_media_session"),
    ]

    operations = [
        migrations.AlterField(
            model_name="media",
            name="session",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="media",
                to="video_app.session",
            ),
        ),
    ]