from django.db import models
from django.utils.translation import gettext_lazy as _

from applications.children.models import Child
from applications.facilities.models import Program, Site


# Create your models here.
def days_of_week_template():
    return {
        "sunday": False,
        "monday":True,
        "tuesday": True,
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
    """
    Represents a child's enrollment in a specific program at a site. 

    Enrollments track the active period and current status of a child's participation.
    """
    child= models.ForeignKey(Child,on_delete=models.CASCADE )
    program= models.ForeignKey(Program, on_delete=models.CASCADE)
    site= models.ForeignKey(Site, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField(null=True,blank=True)
    status = models.CharField(max_length=5, choices=ENROLLMENT_STATUS.choices)
    def __str__(self) -> str:
        return f"{self.child.last_name}, {self.child.first_name} ({self.program}: {self.start_date} - {self.end_date})"
class ChildSchedule(models.Model):
    """
    Represents a recurring weekly schedule for a child's participation in a program. 

    Child schedules define active days and times for attendance, and can be toggled on or off as needed.
    """
    child= models.ForeignKey(Child,on_delete=models.CASCADE )
    program= models.ForeignKey(Program, on_delete=models.CASCADE)
    enrollment= models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    days_of_week = models.JSONField(default=days_of_week_template)
    is_active = models.BooleanField(default=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    def toggle_active_status(self):
        """
        Toggles whether the child's schedule is currently active. 

        This method flips the active flag on the schedule and persists the change.

        Returns:
            bool: The updated active status after toggling.
        """
        self.is_active = not self.is_active
        self.save()