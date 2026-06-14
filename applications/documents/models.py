from django.db import models
from django.utils.translation import gettext_lazy as _

from applications.accounts.models import User
from applications.children.models import Child


class DOCUMENT_TYPE(models.TextChoices):
    GENERAL = "G", _("General")
    FINANCIAL = "F", _("Financial")
    LEGAL = "L", _("Legal")
    INTERNAL = "I", _("Internal")
    OTHER = "O", _("Other")
    MEDICAL = "M", _("Medical")


class Document(models.Model):
    child = models.ForeignKey(Child, on_delete=models.CASCADE, related_name="documents")
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    document_type = models.CharField(max_length=12, choices=DOCUMENT_TYPE.choices)
    file = models.CharField(max_length=3000, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
