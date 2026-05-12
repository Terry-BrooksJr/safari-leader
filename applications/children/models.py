from django.db import models
from django.utils.translation import gettext_lazy as _
from applications.accounts.models import User
from fernet_fields import EncryptedIntegerField
import secrets
from arrow import now, get
from django.conf import settings

class STUDENT_STATUS(models.TextChoices):
    ENROLLED = 'E', _('Enrolled')
    ACTIVE = 'A', _('Active')
    CANCELLED = 'C', _('Cancelled')
    SUSPENDED  = "S", _('Suspended')
    TRANSFERRED = 'X', _('Transferred')

class RELATIONSHIP(models.TextChoices):
    PARENT = 'P', _('Parent')
    GRANDPARENT = 'GP', _('Grandparent')
    AVUNCULAR = 'AV', _('Aunt/Uncle')
    SIBLING  = "S", _('Sibling')
    GUARDIAN = 'G', _('Legal Guardian')
    
class ALLERGEN_SEVERITY(models.TextChoices):
    MILD = 'M', _('Mild')
    MODERATE = 'MD', _('Moderate')
    SEVERE = 'S', _('Severe')
    LIFE  = "LT", _('Life-Threatening')
    FATAL = 'F', _('Fatal')

class RESTRICTION_TYPE(models.TextChoices):
    NO_PICKUP = 'X', _('No Pickup')
    SUP_PU = 'SPO', _('Supervised Pickup Only')
    AUTH_PU = 'APO', _('Authorized Pickup List Only')
    TEMP_SUS  = "TEMP", _('Temporary Pickup Suspension')
    COURT = 'CO', _('Court Order On File')

class Child(models.Model):
    first_name = models.CharField(max_length=325)
    last_name = models.CharField(max_length=325)
    date_of_birth = models.DateField()
    status = models.CharField(max_length=3, choices=STUDENT_STATUS.choices)
    created_at = models.DateField(auto_now_add=True)
    
    @property
    def age(self) -> int:
        child_dob = get(self.date_of_birth, 'YYYY-MM-DD')
        today = now(settings.TIME_ZONE)
        age = today.year - child_dob.year
        if (today.month, today.day) < (child_dob.month, child_dob.day):
            age -= 1
        return age
    
class AuthorizedPickupProfile(models.Model): 
    child_id = models.ForeignKey(Child, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    relationship = models.CharField(max_length=3, choices=RELATIONSHIP.choices)
    is_authorized = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    pickup_pin = EncryptedIntegerField()
    verification_notes = models.TextField(null=True, blank=True)
    
    def toggle_active_status(self):
        if self.is_active:
            self.is_active = False
        else: 
            self.is_active = True
        self.save()
        
    def toggle_authorization_status(self):
        if self.is_authorized:
            self.is_authorized = False
        else: 
            self.is_authorized = True
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
                candidate_pin = str(provided_pin).strip()

                return secrets.compare_digest(stored_pin, candidate_pin)

            except (TypeError, ValueError):
                return False
            
class Allergy(models.Model):
    child_id = models.ForeignKey(Child, on_delete=models.CASCADE)
    allergen = models.CharField(max_length=50)
    severity = models.CharField(choices=ALLERGEN_SEVERITY.choices)
    instructions = models.TextField()
    is_active = models.BooleanField(default=True)
    
    def toggle_active_status(self):
        if self.is_active:
            self.is_active = False
        else: 
            self.is_active = True
        self.save()
        
class MedicalNote(models.Model):
    note = models.TextField()
    is_active = models.BooleanField(default=True)
    
    def toggle_active_status(self):
        if self.is_active:
            self.is_active = False
        else: 
            self.is_active = True
        self.save()
        
class CustodyRestriction(models.Model):
    child_id = models.ForeignKey(Child, on_delete=models.CASCADE)
    notes = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    restriction_type = models.CharField(max_length=10, choices=RESTRICTION_TYPE.choices)
    notes = models.TextField()
    is_active = models.BooleanField(default=True)
    
    def toggle_active_status(self):
        if self.is_active:
            self.is_active = False
        else: 
            self.is_active = True
        self.save()

class EmergencyContact(models.Model): 
    child_id = models.ForeignKey(Child, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80)
    contact_number = models.CharField(max_length=12)
    relationship = models.CharField(max_length=3, choices=RELATIONSHIP.choices)
    is_authorized = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    verification_notes = models.TextField(null=True, blank=True)
    
    def toggle_active_status(self):
        if self.is_active:
            self.is_active = False
        else: 
            self.is_active = True
        self.save()
        
class GuardianProfile(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    contact_number = models.CharField(max_length=12)
    is_primary_contact = models.BooleanField()
    created_at = models.DateField(auto_now=True)
    
    def toggle_primary_contact_status(self):
        if self.is_primary_contact:
            self.is_primary_contact = False
        else: 
            self.is_primary_contact = True
        self.save()
    
class ChildGuardianRelationship(models.Model):
    child_id = models.ForeignKey(Child, on_delete=models.CASCADE)
    guardian_id = models.ForeignKey(GuardianProfile, on_delete=models.CASCADE)
    relationship = models.CharField(max_length=3, choices=RELATIONSHIP.choices)
    is_primary = models.BooleanField()
    has_custody_rights = models.BooleanField()
    can_pickup = models.BooleanField()
    is_active = models.BooleanField(default=True)

    def toggle_primary_status(self):
        if self.is_primary:
            self.is_primary = False
        else: 
            self.is_primary = True
        self.save()
        
    def toggle_active_status(self):
        if self.is_active:
            self.is_active = False
        else: 
            self.is_active = True
        self.save()
        
    def toggle_has_custody_rights_status(self):
        if self.has_custody_rights:
            self.has_custody_rights = False
        else: 
            self.has_custody_rights = True
        self.save()

    def toggle_can_pickup_status(self):
        if self.can_pickup:
            self.can_pickup = False
        else: 
            self.can_pickup = True
        self.save()