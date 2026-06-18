from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from common.helpers.model import ModelModifer


# Create your models here.
class ROLES(models.TextChoices):
    """
    Enum Values for Role Name Used in the Role Class Name Fields
    """

    ADMIN = "ADMIN", _("Administrator")
    DIRECTOR = "DIRECTOR", _("Site Director")
    INSTRUCTOR = "INSTRUCTOR", _("Instructor")
    AIDE = "AIDE", _("Teacher's Aide")
    GUARDIAN = "GUARDIAN", _("Guardian")
    PICKUP = "PICKUP", _("Authorized Pickup")
    CLERICAL = "CLERICAL", _("Clerical/Auditing/Admin Support")


class User(AbstractUser):
    pass


class Role(models.Model):
    name = models.CharField(
        max_length=265, blank=False, unique=True, db_index=True, choices=ROLES.choices
    )
    description = models.TextField()
    created = models.DateField(auto_now_add=True)
    deleted = models.DateField(
        blank=True, null=True
    )  # TODO: Overide Djagno.objects.delete methods to add this date

    def __str__(self):
        return self.name


class RoleAssignment(ModelModifer, models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="assignment")
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    child = models.ForeignKey(
        "children.Child", null=True, blank=True, on_delete=models.SET_NULL
    )
    room = models.ForeignKey(
        "facilities.Room", null=True, blank=True, on_delete=models.SET_NULL
    )
    is_active = models.BooleanField(default=True)
    created = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.last_name}, {self.user.first_name} ({self.role.name})"
