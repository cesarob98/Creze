# Generated by Django 5.1.6 on 2025-02-27 06:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authenticator', '0010_alter_user_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='mfa_secret',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
    ]
