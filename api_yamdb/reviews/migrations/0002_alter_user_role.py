# Generated by Django 3.2 on 2023-05-11 17:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('user', 'user'), ('moderator', 'moderator'), ('admin', 'admin')], default='user', error_messages={'invalid_choice': 'роли не существует.'}, max_length=32),
        ),
    ]
