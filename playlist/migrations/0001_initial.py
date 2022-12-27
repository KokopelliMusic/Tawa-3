# Generated by Django 4.1.4 on 2022-12-26 20:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Playlist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('creator', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Playlist',
                'verbose_name_plural': 'Playlists',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Song',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('artists', models.CharField(max_length=200)),
                ('album', models.CharField(max_length=200)),
                ('length', models.IntegerField()),
                ('cover', models.CharField(max_length=200)),
                ('platform_id', models.CharField(max_length=200)),
                ('song_type', models.CharField(choices=[('spotify', 'Spotify'), ('youtube', 'YouTube'), ('soundcloud', 'SoundCloud'), ('mp3', 'MP3')], default='spotify', max_length=20)),
                ('added_by', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('playlist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='songs', to='playlist.playlist')),
            ],
        ),
    ]
