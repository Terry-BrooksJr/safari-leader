from django.db import models
from django.utils.translation import gettext_lazy as _

from applications.children.models import AuthorizedPickupProfile, Child
from applications.staffing.models import StaffProfile


class RECORD_STATUS(models.TextChoices):
    DRAFT = "D", _("Draft")
    FINAL = "F", _("Final")
    MODIFIED = "M", _("Final - Modified")


class EVENT_TYPE(models.TextChoices):
    AM_CHECKIN = "CI-AM", _("Check-In(AM)")
    AM_CHECKOUT = "CO-AM", _("Check-Out(AM)")
    PM_CHECKIN = "CI-PM", _("Pickup(PM)")
    PM_CHECKOUT = "CO-PM", _("Check-Out(PM)")


class AttendanceRecord(models.Model):
    """A child's attendance for a single day.

    Acts as the parent collection for that day's check-in/out events and
    handoff events, reachable via ``record.check_in_out_events`` and
    ``record.handoff_events``.
    """

    child = models.ForeignKey(Child, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(
        max_length=3, choices=RECORD_STATUS.choices, default=RECORD_STATUS.DRAFT
    )
    created = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]
        constraints = [
            models.UniqueConstraint(
                fields=["child", "date"],
                name="one_attendance_record_per_child_per_day",
            )
        ]

    def __str__(self) -> str:
        return (
            f"{self.child.last_name}, {self.child.first_name} — "
            f"{self.date} ({self.get_status_display()})"
        )

    @property
    def timeline(self):
        """All events for the day (check-in/out + handoff), oldest first."""
        events = list(self.check_in_out_events.all()) + list(
            self.handoff_events.all()
        )
        return sorted(events, key=lambda event: event.timestamp)

    def finalize_record(self):
        type(self).objects.filter(pk=self.pk).update(status=RECORD_STATUS.FINAL)

    def save(
        self, *, force_insert=False, force_update=False, using=None, update_fields=None
    ) -> None:
        if self.status == RECORD_STATUS.DRAFT:
            return super().save(force_insert, force_update, using, update_fields)
        elif self.status == RECORD_STATUS.FINAL:
            type(self).objects.filter(pk=self.pk).update(status=RECORD_STATUS.MODIFIED)
            return super().save(force_insert, force_update, using, update_fields)


class CheckInOutEvent(models.Model):
    attendance_record = models.ForeignKey(
        AttendanceRecord,
        on_delete=models.CASCADE,
        related_name="check_in_out_events",
    )
    event_type = models.CharField(max_length=5, choices=EVENT_TYPE.choices)
    timestamp = models.DateTimeField(auto_now=True)
    performed_by = models.ForeignKey(
        AuthorizedPickupProfile, on_delete=models.SET_NULL, null=True
    )
    recorded_by = models.ForeignKey(StaffProfile, on_delete=models.SET_NULL, null=True)
    notes = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ["timestamp"]

    @property
    def child(self):
        """The child this event belongs to, via its attendance record."""
        return self.attendance_record.child
