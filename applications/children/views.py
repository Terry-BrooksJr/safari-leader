from django.core.paginator import Paginator
from django.views.generic import DetailView, ListView

from applications.children.models import Child


def paginate_queryset(request, queryset, page_param, per_page):
    paginator = Paginator(queryset, per_page)
    return paginator.get_page(request.GET.get(page_param))

class ChildrenList(ListView):
    template_name = 'children/children_list.html'
    queryset = Child.objects.all().order_by("last_name")
    context_object_name = "children"
    paginate_by = 25

    
class ChildDetailView(DetailView):
    template_name = "children/child_detail.html"
    context_object_name = "child"
    queryset = Child.objects.prefetch_related(
        "authorized_pickup",       # Authorized pickups
        "authorized_pickup__user",  # + User on each authorized pickup
        "childguardianrelationship_set",      # Guardian links
        "childguardianrelationship_set__guardian",  # + the GuardianProfile
        "childguardianrelationship_set__guardian__user",  # + User on each GuardianProfile
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
            child.checkinoutevent_set.all().order_by("-timestamp"),
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
            child.handoffevent_set.all().order_by("-timestamp"),
            "handoffevents_page",
            5,
        )

        return context