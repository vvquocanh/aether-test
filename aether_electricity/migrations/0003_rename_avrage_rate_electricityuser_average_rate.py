# Generated by Django 5.1.7 on 2025-04-02 15:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aether_electricity', '0002_rename_tariff_maxtrix_proposalutility_tariff_matrix'),
    ]

    operations = [
        migrations.RenameField(
            model_name='electricityuser',
            old_name='avrage_rate',
            new_name='average_rate',
        ),
    ]
