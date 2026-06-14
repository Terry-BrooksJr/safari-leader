# Create your views here.
from django.views.generic import DetailView,ListView
from applications.attendance.models import AttendanceRecord, CheckInOutEvent


class CheckInOutEventDetail(DetailView):
    template_name = "attendance/checkinout_event_detail.html"
    context_object_name = "event"
    queryset = CheckInOutEvent.objects.select_related("child", "recorded_by", "performed_by")
    
    
class AttendanceRecordDetail(DetailView):
    template_name = "attendance/attendance_record_detail.html"
    context_object_name = "record"
    queryset = AttendanceRecord.objects.select_related("child")
    
    
class CheckInOutEventList(ListView):
    template_name = "children/children_list.html"
    context_object_name = "events"
    paginate_by = 25
    queryset = CheckInOutEvent.objects.all().order_by("-timestamp")
    
class AttendanceRecordList(ListView):
    template_name = "children/children_list.html"
    context_object_name = "records"
    paginate_by = 25
    queryset = AttendanceRecord.objects.all().order_by("-date","-child")