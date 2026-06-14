import secrets

from arrow import get, now
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from encrypted_fields.fields import EncryptedIntegerField

from applications.accounts.models import User


class STUDENT_STATUS(models.TextChoices):
    ENROLLED = "E", _("Enrolled")
    ACTIVE = "A", _("Active")
    CANCELLED = "C", _("Cancelled")
    SUSPENDED = "S", _("Suspended")
    TRANSFERRED = "X", _("Transferred")


class RELATIONSHIP(models.TextChoices):
    PARENT = "P", _("Parent")
    GRANDPARENT = "GP", _("Grandparent")
    AVUNCULAR = "AV", _("Aunt/Uncle")
    SIBLING = "S", _("Sibling")
    GUARDIAN = "G", _("Legal Guardian")


class ALLERGEN_SEVERITY(models.TextChoices):
    MILD = "M", _("Mild")
    MODERATE = "MD", _("Moderate")
    SEVERE = "S", _("Severe")
    LIFE = "LT", _("Life-Threatening")
    FATAL = "F", _("Fatal")


class RESTRICTION_TYPE(models.TextChoices):
    NO_PICKUP = "X", _("No Pickup")
    SUP_PU = "SPO", _("Supervised Pickup Only")
    AUTH_PU = "APO", _("Authorized Pickup List Only")
    TEMP_SUS = "TEMP", _("Temporary Pickup Suspension")
    COURT = "CO", _("Court Order On File")


class Child(models.Model):
    """
    Represents a child enrolled in the system and tracks their core profile details.
    Provides basic demographic information used across related child records.
    """

    first_name = models.CharField(max_length=325)
    last_name = models.CharField(max_length=325)
    date_of_birth = models.DateField()
    status = models.CharField(max_length=3, choices=STUDENT_STATUS.choices)
    created_at = models.DateField(auto_now_add=True)
    programs = models.ManyToManyField(
        "facilities.Program",
        through="enrollment.Enrollment",
        related_name="children",
        blank=True,
    )

    def __str__(self) -> str:
        return f"Child: {self.last_name}, {self.first_name} | ({self.age})"

    @property
    def age(self) -> int:
        """
        Calculates the child's current age based on their date of birth.
        Adjusts for whether the child has had their birthday yet this year.
        """
        child_dob = get(self.date_of_birth)
        today = now(settings.TIME_ZONE)
        age = today.year - child_dob.year
        if (today.month, today.day) < (child_dob.month, child_dob.day):
            age -= 1
        return age


class AuthorizedPickupProfile(models.Model):
    child = models.ForeignKey(
        Child, on_delete=models.CASCADE, related_name="authorized_pickup"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    relationship = models.CharField(max_length=3, choices=RELATIONSHIP.choices)
    is_authorized = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    pickup_pin = EncryptedIntegerField()
    verification_notes = models.TextField(null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.user.last_name}, {self.user.first_name} ({self.get_relationship_display()})"

    def toggle_active_status(self):
        """
        Toggles whether the authorized pickup profile is currently active.
        Updates the active state so the profile can be enabled or disabled for future pickups.
        """
        self.is_active = not self.is_active
        self.save()

    def toggle_authorization_status(self):
        """
        Toggles whether the authorized pickup profile currently has pickup permission.
        Updates the authorization flag so the profile can be allowed or blocked from picking up the child.
        """
        self.is_authorized = not self.is_authorized
        self.save()

    def is_verifed(self, provided_pin: str) -> bool:
        """
        Verify a provided pickup PIN against the stored encrypted PIN.

        Args:
            provided_pin (str): PIN entered by the user.

        Returns:
            bool: True if the PIN matches, otherwise False.
        """
        if provided_pin is None:
            return False
        if not self.is_authorized or not self.is_active:
            return False
        try:
            stored_pin = str(self.pickup_pin).strip()
            candidate_pin = provided_pin.strip()

            return secrets.compare_digest(stored_pin, candidate_pin)

        except (TypeError, ValueError):
            return False


class Allergy(models.Model):
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name="allergies")
    allergen = models.CharField(max_length=50)
    severity = models.CharField(max_length=2, choices=ALLERGEN_SEVERITY.choices)
    instructions = models.TextField()
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"{self.get_severity_display()} {self.allergen}"

    def toggle_active_status(self):
        """
        Toggles whether this allergy record is currently marked as active.
        Updates the active state so the allergy can be included or excluded from consideration.
        """
        self.is_active = not self.is_active
        self.save()


class MedicalNote(models.Model):
    child = models.ForeignKey(
        Child, on_delete=models.CASCADE, related_name="medical_notes"
    )
    note = models.TextField()
    is_active = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Medical Note: {self.child.last_name}, {self.child.first_name} ({self.date_created})"

    def toggle_active_status(self):
        """
        Toggles whether this medical note is currently marked as active.
        Updates the active state so the note can be considered or ignored in the child's medical history.
        """
        self.is_active = not self.is_active
        self.save()


class CustodyRestriction(models.Model):
    child = models.ForeignKey(
        Child, on_delete=models.CASCADE, related_name="restrictions"
    )
    notes = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def toggle_active_status(self):
        """
        Toggles whether this custody restriction is currently marked as active.
        Updates the active state so the note can be considered or ignored in the child's medical history.
        """
        self.is_active = not self.is_active
        self.save()


class EmergencyContact(models.Model):
    child = models.ForeignKey(
        Child, on_delete=models.CASCADE, related_name="emergency_contact"
    )
    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80)
    contact_number = models.CharField(max_length=12)
    relationship = models.CharField(max_length=3, choices=RELATIONSHIP.choices)
    is_authorized = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    verification_notes = models.TextField(null=True, blank=True)

    def toggle_active_status(self):
        """
        Toggles whether this emergency contact is currently marked as active.
        Updates the active state so the note can be considered or ignored in the child's medical history.
        """
        self.is_active = not self.is_active
        self.save()


class GuardianProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    contact_number = models.CharField(max_length=12)
    is_primary_contact = models.BooleanField()
    created_at = models.DateField(auto_now=True)

    def toggle_primary_contact_status(self):
        """
        Toggles whether this guardian profile is currently marked as the primary contact.
        Updates the primary contact flag so the main communication point can be reassigned as needed.
        """
        self.is_primary_contact = not self.is_primary_contact
        self.save()


class ChildGuardianRelationship(models.Model):
    child = models.ForeignKey(Child, on_delete=models.CASCADE)
    guardian = models.ForeignKey(GuardianProfile, on_delete=models.CASCADE)
    relationship = models.CharField(max_length=3, choices=RELATIONSHIP.choices)
    is_primary = models.BooleanField()
    has_custody_rights = models.BooleanField()
    can_pickup = models.BooleanField()
    is_active = models.BooleanField(default=True)

    def toggle_primary_status(self):
        """
        Toggles whether this guardian is currently marked as the primary guardian for the child.
        Updates the primary flag so the main point of contact can be reassigned as needed.
        """
        self.is_primary = not self.is_primary
        self.save()

    def toggle_active_status(self):
        """
        Toggles whether this guardian-child relationship is currently marked as active.
        Updates the active state so the relationship can be considered or ignored in child management decisions.
        """
        self.is_active = not self.is_active
        self.save()

    def toggle_has_custody_rights_status(self):
        """
        Toggles whether this guardian currently has recorded custody rights for the child.
        Updates the custody rights flag so legal decision-making authority can be granted or revoked.
        """
        self.has_custody_rights = not self.has_custody_rights
        self.save()

    def toggle_can_pickup_status(self):
        self.can_pickup = not self.can_pickup
        self.save()
