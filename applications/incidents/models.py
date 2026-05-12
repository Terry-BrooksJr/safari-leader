from django.db import models
from applications.children.models import Child
from applications.staffing.models import StaffProfile
from django.utils.translation import gettext_lazy as _

class INCIDENT_TYPE(models.TextChoices):
    SAFETY = 'S', _("Safety")
    MEDICAL = 'M', _("Medical") 
    EDUCATIONAL = 'E', _("Educational")
    OTHER = 'O', _("Other")

class SEVERITY(models.TextChoices):
    MILD = 'M', _('Mild')
    MODERATE = 'MD', _('Moderate')
    SEVERE = 'S', _('Severe')
    LIFE  = "LT", _('Life-Threatening')
    FATAL = 'F', _('Fatal')
    
class IncidentReport(models.Model):
    child_id = models.ForeignKey(Child,on_delete=models.CASCADE )
    reported_by_id = models.ForeignKey(StaffProfile, on_delete=models.CASCADE)
    incident_type = models.CharField(max_length=10, choices=INCIDENT_TYPE.choices) 
    description = models.TextField()
    occurred_on = models.DateField()
    occured_at = models.TimeField()
    severity = models.CharField(max_length=4, choices=SEVERITY.choices)
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def toggle_resolution_status(self):
        if self.is_resolved:
            self.is_resolved = False
        else: 
            self.is_resolved = True
        self.save()