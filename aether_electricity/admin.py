from django.contrib import admin

from .models import ElectricityUser, ProposalUtility

# Register your models here.
admin.site.register(ElectricityUser)
admin.site.register(ProposalUtility)