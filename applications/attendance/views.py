# Create your views here.
from django.views.generic import DetailView, ListView

from applications.attendance.models import AttendanceRecord, CheckInOutEvent


class CheckInOutEventDetail(DetailView):
    template_name = "attendance/checkinout_event_detail.html"
    context_object_name = "event"
    queryset = CheckInOutEvent.objects.select_related(
        "attendance_record__child", "recorded_by", "performed_by"
    )


class AttendanceRecordDetail(DetailView):
    template_name = "attendance/attendance_record_detail.html"
    context_object_name = "record"
    queryset = AttendanceRecord.objects.select_related("child")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        record = self.object
        context["events"] = record.check_in_out_events.select_related(
            "performed_by", "recorded_by"
        ).all()
        context["handoffs"] = record.handoff_events.select_related(
            "pickup_person", "checked_by"
        ).all()
        return context


class CheckInOutEventList(ListView):
    template_name = "attendance/checkinout_event_list.html"
    context_object_name = "events"
    paginate_by = 25

    def get_queryset(self):
        queryset = CheckInOutEvent.objects.all()
        event_type = self.request.GET.get("event_type")
        if event_type == "checkin":
            queryset = queryset.filter(event_type__in=["CI-AM", "CI-PM"])
        elif event_type == "checkout":
            queryset = queryset.filter(event_type__in=["CO-AM", "CO-PM"])
        return queryset.order_by(
            "-timestamp",
            "attendance_record__child__last_name",
            "attendance_record__child__first_name",
        )


class AttendanceRecordList(ListView):
    template_name = "attendance/attendance_record_list.html"
    context_object_name = "records"
    paginate_by = 25
    queryset = AttendanceRecord.objects.all().order_by("-date", "-child")

    def get_queryset(self):
        queryset = AttendanceRecord.objects.select_related("child")
        status = self.request.GET.get("status")
        if status == "draft":
            queryset = queryset.filter(status__in=["D"])
        elif status == "final":
            queryset = queryset.filter(status__in=["F"])
        elif status == "modified":
            queryset = queryset.filter(status__in=["M"])
        return queryset.order_by("-date", "child__last_name", "child__first_name")
