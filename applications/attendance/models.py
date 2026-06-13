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
    child = models.ForeignKey(Child, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(
        max_length=3, choices=RECORD_STATUS.choices, default=RECORD_STATUS.DRAFT
    )
    created = models.DateField(auto_now_add=True)

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
    child = models.ForeignKey(Child, on_delete=models.CASCADE)
    event_type = models.CharField(max_length=5, choices=EVENT_TYPE.choices)
    timestamp = models.DateTimeField(auto_now=True)
    performed_by = models.ForeignKey(
        AuthorizedPickupProfile, on_delete=models.SET_NULL, null=True
    )
    recorded_by = models.ForeignKey(StaffProfile, on_delete=models.SET_NULL, null=True)
    notes = models.TextField(null=True, blank=True)
