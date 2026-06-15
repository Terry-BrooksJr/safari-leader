from django.contrib import admin

from applications.enrollment.models import ChildSchedule, Enrollment

models = {Enrollment, ChildSchedule}

for model in models:
    admin.site.register(model)
