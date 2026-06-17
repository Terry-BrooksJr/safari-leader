from django.db import models
from django.utils.translation import gettext_lazy as _

from applications.children.models import Child
from applications.facilities.models import Program
from applications.staffing.models import StaffProfile
def days_of_week_template():
    return {
        "sunday": False,
        "monday": True,
        "tuesday": True,
        "wednesday": True,
        "thursday": True,
        "friday": True,
        "saturday": False,
    }


class ENROLLMENT_STATUS(models.TextChoices):
    PENDING = "P", _("Pending")
    ACTIVE = "A", _("Active - Current")
    PAST = "PS", _("Inactive - Past")
    WITHDRAWN = "W", _("Inactive - Withdrawn")


class Enrollment(models.Model):
    child = models.ForeignKey(
        Child, on_delete=models.CASCADE, related_name="enrollments"
    )
    program = models.ForeignKey(
        Program, on_delete=models.CASCADE, related_name="enrollments"
    )
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=5, choices=ENROLLMENT_STATUS.choices)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["child"],
                condition=models.Q(status="A"),
                name="one_active_enrollment_per_child",
            )
        ]

    def __str__(self) -> str:
        return f"{self.child.last_name}, {self.child.first_name} ({self.program}: {self.start_date} - {self.end_date})"

    @property
    def site(self):
        return self.program.site


class ChildSchedule(models.Model):
    child = models.ForeignKey(Child, on_delete=models.CASCADE)
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    instructor = models.ForeignKey(StaffProfile, on_delete=models.DO_NOTHING)
    days_of_week = models.JSONField(default=days_of_week_template)
    is_active = models.BooleanField(default=True)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def toggle_active_status(self):
        self.is_active = not self.is_active
        self.save()
