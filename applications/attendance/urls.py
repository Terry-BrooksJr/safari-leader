from django.urls import path

from applications.attendance.views import CheckInOutEventDetail, AttendanceRecordDetail, CheckInOutEventList, AttendanceRecordList

urlpatterns = [
    path("event/<int:pk>", CheckInOutEventDetail.as_view(), name="checkinout-event-detail"),
    path("record/<int:pk>", AttendanceRecordDetail.as_view(), name="attendance-record-detail"),
    path("events/", CheckInOutEventList.as_view(), name="checkinout-event-list"),
    path("records/", AttendanceRecordList.as_view(), name="attendance-list"),
]