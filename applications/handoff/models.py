from django.db import models
from applications.children.models import Child, AuthorizedPickupProfile
from applications.staffing.models import StaffProfile
from django.utils.translation import gettext_lazy as _

# Create your models here.

class HANDOFF_EVENT_TYPE(models.TextChoices):
    AM_PICKUP = 'PU-AM', _('Pickup(AM)')
    AM_DROPOFF = 'DO-AM', _('Dropoff(AM)')
    PM_PICKUP = 'PU-PM', _('Pickup(PM)')
    PM_DROPOFF = 'DO-PM', _('Dropoff(PM)')

class HANDOFF_VERIFICATION_METHODS(models.TextChoices):
    PIN = 'PIN', _('Pin Verification')
    OVERRIDE = 'OR', _('Manual Verification - Employee Override')


class HandoffEvent(models.Model): 
   child= models.ForeignKey(Child,on_delete=models.CASCADE )
   event_type = models.CharField(max_length=5, choices=HANDOFF_EVENT_TYPE.choices)
   pickup_person= models.ForeignKey(AuthorizedPickupProfile, on_delete=models.CASCADE)
   checked_by= models.ForeignKey(StaffProfile, on_delete=models.CASCADE)
   timestamp = models.DateTimeField(auto_now_add=True)