# Generated by Django 5.0.6 on 2024-07-24 18:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("video_app", "0013_comment_parent"),
    ]

    operations = [
        migrations.AddField(
            model_name="comment",
            name="text",
            field=models.TextField(default=0),
            preserve_default=False,
        ),
    ]
