# Generated by Django 5.1.7 on 2025-04-02 14:24

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ProposalUtility',
            fields=[
                ('id', models.CharField(max_length=255, primary_key=True, serialize=False, unique=True)),
                ('tariff_name', models.CharField(max_length=255)),
                ('tariff_maxtrix', models.JSONField(default=list)),
            ],
        ),
        migrations.CreateModel(
            name='ElectricityUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(max_length=255)),
                ('consumption', models.PositiveIntegerField()),
                ('escalator', models.PositiveIntegerField()),
                ('avrage_rate', models.FloatField()),
                ('most_likely_utility_tariff', models.CharField(max_length=255)),
                ('utility_tariff_list', models.JSONField(default=list)),
                ('first_year_cost', models.FloatField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('selected_utility_tariff', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='aether_electricity.proposalutility')),
            ],
        ),
    ]
