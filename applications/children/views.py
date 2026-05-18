from typing import Any

from django.db.models.query import QuerySet
from django.shortcuts import render
from applications.children.models import Child
from django.views.generic import ListView, DetailView


# Create your views here.

class ChildrenList(ListView):
    template_name = 'children/children_list.html'
    queryset = Child.objects.all()
    extra_context = {"children":Child.objects.all().order_by("last_name")}
    paginate_by = 25

    
class ChildDetailView(DetailView):
    template_name = "children/child_detail.html"
    context_object_name = "child"
    queryset = Child.objects.prefetch_related(
        "authorized_pickup",       # Authorized pickups
        "childguardianrelationship_set",      # Guardian links
        "childguardianrelationship_set__guardian",  # + the GuardianProfile
        "allergies",                        # Allergies
        "medical_notes",                    # Medical notes
        "restrictions",             # Custody restrictions
        "emergency_contact",              # Emergency contacts
        "enrollment_set",                     # Enrollments
        "enrollment_set__program",            # + Program on each enrollment
        "enrollment_set__site",               # + Site on each enrollment
        "childschedule_set",                  # Schedules
        "attendancerecord_set",              # Attendance
        "checkinoutevent_set",               # Check-in/out
        "handoffevent_set",                  # Handoffs
        "documents",                          # Documents (has related_name)
        "incidentreport_set",               # Incidents
    ).all()
