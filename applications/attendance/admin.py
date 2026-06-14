from django.contrib import admin
from applications.attendance.models import CheckInOutEvent, AttendanceRecord

models = {CheckInOutEvent, AttendanceRecord}

for model in models:
    admin.site.register(model)