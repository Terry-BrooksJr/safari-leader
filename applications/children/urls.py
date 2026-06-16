from django.urls import path

from applications.children.views import (
    AllergyDetailView,
    AuthorizedPickupDetailView,
    ChildDetailView,
    ChildrenList,
    CustodyRestrictionDetailView,
    EmergencyContactDetailView,
    GuardianDetailView,
    MedicalNoteDetailView,
)

urlpatterns = [
    path("", ChildrenList.as_view(), name="children-list"),
    path("child/<int:pk>", ChildDetailView.as_view(), name="child-detail"),
    path(
        "authorized-pickup/<int:pk>",
        AuthorizedPickupDetailView.as_view(),
        name="authorized-pickup-detail",
    ),
    path("guardian/<int:pk>", GuardianDetailView.as_view(), name="guardian-detail"),
    path(
        "emergency-contact/<int:pk>",
        EmergencyContactDetailView.as_view(),
        name="emergency-contact-detail",
    ),
    path(
        "custody-restriction/<int:pk>",
        CustodyRestrictionDetailView.as_view(),
        name="custody-restriction-detail",
    ),
    path("allergy/<int:pk>", AllergyDetailView.as_view(), name="allergy-detail"),
    path(
        "medical-note/<int:pk>",
        MedicalNoteDetailView.as_view(),
        name="medical-note-detail",
    ),
]
