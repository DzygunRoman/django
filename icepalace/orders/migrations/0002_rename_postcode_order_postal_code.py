# Generated by Django 5.1.8 on 2025-04-10 07:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='postcode',
            new_name='postal_code',
        ),
    ]
