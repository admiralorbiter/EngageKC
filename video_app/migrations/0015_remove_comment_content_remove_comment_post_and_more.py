# Generated by Django 5.0.6 on 2024-07-24 18:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("video_app", "0014_comment_text"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="comment",
            name="content",
        ),
        migrations.RemoveField(
            model_name="comment",
            name="post",
        ),
        migrations.AddField(
            model_name="comment",
            name="media",
            field=models.ForeignKey(
                default=0,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="comments",
                to="video_app.media",
            ),
            preserve_default=False,
        ),
    ]
