from django.core.paginator import Paginator
from django.views.generic import DetailView, ListView

from applications.attendance.models import CheckInOutEvent
from applications.children.models import (
    Allergy,
    AuthorizedPickupProfile,
    Child,
    CustodyRestriction,
    EmergencyContact,
    GuardianProfile,
    MedicalNote,
)
from applications.handoff.models import HandoffEvent


def paginate_queryset(request, queryset, page_param, per_page):
    paginator = Paginator(queryset, per_page)
    return paginator.get_page(request.GET.get(page_param))


class ChildrenList(ListView):
    template_name = "children/children_list.html"
    context_object_name = "children"
    paginate_by = 25

    def get_queryset(self):
        queryset = Child.objects.all()
        status = self.request.GET.get("status")
        if status == "active":
            queryset = queryset.filter(status__in=["A", "E"])
        elif status == "inactive":
            queryset = queryset.filter(status__in=["X", "S", "T"])
        return queryset.order_by("last_name")


class ChildDetailView(DetailView):
    template_name = "children/child_detail.html"
    context_object_name = "child"
    queryset = Child.objects.prefetch_related(
        "authorized_pickup",  # Authorized pickups
        "authorized_pickup__user",  # + User on each authorized pickup
        "childguardianrelationship_set",  # Guardian links
        "childguardianrelationship_set__guardian",  # + the GuardianProfile
        "childguardianrelationship_set__guardian__user",  # + User on each GuardianProfile
        "allergies",  # Allergies
        "medical_notes",  # Medical notes
        "restrictions",  # Custody restrictions
        "emergency_contact",  # Emergency contacts
        "enrollments",  # Enrollments
        "enrollments__program",  # + Program on each enrollment
        "enrollments__program__site",  # + Site through program
        "childschedule_set",  # Schedules
        "documents",  # Documents (has related_name)
    ).all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        child = self.object

        context["attendancerecords"] = paginate_queryset(
            self.request,
            child.attendancerecord_set.all().order_by("-created"),
            "attendancerecords_page",
            5,
        )

        context["checkinoutevents"] = paginate_queryset(
            self.request,
            CheckInOutEvent.objects.filter(attendance_record__child=child)
            .select_related("performed_by", "recorded_by")
            .order_by("-timestamp"),
            "checkinoutevents_page",
            5,
        )

        context["incidentreports"] = paginate_queryset(
            self.request,
            child.incidentreport_set.all().order_by("-occurred_on", "-occured_at"),
            "incidentreports_page",
            5,
        )

        context["handoffevents"] = paginate_queryset(
            self.request,
            HandoffEvent.objects.filter(attendance_record__child=child)
            .select_related("pickup_person", "checked_by")
            .order_by("-timestamp"),
            "handoffevents_page",
            5,
        )

        return context


class AuthorizedPickupDetailView(DetailView):
    template_name = "children/authorized_pickup_detail.html"
    context_object_name = "pickup"
    queryset = AuthorizedPickupProfile.objects.select_related("child", "user")


class GuardianDetailView(DetailView):
    template_name = "children/guardian_detail.html"
    context_object_name = "guardian"
    queryset = GuardianProfile.objects.select_related("user").prefetch_related(
        "childguardianrelationship_set",
        "childguardianrelationship_set__child",
    )


class EmergencyContactDetailView(DetailView):
    template_name = "children/emergency_contact_detail.html"
    context_object_name = "contact"
    queryset = EmergencyContact.objects.select_related("child")


class CustodyRestrictionDetailView(DetailView):
    template_name = "children/custody_restriction_detail.html"
    context_object_name = "restriction"
    queryset = CustodyRestriction.objects.select_related("child")


class AllergyDetailView(DetailView):
    template_name = "children/allergy_detail.html"
    context_object_name = "allergy"
    queryset = Allergy.objects.select_related("child")


class MedicalNoteDetailView(DetailView):
    template_name = "children/medical_note_detail.html"
    context_object_name = "note"
    queryset = MedicalNote.objects.select_related("child")
