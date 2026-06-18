import secrets

from django.db import models
from encrypted_fields.fields import EncryptedIntegerField

from applications.accounts.models import User
from applications.facilities.models import Program, Room, Site
from common.helpers.model import ModelModifer


class StaffProfile(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="employee_record"
    )
    hire_date = models.DateField()
    termination_date = models.DateField(null=True, blank=True)
    personal_pin = EncryptedIntegerField()
    role_title = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"{self.user.last_name}, {self.user.first_name} ({self.role_title})"

    def verify_pin(self, provided_pin: str) -> bool:
        """
        Verify a provided pickup PIN against the stored encrypted PIN.

        Args:
            provided_pin (str): PIN entered by the user.

        Returns:
            bool: True if the PIN matches, otherwise False.
        """
        if provided_pin is None:
            return False

        try:
            stored_pin = str(self.personal_pin).strip()
            candidate_pin = str(provided_pin).strip()

            return secrets.compare_digest(stored_pin, candidate_pin)

        except (TypeError, ValueError):
            return False


class StaffAssignment(ModelModifer, models.Model):
    staff = models.ForeignKey(StaffProfile, on_delete=models.CASCADE)
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)


class Shift(ModelModifer, models.Model):
    staff = models.ForeignKey(StaffProfile, on_delete=models.CASCADE)
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)


class RatioRequirement(ModelModifer, models.Model):
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    min_age = models.IntegerField()
    max_age = models.IntegerField()
    staff_to_child_ratio = models.CharField(max_length=10)
    is_active = models.BooleanField(default=True)
