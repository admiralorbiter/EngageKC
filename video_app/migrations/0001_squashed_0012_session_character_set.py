# Generated by Django 5.1.1 on 2024-10-30 01:51

import django.contrib.auth.models
import django.contrib.auth.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    replaces = [('video_app', '0001_initial'), ('video_app', '0002_alter_session_created_by'), ('video_app', '0003_comment_name_comment_password'), ('video_app', '0004_customadmin_media_password'), ('video_app', '0005_comment_is_admin_alter_comment_name'), ('video_app', '0006_alter_media_options_studentmediainteraction'), ('video_app', '0007_remove_comment_password'), ('video_app', '0008_comment_student'), ('video_app', '0009_student_avatar_image_path_and_more'), ('video_app', '0010_remove_tag_field'), ('video_app', '0011_alter_media_description'), ('video_app', '0012_session_character_set')]

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('session_code', models.CharField(editable=False, max_length=8, unique=True)),
                ('section', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_paused', models.BooleanField(default=False)),
                ('created_by', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='CustomAdmin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('school', models.CharField(max_length=100)),
                ('district', models.CharField(max_length=100)),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to.', related_name='custom_admin_set', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='custom_admin_set', to='auth.permission', verbose_name='user permissions')),
                ('media_password', models.CharField(blank=True, max_length=100, null=True)),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Media',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
                ('media_type', models.CharField(choices=[('video', 'Video'), ('image', 'Image'), ('comment', 'Comment')], max_length=10)),
                ('video_file', models.FileField(blank=True, null=True, upload_to='videos')),
                ('image_file', models.ImageField(blank=True, null=True, upload_to='images')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('graph_likes', models.PositiveIntegerField(default=0)),
                ('eye_likes', models.PositiveIntegerField(default=0)),
                ('read_likes', models.PositiveIntegerField(default=0)),
                ('graph_tag', models.CharField(blank=True, choices=[('bar', 'Bar Chart'), ('line', 'Line Graph'), ('pie', 'Pie Chart'), ('box', 'Box Plot'), ('histogram', 'Histogram'), ('comparison', 'Comparison')], max_length=50, null=True)),
                ('is_graph', models.BooleanField(default=False)),
                ('variable_tag', models.CharField(blank=True, choices=[('gender', 'Gender'), ('languages', 'Languages'), ('handedness', 'Handedness'), ('eye_color', 'Eye Color'), ('hair_color', 'Hair Color'), ('hair_type', 'Hair Type'), ('height', 'Height'), ('left_foot_length', 'Left Foot Length'), ('right_foot_length', 'Right Foot Length'), ('longer_foot', 'Longer Foot'), ('index_finger', 'Index Finger'), ('ring_finger', 'Ring Finger'), ('longer_finger', 'Longer Finger'), ('arm_span', 'Arm Span'), ('travel_method', 'Travel Method to School'), ('bed_time', 'Bed Time'), ('wake_time', 'Wake Time'), ('sport_activity', 'Sport or Activity'), ('youtube', 'YouTube'), ('instagram', 'Instagram'), ('snapchat', 'Snapchat'), ('facebook', 'Facebook'), ('twitter', 'Twitter'), ('tiktok', 'TikTok'), ('twitch', 'Twitch'), ('pinterest', 'Pinterest'), ('bereal', 'BeReal'), ('whatsapp', 'WhatsApp'), ('discord', 'Discord'), ('screen_time', 'Screen Time After School'), ('pineapple_pizza', 'Pineapple on Pizza'), ('ice_cream', 'Ice Cream'), ('cats_or_dogs', 'Cats or Dogs'), ('happiness', 'Happiness'), ('climate_change', 'Climate Change'), ('reaction_time', 'Reaction Time'), ('memory_test', 'Memory Test')], max_length=50, null=True)),
                ('submitted_password', models.CharField(blank=True, max_length=100, null=True)),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='media', to='video_app.session')),
            ],
            options={
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('password', models.CharField(max_length=100)),
                ('device_id', models.CharField(blank=True, max_length=255, null=True)),
                ('admin', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('section', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='students', to='video_app.session')),
                ('avatar_image_path', models.CharField(blank=True, max_length=255, null=True)),
                ('character_description', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.AlterField(
            model_name='session',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='StudentMediaInteraction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('liked_graph', models.BooleanField(default=False)),
                ('liked_eye', models.BooleanField(default=False)),
                ('liked_read', models.BooleanField(default=False)),
                ('comment_count', models.PositiveIntegerField(default=0)),
                ('media', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student_interactions', to='video_app.media')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='media_interactions', to='video_app.student')),
            ],
            options={
                'unique_together': {('student', 'media')},
            },
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('device_id', models.CharField(blank=True, max_length=255, null=True)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='replies', to='video_app.comment')),
                ('media', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='video_app.media')),
                ('name', models.CharField(default='test', max_length=100)),
                ('is_admin', models.BooleanField(default=False)),
                ('student', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='comments', to='video_app.student')),
            ],
        ),
        migrations.AddField(
            model_name='session',
            name='character_set',
            field=models.CharField(default='marvel', max_length=50),
        ),
    ]
