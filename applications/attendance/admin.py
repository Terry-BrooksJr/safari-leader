from django.contrib import admin

from applications.attendance.models import AttendanceRecord, CheckInOutEvent

models = {CheckInOutEvent, AttendanceRecord}

for model in models:
    admin.site.register(model)
