from django.contrib import admin
from applications.children.models import Child, AuthorizedPickupProfile, Allergy, MedicalNote, CustodyRestriction, EmergencyContact, GuardianProfile

models = { Child, AuthorizedPickupProfile, Allergy, MedicalNote, CustodyRestriction, EmergencyContact, GuardianProfile}

for model in models:
    admin.site.register(model)