from django.contrib import admin
from applications.enrollment.models import Enrollment, ChildSchedule

models = {Enrollment, ChildSchedule}

for model in models: 
    admin.site.register(model)