from django.contrib import admin

from applications.children.models import (
    Allergy,
    AuthorizedPickupProfile,
    Child,
    CustodyRestriction,
    EmergencyContact,
    GuardianProfile,
    MedicalNote,
)

models = {
    Child,
    AuthorizedPickupProfile,
    Allergy,
    MedicalNote,
    CustodyRestriction,
    EmergencyContact,
    GuardianProfile,
}

for model in models:
    admin.site.register(model)
