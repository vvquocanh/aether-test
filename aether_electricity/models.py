from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class ElectricityUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=255)
    consumption = models.PositiveIntegerField()
    escalator = models.PositiveIntegerField()
    average_rate = models.FloatField()
    most_likely_utility_tariff = models.CharField(max_length=255)
    utility_tariff_list = models.JSONField(default=list)
    first_year_cost = models.FloatField()
    selected_utility_tariff = models.ForeignKey('ProposalUtility', on_delete=models.SET_NULL, null=True, blank=True)

class ProposalUtility(models.Model):
    id = models.CharField(unique=True, max_length=255, primary_key=True)
    tariff_name = models.CharField(max_length=255) 
    tariff_matrix = models.JSONField(default=list)