# Generated by Django 4.1.4 on 2022-12-30 17:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('playlist', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='song',
            name='play_count',
            field=models.IntegerField(default=0),
        ),
    ]