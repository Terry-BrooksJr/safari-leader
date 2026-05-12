from django.db import models
from applications.children.models import Child
from applications.facilities.models import Program,Site
from django.utils.translation import gettext_lazy as _

# Create your models here.
days_of_week_template = {
    "sunday": False,
    "monday":True, 
    "wednesday": True,
    "thursday": True,
    "friday":True,
    "saturday":False
}
class ENROLLMENT_STATUS(models.TextChoices):
    PENDING = 'P', _("Pending")
    ACTIVE = 'A', _("Active - Current")
    PAST = 'PS', _("Inactive - Past")
    WITHDRAWN = 'W', _("Inactive - Withdrawn")

class Enrollment(models.Model):
    child_id = models.ForeignKey(Child,on_delete=models.CASCADE )
    program_id = models.ForeignKey(Program, on_delete=models.CASCADE)
    site_id = models.ForeignKey(Site, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField(null=True,blank=True)
    status = models.CharField(max_length=5, choices=ENROLLMENT_STATUS.choices)
    
class ChildSchedule(models.Model):
    child_id = models.ForeignKey(Child,on_delete=models.CASCADE )
    program_id = models.ForeignKey(Program, on_delete=models.CASCADE)
    enrollment_id = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    days_of_week = models.JSONField(default=days_of_week_template)
    is_active = models.BooleanField(default=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    def toggle_active_status(self):
        if self.is_active:
            self.is_active = False
        else: 
            self.is_active = True
        self.save()